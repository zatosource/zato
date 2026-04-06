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
    fs_restore_item,
    fs_status,
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
