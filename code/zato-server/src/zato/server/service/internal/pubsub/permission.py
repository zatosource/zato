# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubPermission, SecurityBase
from zato.common.odb.query import pubsub_permission_list, pubsub_subscriptions_by_sec_base, pubsub_subscription_topic_names
from zato.common.pubsub.util import get_permissions_for_sec_base
from zato.common.util.sql import set_instance_opaque_attrs
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub permissions.
    """
    input = 'cluster_id', '-cur_page', '-paginate', '-query'
    output = 'id', 'name', 'pattern', 'access_type', 'sec_base_id', 'subscription_count'

    def get_data(self, session):

        query_config = {}

        if self.request.input['query']:
            query_config['query'] = self.request.input['query'].strip().split()

        query_results = pubsub_permission_list(session, self.request.input.cluster_id, False, **query_config)
        processed_results = []

        for result in query_results:
            permission, name, subscription_count = result
            processed_results.append({
                'id': permission.id,
                'name': name,
                'pattern': permission.pattern,
                'access_type': permission.access_type,
                'sec_base_id': permission.sec_base_id,
                'subscription_count': subscription_count
            })

        return processed_results

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission.
    """
    input = 'sec_base_id', 'pattern', 'access_type', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input
        cluster_id = self.server.cluster_id

        # Validate patterns
        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')

        patterns = [item.strip() for item in input.pattern.splitlines() if item.strip()]

        if not patterns:
            raise Exception('At least one valid pattern is required')

        with closing(self.odb.session()) as session:
            try:
                # Check if permission already exists for this security definition and pattern combination
                existing_perm = session.query(PubSubPermission).\
                    filter(PubSubPermission.cluster_id==cluster_id).\
                    filter(PubSubPermission.sec_base_id==input.sec_base_id).\
                    filter(PubSubPermission.pattern==input.pattern).\
                    filter(PubSubPermission.access_type==input.access_type).first()

                if existing_perm:
                    raise Exception('Permission already exists for this security definition, pattern combination and access type')

                # Create the permission
                permission = PubSubPermission()
                permission.sec_base_id = input.sec_base_id
                permission.access_type = input.access_type
                permission.pattern = '\n'.join(patterns) # type: ignore
                permission.cluster_id = cluster_id       # type: ignore

                set_instance_opaque_attrs(permission, input)

                session.add(permission)
                session.commit()

            except Exception:
                session.rollback()
                raise
            else:
                sec_base = session.query(SecurityBase).filter_by(id=input.sec_base_id).one()

                input.id = permission.id
                input.sec_name = sec_base.name
                input.username = sec_base.username

                input.action = PUBSUB.PERMISSION_CREATE.value
                input.cid = self.cid

                self.response.payload.id = permission.id
                self.response.payload.security = sec_base.name

                self.config_dispatcher.publish(input)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    input = 'id', 'sec_base_id', 'pattern', 'access_type', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input

        # Validate patterns
        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')

        patterns = [item.strip() for item in input.pattern.splitlines() if item.strip()]

        if not patterns:
            raise Exception('At least one valid pattern is required')

        with closing(self.odb.session()) as session:
            try:
                permission = session.query(PubSubPermission).filter_by(id=input.id).one()

                # .. capture old values before the update so we can check
                # .. whether subscriptions need to be deleted afterwards ..
                old_sec_base_id = permission.sec_base_id
                cluster_id = permission.cluster_id

                # Update permission fields
                permission.sec_base_id = input.sec_base_id
                permission.access_type = input.access_type
                permission.pattern = '\n'.join(patterns)

                set_instance_opaque_attrs(permission, input)

                session.commit()

            except Exception:
                session.rollback()
                raise
            else:
                input.id = permission.id
                input.sec_name = permission.sec_base.name
                input.username = permission.sec_base.username

                input.action = PUBSUB.PERMISSION_EDIT.value
                input.cid = self.cid

                self.response.payload.id = permission.id
                self.response.payload.security = permission.sec_base.name

                self.config_dispatcher.publish(input)

                # .. GAP 16: if the pattern was narrowed, delete subscriptions
                # .. whose topics no longer have a matching permission ..
                _delete_subs_without_permission(self, session, input.sec_base_id, cluster_id)

                # .. GAP 17: if sec_base_id changed, the old security definition
                # .. lost a permission - check its subscriptions too ..
                if old_sec_base_id != input.sec_base_id:
                    _delete_subs_without_permission(self, session, old_sec_base_id, cluster_id)

# ################################################################################################################################
# ################################################################################################################################

def _topic_is_covered(topic_name:'str', permissions:'anylist') -> 'bool':
    """ Checks whether any of the given permissions cover the topic name for subscribe access.
    """
    # Zato
    from zato.common.pubsub.matcher import PatternMatcher

    if not permissions:
        return False

    matcher = PatternMatcher()
    client_id = f'cover_check.{topic_name}'
    matcher.add_client(client_id, permissions)

    result = matcher.evaluate(client_id, topic_name, 'subscribe')
    return result.is_ok and bool(result.matched_pattern)

# ################################################################################################################################
# ################################################################################################################################

def _delete_subs_without_permission(
    service:'AdminService',
    session:'object',
    sec_base_id:'int',
    cluster_id:'int',
) -> 'None':
    """ Deletes subscriptions whose topics have no matching permission remaining
    for the given security definition.
    """

    # .. get remaining permissions after the change ..
    remaining_permissions = get_permissions_for_sec_base(session, sec_base_id, cluster_id)

    # .. get all subscriptions for this security definition ..
    subscriptions = pubsub_subscriptions_by_sec_base(session, sec_base_id, cluster_id)

    for sub in subscriptions:

        # .. get the topic names for this subscription ..
        topic_names = pubsub_subscription_topic_names(session, sub.id)

        # .. check if at least one topic still has a matching permission ..
        has_permitted_topic = False

        for topic_name in topic_names:
            if _topic_is_covered(topic_name, remaining_permissions):
                has_permitted_topic = True
                break

        # .. if no topic has a permission, delete the subscription ..
        if not has_permitted_topic:
            _ = service.invoke('zato.pubsub.subscription.delete', {'id': sub.id})

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission and cascade-deletes any subscriptions
    that no longer have a matching permission remaining.
    """
    input = 'id',

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            try:
                permission = session.query(PubSubPermission).\
                    filter(PubSubPermission.id==self.request.input.id).\
                    one()

                # .. store permission details before deletion ..
                sec_base_id = permission.sec_base_id
                cluster_id = permission.cluster_id
                self.request.input.sec_base_id = sec_base_id
                self.request.input.pattern = permission.pattern
                self.request.input.access_type = permission.access_type
                self.request.input.username = permission.sec_base.username

                session.delete(permission)
                session.commit()
            except Exception:
                session.rollback()
                raise
            else:

                # .. notify config manager about the permission deletion ..
                self.request.input.action = PUBSUB.PERMISSION_DELETE.value
                self.request.input.cid = self.cid
                self.config_dispatcher.publish(self.request.input)

                # .. now, find and delete any subscriptions that no longer
                # .. have a matching permission for this security definition.
                _delete_subs_without_permission(self, session, sec_base_id, cluster_id)

# ################################################################################################################################
# ################################################################################################################################
