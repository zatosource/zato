# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from urllib.parse import quote

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubSubscription, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.util.api import new_sub_key
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

def get_topic_link(topic_name:'str') -> 'str':
    topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}">{}</a>'.format(quote(topic_name), topic_name)
    return topic_link

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Pub/Sub subscriptions available.
    """
    _filter_by = PubSubSubscription.sub_key,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_subscription_get_list_request'
        response_elem = 'zato_pubsub_subscription_get_list_response'
        input_required = 'cluster_id'
        output_required = 'id', 'sub_key', 'is_active', 'created', 'pattern_matched', AsIs('topic_name'), 'sec_name', \
            'delivery_type', 'rest_push_endpoint_id'
        output_optional = 'rest_push_endpoint_name'

    def get_data(self, session):

        data = []
        data = elems_with_opaque(data)
        return data

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_create_request'
        response_elem = 'zato_pubsub_subscription_create_response'
        input_required = 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name', 'delivery_type'

    def handle(self):
        with closing(self.odb.session()) as session:
            pass

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_edit_request'
        response_elem = 'zato_pubsub_subscription_edit_response'
        input_required = 'sub_key', 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', AsIs('topic_name_list'), 'topic_name', 'sec_name', 'delivery_type', 'is_active'

    def handle(self):
        with closing(self.odb.session()) as session:
            pass

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

                # Find all subscriptions with the same sub_key and sec_base_id (multi-topic subscription group)
                related_subscriptions = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.sub_key==subscription.sub_key).\
                    filter(PubSubSubscription.sec_base_id==subscription.sec_base_id).\
                    all()

                # Delete all related subscriptions
                for related_sub in related_subscriptions:
                    session.delete(related_sub)

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
