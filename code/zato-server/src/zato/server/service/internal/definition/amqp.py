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
from zato.common.broker_message import MESSAGE_TYPE, DEFINITION
from zato.common.odb.model import Cluster, ConnDefAMQP
from zato.common.odb.query import def_amqp_list
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase, ReconnectBase

class GetList(AdminService):
    """ Returns a list of AMQP definitions available.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            definition_list = Element('definition_list')
            definitions = def_amqp_list(session, params['cluster_id'])
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.host = definition.host
                definition_elem.port = definition.port
                definition_elem.vhost = definition.vhost
                definition_elem.username = definition.username
                definition_elem.frame_max = definition.frame_max
                definition_elem.heartbeat = definition.heartbeat
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)
        
class GetByID(AdminService):
    """ Returns a particular AMQP definition
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['id'], 'data.')
        
        with closing(self.server.odb.session()) as session:

            definition = session.query(ConnDefAMQP.id, ConnDefAMQP.name, ConnDefAMQP.host,
                ConnDefAMQP.port, ConnDefAMQP.vhost, ConnDefAMQP.username,
                ConnDefAMQP.frame_max, ConnDefAMQP.heartbeat).\
                filter(ConnDefAMQP.id==params['id']).\
                one()            
            
            definition_elem = Element('definition')
            
            definition_elem.id = definition.id
            definition_elem.name = definition.name
            definition_elem.host = definition.host
            definition_elem.port = definition.port
            definition_elem.vhost = definition.vhost
            definition_elem.username = definition.username
            definition_elem.frame_max = definition.frame_max
            definition_elem.heartbeat = definition.heartbeat
    
            return ZATO_OK, etree.tostring(definition_elem)
        
class Create(AdminService):
    """ Creates a new AMQP definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'name', 'host', 'port', 'vhost', 
                'username', 'frame_max', 'heartbeat']
            
            params = _get_params(payload, request_params, 'data.')
            name = params['name']
            params['heartbeat'] = is_boolean(params['heartbeat'])
            
            cluster_id = params['cluster_id']
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            password = uuid4().hex
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ConnDefAMQP).\
                filter(ConnDefAMQP.cluster_id==Cluster.id).\
                filter(ConnDefAMQP.def_type=='amqp').\
                filter(ConnDefAMQP.name==name).\
                first()
            
            if existing_one:
                raise Exception('AMQP definition [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('def_amqp')
            
            try:
                def_ = ConnDefAMQP(None, name, 'amqp', params['host'], params['port'], params['vhost'], 
                    params['username'], password, params['frame_max'], params['heartbeat'],
                    cluster_id)
                session.add(def_)
                session.commit()
                
                created_elem.id = def_.id
                
                params['id'] = int(def_.id)
                params['action'] = DEFINITION.AMQP_CREATE
                kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)                
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an AMQP definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['id', 'cluster_id', 'name', 'host', 'port', 
                'vhost',  'username', 'frame_max', 'heartbeat']
            
            params = _get_params(payload, request_params, 'data.')
            
            id = params['id']
            name = params['name']
            
            cluster_id = params['cluster_id']
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            password = uuid4().hex
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ConnDefAMQP).\
                filter(ConnDefAMQP.cluster_id==Cluster.id).\
                filter(ConnDefAMQP.def_type=='amqp').\
                filter(ConnDefAMQP.id != id).\
                filter(ConnDefAMQP.name==name).\
                first()
            
            if existing_one:
                raise Exception('AMQP definition [{0}] already exists on this cluster'.format(name))
            
            def_amqp_elem = Element('def_amqp')
            
            try:
                
                def_amqp = session.query(ConnDefAMQP).filter_by(id=id).one()
                old_name = def_amqp.name
                def_amqp.name = name
                def_amqp.host = params['host']
                def_amqp.port = params['port']
                def_amqp.vhost = params['vhost']
                def_amqp.username = params['username']
                def_amqp.frame_max = params['frame_max']
                def_amqp.heartbeat = params['heartbeat']
                
                session.add(def_amqp)
                session.commit()
                
                def_amqp_elem.id = def_amqp.id
                
                params['id'] = int(params['id'])
                params['action'] = DEFINITION.AMQP_EDIT
                params['old_name'] = old_name
                kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)                
                
                return ZATO_OK, etree.tostring(def_amqp_elem)
                
            except Exception, e:
                msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
        
class Delete(AdminService):
    """ Deletes an AMQP definition.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = int(params['id'])
                
                def_ = session.query(ConnDefAMQP).\
                    filter(ConnDefAMQP.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': DEFINITION.AMQP_DELETE, 'id': id}
                kwargs['thread_ctx'].broker_client.send_json(msg, MESSAGE_TYPE.TO_PARALLEL_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
        
class ChangePassword(ChangePasswordBase):
    """ Changes the password of an HTTP Basic Auth definition.
    """
    def handle(self, *args, **kwargs):
        
        def _auth(instance, password):
            instance.password = password
            
        return self._handle(ConnDefAMQP, _auth, 
                            DEFINITION.AMQP_CHANGE_PASSWORD, **kwargs)

    
class Reconnect(ReconnectBase):
    """ Forces an AMQP definition to reconnect.
    """
    def handle(self, *args, **kwargs):
        return self._handle(DEFINITION.AMQP_RECONNECT, *args, **kwargs)
    