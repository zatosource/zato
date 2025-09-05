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
from zato.common.odb.query import pubsub_permission_list
from zato.common.util.sql import set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub permissions.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_permission_get_list_request'
        response_elem = 'zato_pubsub_permission_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'pattern', 'access_type', 'sec_base_id', 'subscription_count'

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_create_request'
        response_elem = 'zato_pubsub_permission_create_response'
        input_required = 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = 'id', 'name'

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

                self.response.payload.id = permission.id
                self.response.payload.name = sec_base.name

                self.broker_client.publish(input)
                self.broker_client.publish_to_pubsub(input)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_edit_request'
        response_elem = 'zato_pubsub_permission_edit_response'
        input_required = 'id', 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id',
        output_required = 'id', 'name'

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

                self.response.payload.id = permission.id
                self.response.payload.name = permission.sec_base.name

                self.broker_client.publish(input)
                self.broker_client.publish_to_pubsub(input)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_delete_request'
        response_elem = 'zato_pubsub_permission_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                permission = session.query(PubSubPermission).\
                    filter(PubSubPermission.id==self.request.input.id).\
                    one()

                # Store permission details before deletion
                self.request.input.sec_base_id = permission.sec_base_id
                self.request.input.pattern = permission.pattern
                self.request.input.access_type = permission.access_type

                session.delete(permission)
                session.commit()
            except Exception:
                session.rollback()
                raise
            else:
                self.request.input.action = PUBSUB.PERMISSION_DELETE.value
                self.request.input.username = permission.sec_base.username

                self.broker_client.publish(self.request.input)
                self.broker_client.publish_to_pubsub(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
