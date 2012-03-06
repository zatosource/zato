# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster, WSSDefinition
from zato.common.odb.query import wss_list
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
            definition_list = Element('definition_list')
            definitions = wss_list(session, params['cluster_id'], False)
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.password_type = definition.password_type
                definition_elem.username = definition.username
                definition_elem.reject_empty_nonce_creat = definition.reject_empty_nonce_creat
                definition_elem.reject_stale_tokens = definition.reject_stale_tokens
                definition_elem.reject_expiry_limit = definition.reject_expiry_limit
                definition_elem.nonce_freshness_time = definition.nonce_freshness_time
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new WS-Security definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'name', 'is_active', 'username', 
                              'password_type', 'reject_empty_nonce_creat', 
                              'reject_stale_tokens',  'reject_expiry_limit',
                              'nonce_freshness_time']
            params = _get_params(payload, request_params, 'data.')
            
            cluster_id = params['cluster_id']
            name = params['name']
            
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==cluster_id).\
                filter(WSSDefinition.name==name).first()
            
            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(name))
            
            wss_elem = Element('wss')
            password = uuid4().hex
    
            try:
                wss = WSSDefinition(None, name, params['is_active'], params['username'], 
                                    password, params['password_type'],
                                    params['reject_empty_nonce_creat'], 
                                    params['reject_stale_tokens'], params['reject_expiry_limit'], 
                                    params['nonce_freshness_time'], cluster)
                
                session.add(wss)
                session.commit()
                
                wss_elem.id = wss.id
                
            except Exception, e:
                msg = "Could not create a WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                params['action'] = SECURITY.WSS_CREATE
                params['password'] = password
                kwargs['thread_ctx'].broker_client.send_json(params, 
                    msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            return ZATO_OK, etree.tostring(wss_elem)

class Edit(AdminService):
    """ Updates a WS-S definition.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['id', 'is_active', 'name', 'username', 'password_type', 
                              'reject_empty_nonce_creat', 'reject_stale_tokens', 
                              'reject_expiry_limit', 'nonce_freshness_time', 'cluster_id']
            new_params = _get_params(payload, request_params, 'data.')
            
            def_id = new_params['id']
            name = new_params['name']
            cluster_id = new_params['cluster_id']
            
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==cluster_id).\
                filter(WSSDefinition.name==name).\
                filter(WSSDefinition.id != def_id).\
                first()
            
            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(name))
            
            wss_elem = Element('wss')
    
            try:
                wss = session.query(WSSDefinition).filter_by(id=def_id).one()
                old_name = wss.name
                
                wss.name = name
                wss.is_active = new_params['is_active']
                wss.username = new_params['username']
                wss.password_type = new_params['password_type']
                wss.reject_empty_nonce_creat = new_params['reject_empty_nonce_creat']
                wss.reject_stale_tokens = new_params['reject_stale_tokens']
                wss.reject_expiry_limit = new_params['reject_expiry_limit']
                wss.nonce_freshness_time = new_params['nonce_freshness_time']
    
                session.add(wss)
                session.commit()
                
                wss_elem.id = wss.id
                
            except Exception, e:
                msg = "Could not update the WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                new_params['action'] = SECURITY.WSS_EDIT
                new_params['old_name'] = old_name
                kwargs['thread_ctx'].broker_client.send_json(new_params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
    
            return ZATO_OK, etree.tostring(wss_elem)
    
class ChangePassword(ChangePasswordBase):
    """ Changes the password of a WS-Security definition.
    """
    def handle(self, *args, **kwargs):
        def _auth(instance, password):
            instance.password = password
            
        return self._handle(WSSDefinition, _auth, 
                            SECURITY.WSS_CHANGE_PASSWORD, **kwargs)
    
class Delete(AdminService):
    """ Deletes a WS-Security definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['wss_id']
                params = _get_params(payload, request_params, 'data.')
                
                wss_id = params['wss_id']
                
                wss = session.query(WSSDefinition).\
                    filter(WSSDefinition.id==wss_id).\
                    one()
                
                session.delete(wss)
                session.commit()
            except Exception, e:
                msg = "Could not delete the WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            else:
                params['action'] = SECURITY.WSS_DELETE
                params['name'] = wss.name
                kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            return ZATO_OK, ''