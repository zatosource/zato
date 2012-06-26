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

# Zato
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.odb.model import ChannelWMQ, Cluster, ConnDefWMQ, Service
from zato.common.odb.query import channel_jms_wmq_list
from zato.server.connection.jms_wmq.channel import start_connector
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of JMS WebSphere MQ channels.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'queue', 'service_name', 'def_name', 'def_id', 'data_format')
        
    def get_data(self, session):
        return channel_jms_wmq_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
        
class Create(AdminService):
    """ Creates a new WebSphere MQ channel.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'queue',  'service')
        input_optional = ('data_format',)
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('A WebSphere MQ channel [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                logger.error(msg)
                raise Exception(msg)
            
            try:

                item = ChannelWMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = input.def_id
                item.service = service
                item.data_format = input.data_format
                
                session.add(item)
                session.commit()
                
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not create a WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates a JMS WebSphere MQ channel.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue',  'service')
        input_optional = ('data_format',)
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==input.name).\
                filter(ChannelWMQ.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('A JMS WebSphere MQ channel [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)
            
            try:
                item = session.query(ChannelWMQ).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = input.def_id
                item.service = service
                item.data_format = input.data_format
                
                session.add(item)
                session.commit()
                
                input.action = CHANNEL.JMS_WMQ_EDIT
                input.old_name = old_name
                input.service = service.impl_name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an JMS WebSphere MQ channel.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(ChannelWMQ).\
                    filter(ChannelWMQ.id==self.request.input.id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': CHANNEL.JMS_WMQ_DELETE, 'name': def_.name, 'id':def_.id}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
