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

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster, HTTPBasicAuth
from zato.common.odb.query import basic_auth_list
from zato.server.service.internal import AdminService, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of HTTP Basic Auth definitions available.
    """
    class SimpleIO:
        input_required = ('cluster_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            definition_list = Element('definition_list')
            definitions = basic_auth_list(session, self.request.input.cluster_id, False)
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.username = definition.username
                definition_elem.realm = definition.realm
    
                definition_list.append(definition_elem)
    
            self.response.payload = etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new HTTP Basic Auth definition.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'username', 'realm')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex
        
        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
                
                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(HTTPBasicAuth.name==input.name).first()
                
                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(input.name))
                
                auth_elem = Element('basic_auth')
                
                auth = HTTPBasicAuth(None, input.name, input.is_active, input.username, 
                    input.realm, input.password, cluster)
                
                session.add(auth)
                session.commit()
                
                auth_elem.id = auth.id
                
            except Exception, e:
                msg = 'Could not create an HTTP Basic Auth definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.BASIC_AUTH_CREATE
                input.sec_type = 'basic_auth'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            self.response.payload = etree.tostring(auth_elem)

class Edit(AdminService):
    """ Updates an HTTP Basic Auth definition.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username', 'realm')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(HTTPBasicAuth.name==input.name).\
                    filter(HTTPBasicAuth.id!=input.id).\
                    first()
                
                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(input.name))
                
                auth_elem = Element('basic_auth')
                
                definition = session.query(HTTPBasicAuth).filter_by(id=input.id).one()
                old_name = definition.name
                
                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username
                definition.realm = input.realm
    
                session.add(definition)
                session.commit()
                
                auth_elem.id = definition.id
                
            except Exception, e:
                msg = 'Could not update the HTTP Basic Auth definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.BASIC_AUTH_EDIT
                input.old_name = old_name
                input.sec_type = 'basic_auth'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
    
            self.response.payload = etree.tostring(auth_elem)
    
class ChangePassword(ChangePasswordBase):
    """ Changes the password of an HTTP Basic Auth definition.
    """
    def handle(self):
        def _auth(instance, password):
            instance.password = password
            
        return self._handle(HTTPBasicAuth, _auth, SECURITY.BASIC_AUTH_CHANGE_PASSWORD)

class Delete(AdminService):
    """ Deletes an HTTP Basic Auth definition.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id==self.request.input.id).\
                    one()
                
                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the HTTP Basic Auth definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            else:
                self.request.input.action = SECURITY.BASIC_AUTH_DELETE
                self.request.input.name = auth.name
                self.broker_client.send_json(self.request.input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
