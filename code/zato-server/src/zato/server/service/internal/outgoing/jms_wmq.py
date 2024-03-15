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
from zato.common.odb.model import ConnDefWMQ, OutgoingWMQ
from zato.common.odb.query import out_wmq, out_wmq_list
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

_base_required = ('id', Integer('delivery_mode'), Integer('priority'))
_get_required = _base_required + ('name', 'is_active', 'def_id', 'def_name')
_optional = (Integer('expiration'),)

# ################################################################################################################################

class _GetSIO(AdminSIO):
    output_required = _get_required
    output_optional = _optional + ('def_name_full_text',)

# ################################################################################################################################

class Get(AdminService):
    """ Returns details of a single outgoing IBM MQ connection.
    """
    class SimpleIO(_GetSIO):
        request_elem = 'zato_outgoing_jms_wmq_get_request'
        response_elem = 'zato_outgoing_jms_wmq_get_response'
        input_required = ('cluster_id', 'id')
        output_optional = _GetSIO.output_optional

    def handle(self):
        with closing(self.odb.session()) as session:
            item = out_wmq(session, self.request.input.cluster_id, self.request.input.id)
            self.response.payload = item

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing IBM MQ connections.
    """
    _filter_by = OutgoingWMQ.name,

    class SimpleIO(_GetSIO, GetListAdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_get_list_request'
        response_elem = 'zato_outgoing_jms_wmq_get_list_response'
        input_required = ('cluster_id',)

    def get_data(self, session):
        return self._search(out_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing IBM MQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_create_request'
        response_elem = 'zato_outgoing_jms_wmq_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', Integer('delivery_mode'), Integer('priority'))
        input_optional = ('expiration',)
        output_required = ('id', 'name')

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
                raise Exception('An outgoing IBM MQ connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = OutgoingWMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.expiration = input.expiration

                # Commit to DB
                session.add(item)
                session.commit()

                # Notify other servers
                input.id = item.id
                input.action = OUTGOING.WMQ_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not create an outgoing IBM MQ connection, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing IBM MQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_edit_request'
        response_elem = 'zato_outgoing_jms_wmq_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', Integer('delivery_mode'), Integer('priority'))
        input_optional = ('expiration',)
        output_required = ('id', 'name')

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
                raise Exception('An outgoing IBM MQ connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = session.query(OutgoingWMQ).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.expiration = input.expiration

                # Commit to DB
                session.add(item)
                session.commit()

                input.action = OUTGOING.WMQ_EDIT.value
                input.old_name = old_name

                # Notify other servers
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update IBM MQ definition, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing IBM MQ connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_delete_request'
        response_elem = 'zato_outgoing_jms_wmq_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingWMQ).\
                    filter(OutgoingWMQ.id==self.request.input.id).\
                    one()

                # Commit to DB
                session.delete(item)
                session.commit()

                # Notify other servers
                self.broker_client.publish({
                    'action': OUTGOING.WMQ_DELETE.value,
                    'name': item.name,
                    'old_name': item.name,
                    'id':item.id
                })

            except Exception:
                session.rollback()
                self.logger.error('Could not delete outgoing IBM MQ connection, e:`{}`', format_exc())

                raise

# ################################################################################################################################

class SendMessage(AdminService):
    """ Sends a message to an IBM MQ queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_send_message_request'
        response_elem = 'zato_outgoing_jms_wmq_message_response'
        input_required = _base_required + ('cluster_id', 'queue_name', 'data')
        input_optional = _optional + ('reply_to', AsIs('correl_id'), AsIs('msg_id'))

    def handle(self):
        self.server.connector_ibm_mq.send_wmq_message(self.request.input)

# ################################################################################################################################
