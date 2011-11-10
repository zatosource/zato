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
from zato.common.odb.model import Cluster, ConnDefAMQP, OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_amqp_list(session, params['cluster_id'])
    
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
    
            return ZATO_OK, etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            
            core_params = ['cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['content_type', 'content_encoding', 'expiration', 'user_id', 'app_id']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)
        
            priority = int(core_params['priority'])
        
            if not(priority >= 0 and priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
                raise ValueError(msg)
            
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection[{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('out_amqp')
            
            try:

                core_params['delivery_mode'] = int(core_params['delivery_mode'])
                core_params['priority'] = int(core_params['priority'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = OutgoingAMQP()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.def_id = core_params['def_id']
                item.delivery_mode = core_params['delivery_mode']
                item.priority = core_params['priority']
                item.content_type = optional_params['content_type']
                item.content_encoding = optional_params['content_encoding'] 
                item.expiration = optional_params['expiration']
                item.user_id = optional_params['user_id']
                item.app_id = optional_params['app_id']
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                
                core_params['action'] = OUTGOING.AMQP_CREATE
                core_params.update(optional_params)
                kwargs['thread_ctx'].broker_client.send_json(core_params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)                
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = "Could not create an outgoing AMQP connection, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['content_type', 'content_encoding', 'expiration', 'user_id', 'app_id']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)
        
            priority = int(core_params['priority'])
        
            if not(priority >= 0 and priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
                raise ValueError(msg)
            
            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==name).\
                filter(OutgoingAMQP.id!=id).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection [{0}] already exists on this cluster'.format(name))
            
            xml_item = Element('out_amqp')
            
            try:
                
                core_params['delivery_mode'] = int(core_params['delivery_mode'])
                core_params['priority'] = int(core_params['priority'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                
                item = session.query(OutgoingAMQP).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = core_params['is_active']
                item.def_id = core_params['def_id']
                item.delivery_mode = core_params['delivery_mode']
                item.priority = core_params['priority']
                item.content_type = optional_params['content_type']
                item.content_encoding = optional_params['content_encoding']
                item.expiration = optional_params['expiration']
                item.user_id = optional_params['user_id']
                item.app_id = optional_params['app_id']
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                core_params['action'] = OUTGOING.AMQP_EDIT
                core_params['old_name'] = old_name
                core_params.update(optional_params)
                kwargs['thread_ctx'].broker_client.send_json(core_params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)                
                
                return ZATO_OK, etree.tostring(xml_item)
                
            except Exception, e:
                msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                def_ = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': OUTGOING.AMQP_DELETE, 'name': def_.name}
                kwargs['thread_ctx'].broker_client.send_json(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing AMQP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
