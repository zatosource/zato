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

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.odb.model import ChannelAMQP, Cluster, ConnDefAMQP, Service
from zato.common.odb.query import channel_amqp_list
from zato.server.connection.amqp.channel import start_connector
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of AMQP channels.
    """
    class SimpleIO:
        input_required = ('cluster_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = channel_amqp_list(session, self.request.input.cluster_id, False)
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.queue = db_item.queue
                item.consumer_tag_prefix = db_item.consumer_tag_prefix
                item.service_name = db_item.service_name
                item.def_name = db_item.def_name
                item.def_id = db_item.def_id
    
                item_list.append(item)

            self.response.payload = etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new AMQP channel.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'queue', 
            'consumer_tag_prefix', 'service')

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
                raise Exception('An AMQP channel [{0}] already exists on this cluster'.format(name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)
            
            created_elem = Element('channel_amqp')
            
            try:
                item = ChannelAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.def_id = input.def_id
                item.service = service
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload = etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create an AMQP channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an AMQP channel.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 
            'consumer_tag_prefix', 'service')

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
                raise Exception('An AMQP channel [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)
            
            xml_item = Element('channel_amqp')
            
            try:
                item = session.query(ChannelAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.consumer_tag_prefix = input.consumer_tag_prefix
                item.def_id = input.def_id
                item.service = service
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                input.action = CHANNEL.AMQP_EDIT
                old_name = old_name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
                self.response.payload = etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an AMQP channel.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(ChannelAMQP).\
                    filter(ChannelAMQP.id==self.request.input.id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': CHANNEL.AMQP_DELETE, 'name': def_.name, 'id':def_.id}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the AMQP channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
