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

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import ConnDefAMQP, OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.connection.amqp.outgoing import start_connector
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService

class _AMQPService(AdminService):
    def delete_outgoing(self, outgoing):
        msg = {'action': OUTGOING.AMQP_DELETE, 'name': outgoing.name, 'id':outgoing.id}
        self.broker_client.send_json(msg, MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'delivery_mode', 'priority',
            'content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'),
            'def_name', 'def_id')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = out_amqp_list(session, self.request.input.cluster_id, False)
        
class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority')
        input_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id',)
    
    def handle(self):
        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection[{0}] already exists on this cluster'.format(input.name))
            
            try:
                item = OutgoingAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding 
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id
                
                session.add(item)
                session.commit()
                
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = "Could not create an outgoing AMQP connection, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(_AMQPService):
    """ Updates an outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', Integer('priority'))
        input_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id',)
    
    def handle(self):
        
        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)
        
        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                filter(OutgoingAMQP.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('An outgoing AMQP connection [{0}] already exists on this cluster'.format(input.name))
            
            try:
                item = session.query(OutgoingAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id
                
                session.add(item)
                session.commit()
                
                self.delete_outgoing(item)
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not update the AMQP definition, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(_AMQPService):
    """ Deletes an outgoing AMQP connection.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                channel = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==self.request.input.id).\
                    one()
                
                session.delete(channel)
                session.commit()
                
                self.delete_outgoing(channel)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing AMQP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
