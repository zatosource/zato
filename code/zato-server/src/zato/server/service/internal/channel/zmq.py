# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, CHANNEL
from zato.common.odb.model import ChannelZMQ, Cluster, Service
from zato.common.odb.query import channel_zmq_list
from zato.server.connection.zmq_.channel import start_connector
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of ZeroMQ channels.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'sub_key', 'service_name')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = channel_zmq_list(session, self.request.input.cluster_id, False)
        
class Create(AdminService):
    """ Creates a new ZeroMQ channel.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service')
        input_optional = ('sub_key',)
        output_required = ('id',)

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
                
                session.add(item)
                session.commit()
                
                start_connector(self.server.repo_location, item.id)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not create a ZeroMQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates a ZeroMQ channel.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service')
        input_optional = ('sub_key',)
        output_required = ('id',)

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
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.sub_key = input.sub_key
                item.service = service
                
                session.add(item)
                session.commit()
                
                input.action = CHANNEL.ZMQ_EDIT
                input.sub_key = input.get('sub_key', b'')
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not update the ZeroMQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes a ZeroMQ channel.
    """
    class SimpleIO:
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
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the ZeroMQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
