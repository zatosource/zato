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
from zato.common.broker_message import PUB_SUB_PRODUCER
from zato.common.odb.model import PubSubProducer, PubSubTopic
from zato.common.odb.query import pubsub_producer_list
from zato.server.service import UTC
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub producers available.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_producers_get_list_request'
        response_elem = 'zato_pubsub_producers_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'sec_type', 'topic_name')
        output_optional = (UTC('last_seen'),)
        output_repeated = True

    def get_data(self, session):
        topic_name = self.request.input.get('topic_name')
        for item in pubsub_producer_list(session, self.request.input.cluster_id, topic_name):
            item.last_seen = self.pubsub.get_producer_last_seen(item.client_id)
            yield item

    def handle(self):
        with closing(self.odb.session()) as session:
            for item in self.get_data(session):
                self.response.payload.append(item)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub producer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_producers_create_request'
        response_elem = 'zato_pubsub_producers_create_response'
        input_required = ('cluster_id', 'client_id', 'topic_name', 'is_active')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                # Find a topic by its name so it can be paired with client_id later on
                topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.cluster_id==input.cluster_id).\
                    filter(PubSubTopic.name==input.topic_name).\
                    one()

                producer = PubSubProducer(None, input.is_active, topic.id, input.client_id, input.cluster_id)

                session.add(producer)
                session.commit()

            except Exception, e:
                msg = 'Could not create a producer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = PUB_SUB_PRODUCER.CREATE.value
                input.name = producer.sec_def.name
                self.broker_client.publish(input)

            self.response.payload.id = producer.id
            self.response.payload.name = producer.sec_def.name

# ################################################################################################################################

class GetInfo(AdminService):
    """ Returns basic information regarding a producer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_get_info_request'
        response_elem = 'zato_pubsub_topics_get_info_response'
        input_required = ('id',)
        output_required = ('cluster_id', 'name', UTC('last_seen'))

    def handle(self):
        with closing(self.odb.session()) as session:

            producer = session.query(PubSubProducer).\
                filter(PubSubProducer.id==self.request.input.id).\
                one()

            self.response.payload.cluster_id = producer.cluster_id
            self.response.payload.name = producer.sec_def.name
            self.response.payload.last_seen = self.pubsub.get_producer_last_seen(producer.sec_def.id)

# ################################################################################################################################

class Edit(AdminService):
    """ Edits a new pub/sub producer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_producers_edit_request'
        response_elem = 'zato_pubsub_producers_edit_response'
        input_required = ('id', 'is_active')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                # Find a topic by its name so it can be paired with client_id later on
                producer = session.query(PubSubProducer).\
                    filter(PubSubProducer.id==input.id).\
                    one()

                producer.is_active = input.is_active

                client_id = producer.sec_def.id
                client_name = producer.sec_def.name

                topic_id = producer.topic.id
                topic_name = producer.topic.name

                session.add(producer)
                session.commit()

            except Exception, e:
                msg = 'Could not edit a producer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                msg = Bunch()
                msg.action = PUB_SUB_PRODUCER.EDIT.value

                msg.is_active = producer.is_active

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                self.broker_client.publish(msg)

            self.response.payload.id = producer.id
            self.response.payload.name = producer.sec_def.name

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a producer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_producers_delete_request'
        response_elem = 'zato_pubsub_producers_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                producer = session.query(PubSubProducer).\
                    filter(PubSubProducer.id==self.request.input.id).\
                    one()

                client_id = producer.sec_def.id
                client_name = producer.sec_def.name

                topic_id = producer.topic.id
                topic_name = producer.topic.name

                session.delete(producer)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the producer, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                msg = Bunch()
                msg.action = PUB_SUB_PRODUCER.DELETE.value

                msg.client_id = client_id
                msg.client_name = client_name

                msg.topic_id = topic_id
                msg.topic_name = topic_name

                self.broker_client.publish(msg)

# ################################################################################################################################
