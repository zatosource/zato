# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import Cluster, PubSubTopic
from zato.common.odb.query import pubsub_topic_list
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub topics available.
    """
    _filter_by = PubSubTopic.name, PubSubTopic.description,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_topic_get_list_request'
        response_elem = 'zato_pubsub_topic_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active'
        output_optional = 'description', 'publisher_count', 'subscriber_count'

    def get_data(self, session):
        result = self._search(pubsub_topic_list, session, self.request.input.cluster_id, None, False)
        data = []

        for item, publisher_count, subscriber_count in result:

            item_dict = item.asdict()
            item_dict['publisher_count'] = publisher_count
            item_dict['subscriber_count'] = subscriber_count

            data.append(item_dict)

        return elems_with_opaque(data)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_create_request'
        response_elem = 'zato_pubsub_topic_create_response'
        input_required = 'name', 'is_active'
        input_optional = 'cluster_id', 'description'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input
        cluster_id = self.server.cluster_id

        # Validate topic name
        validate_topic_name(input.name)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name).first()

                if existing_one:
                    raise Exception('Pub/sub topic `{}` already exists in this cluster'.format(input.name))

                topic = PubSubTopic()
                topic.name = input.name
                topic.is_active = input.is_active
                topic.cluster = cluster
                topic.description = input.description

                set_instance_opaque_attrs(topic, input)

                session.add(topic)
                session.commit()

            except Exception:
                self.logger.error('Could not create a pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Note that we don't need to notify the broker about the creation of a new topic.
                # This is because the broker only cares about topics that have subscribers
                # and at this point this topic has none.

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_edit_request'
        response_elem = 'zato_pubsub_topic_edit_response'
        input_required = 'name', 'is_active'
        input_optional = 'id', 'cluster_id', 'description'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input
        input_id = input.get('id')
        cluster_id = self.server.cluster_id

        # Validate topic name
        validate_topic_name(input.name)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(PubSubTopic.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('Pub/sub topic `{}` already exists on this cluster'.format(input.name))

                topic = session.query(PubSubTopic)

                if input_id:
                    topic = topic.filter_by(id=input.id)
                else:
                    topic = topic.filter_by(name=input.name)
                topic = topic.one()

                old_name = topic.name

                set_instance_opaque_attrs(topic, input)

                topic.name = input.name
                topic.is_active = input.is_active
                topic.description = input.description

                session.add(topic)
                session.commit()

            except Exception:
                self.logger.error('Could not update pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Don't notify the broker only if the names are different, otherwise, there's no need to.
                if input.name != old_name:

                    pubsub_msg = Bunch()
                    pubsub_msg.cid = self.cid
                    pubsub_msg.action = PUBSUB.TOPIC_EDIT.value
                    pubsub_msg.new_topic_name = input.name
                    pubsub_msg.old_topic_name = old_name

                    self.broker_client.publish(pubsub_msg)
                    self.broker_client.publish(pubsub_msg, routing_key='pubsub')

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_delete_request'
        response_elem = 'zato_pubsub_topic_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.id==self.request.input.id).\
                    one()

                session.delete(topic)
                session.commit()
            except Exception:
                self.logger.error('Could not delete pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.action = PUBSUB.TOPIC_DELETE.value
                pubsub_msg.topic_name = topic.name

                self.broker_client.publish(pubsub_msg)
                self.broker_client.publish(pubsub_msg, routing_key='pubsub')

# ################################################################################################################################
# ################################################################################################################################

class GetMatches(AdminService):
    """ Returns a list of pub/sub topics matching a given pattern.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_get_matches_request'
        response_elem = 'zato_pubsub_topic_get_matches_response'
        input_required = 'cluster_id', 'pattern'
        output_optional = 'id', 'name', 'description'

    def handle(self):

        input_pattern = self.request.input.pattern
        cluster_id = self.request.input.cluster_id

        # Extract the actual topic pattern (after pub= or sub= if present)
        if input_pattern.startswith('pub=') or input_pattern.startswith('sub='):
            topic_pattern = input_pattern.split('=', 1)[1]
        else:
            topic_pattern = input_pattern

        with closing(self.odb.session()) as session:
            # Get all topics for this cluster
            topics = session.query(PubSubTopic).filter(
                PubSubTopic.cluster_id == cluster_id,
                PubSubTopic.is_active == True
            ).all()

            # Create temporary matcher with the pattern
            matcher = PatternMatcher()
            client_id = 'temp_client'
            permissions = [{
                'pattern': topic_pattern,
                'access_type': 'subscriber'
            }]
            matcher.add_client(client_id, permissions)

            matching_topics = []
            for topic in topics:
                result = matcher.evaluate(client_id, topic.name, 'subscribe')
                if result.is_ok:
                    matching_topics.append({
                        'id': topic.id,
                        'name': topic.name,
                        'description': topic.description or ''
                    })

            self.response.payload = matching_topics

# ################################################################################################################################
# ################################################################################################################################
