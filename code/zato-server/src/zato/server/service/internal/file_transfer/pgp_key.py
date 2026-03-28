# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.common.file_transfer.model import PGPKey
from zato.common.file_transfer.pgp import PGPManager
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    name = 'file-transfer.pgp-key.get-list'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        keys = store.list_pgp_keys()

        self.response.payload = [
            {
                'id': k.id,
                'name': k.name,
                'key_type': k.key_type.value if hasattr(k.key_type, 'value') else k.key_type,
                'usage': ','.join(u.value if hasattr(u, 'value') else u for u in k.usage),
                'fingerprint': k.fingerprint,
                'algorithm': k.algorithm,
                'key_size': k.key_size,
                'expires_at': k.expires_at,
                'is_enabled': k.is_enabled,
            }
            for k in keys
        ]

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.pgp-key.get'

    def handle(self):
        input = self.request.raw_request or {}
        key_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        key = store.get_pgp_key(key_id)

        if not key:
            self.response.payload = {}
            return

        self.response.payload = key.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Import(Service):
    name = 'file-transfer.pgp-key.import'

    def handle(self):
        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        pgp_manager = PGPManager()

        name = input.get('name')
        key_data = input.get('key_data')

        key = pgp_manager.import_key(key_data)
        key.id = f'key-{uuid4().hex[:8]}'
        key.name = name

        is_enabled = input.get('is_enabled')
        if is_enabled is not None:
            key.is_enabled = is_enabled

        store.create_pgp_key(key)
        self.response.payload = {'id': key.id}

# ################################################################################################################################
# ################################################################################################################################

class Generate(Service):
    name = 'file-transfer.pgp-key.generate'

    def handle(self):
        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        pgp_manager = PGPManager()

        name = input.get('name')
        email = input.get('email')
        algorithm = input.get('algorithm', 'RSA')
        key_size = int(input.get('key_size') or 4096)
        passphrase = input.get('passphrase', '')

        public_key, private_key = pgp_manager.generate_keypair(
            name=name,
            email=email,
            algorithm=algorithm,
            key_size=key_size,
            passphrase=passphrase,
        )

        public_key.id = f'key-{uuid4().hex[:8]}'
        public_key.name = f'{name} (public)'
        store.create_pgp_key(public_key)

        private_key.id = f'key-{uuid4().hex[:8]}'
        private_key.name = f'{name} (private)'
        store.create_pgp_key(private_key)

        self.response.payload = {'public_key_id': public_key.id, 'private_key_id': private_key.id}

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.pgp-key.edit'

    def handle(self):
        input = self.request.raw_request or {}
        key_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        key = store.get_pgp_key(key_id)
        if not key:
            raise ValueError(f'PGP key not found: {key_id}')

        for field in ('name', 'usage', 'is_enabled'):
            value = input.get(field)
            if value is not None:
                setattr(key, field, value)

        store.update_pgp_key(key)
        self.response.payload = {'id': key.id}

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.pgp-key.delete'

    def handle(self):
        input = self.request.raw_request or {}
        key_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.delete_pgp_key(key_id)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################
