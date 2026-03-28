# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import time
from typing import Optional, Tuple

# Zato
from zato.common.file_transfer.const import ActionType, ExecMode, TaskStatus, TaskType
from zato.common.file_transfer.model import RuleAction, Task, Transaction

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

class ActionExecutor:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        service_invoker:'callable_'=None,
        delivery_handler:'callable_'=None,
        notification_sender:'callable_'=None,
    ) -> 'None':
        self.store = store
        self.service_invoker = service_invoker
        self.delivery_handler = delivery_handler
        self.notification_sender = notification_sender

# ################################################################################################################################

    def execute(
        self,
        action:'RuleAction',
        txn:'Transaction',
        content:'Optional[bytes]'=None,
    ) -> 'Tuple[bool, Optional[str]]':

        action_type = action.type
        if isinstance(action_type, str):
            action_type = ActionType(action_type)

        if action_type == ActionType.Execute_Service:
            return self._execute_service(action, txn, content)

        elif action_type == ActionType.Deliver:
            return self._deliver_document(action, txn, content)

        elif action_type == ActionType.Notify:
            return self._send_notification(action, txn)

        elif action_type == ActionType.Change_Status:
            return self._change_user_status(action, txn)

        return False, f'Unknown action type: {action_type}'

# ################################################################################################################################

    def _execute_service(
        self,
        action:'RuleAction',
        txn:'Transaction',
        content:'Optional[bytes]',
    ) -> 'Tuple[bool, Optional[str]]':

        exec_mode = action.exec_mode
        if isinstance(exec_mode, str):
            exec_mode = ExecMode(exec_mode)

        if exec_mode == ExecMode.Reliable:
            task = Task(
                id=self.store.next_task_id(),
                transaction_id=txn.id,
                task_type=TaskType.Service_Execution,
                status=TaskStatus.New,
                created=time.time(),
                updated=time.time(),
                max_retries=action.max_retries,
                retry_wait_ms=action.retry_wait_ms,
                backoff_factor=action.backoff_factor,
                service_name=action.service_name,
            )
            self.store.create_task(task)
            return True, None

        if self.service_invoker:
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

                if exec_mode == ExecMode.Asynchronous:
                    self.service_invoker(action.service_name, request_data, async_=True)
                    return True, None
                else:
                    result = self.service_invoker(action.service_name, request_data)
                    return True, None

            except Exception as e:
                return False, f'Service execution failed: {e}'

        return True, None

# ################################################################################################################################

    def _deliver_document(
        self,
        action:'RuleAction',
        txn:'Transaction',
        content:'Optional[bytes]',
    ) -> 'Tuple[bool, Optional[str]]':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=txn.id,
            task_type=TaskType.Delivery,
            status=TaskStatus.New,
            created=time.time(),
            updated=time.time(),
            max_retries=action.max_retries,
            retry_wait_ms=action.retry_wait_ms,
            backoff_factor=action.backoff_factor,
            delivery_protocol=action.method.value if hasattr(action.method, 'value') else str(action.method),
            delivery_detail=f'{action.connection}:{action.path}',
        )
        self.store.create_task(task)

        return True, None

# ################################################################################################################################

    def _send_notification(
        self,
        action:'RuleAction',
        txn:'Transaction',
    ) -> 'Tuple[bool, Optional[str]]':

        subject = self._expand_template(action.subject, txn)
        body = self._expand_template(action.body, txn)

        if self.notification_sender:
            try:
                self.notification_sender(
                    channel=action.channel,
                    to=action.to,
                    subject=subject,
                    body=body,
                )
                return True, None
            except Exception as e:
                return False, f'Notification failed: {e}'

        return True, None

# ################################################################################################################################

    def _change_user_status(
        self,
        action:'RuleAction',
        txn:'Transaction',
    ) -> 'Tuple[bool, Optional[str]]':

        txn.user_status = action.new_status
        self.store.update_transaction(txn)
        return True, None

# ################################################################################################################################

    def _expand_template(self, template:'str', txn:'Transaction') -> 'str':

        if not template:
            return ''

        replacements = {
            'transaction_id': txn.id,
            'filename': txn.filename,
            'sender': txn.sender,
            'receiver': txn.receiver,
            'document_id': txn.document_id,
            'doc_type': txn.doc_type_id,
            'processing_status': txn.processing_status.value if hasattr(txn.processing_status, 'value') else str(txn.processing_status),
            'user_status': txn.user_status,
            'file_size': str(txn.file_size),
            'date': str(txn.created),
        }

        for key, value in txn.custom_attrs.items():
            replacements[key] = str(value)

        result = template
        for key, value in replacements.items():
            result = result.replace('{' + key + '}', value)

        return result

# ################################################################################################################################
# ################################################################################################################################
