# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_amqp'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    name = 'zato.outgoing.amqp.get-list'

    input = 'cluster_id'
    output = 'id', 'name', 'address', 'username', 'password', 'is_active', 'delivery_mode', 'priority', 'pool_size', \
        '-content_type', '-content_encoding', '-expiration', AsIs('-user_id'), AsIs('-app_id')

    def handle(self):
        items = self.server.config_store.get_list(_entity_type)
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.create'

    input = 'cluster_id', 'name', 'is_active', 'delivery_mode', Int('priority'), Int('pool_size'), \
        '-address', '-username', '-password', '-content_type', '-content_encoding', \
        '-expiration', AsIs('-user_id'), AsIs('-app_id')
    output = 'id', 'name'

    def handle(self):

        input = self.request.input

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'address': input.address,
            'username': input.username,
            'password': input.password,
            'delivery_mode': input.delivery_mode,
            'priority': input.priority,
            'content_type': input.content_type,
            'content_encoding': input.content_encoding,
            'expiration': input.expiration,
            'pool_size': input.pool_size,
            'user_id': input.user_id,
            'app_id': input.app_id,
            'frame_max': 131072,
            'heartbeat': 30,
        }

        name = input.name
        self.server.config_store.set(_entity_type, name, data)

        stored = self.server.config_store.get(_entity_type, name)
        self.response.payload.id = stored['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.edit'

    input = 'id', 'cluster_id', 'name', 'is_active', 'delivery_mode', Int('priority'), Int('pool_size'), \
        '-address', '-username', '-password', '-content_type', '-content_encoding', \
        '-expiration', AsIs('-user_id'), AsIs('-app_id')
    output = 'id', 'name'

    def handle(self):

        input = self.request.input

        target_id = str(input.id)
        old_name = None
        existing = None
        for item in self.server.config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id:
                old_name = item['name']
                existing = self.server.config_store.get(_entity_type, old_name)
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
            'delivery_mode': input.delivery_mode,
            'priority': input.priority,
            'content_type': input.content_type,
            'content_encoding': input.content_encoding,
            'expiration': input.expiration,
            'pool_size': input.pool_size,
            'user_id': input.user_id,
            'app_id': input.app_id,
        })
        if input.get('password'):
            existing['password'] = input.password

        if old_name != input.name:
            self.server.config_store.delete(_entity_type, old_name)

        self.server.config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.delete'

    input = 'id'

    def handle(self):
        target_id = str(self.request.input.id)
        for item in self.server.config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.config_store.delete(_entity_type, item['name'])
                return
        raise Exception('Outgoing AMQP connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class Publish(AdminService):
    """ Publishes a message to an AMQP broker.
    """
    name = 'zato.outgoing.amqp.publish'

    input = 'request_data', 'conn_name', 'exchange', 'routing_key'
    output = '-response_data'

    def handle(self):
        input = self.request.input
        self.out.amqp.publish(input.conn_name, input.request_data, input.exchange, input.routing_key)
        self.response.payload.response_data = '{"result": "OK"}'

# ################################################################################################################################
# ################################################################################################################################
