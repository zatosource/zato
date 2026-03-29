# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.file_transfer.const import TaskStatus, TaskType
from zato.common.file_transfer.model import ActionResult, Task

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
        tx_id:'str',
        protocol:'str',
        detail:'str',
        max_retries:'int'=3,
        retry_wait_ms:'int'=60000,
        backoff_factor:'float'=2.0,
    ) -> 'Task':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=tx_id,
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
        tx_id:'str',
        service_name:'str',
        max_retries:'int'=3,
        retry_wait_ms:'int'=60000,
        backoff_factor:'float'=2.0,
    ) -> 'Task':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=tx_id,
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

    def execute_task(self, task:'Task') -> 'ActionResult':

        task.status = TaskStatus.Delivering
        task.updated = time.time()
        self.store.update_task(task)

        task_type = task.task_type
        if isinstance(task_type, str):
            task_type = TaskType(task_type)

        try:
            if task_type == TaskType.Delivery:
                result = self._execute_delivery(task)
            elif task_type == TaskType.Service_Execution:
                result = self._execute_service(task)
            else:
                result = ActionResult(is_ok=False, error=f'Unknown task type: {task_type}')

            if result.is_ok:
                task.status = TaskStatus.Done
                task.updated = time.time()
                task.next_retry_at = None
                self.store.update_task(task)
            else:
                self.handle_task_failure(task, result.error)

            return result

        except Exception as e:
            error = str(e)
            self.handle_task_failure(task, error)
            return ActionResult(is_ok=False, error=error)

# ################################################################################################################################

    def _execute_delivery(self, task:'Task') -> 'ActionResult':

        if self.delivery_handler:
            tx = self.store.get_transaction(task.transaction_id)
            if not tx:
                return ActionResult(is_ok=False, error=f'Transaction not found: {task.transaction_id}')

            content = self.store.get_content(task.transaction_id)
            if not content:
                return ActionResult(is_ok=False, error=f'Content not found for transaction: {task.transaction_id}')

            try:
                result = self.delivery_handler(
                    content=content,
                    protocol=task.delivery_protocol,
                    detail=task.delivery_detail,
                    filename=tx.filename,
                )
                return ActionResult(is_ok=result.is_ok, error=result.error)
            except Exception as e:
                return ActionResult(is_ok=False, error=str(e))

        return ActionResult()

# ################################################################################################################################

    def _execute_service(self, task:'Task') -> 'ActionResult':

        if self.service_invoker:
            tx = self.store.get_transaction(task.transaction_id)
            if not tx:
                return ActionResult(is_ok=False, error=f'Transaction not found: {task.transaction_id}')

            content = self.store.get_content(task.transaction_id)

            try:
                request_data = {
                    'transaction_id': tx.id,
                    'filename': tx.filename,
                    'sender': tx.sender,
                    'receiver': tx.receiver,
                    'document_id': tx.document_id,
                    'doc_type_id': tx.doc_type_id,
                    'custom_attrs': tx.custom_attrs,
                }
                if content:
                    request_data['content'] = content

                self.service_invoker(task.service_name, request_data)
                return ActionResult()
            except Exception as e:
                return ActionResult(is_ok=False, error=str(e))

        return ActionResult()

# ################################################################################################################################

    def handle_task_failure(self, task:'Task', error:'str') -> 'None':

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
