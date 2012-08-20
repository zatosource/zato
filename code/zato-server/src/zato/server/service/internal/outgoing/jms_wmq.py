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

# Zato
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import ConnDefWMQ, OutgoingWMQ
from zato.common.odb.query import out_jms_wmq_list
from zato.server.connection.jms_wmq.outgoing import start_connector
from zato.server.service import Integer
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of outgoing JMS WebSphere MQ connections.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'delivery_mode', 
            'priority', 'expiration', 'def_name', 'def_id')
        
    def get_data(self, session):
        return out_jms_wmq_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
        
class Create(AdminService):
    """ Creates a new outgoing JMS WebSphere MQ connection.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', Integer('priority'))
        input_optional = ('expiration',)
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            if not(input.priority >= 0 and input.priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
                raise ValueError(msg)
            
            existing_one = session.query(OutgoingWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
                filter(OutgoingWMQ.name==input.name).\
                first()
            
            if existing_one:
                raise Exception('An outgoing JMS WebSphere MQ connection [{0}] already exists on this cluster'.format(input.name))
            
            try:
                item = OutgoingWMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.expiration = input.expiration
                
                session.add(item)
                session.commit()
                
                start_connector(self.server.repo_location, item.id, item.def_id)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not create an outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

class Edit(AdminService):
    """ Updates an outgoing JMS WebSphere MQ connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', Integer('priority'))
        input_optional = ('expiration',)
        output_required = ('id',)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            if not(input.priority >= 0 and input.priority <= 9):
                msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
                raise ValueError(msg)
            
            existing_one = session.query(OutgoingWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
                filter(OutgoingWMQ.name==input.name).\
                filter(OutgoingWMQ.id!=input.id).\
                first()
            
            if existing_one:
                raise Exception('An outgoing JMS WebSphere MQ connection [{0}] already exists on this cluster'.format(input.name))
            
            try:
                item = session.query(OutgoingWMQ).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.expiration = input.expiration
                
                session.add(item)
                session.commit()
                
                input.action = OUTGOING.JMS_WMQ_EDIT
                input.old_name = old_name
                self.broker_client.publish(input, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL)
                
                self.response.payload.id = item.id
                
            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise  
        
class Delete(AdminService):
    """ Deletes an outgoing JMS WebSphere MQ connection.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingWMQ).\
                    filter(OutgoingWMQ.id==self.request.input.id).\
                    one()
                
                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.JMS_WMQ_DELETE, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
