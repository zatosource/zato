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

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster, WSSDefinition
from zato.common.odb.query import wss_list
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'password_type', 'username', 
            'reject_empty_nonce_creat', 'reject_stale_tokens', 'reject_expiry_limit', 
            'nonce_freshness_time')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = wss_list(session, self.request.input.cluster_id, False)

class Create(AdminService):
    """ Creates a new WS-Security definition.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'username', 
            'password_type', Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'),
            'reject_expiry_limit', Integer('nonce_freshness_time'))
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==input.cluster_id).\
                filter(WSSDefinition.name==input.name).first()
            
            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(input.name))
            
            password = uuid4().hex
    
            try:
                wss = WSSDefinition(None, input.name, input.is_active, input.username, 
                    password, input.password_type, input.reject_empty_nonce_creat, 
                    input.reject_stale_tokens, input.reject_expiry_limit, input.nonce_freshness_time, 
                    cluster)
                
                session.add(wss)
                session.commit()
                
            except Exception, e:
                msg = "Could not create a WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.WSS_CREATE
                input.password = password
                input.sec_type = 'wss'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            self.response.payload.id = wss.id

class Edit(AdminService):
    """ Updates a WS-S definition.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username', 
            'password_type', Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'),
            'reject_expiry_limit', Integer('nonce_freshness_time'))
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==input.cluster_id).\
                filter(WSSDefinition.name==input.name).\
                filter(WSSDefinition.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(input.name))
            
            try:
                wss = session.query(WSSDefinition).filter_by(id=input.id).one()
                old_name = wss.name
                
                wss.name = input.name
                wss.is_active = input.is_active
                wss.username = input.username
                wss.password_type = input.password_type
                wss.reject_empty_nonce_creat = input.reject_empty_nonce_creat
                wss.reject_stale_tokens = input.reject_stale_tokens
                wss.reject_expiry_limit = input.reject_expiry_limit
                wss.nonce_freshness_time = input.nonce_freshness_time
    
                session.add(wss)
                session.commit()
                
            except Exception, e:
                msg = "Could not update the WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.WSS_EDIT
                input.old_name = old_name
                input.sec_type = 'wss'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
    
            self.response.payload.id = wss.id
    
class ChangePassword(ChangePasswordBase):
    """ Changes the password of a WS-Security definition.
    """
    def handle(self):
        def _auth(instance, password):
            instance.password = password
            
        return self._handle(WSSDefinition, _auth, SECURITY.WSS_CHANGE_PASSWORD)
    
class Delete(AdminService):
    """ Deletes a WS-Security definition.
    """
    class SimpleIO:
        input_required = ('wss_id',)

    def handle(self):
        
        with closing(self.odb.session()) as session:
            try:
                wss = session.query(WSSDefinition).\
                    filter(WSSDefinition.id==self.request.input.wss_id).\
                    one()

                session.delete(wss)
                session.commit()
            except Exception, e:
                msg = "Could not delete the WS-Security definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            else:
                self.request.input.action = SECURITY.WSS_DELETE
                self.request.input.name = wss.name
                self.broker_client.send_json(self.request.input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
