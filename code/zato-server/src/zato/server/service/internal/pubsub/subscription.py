# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubSubscription
from zato.common.odb.query import pubsub_subscription_list
from zato.common.util.sql import elems_with_opaque
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Pub/Sub subscriptions available.
    """
    _filter_by = PubSubSubscription.sub_key,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_subscription_get_list_request'
        response_elem = 'zato_pubsub_subscription_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'sub_key', 'is_active', 'created', 'pattern_matched', 'topic_name', 'sec_name'

    def get_data(self, session):
        result = self._search(pubsub_subscription_list, session, self.request.input.cluster_id, None, False)
        data = []

        for subscription, topic_name, sec_name in result:
            item_dict = subscription.asdict()
            item_dict['topic_name'] = topic_name
            item_dict['sec_name'] = sec_name
            data.append(item_dict)

        return elems_with_opaque(data)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_create_request'
        response_elem = 'zato_pubsub_subscription_create_response'
        input_required = 'cluster_id', 'topic_id', 'sec_base_id'
        input_optional = 'is_active',
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name'

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.topic_id==self.request.input.topic_id).\
                    filter(PubSubSubscription.sec_base_id==self.request.input.sec_base_id).\
                    first()

                if existing_one:
                    raise Exception('A subscription already exists for this topic and security definition')

                # Generate unique subscription key
                import uuid
                sub_key = 'zpsk.rest.' + uuid.uuid4().hex[:6]

                item = PubSubSubscription()
                item.cluster_id = self.request.input.cluster_id
                item.topic_id = self.request.input.topic_id
                item.sec_base_id = self.request.input.sec_base_id
                item.sub_key = sub_key
                item.is_active = self.request.input.get('is_active', True)
                # Ensure pattern_matched is set to default value immediately before save
                item.pattern_matched = '*'

                session.add(item)
                session.commit()

                # Get topic and security names for the response
                topic = session.query(PubSubTopic).filter(PubSubTopic.id == item.topic_id).first()
                security = session.query(HTTPBasicAuth).filter(HTTPBasicAuth.id == item.sec_base_id).first()

                self.response.payload.id = item.id
                self.response.payload.sub_key = item.sub_key
                self.response.payload.is_active = item.is_active
                self.response.payload.created = item.creation_time.isoformat()
                self.response.payload.topic_name = topic.name
                self.response.payload.sec_name = security.name

            except Exception:
                self.logger.error('Could not create Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_edit_request'
        response_elem = 'zato_pubsub_subscription_edit_response'
        input_required = 'id', 'cluster_id', 'topic_id', 'sec_base_id'
        input_optional = 'is_active',
        output_required = 'id', 'sub_key'

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.topic_id==self.request.input.topic_id).\
                    filter(PubSubSubscription.sec_base_id==self.request.input.sec_base_id).\
                    filter(PubSubSubscription.id!=self.request.input.id).\
                    first()

                if existing_one:
                    raise Exception('A subscription already exists for this topic and security definition')

                item = session.query(PubSubSubscription).filter(PubSubSubscription.id==self.request.input.id).one()
                item.topic_id = self.request.input.topic_id
                item.sec_base_id = self.request.input.sec_base_id
                item.pattern_matched = '*'  # Set explicitly to default pattern
                item.is_active = self.request.input.get('is_active', True)

                session.add(item)
                session.commit()

                self.response.payload.id = item.id
                self.response.payload.sub_key = item.sub_key

            except Exception:
                self.logger.error('Could not update Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_delete_request'
        response_elem = 'zato_pubsub_subscription_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                subscription = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.id==self.request.input.id).\
                    one()

                session.delete(subscription)
                session.commit()
            except Exception:
                self.logger.error('Could not delete Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = PUBSUB.SUBSCRIPTION_DELETE.value
                self.request.input.sub_key = subscription.sub_key
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
