# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import Cluster, PubSubTopic
from zato.common.odb.query import pubsub_topic_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Pub/Sub topics available.
    """
    _filter_by = PubSubTopic.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_topic_get_list_request'
        response_elem = 'zato_pubsub_topic_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active'
        output_optional = 'description'

    def get_data(self, session):
        data = elems_with_opaque(self._search(pubsub_topic_list, session, self.request.input.cluster_id, None, False))
        return data

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Pub/Sub topic.
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

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name).first()

                if existing_one:
                    raise Exception('Pub/Sub topic `{}` already exists in this cluster'.format(input.name))

                topic = PubSubTopic()
                topic.name = input.name
                topic.is_active = input.is_active
                topic.cluster = cluster
                topic.description = input.description

                set_instance_opaque_attrs(topic, input)

                session.add(topic)
                session.commit()

            except Exception:
                self.logger.error('Could not create a Pub/Sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.id = topic.id
                input.action = PUBSUB.TOPIC_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Pub/Sub topic.
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

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(PubSubTopic.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('Pub/Sub topic `{}` already exists on this cluster'.format(input.name))

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
                self.logger.error('Could not update Pub/Sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = PUBSUB.TOPIC_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Pub/Sub topic.
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
                self.logger.error('Could not delete Pub/Sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = PUBSUB.TOPIC_DELETE.value
                self.request.input.name = topic.name
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
