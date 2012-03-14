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
from zato.common.odb.model import ConnDefWMQ, OutgoingWMQ
from zato.common.odb.query import out_jms_wmq_list
from zato.server.connection.jms_wmq.outgoing import start_connector
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing JMS WebSphere MQ connections.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_jms_wmq_list(session, params['cluster_id'], False)
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.delivery_mode = db_item.delivery_mode
                item.priority = db_item.priority
                item.expiration = db_item.expiration
                item.def_name = db_item.def_name
                item.def_id = db_item.def_id
    
                item_list.append(item)
    
            self.response.payload = etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new outgoing JMS WebSphere MQ connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            
            core_params = ['cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['expiration']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)
        
            priority = int(core_params['priority'])
        
            if not(priority >= 0 and priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
                raise ValueError(msg)
            
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            core_params['def_id'] = int(core_params['def_id'])
            
            existing_one = session.query(OutgoingWMQ.id).\
                filter(ConnDefWMQ.cluster_id==cluster_id).\
                filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
                filter(OutgoingWMQ.name==name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing JMS WebSphere MQ connection [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('out_jms_wmq')
            
            try:

                core_params['delivery_mode'] = int(core_params['delivery_mode'])
                core_params['priority'] = int(core_params['priority'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = OutgoingWMQ()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.def_id = core_params['def_id']
                item.delivery_mode = core_params['delivery_mode']
                item.priority = core_params['priority']
                item.expiration = optional_params['expiration']
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload = etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create an outgoing JMS WebSphere MQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing JMS WebSphere MQ connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['expiration']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)
        
            priority = int(core_params['priority'])
        
            if not(priority >= 0 and priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
                raise ValueError(msg)
            
            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            core_params['def_id'] = int(core_params['def_id'])
            
            existing_one = session.query(OutgoingWMQ.id).\
                filter(ConnDefWMQ.cluster_id==cluster_id).\
                filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
                filter(OutgoingWMQ.name==name).\
                filter(OutgoingWMQ.id!=core_params['id']).\
                first()
            
            if existing_one:
                raise Exception('An outgoing JMS WebSphere MQ connection [{0}] already exists on this cluster'.format(name))
            
            xml_item = Element('out_jms_wmq')
            
            try:
                
                core_params['id'] = int(core_params['id'])
                core_params['delivery_mode'] = int(core_params['delivery_mode'])
                core_params['priority'] = int(core_params['priority'])
                core_params['def_id'] = int(core_params['def_id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = session.query(OutgoingWMQ).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = core_params['is_active']
                item.def_id = core_params['def_id']
                item.delivery_mode = core_params['delivery_mode']
                item.priority = core_params['priority']
                item.expiration = optional_params['expiration']
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                core_params['action'] = OUTGOING.JMS_WMQ_EDIT
                core_params['old_name'] = old_name
                core_params.update(optional_params)
                self.broker_client.send_json(core_params, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
                self.response.payload = etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing JMS WebSphere MQ connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                item = session.query(OutgoingWMQ).\
                    filter(OutgoingWMQ.id==id).\
                    one()
                
                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.JMS_WMQ_DELETE, 'name': item.name, 'id':item.id}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing JMS WebSphere MQ connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
