# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.common.file_transfer.model import PickupChannel
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    name = 'file-transfer.pickup-channel.get-list'

    class SimpleIO:
        output_optional = 'id', 'name', 'source_type', 'connection_name', 'remote_path', 'file_pattern', \
            'poll_interval_seconds', 'post_processing_action', 'archive_path', 'is_enabled'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        channels = store.list_pickup_channels()

        self.response.payload[:] = [
            {
                'id': c.id,
                'name': c.name,
                'source_type': c.source_type.value if hasattr(c.source_type, 'value') else c.source_type,
                'connection_name': c.connection_name,
                'remote_path': c.remote_path,
                'file_pattern': c.file_pattern,
                'poll_interval_seconds': c.poll_interval_seconds,
                'post_processing_action': c.post_processing_action.value if hasattr(c.post_processing_action, 'value') else c.post_processing_action,
                'archive_path': c.archive_path,
                'is_enabled': c.is_enabled,
            }
            for c in channels
        ]

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.pickup-channel.get'

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'name', 'source_type', 'connection_name', 'remote_path', 'file_pattern', \
            'poll_interval_seconds', 'post_processing_action', 'archive_path', 'is_enabled'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        channel = store.get_pickup_channel(self.request.input.id)

        if not channel:
            self.response.payload = {}
            return

        self.response.payload = channel.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.pickup-channel.create'

    class SimpleIO:
        input_required = 'name',
        input_optional = 'source_type', 'connection_name', 'remote_path', 'file_pattern', \
            'poll_interval_seconds', 'post_processing_action', 'archive_path', 'is_enabled'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        channel = PickupChannel(
            id=f'pickup-{uuid4().hex[:8]}',
            name=self.request.input.name,
            source_type=self.request.input.get('source_type', 'Sftp'),
            connection_name=self.request.input.get('connection_name', ''),
            remote_path=self.request.input.get('remote_path', '/'),
            file_pattern=self.request.input.get('file_pattern', '*'),
            poll_interval_seconds=float(self.request.input.get('poll_interval_seconds', 60)),
            post_processing_action=self.request.input.get('post_processing_action', 'Delete'),
            archive_path=self.request.input.get('archive_path', ''),
            is_enabled=self.request.input.get('is_enabled', True),
        )

        store.create_pickup_channel(channel)
        self.response.payload.id = channel.id

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.pickup-channel.edit'

    class SimpleIO:
        input_required = 'id',
        input_optional = 'name', 'source_type', 'connection_name', 'remote_path', 'file_pattern', \
            'poll_interval_seconds', 'post_processing_action', 'archive_path', 'is_enabled'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        channel = store.get_pickup_channel(self.request.input.id)
        if not channel:
            raise ValueError(f'Pickup channel not found: {self.request.input.id}')

        for field in ('name', 'source_type', 'connection_name', 'remote_path', 'file_pattern',
                      'poll_interval_seconds', 'post_processing_action', 'archive_path', 'is_enabled'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                setattr(channel, field, value)

        store.update_pickup_channel(channel)
        self.response.payload.id = channel.id

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.pickup-channel.delete'

    class SimpleIO:
        input_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.delete_pickup_channel(self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################
