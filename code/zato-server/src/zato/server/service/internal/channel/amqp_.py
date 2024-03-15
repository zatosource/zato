# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import CHANNEL
from zato.common.exception import ServiceMissingException
from zato.common.odb.model import ChannelAMQP, Cluster, ConnDefAMQP, Service
from zato.common.odb.query import channel_amqp_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of AMQP channels.
    """
    name = 'zato.channel.amqp.get-list'
    _filter_by = ChannelAMQP.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_channel_amqp_get_list_request'
        response_elem = 'zato_channel_amqp_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'queue', 'consumer_tag_prefix', 'def_name', 'def_id', 'service_name',
            'pool_size', 'ack_mode','prefetch_count')
        output_optional = ('data_format',)

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

    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_amqp_create_request'
        response_elem = 'zato_channel_amqp_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service', 'pool_size',
            'ack_mode','prefetch_count')
        input_optional = ('data_format',)
        output_required = ('id', 'name')

    def handle(self):
        with closing(self.odb.session()) as session:
            input = self.request.input

            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
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
                item.queue = input.queue
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.def_id = input.def_id
                item.service = service
                item.pool_size = input.pool_size
                item.ack_mode = input.ack_mode
                item.prefetch_count = input.prefetch_count
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.AMQP_CREATE.value
                input.def_name = item.def_.name
                input.id = item.id
                input.service_name = service.name
                self.broker_client.publish(input)

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

    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_amqp_edit_request'
        response_elem = 'zato_channel_amqp_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service',
            'pool_size', 'ack_mode','prefetch_count')
        input_optional = ('data_format',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
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
                item.queue = input.queue
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.def_id = input.def_id
                item.service = service
                item.pool_size = input.pool_size
                item.ack_mode = input.ack_mode
                item.prefetch_count = input.prefetch_count
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.AMQP_EDIT.value
                input.def_name = item.def_.name
                input.id = item.id
                input.old_name = old_name
                input.service_name = service.name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update the AMQP definition, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an AMQP channel.
    """
    name = 'zato.channel.amqp.delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_amqp_delete_request'
        response_elem = 'zato_channel_amqp_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(ChannelAMQP).\
                    filter(ChannelAMQP.id==self.request.input.id).\
                    one()

                item_id = item.id
                def_name = item.def_.name

                session.delete(item)
                session.commit()

                self.broker_client.publish({
                    'action': CHANNEL.AMQP_DELETE.value,
                    'name': item.name,
                    'id':item_id,
                    'def_name':def_name,
                })

            except Exception:
                session.rollback()
                self.logger.error('Could not delete the AMQP channel, e:`%s`', format_exc())

                raise

# ################################################################################################################################
