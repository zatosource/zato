# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from typing import Optional, Tuple

# Zato
from zato.common.file_transfer.const import TaskStatus, TaskType
from zato.common.file_transfer.model import Task

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

class TaskManager:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        service_invoker:'callable_'=None,
        delivery_handler:'callable_'=None,
    ) -> 'None':
        self.store = store
        self.service_invoker = service_invoker
        self.delivery_handler = delivery_handler

# ################################################################################################################################

    def create_delivery_task(
        self,
        txn_id:'str',
        protocol:'str',
        detail:'str',
        max_retries:'int'=3,
        retry_wait_ms:'int'=60000,
        backoff_factor:'float'=2.0,
    ) -> 'Task':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=txn_id,
            task_type=TaskType.Delivery,
            status=TaskStatus.New,
            created=time.time(),
            updated=time.time(),
            max_retries=max_retries,
            retry_wait_ms=retry_wait_ms,
            backoff_factor=backoff_factor,
            delivery_protocol=protocol,
            delivery_detail=detail,
        )

        self.store.create_task(task)
        return task

# ################################################################################################################################

    def create_service_task(
        self,
        txn_id:'str',
        service_name:'str',
        max_retries:'int'=3,
        retry_wait_ms:'int'=60000,
        backoff_factor:'float'=2.0,
    ) -> 'Task':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=txn_id,
            task_type=TaskType.Service_Execution,
            status=TaskStatus.New,
            created=time.time(),
            updated=time.time(),
            max_retries=max_retries,
            retry_wait_ms=retry_wait_ms,
            backoff_factor=backoff_factor,
            service_name=service_name,
        )

        self.store.create_task(task)
        return task

# ################################################################################################################################

    def execute_task(self, task:'Task') -> 'Tuple[bool, Optional[str]]':

        task.status = TaskStatus.Delivering
        task.updated = time.time()
        self.store.update_task(task)

        task_type = task.task_type
        if isinstance(task_type, str):
            task_type = TaskType(task_type)

        try:
            if task_type == TaskType.Delivery:
                success, error = self._execute_delivery(task)
            elif task_type == TaskType.Service_Execution:
                success, error = self._execute_service(task)
            else:
                success, error = False, f'Unknown task type: {task_type}'

            if success:
                task.status = TaskStatus.Done
                task.updated = time.time()
                task.next_retry_at = None
                self.store.update_task(task)
            else:
                self.handle_task_failure(task, error)

            return success, error

        except Exception as e:
            error = str(e)
            self.handle_task_failure(task, error)
            return False, error

# ################################################################################################################################

    def _execute_delivery(self, task:'Task') -> 'Tuple[bool, Optional[str]]':

        if self.delivery_handler:
            txn = self.store.get_transaction(task.transaction_id)
            if not txn:
                return False, f'Transaction not found: {task.transaction_id}'

            content = self.store.get_content(task.transaction_id)
            if not content:
                return False, f'Content not found for transaction: {task.transaction_id}'

            try:
                success, error = self.delivery_handler(
                    content=content,
                    protocol=task.delivery_protocol,
                    detail=task.delivery_detail,
                    filename=txn.filename,
                )
                return success, error
            except Exception as e:
                return False, str(e)

        return True, None

# ################################################################################################################################

    def _execute_service(self, task:'Task') -> 'Tuple[bool, Optional[str]]':

        if self.service_invoker:
            txn = self.store.get_transaction(task.transaction_id)
            if not txn:
                return False, f'Transaction not found: {task.transaction_id}'

            content = self.store.get_content(task.transaction_id)

            try:
                request_data = {
                    'transaction_id': txn.id,
                    'filename': txn.filename,
                    'sender': txn.sender,
                    'receiver': txn.receiver,
                    'document_id': txn.document_id,
                    'doc_type_id': txn.doc_type_id,
                    'custom_attrs': txn.custom_attrs,
                }
                if content:
                    request_data['content'] = content

                self.service_invoker(task.service_name, request_data)
                return True, None
            except Exception as e:
                return False, str(e)

        return True, None

# ################################################################################################################################

    def handle_task_failure(self, task:'Task', error:'Optional[str]') -> 'None':

        task.retry_count += 1
        task.error_detail = error or ''
        task.updated = time.time()

        if task.retry_count >= task.max_retries:
            task.status = TaskStatus.Failed
            task.next_retry_at = None
        else:
            task.status = TaskStatus.Pending
            wait_ms = task.retry_wait_ms * (task.backoff_factor ** (task.retry_count - 1))
            task.next_retry_at = time.time() + (wait_ms / 1000.0)

        self.store.update_task(task)

# ################################################################################################################################

    def stop_task(self, task_id:'str') -> 'bool':

        task = self.store.get_task(task_id)
        if not task:
            return False

        task.status = TaskStatus.Stopped
        task.next_retry_at = None
        task.updated = time.time()
        self.store.update_task(task)
        return True

# ################################################################################################################################

    def restart_task(self, task_id:'str') -> 'bool':

        task = self.store.get_task(task_id)
        if not task:
            return False

        task.retry_count = 0
        task.status = TaskStatus.New
        task.error_detail = ''
        task.next_retry_at = None
        task.updated = time.time()
        self.store.update_task(task)

        return True

# ################################################################################################################################
# ################################################################################################################################
