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
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.odb.model import ChannelWMQ, Cluster, ConnDefWMQ, Service
from zato.common.odb.query import channel_jms_wmq_list
#from zato.server.amqp.channel import start_connector
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of JMS WebSphere MQ channels.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = channel_jms_wmq_list(session, params['cluster_id'])
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.queue = db_item.queue
                item.service_name = db_item.service_name
                item.def_name = db_item.def_name
                item.def_id = db_item.def_id
    
                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new WebSphere MQ channel.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            
            params = ['cluster_id', 'name', 'is_active', 'def_id', 'queue',  'service']
            params = _get_params(payload, params, 'data.')
            
            name = params['name']
            cluster_id = params['cluster_id']
            service_name = params['service']
            params['def_id'] = int(params['def_id'])
            
            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==name).\
                first()
            
            if existing_one:
                raise Exception('A WebSphere MQ channel [{0}] already exists on this cluster'.format(name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==cluster_id).\
                filter(Service.name==service_name).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(service_name)
                logger.error(msg)
                raise Exception(msg)
            
            created_elem = Element('channel_jms_wmq')
            
            try:

                params['is_active'] = is_boolean(params['is_active'])
                
                item = ChannelWMQ()
                item.name = params['name']
                item.is_active = params['is_active']
                item.queue = params['queue']
                item.def_id = params['def_id']
                item.service = service
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                #start_connector(self.server.repo_location, item.id, item.def_id)
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create a WebSphere MQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates a JMS WebSphere MQ channel.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            params = ['id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'service']
            params = _get_params(payload, params, 'data.')
            
            id = params['id']
            name = params['name']
            cluster_id = params['cluster_id']
            service_name = params['service']
            params['def_id'] = int(params['def_id'])
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==name).\
                filter(ChannelWMQ.id!=id).\
                first()
            
            if existing_one:
                raise Exception('A JMS WebSphere MQ channel [{0}] already exists on this cluster'.format(name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==cluster_id).\
                filter(Service.name==service_name).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(service_name)
                raise Exception(msg)
            
            xml_item = Element('channel_jms_wmq')
            
            try:
                
                params['id'] = int(params['id'])
                params['def_id'] = int(params['def_id'])
                params['is_active'] = is_boolean(params['is_active'])
                
                item = session.query(ChannelWMQ).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = params['is_active']
                item.queue = params['queue']
                item.def_id = params['def_id']
                item.service = service
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                #params['action'] = CHANNEL.JMS_WMQ_EDIT
                #params['old_name'] = old_name
                #kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
                return ZATO_OK, etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an JMS WebSphere MQ channel.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                def_ = session.query(ChannelWMQ).\
                    filter(ChannelWMQ.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                #msg = {'action': CHANNEL.JMS_WMQ_DELETE, 'name': def_.name, 'id':def_.id}
                #self.broker_client.send_json(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the JMS WebSphere MQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
