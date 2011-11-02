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
from zato.common.odb.model import Cluster, ConnDef, ConnDefAMQP
from zato.common.odb.query import amqp_def_list
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of AMQP definitions available.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.server.odb.session()) as session:
            definition_list = Element('definition_list')
            definitions = amqp_def_list(session, params['cluster_id'])
    
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
            existing_one = session.query(ConnDef).\
                filter(ConnDef.cluster_id==Cluster.id).\
                filter(ConnDef.def_type=='amqp').\
                filter(ConnDef.name==name).first()
            
            if existing_one:
                raise Exception('AMQP definition [{0}] already exists on this cluster'.format(name))
            
            created_elem = Element('def_amqp')
            
            try:
                def_ = ConnDef(None, name, 'amqp', cluster_id)
                def_amqp = ConnDefAMQP(None, params['host'], params['port'], params['vhost'], 
                    params['username'], password, params['frame_max'], params['heartbeat'])
                def_.amqp = def_amqp
                session.add(def_)
                session.commit()
                
                created_elem.id = def_.id
                
            except Exception, e:
                msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
            return ZATO_OK, etree.tostring(created_elem)
        
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
                
                def_ = session.query(ConnDef).\
                    filter(ConnDef.id==ConnDefAMQP.def_id).\
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
        