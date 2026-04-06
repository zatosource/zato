# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import loads

# zato-broker-core (Rust extension)
from zato_broker_core import (
    fs_backup,
    fs_eda_overview,
    fs_message_detail,
    fs_message_list,
    fs_queue_detail,
    fs_queue_purge,
    fs_restore_item,
    fs_status,
    fs_stream_xadd,
    fs_topic_detail,
    fs_topic_purge,
    fs_topic_stats,
    fs_validate,
)

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    StaticID = 12345

# ################################################################################################################################
# ################################################################################################################################

class GetConfig(Service):

    output = 'id', 'is_active', 'name', 'broker_dir', 'poll_interval', \
        'reply_poll_interval', 'cleanup_interval', 'ttl_check_interval'

    def handle(self) -> 'None':
        client = self.server.broker_client

        self.response.payload.id = ModuleCtx.StaticID
        self.response.payload.name = 'default'
        self.response.payload.is_active = True
        self.response.payload.broker_dir = client.broker_dir
        self.response.payload.poll_interval = client._poll_interval
        self.response.payload.reply_poll_interval = client._reply_poll_interval
        self.response.payload.cleanup_interval = int(os.environ.get('Zato_Broker_Cleanup_Interval', '60'))
        self.response.payload.ttl_check_interval = int(os.environ.get('Zato_Broker_TTL_Check_Interval', '1'))

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):

    input = 'broker_dir', 'poll_interval', 'reply_poll_interval', 'cleanup_interval', 'ttl_check_interval'
    output = 'id', 'name'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        client._poll_interval = float(input.poll_interval)
        client._reply_poll_interval = float(input.reply_poll_interval)

        os.environ['Zato_Broker_Cleanup_Interval'] = str(input.cleanup_interval)
        os.environ['Zato_Broker_TTL_Check_Interval'] = str(input.ttl_check_interval)

        self.response.payload.id = ModuleCtx.StaticID
        self.response.payload.name = 'default'

# ################################################################################################################################
# ################################################################################################################################

class Status(Service):

    output = 'is_ok', 'broker_dir', 'channels', 'kv_keys', 'lists', 'sets', 'streams'

    def handle(self) -> 'None':
        client = self.server.broker_client
        status = loads(fs_status(client._cfg))

        self.response.payload.is_ok = True
        self.response.payload.broker_dir = client.broker_dir
        self.response.payload.channels = status['channels']
        self.response.payload.kv_keys = status['kv_keys']
        self.response.payload.lists = status['lists']
        self.response.payload.sets = status['sets']
        self.response.payload.streams = status['streams']

# ################################################################################################################################
# ################################################################################################################################

class Validate(Service):

    output = 'valid', 'errors'

    def handle(self) -> 'None':
        client = self.server.broker_client
        is_valid, errors = fs_validate(client._cfg)

        self.response.payload.valid = is_valid
        self.response.payload.errors = errors

# ################################################################################################################################
# ################################################################################################################################

class Backup(Service):

    input = '-backup_dir', '-compress'
    output = 'is_ok', 'backup_path', 'size_bytes', 'duration_ms'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        backup_dir = input.get('backup_dir') or os.path.join(client.broker_dir, '_backups')
        compress = bool(input.get('compress'))

        result = loads(fs_backup(client._cfg, backup_dir, compress))

        self.response.payload.is_ok = True
        self.response.payload.backup_path = result['backup_dir']
        self.response.payload.size_bytes = result['size_bytes']
        self.response.payload.duration_ms = result['duration_ms']

# ################################################################################################################################
# ################################################################################################################################

