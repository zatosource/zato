# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.file_transfer.const import ActionType, ExecMode, TaskStatus, TaskType
from zato.common.file_transfer.model import ActionResult, RuleAction, Task, Transaction

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
        tx:'Transaction',
        content:'bytes'=None,
    ) -> 'ActionResult':

        action_type = action.type
        if isinstance(action_type, str):
            action_type = ActionType(action_type)

        if action_type == ActionType.Execute_Service:
            return self._execute_service(action, tx, content)

        elif action_type == ActionType.Deliver:
            return self._deliver_document(action, tx, content)

        elif action_type == ActionType.Notify:
            return self._send_notification(action, tx)

        elif action_type == ActionType.Change_Status:
            return self._change_user_status(action, tx)

        return ActionResult(is_ok=False, error=f'Unknown action type: {action_type}')

# ################################################################################################################################

    def _execute_service(
        self,
        action:'RuleAction',
        tx:'Transaction',
        content:'bytes',
    ) -> 'ActionResult':

        exec_mode = action.exec_mode
        if isinstance(exec_mode, str):
            exec_mode = ExecMode(exec_mode)

        if exec_mode == ExecMode.Reliable:
            task = Task(
                id=self.store.next_task_id(),
                transaction_id=tx.id,
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
            return ActionResult()

        if self.service_invoker:
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

                if exec_mode == ExecMode.Asynchronous:
                    self.service_invoker(action.service_name, request_data, async_=True)
                    return ActionResult()
                else:
                    self.service_invoker(action.service_name, request_data)
                    return ActionResult()

            except Exception as e:
                return ActionResult(is_ok=False, error=f'Service execution failed: {e}')

        return ActionResult()

# ################################################################################################################################

    def _deliver_document(
        self,
        action:'RuleAction',
        tx:'Transaction',
        content:'bytes',
    ) -> 'ActionResult':

        task = Task(
            id=self.store.next_task_id(),
            transaction_id=tx.id,
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

        return ActionResult()

# ################################################################################################################################

    def _send_notification(
        self,
        action:'RuleAction',
        tx:'Transaction',
    ) -> 'ActionResult':

        subject = self._expand_template(action.subject, tx)
        body = self._expand_template(action.body, tx)

        if self.notification_sender:
            try:
                self.notification_sender(
                    channel=action.channel,
                    to=action.to,
                    subject=subject,
                    body=body,
                )
                return ActionResult()
            except Exception as e:
                return ActionResult(is_ok=False, error=f'Notification failed: {e}')

        return ActionResult()

# ################################################################################################################################

    def _change_user_status(
        self,
        action:'RuleAction',
        tx:'Transaction',
    ) -> 'ActionResult':

        tx.user_status = action.new_status
        self.store.update_transaction(tx)
        return ActionResult()

# ################################################################################################################################

    def _expand_template(self, template:'str', tx:'Transaction') -> 'str':

        if not template:
            return ''

        replacements = {
            'transaction_id': tx.id,
            'filename': tx.filename,
            'sender': tx.sender,
            'receiver': tx.receiver,
            'document_id': tx.document_id,
            'doc_type': tx.doc_type_id,
            'processing_status': tx.processing_status.value if hasattr(tx.processing_status, 'value') else str(tx.processing_status),
            'user_status': tx.user_status,
            'file_size': str(tx.file_size),
            'date': str(tx.created),
        }

        for key, value in tx.custom_attrs.items():
            replacements[key] = str(value)

        result = template
        for key, value in replacements.items():
            result = result.replace('{' + key + '}', value)

        return result

# ################################################################################################################################
# ################################################################################################################################
