# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.engine import FileTransferEngine
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Search(Service):
    name = 'file-transfer.transaction.search'

    class SimpleIO:
        input_optional = 'date_from', 'date_to', 'status', 'sender', 'receiver', 'doc_type_id', 'limit', 'offset'
        output_optional = 'id', 'created', 'filename', 'doc_type_id', 'sender', 'receiver', 'processing_status', 'user_status'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        date_from = self.request.input.get('date_from')
        date_to = self.request.input.get('date_to')
        if date_from:
            date_from = float(date_from)
        if date_to:
            date_to = float(date_to)

        transactions, total = store.search_transactions(
            date_from=date_from,
            date_to=date_to,
            status=self.request.input.get('status'),
            sender=self.request.input.get('sender'),
            receiver=self.request.input.get('receiver'),
            doc_type_id=self.request.input.get('doc_type_id'),
            limit=int(self.request.input.get('limit', 100)),
            offset=int(self.request.input.get('offset', 0)),
        )

        self.response.payload[:] = [
            {
                'id': t.id,
                'created': t.created,
                'filename': t.filename,
                'doc_type_id': t.doc_type_id,
                'sender': t.sender,
                'receiver': t.receiver,
                'processing_status': t.processing_status.value if hasattr(t.processing_status, 'value') else t.processing_status,
                'user_status': t.user_status,
            }
            for t in transactions
        ]

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.transaction.get'

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'created', 'completed', 'filename', 'file_size', 'source_checksum', 'dest_checksum', \
            'source_protocol', 'source_detail', 'doc_type_id', 'sender', 'receiver', 'document_id', \
            'conversation_id', 'group_id', 'processing_status', 'user_status', 'matched_rule_id', \
            'has_errors', 'duration_ms', 'content_saved', 'resubmitted_from', 'custom_attrs'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        txn = store.get_transaction(self.request.input.id)

        if not txn:
            self.response.payload = {}
            return

        self.response.payload = txn.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class GetContent(Service):
    name = 'file-transfer.transaction.get-content'

    class SimpleIO:
        input_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        content = store.get_content(self.request.input.id)

        if content:
            self.response.payload = content
        else:
            self.response.payload = b''

# ################################################################################################################################
# ################################################################################################################################

class GetActivity(Service):
    name = 'file-transfer.transaction.get-activity'

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'transaction_id', 'timestamp', 'activity_class', 'severity', 'message', 'detail'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        entries = store.get_logs_for_transaction(self.request.input.id)

        self.response.payload[:] = [
            {
                'id': e.id,
                'transaction_id': e.transaction_id,
                'timestamp': e.timestamp,
                'activity_class': e.activity_class.value if hasattr(e.activity_class, 'value') else e.activity_class,
                'severity': e.severity.value if hasattr(e.severity, 'value') else e.severity,
                'message': e.message,
                'detail': e.detail,
            }
            for e in entries
        ]

# ################################################################################################################################
# ################################################################################################################################

class GetTasks(Service):
    name = 'file-transfer.transaction.get-tasks'

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'transaction_id', 'task_type', 'status', 'created', 'retry_count', 'max_retries', 'next_retry_at', 'error_detail'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        tasks = store.get_tasks_for_transaction(self.request.input.id)

        self.response.payload[:] = [
            {
                'id': t.id,
                'transaction_id': t.transaction_id,
                'task_type': t.task_type.value if hasattr(t.task_type, 'value') else t.task_type,
                'status': t.status.value if hasattr(t.status, 'value') else t.status,
                'created': t.created,
                'retry_count': t.retry_count,
                'max_retries': t.max_retries,
                'next_retry_at': t.next_retry_at,
                'error_detail': t.error_detail,
            }
            for t in tasks
        ]

# ################################################################################################################################
# ################################################################################################################################

class Resubmit(Service):
    name = 'file-transfer.transaction.resubmit'

    class SimpleIO:
        input_required = 'id',
        output_required = 'new_id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        engine = FileTransferEngine(store)

        new_txn = engine.resubmit(self.request.input.id)

        if new_txn:
            self.response.payload.new_id = new_txn.id
        else:
            raise ValueError(f'Could not resubmit transaction: {self.request.input.id}')

# ################################################################################################################################
# ################################################################################################################################

class Reprocess(Service):
    name = 'file-transfer.transaction.reprocess'

    class SimpleIO:
        input_required = 'id',
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        engine = FileTransferEngine(store)

        txn = engine.reprocess(self.request.input.id)

        if txn:
            self.response.payload.id = txn.id
        else:
            raise ValueError(f'Could not reprocess transaction: {self.request.input.id}')

# ################################################################################################################################
# ################################################################################################################################
