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
from zato.common.broker_message import PUB_SUB_TOPIC
from zato.common.odb.model import Cluster, PubSubTopic
from zato.common.odb.query import pubsub_topic_list
from zato.server.service import AsIs, Int, UTC
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of topics available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_get_list_request'
        response_elem = 'zato_pubsub_topics_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', Int('current_depth'), Int('max_depth'),
            Int('consumers_count'), Int('producers_count'))
        output_optional = (UTC('last_pub_time'),)

    def get_data(self, session):
        for item in pubsub_topic_list(session, self.request.input.cluster_id, False):
            item.current_depth = self.pubsub.get_topic_depth(item.name)
            item.consumers_count = self.pubsub.get_consumers_count(item.name)
            item.producers_count = self.pubsub.get_producers_count(item.name)
            item.last_pub_time = self.pubsub.get_last_pub_time(item.name)
            yield item

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class GetInfo(AdminService):
    """ Returns basic information regarding a topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_get_info_request'
        response_elem = 'zato_pubsub_topics_get_info_response'
        input_required = ('cluster_id', 'name')
        output_required = (Int('current_depth'), Int('consumers_count'), Int('producers_count'), UTC('last_pub_time'))

    def handle(self):
        self.response.payload.current_depth = self.pubsub.get_topic_depth(self.request.input.name)
        self.response.payload.consumers_count = self.pubsub.get_consumers_count(self.request.input.name)
        self.response.payload.producers_count = self.pubsub.get_producers_count(self.request.input.name)
        self.response.payload.last_pub_time = self.pubsub.get_last_pub_time(self.request.input.name)

# ################################################################################################################################

class Publish(AdminService):
    """ Publishes a messages to a topic of choice. If not client_id is given on input the message is published using
    an internal account.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_publish_request'
        response_elem = 'zato_pubsub_topics_publish_response'
        input_required = ('cluster_id', 'name', 'mime_type', Int('priority'), Int('expiration'))
        input_optional = ('client_id', 'payload')
        output_required = (AsIs('msg_id'),)

    def handle(self):
        client_id = self.request.input.get('client_id') or self.pubsub.get_default_producer().id

        self.response.payload.msg_id = self.pubsub.publish(self.request.input.payload, self.request.input.name,
           self.request.input.mime_type, self.request.input.priority, self.request.input.expiration, client_id=client_id)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_create_request'
        response_elem = 'zato_pubsub_topics_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'max_depth')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a topic of that name before committing
                # any stuff into the database.
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(PubSubTopic.name==input.name).first()

                if existing_one:
                    raise Exception('Topic `{}` already exists on this cluster'.format(input.name))

                topic = PubSubTopic(None, input.name, input.is_active, input.max_depth, cluster.id)

                session.add(topic)
                session.commit()

                # Now that the topic is added we can let our own internal producer publish to it.
                create_prod_req = Bunch()
                create_prod_req.cluster_id = input.cluster_id
                create_prod_req.client_id = self.server.config.pubsub.default_producer.id
                create_prod_req.topic_name = topic.name
                create_prod_req.is_active = True

                self.invoke('zato.pubsub.producers.create', create_prod_req)

            except Exception, e:
                msg = 'Could not create a topic, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise 
            else:
                input.action = PUB_SUB_TOPIC.CREATE
                self.broker_client.publish(input)

            self.response.payload.id = topic.id
            self.response.payload.name = topic.name

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_edit_request'
        response_elem = 'zato_pubsub_topics_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'max_depth')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(PubSubTopic.name==input.name).\
                    filter(PubSubTopic.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('Topic `{}` already exists on this cluster'.format(input.name))

                topic = session.query(PubSubTopic).filter_by(id=input.id).one()
                old_name = topic.name

                topic.is_active = input.is_active
                topic.max_depth = input.max_depth

                session.add(topic)
                session.commit()

            except Exception, e:
                msg = 'Could not update the topic, e:`{}'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise 
            else:
                input.action = PUB_SUB_TOPIC.EDIT
                input.old_name = old_name
                input.name = topic.name
                self.broker_client.publish(input)

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topics_delete_request'
        response_elem = 'zato_pubsub_topics_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.id==self.request.input.id).\
                    one()

                session.delete(topic)
                session.commit()

            except Exception, e:
                msg = 'Could not delete the topic, e:`{}`'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = PUB_SUB_TOPIC.DELETE
                self.request.input.name = topic.name
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
