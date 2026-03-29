# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.common.file_transfer.tasks import TaskManager
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Search(Service):
    name = 'file-transfer.task.search'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        status = self.request.input.get('status')
        tx_id = self.request.input.get('transaction_id')

        if tx_id:
            tasks = store.get_tasks_for_transaction(tx_id)
        elif status:
            task_ids = store.redis.zrange(
                f'zato:file-transfer:{store.cluster_id}:idx:task:by-status:{status}',
                0, -1
            )
            tasks = []
            for task_id in task_ids:
                if isinstance(task_id, bytes):
                    task_id = task_id.decode()
                task = store.get_task(task_id)
                if task:
                    tasks.append(task)
        else:
            tasks = []

        self.response.payload = [
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

class Stop(Service):
    name = 'file-transfer.task.stop'

    def handle(self):
        input = self.request.raw_request or {}
        task_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        task_manager = TaskManager(store)
        task_manager.stop_task(task_id)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################

class Restart(Service):
    name = 'file-transfer.task.restart'

    def handle(self):
        input = self.request.raw_request or {}
        task_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        task_manager = TaskManager(store)
        task_manager.restart_task(task_id)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.task.delete'

    def handle(self):
        input = self.request.raw_request or {}
        task_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.delete_task(task_id)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################
