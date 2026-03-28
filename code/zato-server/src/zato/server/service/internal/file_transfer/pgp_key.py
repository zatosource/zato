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

    class SimpleIO:
        output_optional = 'id', 'name', 'key_type', 'usage', 'fingerprint', 'algorithm', 'key_size', 'expires_at', 'is_enabled'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        keys = store.list_pgp_keys()

        self.response.payload[:] = [
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

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'name', 'key_type', 'usage', 'key_data', 'fingerprint', 'algorithm', 'key_size', 'created_at', 'expires_at', 'is_enabled'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        key = store.get_pgp_key(self.request.input.id)

        if not key:
            self.response.payload = {}
            return

        self.response.payload = key.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Import(Service):
    name = 'file-transfer.pgp-key.import'

    class SimpleIO:
        input_required = 'name', 'key_data'
        input_optional = 'is_enabled',
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        pgp_manager = PGPManager()

        key = pgp_manager.import_key(self.request.input.key_data)
        key.id = f'key-{uuid4().hex[:8]}'
        key.name = self.request.input.name

        is_enabled = self.request.input.get('is_enabled')
        if is_enabled is not None:
            key.is_enabled = is_enabled

        store.create_pgp_key(key)
        self.response.payload.id = key.id

# ################################################################################################################################
# ################################################################################################################################

class Generate(Service):
    name = 'file-transfer.pgp-key.generate'

    class SimpleIO:
        input_required = 'name', 'email'
        input_optional = 'algorithm', 'key_size', 'passphrase'
        output_required = 'public_key_id', 'private_key_id'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        pgp_manager = PGPManager()

        algorithm = self.request.input.get('algorithm', 'RSA')
        key_size = int(self.request.input.get('key_size', 4096))
        passphrase = self.request.input.get('passphrase', '')

        public_key, private_key = pgp_manager.generate_keypair(
            name=self.request.input.name,
            email=self.request.input.email,
            algorithm=algorithm,
            key_size=key_size,
            passphrase=passphrase,
        )

        public_key.id = f'key-{uuid4().hex[:8]}'
        public_key.name = f'{self.request.input.name} (public)'
        store.create_pgp_key(public_key)

        private_key.id = f'key-{uuid4().hex[:8]}'
        private_key.name = f'{self.request.input.name} (private)'
        store.create_pgp_key(private_key)

        self.response.payload.public_key_id = public_key.id
        self.response.payload.private_key_id = private_key.id

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.pgp-key.edit'

    class SimpleIO:
        input_required = 'id',
        input_optional = 'name', 'usage', 'is_enabled'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        key = store.get_pgp_key(self.request.input.id)
        if not key:
            raise ValueError(f'PGP key not found: {self.request.input.id}')

        for field in ('name', 'usage', 'is_enabled'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                setattr(key, field, value)

        store.update_pgp_key(key)
        self.response.payload.id = key.id

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.pgp-key.delete'

    class SimpleIO:
        input_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.delete_pgp_key(self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################
