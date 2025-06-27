# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    name = 'zato.outgoing.amqp.get-list'
    _filter_by = OutgoingAMQP.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_amqp_get_list_request'
        response_elem = 'zato_outgoing_amqp_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'address', 'username', 'password', 'is_active', 'delivery_mode', 'priority', 'pool_size')
        output_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))

    def get_data(self, session):
        return self._search(out_amqp_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.create'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_create_request'
        response_elem = 'zato_outgoing_amqp_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'delivery_mode', 'priority', 'pool_size')
        input_optional = ('address', 'username', 'password', 'content_type', 'content_encoding',
            'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id', 'name')

    def handle(self):

        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)
        input.expiration = int(input.expiration) if input.expiration else None

        input.frame_max = 131072
        input.heartbeat = 30

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)

        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing AMQP connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = OutgoingAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.username = input.username
                item.password = input.password
                item.delivery_mode = input.delivery_mode # type: ignore
                item.priority = input.priority # type: ignore
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration # type: ignore
                item.pool_size = input.pool_size
                item.user_id = input.user_id
                item.app_id = input.app_id
                item.frame_max = input.frame_max # type: ignore
                item.heartbeat = input.heartbeat # type: ignore

                session.add(item)
                session.commit()

                input.action = OUTGOING.AMQP_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not create an outgoing AMQP connection, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.edit'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_edit_request'
        response_elem = 'zato_outgoing_amqp_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'delivery_mode', 'priority', 'pool_size')
        input_optional = ('address', 'username', 'password', 'content_type', 'content_encoding',
            'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id', 'name')

    def handle(self):

        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)
        input.expiration = int(input.expiration) if input.expiration else None

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)

        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                filter(OutgoingAMQP.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An outgoing AMQP connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = session.query(OutgoingAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.username = input.username
                item.password = input.password
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.pool_size = input.pool_size
                item.user_id = input.user_id
                item.app_id = input.app_id

                session.add(item)
                session.commit()

                input.action = OUTGOING.AMQP_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update the outgoing AMQP connection, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_delete_request'
        response_elem = 'zato_outgoing_amqp_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==self.request.input.id).\
                    one()

                item_id = item.id

                session.delete(item)
                session.commit()

                self.broker_client.publish({
                    'action': OUTGOING.AMQP_DELETE.value,
                    'name': item.name,
                    'id':item_id,
                })

            except Exception:
                session.rollback()
                self.logger.error('Could not delete the outgoing AMQP connection, e:`%s`', format_exc())

                raise

# ################################################################################################################################
# ################################################################################################################################
