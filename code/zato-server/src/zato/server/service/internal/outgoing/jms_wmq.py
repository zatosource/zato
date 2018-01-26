# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import ConnDefWMQ, OutgoingWMQ
from zato.common.odb.query import out_wmq_list
from zato.server.connection.jms_wmq.outgoing import start_connector
from zato.server.service import Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of outgoing JMS WebSphere MQ connections.
    """
    _filter_by = OutgoingWMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_jms_wmq_get_list_request'
        response_elem = 'zato_outgoing_jms_wmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'def_id', Integer('delivery_mode'), Integer('priority'), 'def_name')
        output_optional = ('expiration',)

    def get_data(self, session):
        return self._search(out_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new outgoing JMS WebSphere MQ connection.
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

                if item.is_active:
                    start_connector(self.server.repo_location, item.id, item.def_id)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not create an outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates an outgoing JMS WebSphere MQ connection.
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

                input.action = OUTGOING.WMQ_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an outgoing JMS WebSphere MQ connection.
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

                session.delete(item)
                session.commit()

                msg = {'action': OUTGOING.WMQ_DELETE.value, 'name': item.name,
                       'old_name': item.name, 'id':item.id}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise
