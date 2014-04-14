# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common import PUB_SUB
from zato.common.broker_message import PUB_SUB_CONSUMER, PUB_SUB_TOPIC
from zato.common.odb.model import Cluster, PubSubConsumer, PubSubTopic
from zato.common.odb.query import pubsub_consumer_list
from zato.common.pubsub import Client
from zato.common.util import new_cid
from zato.server.service import AsIs, Int, UTC
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub consumers available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_get_list_request'
        response_elem = 'zato_pubsub_consumers_get_list_response'
        input_required = ('cluster_id', 'topic_name')
        output_required = ('id', 'name', 'is_active', 'sec_type', Int('max_backlog'), Int('current_depth'), 
            'sub_key', 'delivery_mode')
        output_optional = (UTC('last_seen'), 'callback')

    def get_data(self, session):
        for item in pubsub_consumer_list(session, self.request.input.cluster_id, self.request.input.topic_name)[0]:
            item.last_seen = self.pubsub.get_consumer_last_seen(item.client_id)
            item.current_depth = self.pubsub.get_consumer_queue_current_depth(item.sub_key)
            yield item

    def handle(self):
        with closing(self.odb.session()) as session:
            for item in self.get_data(session):
                self.response.payload.append(item)

# ################################################################################################################################

class GetInfo(AdminService):
    """ Returns basic information regarding a consumer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_get_info_request'
        response_elem = 'zato_pubsub_consumers_get_info_response'
        input_required = ('id',)
        output_required = ('cluster_id', 'name', UTC('last_seen'), Int('current_depth'), 'sub_key')

    def handle(self):
        with closing(self.odb.session()) as session:

            consumer = session.query(PubSubConsumer).\
                filter(PubSubConsumer.id==self.request.input.id).\
                one()

            self.response.payload.cluster_id = consumer.cluster_id
            self.response.payload.name = consumer.sec_def.name
            self.response.payload.last_seen = self.pubsub.get_consumer_last_seen(consumer.sec_def.id)
            self.response.payload.current_depth = self.pubsub.get_consumer_queue_current_depth(consumer.sub_key)
            self.response.payload.sub_key = consumer.sub_key
    
# ################################################################################################################################

class _CreateEdit(AdminService):

    def _validate_input(self, input):

        if not input.delivery_mode in (elem.id for elem in PUB_SUB.DELIVERY_MODE):
            msg = 'Invalid delivery_mode `{}`, expected one of `{}`'.format(input.delivery_mode, PUB_SUB.DELIVERY_MODE)
            raise ValueError(msg)

        if input.delivery_mode == PUB_SUB.DELIVERY_MODE.CALLBACK_URL.id and not input.get('http_soap_id'):
            msg = 'HTTP callback connection missing on input'
            raise ValueError(msg)

# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new pub/sub consumer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_create_request'
        response_elem = 'zato_pubsub_consumers_create_response'
        input_required = ('cluster_id', 'client_id', 'topic_name', 'is_active', 'max_backlog', 'delivery_mode')
        input_optional = ('http_soap_id',)
        output_required = ('id', 'name', 'sub_key')

    def handle(self):
        input = self.request.input
        self._validate_input(input)

        with closing(self.odb.session()) as session:
            try:
                # Find a topic by its name so it can be paired with client_id later on
                topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.cluster_id==input.cluster_id).\
                    filter(PubSubTopic.name==input.topic_name).\
                    one()

                sub_key = new_cid()
                consumer = PubSubConsumer(
                    None, input.is_active, sub_key, input.max_backlog, input.delivery_mode, input.get('http_soap_id'),
                    topic.id, input.client_id, input.cluster_id)

                session.add(consumer)
                session.commit()

            except Exception, e:
                msg = 'Could not create a consumer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise 
            else:
                input.action = PUB_SUB_CONSUMER.CREATE
                input.client_name = consumer.sec_def.name
                input.sub_key = sub_key
                self.broker_client.publish(input)

            self.response.payload.id = consumer.id
            self.response.payload.name = consumer.sec_def.name
            self.response.payload.sub_key = sub_key

# ################################################################################################################################

class Edit(_CreateEdit):
    """ Edits a pub/sub consumer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_edit_request'
        response_elem = 'zato_pubsub_consumers_edit_response'
        input_required = ('id', 'is_active', 'max_backlog', 'delivery_mode')
        input_optional = ('http_soap_id',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        self._validate_input(input)

        with closing(self.odb.session()) as session:
            try:
                # Find a topic by its name so it can be paired with client_id later on
                consumer = session.query(PubSubConsumer).\
                    filter(PubSubConsumer.id==input.id).\
                    one()

                consumer.is_active = input.is_active
                consumer.max_backlog = input.max_backlog
                consumer.delivery_mode = input.delivery_mode
                consumer.http_soap_id = input.get('http_soap_id')

                client_id = consumer.sec_def.id
                client_name = consumer.sec_def.name

                topic_id = consumer.topic.id
                topic_name = consumer.topic.name

                session.add(consumer)
                session.commit()

            except Exception, e:
                msg = 'Could not edit a consumer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise 
            else:
                msg = Bunch()
                msg.action = PUB_SUB_CONSUMER.EDIT

                msg.is_active = consumer.is_active
                msg.max_backlog = consumer.max_backlog
                msg.sub_key = consumer.sub_key
                msg.delivery_mode = consumer.delivery_mode
                msg.http_soap_id = consumer.http_soap_id

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                self.broker_client.publish(msg)

            self.response.payload.id = consumer.id
            self.response.payload.name = consumer.sec_def.name

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a consumer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_delete_request'
        response_elem = 'zato_pubsub_consumers_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                consumer = session.query(PubSubConsumer).\
                    filter(PubSubConsumer.id==self.request.input.id).\
                    one()

                client_id = consumer.sec_def.id
                client_name = consumer.sec_def.name

                topic_id = consumer.topic.id
                topic_name = consumer.topic.name

                session.delete(consumer)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the consumer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                msg = Bunch()
                msg.action = PUB_SUB_CONSUMER.DELETE

                msg.is_active = consumer.is_active
                msg.max_backlog = consumer.max_backlog
                msg.sub_key = consumer.sub_key

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                self.broker_client.publish(msg)

# ################################################################################################################################
