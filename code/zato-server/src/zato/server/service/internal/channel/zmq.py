# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelZMQ, Cluster, Service as ServiceModel
from zato.common.odb.query import channel_zmq_list
from zato.common.util.api import is_port_taken, require_tcp_port
from zato.common.simpleio_ import drop_sio_elems
from zato.server.service import Int, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class _UpdateSIO(AdminSIO):
    """ Common class for Create, Edit and Start SIO parameters.
    """
    input_required = ('cluster_id', 'name', 'is_active', 'address', 'socket_type', 'socket_method', 'pool_strategy', \
        'service_source', 'service')
    input_optional = ('id', 'sub_key', 'data_format', 'msg_source')

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of ZeroMQ channels.
    """
    _filter_by = ChannelZMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_channel_zmq_get_list_request'
        response_elem = 'zato_channel_zmq_get_list_response'
        input_required = ('cluster_id',)
        input_optional = GetListAdminSIO.input_optional + ('msg_source',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'socket_method',
            'service_name', 'pool_strategy', 'service_source', 'data_format')
        output_optional = ('sub_key',)

    def get_data(self, session):
        return self._search(channel_zmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new ZeroMQ channel.
    """
    class SimpleIO(_UpdateSIO):
        request_elem = 'zato_channel_zmq_create_request'
        response_elem = 'zato_channel_zmq_create_response'
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        require_tcp_port(input.address)

        with closing(self.odb.session()) as session:
            existing_one = session.query(ChannelZMQ.id).\
                filter(ChannelZMQ.cluster_id==input.cluster_id).\
                filter(ChannelZMQ.name==input.name).\
                first()

            if existing_one:
                raise Exception('A ZeroMQ channel `{}` already exists in this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(ServiceModel).\
                filter(Cluster.id==input.cluster_id).\
                filter(ServiceModel.cluster_id==Cluster.id).\
                filter(ServiceModel.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist in this cluster'.format(input.service)
                raise Exception(msg)

            try:

                sub_key = input.get('sub_key', b'')

                item = ChannelZMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.socket_method = input.socket_method
                item.sub_key = sub_key
                item.cluster_id = input.cluster_id
                item.service = service
                item.pool_strategy = input.pool_strategy
                item.service_source = input.service_source
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.ZMQ_CREATE.value
                input.sub_key = sub_key
                input.service_name = service.name
                input.source_server = self.server.get_full_name()
                input.id = item.id
                input.config_cid = 'channel.zmq.create.{}.{}'.format(input.source_server, self.cid)

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('ZeroMQ channel could not be created, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a ZeroMQ channel.
    """
    class SimpleIO(_UpdateSIO):
        request_elem = 'zato_channel_zmq_edit_request'
        response_elem = 'zato_channel_zmq_edit_response'
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        require_tcp_port(input.address)

        with closing(self.odb.session()) as session:
            existing_one = session.query(ChannelZMQ.id).\
                filter(ChannelZMQ.cluster_id==input.cluster_id).\
                filter(ChannelZMQ.name==input.name).\
                filter(ChannelZMQ.id!=input.id).\
                first()

            if existing_one:
                raise Exception('A ZeroMQ channel `{}` already exists in this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(ServiceModel).\
                filter(Cluster.id==input.cluster_id).\
                filter(ServiceModel.cluster_id==Cluster.id).\
                filter(ServiceModel.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist in this cluster'.format(input.service)
                raise Exception(msg)

            try:
                item = session.query(ChannelZMQ).filter_by(id=input.id).one()

                if item.socket_type != input.socket_type:
                    raise ValueError('Cannot change a ZeroMQ channel\'s socket type')

                old_socket_type = item.socket_type
                old_name = item.name

                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.socket_method = input.socket_method
                item.sub_key = input.sub_key
                item.service = service
                item.pool_strategy = input.pool_strategy
                item.service_source = input.service_source
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.ZMQ_EDIT.value
                input.sub_key = input.get('sub_key', b'')
                input.service_name = service.name
                input.source_server = self.server.get_full_name()
                input.id = item.id
                input.config_cid = 'channel.zmq.edit.{}.{}'.format(input.source_server, self.cid)
                input.old_socket_type = old_socket_type
                input.old_name = old_name

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('ZeroMQ channel could not be created, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a ZeroMQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_zmq_delete_request'
        response_elem = 'zato_channel_zmq_delete_response'
        input_required = ('id',)
        input_optional = ('msg_source',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(ChannelZMQ).\
                    filter(ChannelZMQ.id==self.request.input.id).\
                    one()

                session.delete(item)
                session.commit()

                source_server = self.server.get_full_name()

                msg = {
                    'action': CHANNEL.ZMQ_DELETE.value,
                    'name': item.name,
                    'id':item.id,
                    'source_server': source_server,
                    'socket_type': item.socket_type,
                    'config_cid': 'channel.zmq.delete.{}.{}'.format(source_server, self.cid)
                }
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                self.logger.error('ZeroMQ channel could not be deleted, e:`%s`', format_exc())

                raise

# ################################################################################################################################

class Start(Service):
    """ Starts a ZeroMQ channel.
    """
    class SimpleIO(_UpdateSIO):
        input_required = _UpdateSIO.input_required + ('id', 'config_cid')
        input_optional = tuple(drop_sio_elems(_UpdateSIO.input_optional, 'id')) + (Int('bind_port'), 'service_name')
        request_elem = 'zato_channel_zmq_start_request'
        response_elem = 'zato_channel_zmq_start_response'

    def handle(self):
        input = self.request.input
        if input.bind_port and is_port_taken(input.bind_port):
            self.logger.warning('Cannot bind Zero MQ channel `%s` to TCP port %s (already taken)', input.name, input.bind_port)
        else:
            self.server.worker_store.zmq_channel_create(self.request.input)

# ################################################################################################################################
