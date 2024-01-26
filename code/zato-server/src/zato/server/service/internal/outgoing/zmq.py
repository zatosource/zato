# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingZMQ
from zato.common.odb.query import out_zmq_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing ZeroMQ connections.
    """
    _filter_by = OutgoingZMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_zmq_get_list_request'
        response_elem = 'zato_outgoing_zmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'socket_method')

    def get_data(self, session):
        return self._search(out_zmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing ZeroMQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_zmq_create_request'
        response_elem = 'zato_outgoing_zmq_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'address', 'socket_type', 'socket_method')
        input_optional = ('msg_source',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==input.cluster_id).\
                filter(OutgoingZMQ.name==input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing ZeroMQ connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = self._new_zato_instance_with_cluster(OutgoingZMQ)
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.socket_method = input.socket_method
                item.cluster_id = input.cluster_id

                session.add(item)
                session.commit()

                input.action = OUTGOING.ZMQ_CREATE.value
                input.id = item.id
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                msg = 'Could not create an outgoing ZeroMQ connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing ZeroMQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_zmq_edit_request'
        response_elem = 'zato_outgoing_zmq_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type', 'socket_method')
        input_optional = ('msg_source',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingZMQ.id).\
                filter(OutgoingZMQ.cluster_id==input.cluster_id).\
                filter(OutgoingZMQ.name==input.name).\
                filter(OutgoingZMQ.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An outgoing ZeroMQ connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = session.query(OutgoingZMQ).filter_by(id=input.id).one()

                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.socket_type = input.socket_type
                item.socket_method = input.socket_method

                session.add(item)
                session.commit()

                input.action = OUTGOING.ZMQ_EDIT.value
                input.id = item.id
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                msg = 'Could not update the outgoing ZeroMQ connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing ZeroMQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_zmq_delete_request'
        response_elem = 'zato_outgoing_zmq_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingZMQ).\
                    filter(OutgoingZMQ.id==self.request.input.id).\
                    one()

                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.ZMQ_DELETE.value, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                msg = 'Could not delete the outgoing ZeroMQ connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)

                raise

# ################################################################################################################################
