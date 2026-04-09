# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'channel_amqp'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of AMQP channels.
    """
    name = 'zato.channel.amqp.get-list'

    input = 'cluster_id'
    output = ('id', 'name', 'address', 'username', 'password', 'is_active', 'queue', 'consumer_tag_prefix',
        'service_name', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format')
    output_repeated = True

    def handle(self):
        items = self.server.config_store.get_list(_entity_type)
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new AMQP channel.
    """
    name = 'zato.channel.amqp.create'

    input = ('cluster_id', 'name', 'is_active', 'address', 'username', 'password', 'queue', 'consumer_tag_prefix',
        'service', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'address': input.address,
            'username': input.username,
            'password': input.password,
            'queue': input.queue,
            'consumer_tag_prefix': input.consumer_tag_prefix,
            'service_name': input.service,
            'pool_size': input.pool_size,
            'ack_mode': input.ack_mode,
            'prefetch_count': input.prefetch_count,
            'data_format': input.get('data_format'),
            'frame_max': 131072,
            'heartbeat': 30,
        }

        name = input.name
        self.server.config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an AMQP channel.
    """
    name = 'zato.channel.amqp.edit'

    input = ('id', 'cluster_id', 'name', 'is_active', 'address', 'username', 'password', 'queue',
        'consumer_tag_prefix', 'service', 'pool_size', 'ack_mode', 'prefetch_count', '-data_format')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input

        data = {
            'id': input.id,
            'name': input.name,
            'is_active': input.is_active,
            'address': input.address,
            'username': input.username,
            'password': input.password,
            'queue': input.queue,
            'consumer_tag_prefix': input.consumer_tag_prefix,
            'service_name': input.service,
            'pool_size': input.pool_size,
            'ack_mode': input.ack_mode,
            'prefetch_count': input.prefetch_count,
            'data_format': input.get('data_format'),
        }

        name = input.name
        self.server.config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an AMQP channel.
    """
    name = 'zato.channel.amqp.delete'

    input = 'id'

    def handle(self):
        name = str(self.request.input.id)
        self.server.config_store.delete(_entity_type, name)

# ################################################################################################################################
# ################################################################################################################################
