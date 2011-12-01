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
from zato.common.odb.model import ChannelAMQP, Cluster, ConnDefAMQP
from zato.common.odb.query import channel_amqp_list
#from zato.server.amqp import start_connector_listener
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = channel_amqp_list(session, params['cluster_id'])
    
            for db_item in db_items:
    
                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.queue = db_item.queue
                item.consumer_tag_prefix = db_item.consumer_tag_prefix
                item.def_name = db_item.def_name
                item.def_id = db_item.def_id
    
                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)
        
class Create(AdminService):
    """ Creates a new AMQP channel.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')
            
            params = ['cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix']
            params = _get_params(payload, params, 'data.')
            
            name = params['name']
            cluster_id = params['cluster_id']
            params['def_id'] = int(params['def_id'])
            
            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ConnDefAMQP.cluster_id==cluster_id).\
                filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
                filter(ChannelAMQP.name==name).\
                first()
            
            if existing_one:
                raise Exception('An AMQP channel [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('channel_amqp')
            
            try:

                params['is_active'] = is_boolean(params['is_active'])
                
                item = ChannelAMQP()
                item.name = params['name']
                item.is_active = params['is_active']
                item.queue = params['queue']
                item.consumer_tag_prefix = params['consumer_tag_prefix']
                item.def_id = params['def_id']
                
                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                #start_connector_listener(self.server.repo_location, item.id, item.def_id)
                
                return ZATO_OK, etree.tostring(created_elem)
                
            except Exception, e:
                msg = 'Could not create an AMQP channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            params = ['id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix']
            params = _get_params(payload, params, 'data.')
            
            id = params['id']
            name = params['name']
            cluster_id = params['cluster_id']
            params['def_id'] = int(params['def_id'])
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelAMQP.id).\
                filter(ConnDefAMQP.cluster_id==cluster_id).\
                filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
                filter(ChannelAMQP.name==name).\
                filter(ChannelAMQP.id!=id).\
                first()
            
            if existing_one:
                raise Exception('An AMQP channel [{0}] already exists on this cluster'.format(name))
            
            xml_item = Element('channel_amqp')
            
            try:
                
                params['id'] = int(params['id'])
                params['def_id'] = int(params['def_id'])
                params['is_active'] = is_boolean(params['is_active'])
                
                item = session.query(ChannelAMQP).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = params['is_active']
                item.queue = params['queue']
                item.consumer_tag_prefix = params['consumer_tag_prefix']
                item.def_id = params['def_id']
                
                session.add(item)
                session.commit()
                
                xml_item.id = item.id
                
                params['action'] = CHANNEL.AMQP_EDIT
                params['old_name'] = old_name
                kwargs['thread_ctx'].broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
                return ZATO_OK, etree.tostring(xml_item)
                
            except Exception, e:
                msg = 'Could not update the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an AMQP channel.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                def_ = session.query(ChannelAMQP).\
                    filter(ChannelAMQP.id==id).\
                    one()
                
                session.delete(def_)
                session.commit()

                msg = {'action': CHANNEL.AMQP_DELETE, 'name': def_.name, 'id':def_.id}
                kwargs['thread_ctx'].broker_client.send_json(msg, MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the AMQP channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
