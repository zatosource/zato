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

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.odb.model import Cluster, WSSDefinition
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
            definition_list = Element('definition_list')
            definitions = session.query(WSSDefinition).\
                filter(Cluster.id==params['cluster_id']).\
                order_by('wss_def.name').\
                all()
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.password_type = definition.password_type
                definition_elem.username = definition.username
                definition_elem.reject_empty_nonce_ts = definition.reject_empty_nonce_ts
                definition_elem.reject_stale_username = definition.reject_stale_username
                definition_elem.expiry_limit = definition.expiry_limit
                definition_elem.nonce_freshness = definition.nonce_freshness
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new WS-Security definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'name', 'is_active', 'username', 
                              'password_type', 'reject_empty_nonce_ts', 
                              'reject_stale_username',  'expiry_limit',
                              'nonce_freshness']
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
    
            try:
                wss = WSSDefinition(None, name, params['is_active'], params['username'], 
                                    uuid4().hex,  params['password_type'],
                                    params['reject_empty_nonce_ts'], 
                                    params['reject_stale_username'], params['expiry_limit'], 
                                    params['nonce_freshness'], cluster)
                
                session.add(wss)
                session.commit()
                
                wss_elem.id = wss.id
                
            except Exception, e:
                msg = "Could not create a WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
            return ZATO_OK, etree.tostring(wss_elem)

class Edit(AdminService):
    """ Updates a WS-S definition.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['id', 'is_active', 'name', 'username', 'password_type', 
                              'reject_empty_nonce_ts', 'reject_stale_username', 
                              'expiry_limit', 'nonce_freshness', 'cluster_id']
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
                
                wss.name = name
                wss.is_active = new_params['is_active']
                wss.username = new_params['username']
                wss.password_type = new_params['password_type']
                wss.reject_empty_nonce_ts = new_params['reject_empty_nonce_ts']
                wss.reject_stale_username = new_params['reject_stale_username']
                wss.expiry_limit = new_params['expiry_limit']
                wss.nonce_freshness = new_params['nonce_freshness']
    
                session.add(wss)
                session.commit()
                
                wss_elem.id = wss.id
                
            except Exception, e:
                msg = "Could not update the WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
    
            return ZATO_OK, etree.tostring(wss_elem)
    
class ChangePassword(AdminService):
    """ Changes the password of a WS-Security definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id', 'password1', 'password2']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                password1 = params.get('password1')
                password2 = params.get('password2')
                
                if not password1:
                    raise Exception('Password must not be empty')
                
                if not password2:
                    raise Exception('Password must be repeated')
                
                if password1 != password2:
                    raise Exception('Passwords need to be the same')
                
                wss = session.query(WSSDefinition).\
                    filter(WSSDefinition.id==id).\
                    one()
                
                wss.password = password1
            
                session.add(wss)
                session.commit()
            except Exception, e:
                msg = "Could not update the password, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
            return ZATO_OK, ''
    
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
            
            return ZATO_OK, ''