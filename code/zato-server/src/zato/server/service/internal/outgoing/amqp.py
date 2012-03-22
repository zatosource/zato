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
from zato.common.odb.model import ConnDefAMQP, OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.connection.amqp.outgoing import start_connector
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    class SimpleIO:
        input_required = ('cluster_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_amqp_list(session, self.request.input.cluster_id, False)
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.delivery_mode = db_item.delivery_mode
                item.priority = db_item.priority
                item.content_type = db_item.content_type
                item.content_encoding = db_item.content_encoding
                item.expiration = db_item.expiration
                item.user_id = db_item.user_id
                item.app_id = db_item.app_id
                item.def_name = db_item.def_name
                item.def_id = db_item.def_id
    
                item_list.append(item)
    
            self.response.payload = etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority')
        input_optional = ('content_type', 'content_encoding', 'expiration', 'user_id', 'app_id')
    
    def handle(self):
        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection[{0}] already exists on this cluster'.format(input.name))
            
            created_elem = Element('out_amqp')
            
            try:
                item = OutgoingAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding 
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload = etree.tostring(created_elem)
                
            except Exception, e:
                msg = "Could not create an outgoing AMQP connection, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority')
        input_optional = ('content_type', 'content_encoding', 'expiration', 'user_id', 'app_id')
    
    def handle(self):
        
        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                filter(OutgoingAMQP.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection [{0}] already exists on this cluster'.format(input.name))
            
            xml_item = Element('out_amqp')
            
            try:
                item = session.query(OutgoingAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                input.action = OUTGOING.AMQP_EDIT
                input.old_name = old_name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
                self.response.payload = etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==self.request.input.id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': OUTGOING.AMQP_DELETE, 'name': def_.name, 'id':def_.id}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing AMQP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
