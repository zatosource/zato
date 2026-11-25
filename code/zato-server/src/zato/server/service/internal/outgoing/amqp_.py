# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import query_parameters
from zato.common.broker_message import OUTGOING
from zato.common.exception import PingNotSupported
from zato.common.json_internal import dumps
from zato.common.odb.model import OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.common.util.time_ import utcnow
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService

_delivery_mode_map = {
    'non_persistent': 1,
    'persistent': 2,
}

def _resolve_delivery_mode(value):
    if isinstance(value, str) and value in _delivery_mode_map:
        return _delivery_mode_map[value]
    return int(value)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    name = 'zato.outgoing.amqp.get-list'
    _filter_by = OutgoingAMQP.name,

    input = '-subtype', *query_parameters
    output = 'id', 'name', 'address', 'username', 'is_active', 'delivery_mode', 'priority', 'pool_size', \
        '-content_type', '-content_encoding', '-expiration', AsIs('-user_id'), AsIs('-app_id')

    def get_data(self, session):

        # Without a subtype on input, connections of all the subtypes are returned
        subtype = self.request.input.subtype or None

        return self._search(out_amqp_list, session, subtype, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.strip_listing_secrets(self.get_data(session))
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    changes_config = True
    name = 'zato.outgoing.amqp.create'

    input = 'name', 'is_active', 'delivery_mode', 'priority', 'pool_size', \
        '-address', '-username', '-password', '-content_type', '-content_encoding', \
        '-expiration', '-subtype', AsIs('-user_id'), AsIs('-app_id')
    output = 'id', 'name'

    def handle(self):

        input = self.request.input

        input.delivery_mode = _resolve_delivery_mode(input.delivery_mode)
        input.priority = int(input.priority)
        input.pool_size = int(input.pool_size)
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
                raise Exception('An outgoing AMQP connection `{}` already exists'.format(input.name))

            try:
                item = OutgoingAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.username = input.username
                item.password = self.encrypt_input_secret(input.password)
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

                # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
                if input.subtype:
                    item.opaque1 = dumps({'subtype': input.subtype})

                session.add(item)
                session.commit()

                # The connector needs the newly assigned ID in the config event
                input.id = item.id

                input.action = OUTGOING.AMQP_CREATE.value
                self.config_dispatcher.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not create an outgoing AMQP connection, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    changes_config = True
    name = 'zato.outgoing.amqp.edit'

    input = 'id', 'name', 'is_active', 'delivery_mode', 'priority', 'pool_size', \
        '-address', '-username', '-password', '-content_type', '-content_encoding', \
        '-expiration', '-subtype', AsIs('-user_id'), AsIs('-app_id')
    output = 'id', 'name'

    def handle(self):

        input = self.request.input

        input.delivery_mode = _resolve_delivery_mode(input.delivery_mode)
        input.priority = int(input.priority)
        input.pool_size = int(input.pool_size)
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
                raise Exception('An outgoing AMQP connection `{}` already exists'.format(input.name))

            try:
                item = session.query(OutgoingAMQP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.address = input.address
                item.username = input.username
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.pool_size = input.pool_size
                item.user_id = input.user_id
                item.app_id = input.app_id

                # A password on input replaces the stored one, a blank field keeps it
                if input.password:
                    item.password = self.encrypt_input_secret(input.password)

                # The subtype, e.g. Azure Service Bus, is kept in the opaque attributes
                if input.subtype:
                    item.opaque1 = dumps({'subtype': input.subtype})

                session.add(item)
                session.commit()

                # The runtime reconnects with the stored password, whichever way it got there
                input.password = item.password

                input.action = OUTGOING.AMQP_EDIT.value
                input.old_name = old_name
                self.config_dispatcher.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update the outgoing AMQP connection, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    changes_config = True
    name = 'zato.outgoing.amqp.delete'

    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==self.request.input.id).\
                    one()

                item_id = item.id

                session.delete(item)
                session.commit()

                self.config_dispatcher.publish({
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

class Publish(AdminService):
    """ Publishes a message to an AMQP broker.
    """
    name = 'zato.outgoing.amqp.publish'

    input = 'request_data', 'conn_name', 'exchange', 'routing_key'
    output = '-response_data',

    def handle(self):
        input = self.request.input
        self.out.amqp.publish(input.conn_name, input.request_data, input.exchange, input.routing_key)
        self.response.payload.response_data = '{"result": "OK"}'

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Connects to the broker of an outgoing AMQP connection without publishing anything.
    """
    name = 'zato.outgoing.amqp.ping'

    input = Int('id')
    output = 'info', '-is_success'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(OutgoingAMQP).\
                filter(OutgoingAMQP.id==self.request.input.id).\
                one()

        start_time = utcnow()

        try:
            self.server.config_manager.amqp_ping(item.name)

        # A broker type without a ping implementation is not a failure of the connection itself ..
        except PingNotSupported as e:
            self.logger.info(e.msg)
            self.response.payload.info = e.msg
            self.response.payload.is_success = False

        # .. whereas this is one.
        except Exception as e:

            # The full traceback goes to the server log ..
            self.logger.warning(format_exc())

            # .. while the caller gets the actual error message alone.
            error_message = str(e)
            if not error_message:
                error_message = e.__class__.__name__

            self.response.payload.info = error_message
            self.response.payload.is_success = False

        else:
            response_time = utcnow() - start_time
            info = f'Connection pinged, response time: {response_time}'
            self.logger.info(info)
            self.response.payload.info = info
            self.response.payload.is_success = True

# ################################################################################################################################
# ################################################################################################################################
