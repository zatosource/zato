# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import MESSAGE_TYPE, CHANNEL
from zato.common.odb.model import ChannelZMQ, Cluster, Service
from zato.common.odb.query import channel_zmq_list
from zato.server.connection.zmq_.channel import start_connector
from zato.server.service.internal import AdminService, AdminSIO

class GetList(AdminService):
    """ Returns a list of ZeroMQ channels.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_zmq_get_list_request'
        response_elem = 'zato_channel_zmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'sub_key', 'service_name', 'data_format')
        
    def get_data(self, session):
        return channel_zmq_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
        
class Create(AdminService):
    """ Creates a new ZeroMQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_zmq_create_request'
        response_elem = 'zato_channel_zmq_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service')
        input_optional = ('sub_key', 'data_format')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            existing_one = session.query(ChannelZMQ.id).\
                filter(ChannelZMQ.cluster_id==input.cluster_id).\
                filter(ChannelZMQ.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('A ZeroMQ channel [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)
            
            try:
                item = ChannelZMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.sub_key = input.sub_key
                item.cluster_id = input.cluster_id
                item.service = service
                item.data_format = input.data_format
                
                session.add(item)
                session.commit()
                
                if item.is_active:
                    start_connector(self.server.repo_location, item.id)
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                
            except Exception, e:
                msg = 'Could not create a ZeroMQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates a ZeroMQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_zmq_edit_request'
        response_elem = 'zato_channel_zmq_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service')
        input_optional = ('sub_key', 'data_format')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            existing_one = session.query(ChannelZMQ.id).\
                filter(ChannelZMQ.cluster_id==input.cluster_id).\
                filter(ChannelZMQ.name==input.name).\
                filter(ChannelZMQ.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('A ZeroMQ channel [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)
            
            try:
                item = session.query(ChannelZMQ).filter_by(id=input.id).one()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.sub_key = input.sub_key
                item.service = service
                item.data_format = input.data_format
                
                session.add(item)
                session.commit()
                
                input.action = CHANNEL.ZMQ_EDIT
                input.sub_key = input.get('sub_key', b'')
                input.service = service.impl_name
                self.broker_client.publish(input, msg_type=MESSAGE_TYPE.TO_ZMQ_CONSUMING_CONNECTOR_ALL)
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                
            except Exception, e:
                msg = 'Could not update the ZeroMQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes a ZeroMQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_zmq_delete_request'
        response_elem = 'zato_channel_zmq_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(ChannelZMQ).\
                    filter(ChannelZMQ.id==self.request.input.id).\
                    one()
                
                session.delete(item)
                session.commit()

                msg = {'action': CHANNEL.ZMQ_DELETE, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_ZMQ_CONSUMING_CONNECTOR_ALL)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the ZeroMQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
