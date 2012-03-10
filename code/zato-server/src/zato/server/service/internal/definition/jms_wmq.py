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
from zato.common.broker_message import MESSAGE_TYPE, DEFINITION
from zato.common.odb.model import Cluster, ConnDefWMQ
from zato.common.odb.query import def_jms_wmq, def_jms_wmq_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of JMS WebSphere MQ definitions available.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.odb.session()) as session:
            definition_list = Element('definition_list')
            definitions = def_jms_wmq_list(session, params['cluster_id'], False)
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.host = definition.host
                definition_elem.port = definition.port
                definition_elem.queue_manager = definition.queue_manager
                definition_elem.channel = definition.channel
                definition_elem.cache_open_send_queues = definition.cache_open_send_queues
                definition_elem.cache_open_receive_queues = definition.cache_open_receive_queues
                definition_elem.use_shared_connections = definition.use_shared_connections
                definition_elem.ssl = definition.ssl
                definition_elem.ssl_cipher_spec = definition.ssl_cipher_spec
                definition_elem.ssl_key_repository = definition.ssl_key_repository
                definition_elem.needs_mcd = definition.needs_mcd
                definition_elem.max_chars_printed = definition.max_chars_printed
    
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)
        
class GetByID(AdminService):
    """ Returns a particular JMS WebSphere MQ definition.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['id', 'cluster_id'], 'data.')
        
        with closing(self.odb.session()) as session:

            definition = def_jms_wmq(session, params['cluster_id'], params['id'])
            
            definition_elem = Element('definition')
            
            definition_elem.id = definition.id
            definition_elem.name = definition.name
            definition_elem.host = definition.host
            definition_elem.port = definition.port
            definition_elem.queue_manager = definition.queue_manager
            definition_elem.channel = definition.channel
            definition_elem.cache_open_send_queues = definition.cache_open_send_queues
            definition_elem.cache_open_receive_queues = definition.cache_open_receive_queues
            definition_elem.use_shared_connections = definition.use_shared_connections
            definition_elem.ssl = definition.ssl
            definition_elem.ssl_cipher_spec = definition.ssl_cipher_spec
            definition_elem.ssl_key_repository = definition.ssl_key_repository
            definition_elem.needs_mcd = definition.needs_mcd
            definition_elem.max_chars_printed = definition.max_chars_printed
    
            return ZATO_OK, etree.tostring(definition_elem)
        
class Create(AdminService):
    """ Creates a new JMS WebSphere MQ definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['cluster_id', 'name', 'host', 'port', 'queue_manager', 
                'channel', 'cache_open_send_queues', 'cache_open_receive_queues',
                'use_shared_connections', 'ssl', 'ssl_cipher_spec', 
                'ssl_key_repository', 'needs_mcd', 'max_chars_printed']
            
            params = _get_params(payload, request_params, 'data.')
            name = params['name']
            params['port'] = int(params['port'])
            params['cache_open_send_queues'] = is_boolean(params['cache_open_send_queues'])
            params['cache_open_receive_queues'] = is_boolean(params['cache_open_receive_queues'])
            params['use_shared_connections'] = is_boolean(params['use_shared_connections'])
            params['ssl'] = is_boolean(params['ssl'])
            params['needs_mcd'] = is_boolean(params['needs_mcd'])
            params['max_chars_printed'] = int(params['max_chars_printed'])
            
            cluster_id = params['cluster_id']
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            # Let's see if we already have an object of that name before committing
            # any stuff into the database.
            existing_one = session.query(ConnDefWMQ).\
                filter(ConnDefWMQ.cluster_id==Cluster.id).\
                filter(ConnDefWMQ.name==name).\
                first()
            
            if existing_one:
                raise Exception('JMS WebSphere MQ definition [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('def_jms_wmq')
            
            try:
                def_ = ConnDefWMQ(None, name, params['host'], params['port'], params['queue_manager'], 
                    params['channel'], params['cache_open_send_queues'], params['cache_open_receive_queues'],
                    params['use_shared_connections'], params['ssl'], params['ssl_cipher_spec'], 
                    params['ssl_key_repository'], params['needs_mcd'], params['max_chars_printed'],
                    cluster_id)
                session.add(def_)
                session.commit()
                
                created_elem.id = def_.id
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = "Could not create a JMS WebSphere MQ definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an JMS WMQ definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['id', 'cluster_id', 'name', 'host', 'port', 'queue_manager', 
                'channel', 'cache_open_send_queues', 'cache_open_receive_queues',
                'use_shared_connections', 'ssl', 'ssl_cipher_spec', 
                'ssl_key_repository', 'needs_mcd', 'max_chars_printed']
            
            params = _get_params(payload, request_params, 'data.')
            
            id = int(params['id'])
            name = params['name']
            params['port'] = int(params['port'])
            params['cache_open_send_queues'] = is_boolean(params['cache_open_send_queues'])
            params['cache_open_receive_queues'] = is_boolean(params['cache_open_receive_queues'])
            params['use_shared_connections'] = is_boolean(params['use_shared_connections'])
            params['ssl'] = is_boolean(params['ssl'])
            params['needs_mcd'] = is_boolean(params['needs_mcd'])
            params['max_chars_printed'] = int(params['max_chars_printed'])
            
            cluster_id = params['cluster_id']
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            # Let's see if we already have an object of that name before committing
            # any stuff into the database.
            existing_one = session.query(ConnDefWMQ).\
                filter(ConnDefWMQ.cluster_id==Cluster.id).\
                filter(ConnDefWMQ.id!=id).\
                filter(ConnDefWMQ.name==name).\
                first()
            
            if existing_one:
                raise Exception('JMS WebSphere MQ definition [{0}] already exists on this cluster'.format(name))
            
            def_jms_wmq_elem = Element('def_jms_wmq')
            
            try:
                
                def_jms_wmq = session.query(ConnDefWMQ).filter_by(id=id).one()
                old_name = def_jms_wmq.name
                def_jms_wmq.name = name
                def_jms_wmq.host = params['host']
                def_jms_wmq.port = params['port']
                def_jms_wmq.queue_manager = params['queue_manager']
                def_jms_wmq.channel = params['channel']
                def_jms_wmq.cache_open_send_queues = params['cache_open_send_queues']
                def_jms_wmq.cache_open_receive_queues = params['cache_open_receive_queues']
                def_jms_wmq.use_shared_connections = params['use_shared_connections']
                def_jms_wmq.ssl = params['ssl']
                def_jms_wmq.ssl_cipher_spec = params['ssl_cipher_spec']
                def_jms_wmq.ssl_key_repository = params['ssl_key_repository']
                def_jms_wmq.needs_mcd = params['needs_mcd']
                def_jms_wmq.max_chars_printed = params['max_chars_printed']
                
                session.add(def_jms_wmq)
                session.commit()
                
                def_jms_wmq_elem.id = def_jms_wmq.id
                
                params['id'] = id
                params['action'] = DEFINITION.JMS_WMQ_EDIT
                params['old_name'] = old_name
                self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
                return ZATO_OK, etree.tostring(def_jms_wmq_elem)
                
            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
        
class Delete(AdminService):
    """ Deletes a JMS WebSphere MQ definition.
    """
    def handle(self, *args, **kwargs):
        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = int(params['id'])
                
                def_ = session.query(ConnDefWMQ).\
                    filter(ConnDefWMQ.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': DEFINITION.JMS_WMQ_DELETE, 'id': id}
                self.broker_client.send_json(msg, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the JMS WebSphere MQ definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''

