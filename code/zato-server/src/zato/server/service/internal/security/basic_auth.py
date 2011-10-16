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

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster, HTTPBasicAuth
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of HTTP Basic Auth definitions available.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            definition_list = Element('definition_list')
            definitions = session.query(HTTPBasicAuth).\
                filter(Cluster.id==params['cluster_id']).\
                order_by('http_basic_auth_def.name').\
                all()
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.username = definition.username
                definition_elem.domain = definition.domain
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new HTTP Basic Auth definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            try:
    
                payload = kwargs.get('payload')
                request_params = ['cluster_id', 'name', 'is_active', 'username', 'domain']
                params = _get_params(payload, request_params, 'data.')
                
                cluster_id = params['cluster_id']
                name = params['name']
    
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()
                
                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==cluster_id).\
                    filter(HTTPBasicAuth.name==name).first()
                
                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(name))
                
                auth_elem = Element('basic_auth')
                
                auth = HTTPBasicAuth(None, name, params['is_active'], params['username'], 
                                    params['domain'], uuid4().hex, cluster)
                
                session.add(auth)
                session.commit()
                
                auth_elem.id = auth.id
                
            except Exception, e:
                msg = "Could not create an HTTP Basic Auth definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
            return ZATO_OK, etree.tostring(auth_elem)

class Edit(AdminService):
    """ Updates an HTTP Basic Auth definition.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            try:
                
                payload = kwargs.get('payload')
                request_params = ['id', 'is_active', 'name', 'username', 'domain', 
                                  'cluster_id']
                new_params = _get_params(payload, request_params, 'data.')
                
                def_id = new_params['id']
                name = new_params['name']
                cluster_id = new_params['cluster_id']
                
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==cluster_id).\
                    filter(HTTPBasicAuth.name==name).\
                    filter(HTTPBasicAuth.id != def_id).\
                    first()
                
                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(name))
                
                definition = session.query(HTTPBasicAuth).filter_by(id=def_id).one()
                
                definition.name = name
                definition.is_active = new_params['is_active']
                definition.username = new_params['username']
                definition.domain = new_params['domain']
    
                session.add(definition)
                session.commit()
                
            except Exception, e:
                msg = "Could not update the HTTP Basic Auth definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
    
            return ZATO_OK, ''
    
class ChangePassword(AdminService):
    """ Changes the password of an HTTP Basic Auth definition.
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
                
                auth = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id==id).\
                    one()
                
                auth.password = password1
            
                session.add(auth)
                session.commit()
            except Exception, e:
                msg = "Could not update the password, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
            return ZATO_OK, ''
    
class Delete(AdminService):
    """ Deletes an HTTP Basic Auth definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                auth = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id==id).\
                    one()
                
                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = "Could not delete the HTTP Basic Auth definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            
            return ZATO_OK, ''
    