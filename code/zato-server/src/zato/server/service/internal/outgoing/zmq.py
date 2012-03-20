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
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import OutgoingZMQ
from zato.common.odb.query import out_zmq_list
from zato.server.connection.zmq_.outgoing import start_connector
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing ZeroMQ connections.
    """
    class SimpleIO:
        input_required = ('cluster_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_zmq_list(session, self.request.input.cluster_id, False)
            
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.address = db_item.address
                item.socket_type = db_item.socket_type
    
                item_list.append(item)
    
            self.response.payload = etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new outgoing ZeroMQ connection.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'address', 'socket_type')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==input.cluster_id).\
                filter(OutgoingZMQ.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing ZeroMQ connection [{0}] already exists on this cluster'.format(input.name))
            
            created_elem = Element('out_zmq')
            
            try:
                item = OutgoingZMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.cluster_id = input.cluster_id
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                start_connector(self.server.repo_location, item.id)
                
                self.response.payload = etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create an outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing ZeroMQ connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==input.cluster_id).\
                filter(OutgoingZMQ.name==input.name).\
                filter(OutgoingZMQ.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('An outgoing ZeroMQ connection [{0}] already exists on this cluster'.format(input.name))
            
            xml_item = Element('out_zmq')
            
            try:
                item = session.query(OutgoingZMQ).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                input.action = OUTGOING.ZMQ_EDIT
                input.old_name = old_name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
                self.response.payload = etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing ZeroMQ connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type')

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingZMQ).\
                    filter(OutgoingZMQ.id==self.request.input.id).\
                    one()
                
                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.ZMQ_DELETE, 'name': item.name, 'id':item.id}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
