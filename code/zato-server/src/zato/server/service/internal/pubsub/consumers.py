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
from zato.common.broker_message import PUB_SUB_CONSUMER
from zato.common.odb.model import HTTPSOAP, PubSubConsumer, PubSubTopic
from zato.common.odb.query import pubsub_consumer_list
from zato.common.util import new_cid
from zato.server.service import Int, UTC
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub consumers available.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_consumers_get_list_request'
        response_elem = 'zato_pubsub_consumers_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'sec_type', 'client_id', Int('max_depth'), Int('current_depth'),
            Int('in_flight_depth'), 'sub_key', 'delivery_mode', 'topic_name')
        output_optional = (UTC('last_seen'), 'callback')
        output_repeated = True

    def get_data(self, session):
        topic_name = self.request.input.get('topic_name')
        for item in pubsub_consumer_list(session, self.request.input.cluster_id, topic_name):
            item.last_seen = self.pubsub.get_consumer_last_seen(item.client_id)
            item.current_depth = self.pubsub.get_consumer_queue_current_depth(item.sub_key)
            item.in_flight_depth = self.pubsub.get_consumer_queue_in_flight_depth(item.sub_key)
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
        output_required = ('cluster_id', 'name', UTC('last_seen'), Int('current_depth'), Int('in_flight_depth'), 'sub_key')

    def handle(self):
        with closing(self.odb.session()) as session:

            consumer = session.query(PubSubConsumer).\
                filter(PubSubConsumer.id==self.request.input.id).\
                one()

            self.response.payload.cluster_id = consumer.cluster_id
            self.response.payload.name = consumer.sec_def.name
            self.response.payload.last_seen = self.pubsub.get_consumer_last_seen(consumer.sec_def.id)
            self.response.payload.current_depth = self.pubsub.get_consumer_queue_current_depth(consumer.sub_key)
            self.response.payload.in_flight_depth = self.pubsub.get_consumer_queue_in_flight_depth(consumer.sub_key)
            self.response.payload.sub_key = consumer.sub_key

# ################################################################################################################################

class _CreateEdit(AdminService):

    def _validate_input(self, input):

        if not input.delivery_mode in (elem.id for elem in PUB_SUB.DELIVERY_MODE):
            msg = 'Invalid delivery_mode `{}`, expected one of `{}`'.format(input.delivery_mode, PUB_SUB.DELIVERY_MODE)
            raise ValueError(msg)

        if input.delivery_mode == PUB_SUB.DELIVERY_MODE.CALLBACK_URL.id and not input.get('callback_id'):
            msg = 'Callback connection missing on input'
            raise ValueError(msg)

    def _get_callback(self, session, input):

        callback_id = input.get('callback_id')
        if callback_id:
            cb = session.query(HTTPSOAP.name, HTTPSOAP.soap_version).\
                filter(HTTPSOAP.id==callback_id).\
                one()
            callback_name = cb.name
            callback_type = PUB_SUB.CALLBACK_TYPE.OUTCONN_SOAP if bool(cb.soap_version) else \
                PUB_SUB.CALLBACK_TYPE.OUTCONN_PLAIN_HTTP
        else:
            callback_name, callback_type = None, None

        return callback_id, callback_name, callback_type

# ##############################################################################################################################

class Create(_CreateEdit):
    """ Creates a new pub/sub consumer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_create_request'
        response_elem = 'zato_pubsub_consumers_create_response'
        input_required = ('cluster_id', 'client_id', 'topic_name', 'is_active', 'max_depth', 'delivery_mode')
        input_optional = ('callback_id',)
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

                callback = self._get_callback(session, input)

                sub_key = new_cid()
                consumer = PubSubConsumer(
                    None, input.is_active, sub_key, input.max_depth, input.delivery_mode, callback[0],
                    callback[2], topic.id, input.client_id, input.cluster_id)

                session.add(consumer)
                session.commit()

            except Exception, e:
                msg = 'Could not create a consumer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = PUB_SUB_CONSUMER.CREATE.value
                input.client_name = consumer.sec_def.name
                input.sub_key = sub_key
                input.callback_name = callback[1]
                input.callback_type = callback[2]
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
        input_required = ('id', 'is_active', 'max_depth', 'delivery_mode')
        input_optional = ('callback_id',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        self._validate_input(input)

        with closing(self.odb.session()) as session:
            try:

                callback = self._get_callback(session, input)

                # Find a topic by its name so it can be paired with client_id later on
                consumer = session.query(PubSubConsumer).\
                    filter(PubSubConsumer.id==input.id).\
                    one()

                consumer.is_active = input.is_active
                consumer.max_depth = input.max_depth
                consumer.delivery_mode = input.delivery_mode
                consumer.callback_id = callback[0]

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
                msg.action = PUB_SUB_CONSUMER.EDIT.value

                msg.is_active = consumer.is_active
                msg.max_depth = consumer.max_depth
                msg.sub_key = consumer.sub_key
                msg.delivery_mode = consumer.delivery_mode
                msg.callback_id = consumer.callback_id

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                msg.callback_name = callback[1]
                msg.callback_type = callback[2]

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
                msg.action = PUB_SUB_CONSUMER.DELETE.value

                msg.is_active = consumer.is_active
                msg.max_depth = consumer.max_depth
                msg.sub_key = consumer.sub_key

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                self.broker_client.publish(msg)

# ################################################################################################################################

class ClearQueue(AdminService):
    """ Clears out a given consumer's message or in-flight queue by deleting or accepting all the messages it contains,
    respectively. Note that the operation isn't atomic - for in-flight queues, first a list of messages to be cleared is obtained
    and next a call to clear them is issued. For message queues, each message is deleted individually.
    In either case, it's possible the list of messages will change in between the calls and the changes will not be visible
    to the call which deletes them.
    """

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_consumers_clear_queue_request'
        response_elem = 'zato_pubsub_consumers_clear_queue_response'
        input_required = ('queue_type', 'client_id',)

    def handle(self):
        sub_key = self.pubsub.get_consumer_by_client_id(self.request.input.client_id).sub_key

        if self.request.input.queue_type == PUB_SUB.QUEUE_TYPE.IN_FLIGHT:
            self.pubsub.acknowledge(sub_key, self.pubsub.get_consumer_in_flight_message_list(sub_key))
        else:
            self.pubsub.delete_from_consumer_queue(
                sub_key, [item.msg_id for item in self.pubsub.get_consumer_queue_message_list(sub_key)])

# ################################################################################################################################
