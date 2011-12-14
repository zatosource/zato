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
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import Cluster, OutgoingZMQ
from zato.common.odb.query import out_zmq_list
#from zato.server.connection.jms_wmq.outgoing import start_connector
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing ZeroMQ connections.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_zmq_list(session, params['cluster_id'])
            
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.address = db_item.address
                item.socket_type = db_item.socket_type
    
                item_list.append(item)
    
            return ZATO_OK, etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new outgoing ZeroMQ connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            
            core_params = ['cluster_id', 'name', 'is_active', 'address', 'socket_type']
            core_params = _get_params(payload, core_params, 'data.')
            
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==cluster_id).\
                filter(OutgoingZMQ.name==name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing ZeroMQ connection [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('out_zmq')
            
            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = OutgoingZMQ()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.address = core_params['address']
                item.socket_type = core_params['socket_type']
                item.cluster_id = core_params['cluster_id']
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                #start_connector(self.server.repo_location, item.id, item.def_id)
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create an outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing ZeroMQ connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type']
            core_params = _get_params(payload, core_params, 'data.')
            
            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==cluster_id).\
                filter(OutgoingZMQ.name==name).\
                filter(OutgoingZMQ.id!=core_params['id']).\
                first()
            
            if existing_one:
                raise Exception('An outgoing ZeroMQ connection [{0}] already exists on this cluster'.format(name))
            
            xml_item = Element('out_zmq')
            
            try:
                
                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = session.query(OutgoingZMQ).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = core_params['is_active']
                item.address = core_params['address']
                item.socket_type = core_params['socket_type']
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                core_params['action'] = OUTGOING.ZMQ_EDIT
                core_params['old_name'] = old_name
                #self.broker_client.send_json(core_params, msg_type=MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
                return ZATO_OK, etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing ZeroMQ connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                item = session.query(OutgoingZMQ).\
                    filter(OutgoingZMQ.id==id).\
                    one()
                
                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.ZMQ_DELETE, 'name': item.name, 'id':item.id}
                #self.broker_client.send_json(msg, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing ZeroMQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
