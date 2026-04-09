# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_amqp'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    name = 'zato.outgoing.amqp.get-list'

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_amqp_get_list_request'
        response_elem = 'zato_outgoing_amqp_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'address', 'username', 'password', 'is_active', 'delivery_mode', 'priority', 'pool_size')
        output_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))

    def handle(self):
        items = self.server.rust_config_store.get_list(_entity_type)
        self.response.payload[:] = items

# ################################################################################################################################
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

        delivery_mode = int(input.delivery_mode)
        priority = int(input.priority)
        expiration = int(input.expiration) if input.expiration else None

        if not(priority >= 0 and priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
            raise ValueError(msg)

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'address': input.address,
            'username': input.username,
            'password': input.password,
            'delivery_mode': delivery_mode,
            'priority': priority,
            'content_type': input.content_type,
            'content_encoding': input.content_encoding,
            'expiration': expiration,
            'pool_size': input.pool_size,
            'user_id': input.user_id,
            'app_id': input.app_id,
            'frame_max': 131072,
            'heartbeat': 30,
        }

        name = input.name
        self.server.rust_config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
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

        delivery_mode = int(input.delivery_mode)
        priority = int(input.priority)
        expiration = int(input.expiration) if input.expiration else None

        if not(priority >= 0 and priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(priority))
            raise ValueError(msg)

        target_id = str(input.id)
        old_name = None
        existing = None
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id:
                old_name = item['name']
                existing = self.server.rust_config_store.get(_entity_type, old_name)
                if not existing:
                    existing = dict(item)
                break
        if not old_name or not existing:
            raise Exception('Outgoing AMQP connection with id `{}` not found'.format(target_id))

        existing.update({
            'id': input.id,
            'name': input.name,
            'is_active': input.is_active,
            'address': input.address,
            'username': input.username,
            'delivery_mode': delivery_mode,
            'priority': priority,
            'content_type': input.content_type,
            'content_encoding': input.content_encoding,
            'expiration': expiration,
            'pool_size': input.pool_size,
            'user_id': input.user_id,
            'app_id': input.app_id,
        })
        if input.get('password'):
            existing['password'] = input.password

        if old_name != input.name:
            self.server.rust_config_store.delete(_entity_type, old_name)

        self.server.rust_config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
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
        target_id = str(self.request.input.id)
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.rust_config_store.delete(_entity_type, item['name'])
                return
        raise Exception('Outgoing AMQP connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class Publish(AdminService):
    """ Publishes a message to an AMQP broker.
    """
    name = 'zato.outgoing.amqp.publish'

    class SimpleIO:
        input_required = 'request_data', 'conn_name', 'exchange', 'routing_key'
        output_optional = 'response_data'
        response_elem = None

    def handle(self):
        input = self.request.input
        self.out.amqp.publish(input.conn_name, input.request_data, input.exchange, input.routing_key)
        self.response.payload.response_data = '{"result": "OK"}'

# ################################################################################################################################
# ################################################################################################################################