class BackupList(Service):

    input = '-backup_dir'
    output = 'backups'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        backup_dir = input.get('backup_dir') or os.path.join(client.broker_dir, '_backups')
        backups:'anylist' = []

        if os.path.isdir(backup_dir):
            for entry in sorted(os.listdir(backup_dir)):
                entry_path = os.path.join(backup_dir, entry)
                if os.path.isdir(entry_path):
                    size = 0
                    for dirpath, _dirnames, filenames in os.walk(entry_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.isfile(fp):
                                size += os.path.getsize(fp)
                    stat = os.stat(entry_path)
                    backups.append({
                        'name': entry,
                        'path': entry_path,
                        'size_bytes': size,
                        'created': stat.st_ctime,
                    })

        self.response.payload.backups = backups

# ################################################################################################################################
# ################################################################################################################################

class Restore(Service):

    input = 'backup_path', '-items'
    output = 'is_ok', 'details'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        backup_path = input.backup_path
        items = input.get('items') or []

        if isinstance(items, str):
            items = loads(items)

        if not items:
            self.response.payload.is_ok = False
            self.response.payload.details = 'Full restore requires stopped components; provide specific items to restore'
            return

        for item in items:
            fs_restore_item(client._cfg, backup_path, item)

        self.response.payload.is_ok = True
        self.response.payload.details = f'Restored {len(items)} item(s) from {backup_path}'

# ################################################################################################################################
# ################################################################################################################################

class Dashboard(Service):

    output = 'topic_count', 'total_messages', 'total_depth', 'total_groups', 'topics', 'queues'

    def handle(self) -> 'None':
        client = self.server.broker_client
        data = loads(fs_eda_overview(client._cfg))

        self.response.payload.topic_count = data['topic_count']
        self.response.payload.total_messages = data['total_messages']
        self.response.payload.total_depth = data['total_depth']
        self.response.payload.total_groups = data['total_groups']
        self.response.payload.topics = data['topics']
        self.response.payload.queues = data['queues']

# ################################################################################################################################
# ################################################################################################################################

class TopicGetDetail(Service):

    input = 'topic_name', '-last_n'
    output = 'name', 'total_published', 'depth', 'last_pub_ts', 'messages', 'queues'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client
        last_n = int(input.get('last_n') or 25)

        data = loads(fs_topic_detail(client._cfg, input.topic_name, last_n))

        self.response.payload.name = data['name']
        self.response.payload.total_published = data['total_published']
        self.response.payload.depth = data['depth']
        self.response.payload.last_pub_ts = data['last_pub_ts']
        self.response.payload.messages = data['messages']
        self.response.payload.queues = data['queues']

# ################################################################################################################################
# ################################################################################################################################

class QueueGetDetail(Service):

    input = 'stream_name', 'group_name', '-last_n'
    output = 'group_name', 'stream_name', 'depth', 'messages'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client
        last_n = int(input.get('last_n') or 25)

        data = loads(fs_queue_detail(client._cfg, input.stream_name, input.group_name, last_n))

        self.response.payload.group_name = data['group_name']
        self.response.payload.stream_name = data['stream_name']
        self.response.payload.depth = data['depth']
        self.response.payload.messages = data['messages']

# ################################################################################################################################
# ################################################################################################################################

class MessageGetList(Service):

    input = '-stream_name', '-offset', '-limit'
    output = 'messages', 'total'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        stream_name = input.get('stream_name') or None
        offset = int(input.get('offset') or 0)
        limit = int(input.get('limit') or 50)

        data = loads(fs_message_list(client._cfg, stream_name, offset, limit))

        self.response.payload.messages = data['messages']
        self.response.payload.total = data['total']

# ################################################################################################################################
# ################################################################################################################################

class MessageGetDetail(Service):

    input = 'stream_name', 'msg_id'
    output = 'msg_id', 'stream_name', 'data', 'size', 'pub_time_ts', 'delivery_status'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        data = loads(fs_message_detail(client._cfg, input.stream_name, input.msg_id))

        self.response.payload.msg_id = data['msg_id']
        self.response.payload.stream_name = data['stream_name']
        self.response.payload.data = data['data']
        self.response.payload.size = data['size']
        self.response.payload.pub_time_ts = data['pub_time_ts']
        self.response.payload.delivery_status = data['delivery_status']

# ################################################################################################################################
# ################################################################################################################################

class TopicPurge(Service):

    input = 'topic_name'
    output = 'is_ok', 'messages_removed'

    def handle(self) -> 'None':
        client = self.server.broker_client
        count = fs_topic_purge(client._cfg, self.request.input.topic_name)

        self.response.payload.is_ok = True
        self.response.payload.messages_removed = count

# ################################################################################################################################
# ################################################################################################################################

class QueuePurge(Service):

    input = 'stream_name', 'group_name'
    output = 'is_ok', 'messages_removed'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client
        count = fs_queue_purge(client._cfg, input.stream_name, input.group_name)

        self.response.payload.is_ok = True
        self.response.payload.messages_removed = count

# ################################################################################################################################
# ################################################################################################################################

class TopicPublish(Service):

    input = 'topic_name', 'data', '-priority', '-expiration'
    output = 'is_ok', 'msg_id'

    def handle(self) -> 'None':
        input = self.request.input
        client = self.server.broker_client

        from json import dumps
        fields = {
            'data': input.data,
            'priority': int(input.get('priority') or 5),
            'expiration': int(input.get('expiration') or 86400),
        }

        msg_id = fs_stream_xadd(client._cfg, input.topic_name, dumps(fields))

        self.response.payload.is_ok = True
        self.response.payload.msg_id = msg_id

# ################################################################################################################################
# ################################################################################################################################
