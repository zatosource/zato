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
from zato.common.file_transfer.const import RedisKey

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ArchivalJob:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        batch_size:'int'=100,
        poll_interval_hours:'float'=24.0,
    ) -> 'None':
        self.store = store
        self.batch_size = batch_size
        self.poll_interval = poll_interval_hours * 3600
        self._stop_event = Event()
        self._thread = None

# ################################################################################################################################

    def start(self) -> 'None':
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info('Archival job started with interval %s hours', self.poll_interval / 3600)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10.0)
        logger.info('Archival job stopped')

# ################################################################################################################################

    def _poll_loop(self) -> 'None':
        while not self._stop_event.is_set():
            try:
                self.run_archival()
            except Exception as e:
                logger.exception('Error in archival job: %s', e)

            self._stop_event.wait(self.poll_interval)

# ################################################################################################################################

    def run_archival(self) -> 'int':

        settings = self.store.get_settings()
        archive_after_days = settings.archive_after_days

        cutoff_timestamp = time.time() - (archive_after_days * 24 * 60 * 60)

        total_archived = 0
        cluster_id = self.store.cluster_id

        while True:
            txn_ids = self.store.redis.zrangebyscore(
                RedisKey.idx_txn_by_created(cluster_id),
                0,
                cutoff_timestamp,
                start=0,
                num=self.batch_size,
            )

            if not txn_ids:
                break

            for txn_id in txn_ids:
                if isinstance(txn_id, bytes):
                    txn_id = txn_id.decode()

                try:
                    self._archive_transaction(txn_id)
                    total_archived += 1
                except Exception as e:
                    logger.warning('Failed to archive transaction %s: %s', txn_id, e)

        logger.info('Archived %d transactions older than %d days', total_archived, archive_after_days)
        return total_archived

# ################################################################################################################################

    def _archive_transaction(self, txn_id:'str') -> 'None':

        cluster_id = self.store.cluster_id

        log_entry_ids = self.store.redis.zrange(
            RedisKey.idx_log_by_txn(cluster_id, txn_id),
            0,
            -1,
        )

        for entry_id in log_entry_ids:
            if isinstance(entry_id, bytes):
                entry_id = entry_id.decode()

            parts = entry_id.split(':')
            seq = int(parts[-1])
            log_key = RedisKey.log_entry(cluster_id, txn_id, seq)
            self.store.redis.delete(log_key)

        self.store.redis.delete(RedisKey.idx_log_by_txn(cluster_id, txn_id))

        task_ids = self.store.redis.zrange(
            RedisKey.idx_task_by_txn(cluster_id, txn_id),
            0,
            -1,
        )

        for task_id in task_ids:
            if isinstance(task_id, bytes):
                task_id = task_id.decode()
            self.store.delete_task(task_id)

        self.store.delete_transaction(txn_id)

# ################################################################################################################################
# ################################################################################################################################

class LogRetentionJob:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        batch_size:'int'=500,
        poll_interval_hours:'float'=24.0,
    ) -> 'None':
        self.store = store
        self.batch_size = batch_size
        self.poll_interval = poll_interval_hours * 3600
        self._stop_event = Event()
        self._thread = None

# ################################################################################################################################

    def start(self) -> 'None':
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info('Log retention job started with interval %s hours', self.poll_interval / 3600)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10.0)
        logger.info('Log retention job stopped')

# ################################################################################################################################

    def _poll_loop(self) -> 'None':
        while not self._stop_event.is_set():
            try:
                self.run_cleanup()
            except Exception as e:
                logger.exception('Error in log retention job: %s', e)

            self._stop_event.wait(self.poll_interval)

# ################################################################################################################################

    def run_cleanup(self) -> 'int':

        settings = self.store.get_settings()
        retention_days = settings.log_retention_days

        cutoff_timestamp = time.time() - (retention_days * 24 * 60 * 60)

        total_deleted = 0
        cluster_id = self.store.cluster_id

        while True:
            entry_ids = self.store.redis.zrangebyscore(
                RedisKey.idx_log_global(cluster_id),
                0,
                cutoff_timestamp,
                start=0,
                num=self.batch_size,
            )

            if not entry_ids:
                break

            for entry_id in entry_ids:
                if isinstance(entry_id, bytes):
                    entry_id = entry_id.decode()

                try:
                    self._delete_log_entry(entry_id)
                    total_deleted += 1
                except Exception as e:
                    logger.warning('Failed to delete log entry %s: %s', entry_id, e)

        logger.info('Deleted %d log entries older than %d days', total_deleted, retention_days)
        return total_deleted

# ################################################################################################################################

    def _delete_log_entry(self, entry_id:'str') -> 'None':

        cluster_id = self.store.cluster_id

        parts = entry_id.split(':')
        txn_id = parts[0]
        seq = int(parts[-1])

        log_key = RedisKey.log_entry(cluster_id, txn_id, seq)
        data = self.store.redis.hgetall(log_key)

        if data:
            decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}

            activity_class = decoded.get('activity_class', '')
            severity = decoded.get('severity', '')

            self.store.redis.zrem(RedisKey.idx_log_by_class(cluster_id, activity_class), entry_id)
            self.store.redis.zrem(RedisKey.idx_log_by_severity(cluster_id, severity), entry_id)

        self.store.redis.zrem(RedisKey.idx_log_global(cluster_id), entry_id)
        self.store.redis.zrem(RedisKey.idx_log_by_txn(cluster_id, txn_id), entry_id)
        self.store.redis.delete(log_key)

# ################################################################################################################################
# ################################################################################################################################
