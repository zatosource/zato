# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from threading import Event, Thread

# Zato
from zato.common.file_transfer.tasks import TaskManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.model import Task
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RetryPoller:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        task_manager:'TaskManager',
        poll_interval_seconds:'float'=10.0,
    ) -> 'None':
        self.store = store
        self.task_manager = task_manager
        self.poll_interval = poll_interval_seconds
        self._stop_event = Event()
        self._thread = None

# ################################################################################################################################

    def start(self) -> 'None':
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info('Retry poller started with interval %s seconds', self.poll_interval)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info('Retry poller stopped')

# ################################################################################################################################

    def _poll_loop(self) -> 'None':
        while not self._stop_event.is_set():
            try:
                self._process_due_tasks()
            except Exception as e:
                logger.exception('Error in retry poller: %s', e)

            self._stop_event.wait(self.poll_interval)

# ################################################################################################################################

    def _process_due_tasks(self) -> 'None':
        now = time.time()
        due_tasks = self.store.get_due_retries(now)

        for task in due_tasks:
            try:
                logger.info('Executing retry for task %s (attempt %d/%d)',
                           task.id, task.retry_count + 1, task.max_retries)
                success, error = self.task_manager.execute_task(task)
                if success:
                    logger.info('Task %s completed successfully', task.id)
                else:
                    logger.warning('Task %s failed: %s', task.id, error)
            except Exception as e:
                logger.exception('Error executing task %s: %s', task.id, e)

# ################################################################################################################################

    def poll_once(self) -> 'list[Task]':
        now = time.time()
        due_tasks = self.store.get_due_retries(now)
        executed = []

        for task in due_tasks:
            try:
                self.task_manager.execute_task(task)
                executed.append(task)
            except Exception as e:
                logger.exception('Error executing task %s: %s', task.id, e)

        return executed

# ################################################################################################################################
# ################################################################################################################################
