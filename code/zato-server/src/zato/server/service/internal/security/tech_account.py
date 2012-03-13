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
from zato.common.odb.model import Cluster, TechnicalAccount
from zato.common.odb.query import tech_acc_list
from zato.common.util import tech_account_password
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of technical accounts defined in the ODB. The items are
    sorted by the 'name' attribute.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            definition_list = Element('definition_list')
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')

            definitions = tech_acc_list(session, params['cluster_id'], False)
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)
    
class GetByID(AdminService):
    """ Returns a technical account of a given ID.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['tech_account_id']
            params = _get_params(payload, request_params, 'data.')
    
            tech_account = session.query(TechnicalAccount.id, 
                                                 TechnicalAccount.name, 
                                                 TechnicalAccount.is_active).\
                filter(TechnicalAccount.id==params['tech_account_id']).one()
            
            tech_account_elem = Element('tech_account')
            tech_account_elem.id = tech_account.id;
            tech_account_elem.name = tech_account.name;
            tech_account_elem.is_active = tech_account.is_active;
            
            return ZATO_OK, etree.tostring(tech_account_elem)
    
class Create(AdminService):
    """ Creates a new technical account.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'name', 'is_active']
            params = _get_params(payload, request_params, 'data.')
            
            cluster_id = params['cluster_id']
            name = params['name']
            
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            salt = uuid4().hex
            password = tech_account_password(uuid4().hex, salt)
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==cluster_id).\
                filter(TechnicalAccount.name==name).first()
            
            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(name))
            
            tech_account_elem = Element('tech_account')
            
            try:
                tech_account = TechnicalAccount(None, name, params['is_active'], password, salt, cluster=cluster)
                session.add(tech_account)
                session.commit()
                
                tech_account_elem.id = tech_account.id
                
            except Exception, e:
                msg = "Could not create a technical account, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                params['action'] = SECURITY.TECH_ACC_CREATE
                params['password'] = password
                self.broker_client.send_json(params, 
                    msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            return ZATO_OK, etree.tostring(tech_account_elem)
    

class Edit(AdminService):
    """ Updates an existing technical account.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'tech_account_id', 'name', 'is_active']
            params = _get_params(payload, request_params, 'data.')
            
            cluster_id = params['cluster_id']
            tech_account_id = params['tech_account_id']
            name = params['name']
            
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==cluster_id).\
                filter(TechnicalAccount.name==name).\
                filter(TechnicalAccount.id != tech_account_id).\
                first()
            
            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(name))
            
            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==tech_account_id).one()
            old_name = tech_account.name
            
            tech_account.name = name
            tech_account.is_active = is_boolean(params['is_active'])

            tech_account_elem = Element('tech_account')            
            
            try:
                session.add(tech_account)
                session.commit()

                tech_account_elem.id = tech_account.id                
                
            except Exception, e:
                msg = "Could not update the technical account, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                params['action'] = SECURITY.TECH_ACC_EDIT
                params['old_name'] = old_name
                self.broker_client.send_json(params, 
                    msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            return ZATO_OK, etree.tostring(tech_account_elem)
    
class ChangePassword(ChangePasswordBase):
    """ Changes the password of a technical account.
    """
    def handle(self, *args, **kwargs):
        def _auth(instance, password):
            salt = uuid4().hex
            instance.password = tech_account_password(password, salt)
            instance.salt = salt

        return self._handle(TechnicalAccount, _auth, 
                            SECURITY.TECH_ACC_CHANGE_PASSWORD, **kwargs)
    
class Delete(AdminService):
    """ Deletes a technical account.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['tech_account_id', 'zato_admin_tech_account_name']
            params = _get_params(payload, request_params, 'data.')
            
            tech_account_id = params['tech_account_id']
            zato_admin_tech_account_name = params['zato_admin_tech_account_name']
            
            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==tech_account_id).\
                one()
            
            if tech_account.name == zato_admin_tech_account_name:
                msg = "Can't delete account [{0}], at least one client console uses it".\
                    format(zato_admin_tech_account_name)
                raise Exception(msg)
            
            try:
                session.delete(tech_account)
                session.commit()
            except Exception, e:
                msg = "Could not delete the account, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            else:
                params['action'] = SECURITY.TECH_ACC_DELETE
                params['name'] = tech_account.name
                self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            return ZATO_OK, ''
    