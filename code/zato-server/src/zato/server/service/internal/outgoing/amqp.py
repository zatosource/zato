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
from zato.common.broker_message import MESSAGE_TYPE, DEFINITION
from zato.common.odb.model import Cluster, ConnDefAMQP
from zato.common.odb.query import out_amqp_list
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of AMQP definitions available.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            items = Element('items')
            db_items = out_amqp_list(session, params['cluster_id'])
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                '''item.host = db_item.host
                item.port = db_item.port
                item.vhost = db_item.vhost
                item.username = db_item.username
                item.frame_max = db_item.frame_max
                item.heartbeat = db_item.heartbeat'''
    
                items.append(item)
    
            return ZATO_OK, etree.tostring(items)
        
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
                
                params['action'] = DEFINITION.AMQP_CREATE
                kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)                
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Creates a new AMQP definition.
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
                
                id = params['id']
                
                def_ = session.query(ConnDefAMQP).\
                    filter(ConnDefAMQP.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': DEFINITION.AMQP_DELETE, 'name': def_.name}
                kwargs['thread_ctx'].broker_client.send_json(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
