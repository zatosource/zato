# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.common.file_transfer.model import DocumentType
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    name = 'file-transfer.doc-type.get-list'

    class SimpleIO:
        output_optional = 'id', 'name', 'description', 'is_enabled', 'file_type'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        doc_types = store.list_document_types()

        self.response.payload[:] = [
            {
                'id': dt.id,
                'name': dt.name,
                'description': dt.description,
                'is_enabled': dt.is_enabled,
                'file_type': dt.file_type.value if hasattr(dt.file_type, 'value') else dt.file_type,
            }
            for dt in doc_types
        ]

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.doc-type.get'

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'name', 'description', 'is_enabled', 'file_type', 'recognition_rules', 'extraction_rules', \
            'preprocess_validate', 'preprocess_validate_schema', 'preprocess_dedup', 'preprocess_dedup_window_days', \
            'preprocess_pgp_verify', 'preprocess_pgp_key_id', 'preprocess_checksum', 'preprocess_save'

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        dt = store.get_document_type(self.request.input.id)

        if not dt:
            self.response.payload = {}
            return

        self.response.payload = dt.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.doc-type.create'

    class SimpleIO:
        input_required = 'name', 'file_type'
        input_optional = 'description', 'is_enabled', 'recognition_rules', 'extraction_rules', \
            'preprocess_validate', 'preprocess_validate_schema', 'preprocess_dedup', 'preprocess_dedup_window_days', \
            'preprocess_pgp_verify', 'preprocess_pgp_key_id', 'preprocess_checksum', 'preprocess_save'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        dt_id = f'dt-{uuid4().hex[:8]}'

        data = {
            'id': dt_id,
            'name': self.request.input.name,
            'file_type': self.request.input.file_type,
        }

        for field in ('description', 'is_enabled', 'recognition_rules', 'extraction_rules',
                      'preprocess_validate', 'preprocess_validate_schema', 'preprocess_dedup',
                      'preprocess_dedup_window_days', 'preprocess_pgp_verify', 'preprocess_pgp_key_id',
                      'preprocess_checksum', 'preprocess_save'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                data[field] = value

        dt = DocumentType.from_dict(data)
        store.create_document_type(dt)

        self.response.payload.id = dt_id

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.doc-type.edit'

    class SimpleIO:
        input_required = 'id',
        input_optional = 'name', 'description', 'is_enabled', 'file_type', 'recognition_rules', 'extraction_rules', \
            'preprocess_validate', 'preprocess_validate_schema', 'preprocess_dedup', 'preprocess_dedup_window_days', \
            'preprocess_pgp_verify', 'preprocess_pgp_key_id', 'preprocess_checksum', 'preprocess_save'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        dt = store.get_document_type(self.request.input.id)
        if not dt:
            raise ValueError(f'Document type not found: {self.request.input.id}')

        for field in ('name', 'description', 'is_enabled', 'file_type', 'recognition_rules', 'extraction_rules',
                      'preprocess_validate', 'preprocess_validate_schema', 'preprocess_dedup',
                      'preprocess_dedup_window_days', 'preprocess_pgp_verify', 'preprocess_pgp_key_id',
                      'preprocess_checksum', 'preprocess_save'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                setattr(dt, field, value)

        store.update_document_type(dt)
        self.response.payload.id = dt.id

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.doc-type.delete'

    class SimpleIO:
        input_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        store.delete_document_type(self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################
