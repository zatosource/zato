# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import query_parameters
from zato.common.broker_message import CHANNEL
from zato.common.exception import ServiceMissingException
from zato.common.odb.model import ChannelAMQP, Cluster, Service
from zato.common.odb.query import channel_amqp_list
from zato.server.service.internal import AdminService

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of AMQP channels.
    """
    name = 'zato.channel.amqp.get-list'
    _filter_by = ChannelAMQP.name,

    input = 'cluster_id', *query_parameters
    output = 'id', 'name', 'address', 'username', 'password', 'is_active', 'queue', 'consumer_tag_prefix', \
        'service_name', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format'

    def get_data(self, session):
        return self._search(channel_amqp_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new AMQP channel.
    """
    name = 'zato.channel.amqp.create'

    input = 'cluster_id', 'name', 'is_active', 'address', 'username', 'password', 'queue', 'consumer_tag_prefix', \
        'service', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format'
    output = 'id', 'name'

    def handle(self):
        with closing(self.odb.session()) as session:

            input = self.request.input

            input.frame_max = 131072
            input.heartbeat = 30

            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ChannelAMQP.name==input.name).\
                first()

            if existing_one:
                raise Exception('An AMQP channel `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).\
                first()

            if not service:
                msg = 'Service `{}` does not exist in this cluster'.format(input.service)
                raise ServiceMissingException(self.cid, msg)

            try:
                item = ChannelAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address # type: ignore
                item.username = input.username # type: ignore
                item.password = input.password
                item.queue = input.queue # type: ignore
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.service = service
                item.pool_size = input.pool_size
                item.ack_mode = input.ack_mode
                item.prefetch_count = input.prefetch_count
                item.data_format = input.data_format
                item.frame_max = input.frame_max # type: ignore
                item.heartbeat = input.heartbeat # type: ignore

                session.add(item)
                session.commit()

                input.action = CHANNEL.AMQP_CREATE.value
                input.id = item.id
                input.service_name = service.name
                self.config_dispatcher.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not create an AMQP channel, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an AMQP channel.
    """
    name = 'zato.channel.amqp.edit'

    input = 'id', 'cluster_id', 'name', 'is_active', 'address', 'username', 'password', 'queue', \
        'consumer_tag_prefix', 'service', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format'
    output = 'id', 'name'

    def handle(self):

        input = self.request.input

        with closing(self.odb.session()) as session:
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ChannelAMQP.name==input.name).\
                filter(ChannelAMQP.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An AMQP channel `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).\
                first()

            if not service:
                msg = 'Service [{0}] does not exist in this cluster'.format(input.service)
                raise Exception(msg)

            try:
                item = session.query(ChannelAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.username = input.username
                item.password = input.password
                item.queue = input.queue
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.service = service
                item.pool_size = input.pool_size
                item.ack_mode = input.ack_mode
                item.prefetch_count = input.prefetch_count
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.AMQP_EDIT.value
                input.id = item.id
                input.old_name = old_name
                input.service_name = service.name
                self.config_dispatcher.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('AMQP channel could not be updated, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an AMQP channel.
    """
    name = 'zato.channel.amqp.delete'

    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(ChannelAMQP).\
                    filter(ChannelAMQP.id==self.request.input.id).\
                    one()

                item_id = item.id

                session.delete(item)
                session.commit()

                self.config_dispatcher.publish({
                    'action': CHANNEL.AMQP_DELETE.value,
                    'name': item.name,
                    'id':item_id,
                })

            except Exception:
                session.rollback()
                self.logger.error('Could not delete the AMQP channel, e:`%s`', format_exc())

                raise

# ################################################################################################################################
