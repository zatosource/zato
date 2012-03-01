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
from zato.common.broker_message import MESSAGE_TYPE, SERVICE
from zato.common.odb.model import Cluster, Service
from zato.common.odb.query import service, service_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of services.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = service_list(session, params['cluster_id'])
            
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.impl_name = db_item.impl_name
                item.is_internal = db_item.is_internal
                item.usage_count = 'TODO getlist'
    
                item_list.append(item)
    
            return ZATO_OK, etree.tostring(item_list)
        
class GetByID(AdminService):
    """ Returns a particular service.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['id', 'cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:

            db_item = service(session, params['cluster_id'], params['id'])
            
            item = Element('item')
            item.id = db_item.id
            item.name = db_item.name
            item.is_active = db_item.is_active
            item.impl_name = db_item.impl_name
            item.is_internal = db_item.is_internal
            item.usage_count = 'TODO getbyid'
    
            return ZATO_OK, etree.tostring(item)
        
class Create(AdminService):
    """ Creates a new JMS WebSphere MQ definition.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
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
    """ Updates a service.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            request_params = ['id', 'is_active', 'name']
            
            params = _get_params(payload, request_params, 'data.')
            id = int(params['id'])
            is_active = is_boolean(params['is_active'])
            name = params['name']
            
            service_elem = Element('service')
            
            try:
                
                service = session.query(Service).filter_by(id=id).one()
                service.is_active = is_active
                service.name = name
                
                session.add(service)
                session.commit()
                
                service_elem.id = service.id
                service_elem.name = service.name
                service_elem.impl_name = service.impl_name
                service_elem.is_internal = service.is_internal
                service_elem.usage_count = 'TODO edit'
                
                params['action'] = SERVICE.EDIT
                self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
                return ZATO_OK, etree.tostring(service_elem)
                
            except Exception, e:
                msg = 'Could not update the service, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
        
class Delete(AdminService):
    """ Deletes a service
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = int(params['id'])
                
                service = session.query(Service).\
                    filter(Service.id==id).\
                    one()
                
                session.delete(service)
                session.commit()

                msg = {'action': SERVICE.DELETE, 'id': id}
                self.broker_client.send_json(msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the service, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''

