# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.file_transfer.const import (
    ProcessingStatus,
    RedisKey,
    Severity,
    TaskStatus,
)
from zato.common.file_transfer.model import (
    ActivityLogEntry,
    DocumentType,
    PGPKey,
    PickupChannel,
    ProcessingRule,
    SearchResult,
    Settings,
    Task,
    Transaction,
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class FileTransferRedisStore:

    def __init__(self, redis_conn:'Redis', cluster_id:'int') -> 'None':
        self.redis = redis_conn
        self.cluster_id = cluster_id

# ################################################################################################################################
# ID generation
# ################################################################################################################################

    def next_txn_id(self) -> 'str':
        seq = self.redis.incr(RedisKey.seq_txn(self.cluster_id))
        return f'TXN-{seq:05d}'

    def next_task_id(self) -> 'str':
        seq = self.redis.incr(RedisKey.seq_task(self.cluster_id))
        return f'TSK-{seq:05d}'

    def next_log_seq(self, txn_id:'str') -> 'int':
        return self.redis.incr(RedisKey.seq_log(self.cluster_id, txn_id))

# ################################################################################################################################
# Transaction CRUD
# ################################################################################################################################

    def create_transaction(self, txn:'Transaction') -> 'None':
        key = RedisKey.txn(self.cluster_id, txn.id)
        self.redis.hset(key, mapping=txn.to_dict())
        self._add_txn_to_indexes(txn)

    def get_transaction(self, txn_id:'str') -> 'Transaction | None':
        key = RedisKey.txn(self.cluster_id, txn_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return Transaction.from_dict(decoded)

    def update_transaction(self, txn:'Transaction') -> 'None':
        key = RedisKey.txn(self.cluster_id, txn.id)
        old_txn = self.get_transaction(txn.id)
        if old_txn:
            self._remove_txn_from_indexes(old_txn)
        self.redis.hset(key, mapping=txn.to_dict())
        self._add_txn_to_indexes(txn)

    def delete_transaction(self, txn_id:'str') -> 'None':
        txn = self.get_transaction(txn_id)
        if txn:
            self._remove_txn_from_indexes(txn)
            self.redis.delete(RedisKey.txn(self.cluster_id, txn_id))
            self.redis.delete(RedisKey.content(self.cluster_id, txn_id))

    def _add_txn_to_indexes(self, txn:'Transaction') -> 'None':
        score = txn.created
        self.redis.zadd(RedisKey.idx_txn_by_created(self.cluster_id), {txn.id: score})
        status_val = txn.processing_status.value if isinstance(txn.processing_status, ProcessingStatus) else txn.processing_status
        self.redis.zadd(RedisKey.idx_txn_by_status(self.cluster_id, status_val), {txn.id: score})
        if txn.sender:
            self.redis.zadd(RedisKey.idx_txn_by_sender(self.cluster_id, txn.sender), {txn.id: score})
        if txn.receiver:
            self.redis.zadd(RedisKey.idx_txn_by_receiver(self.cluster_id, txn.receiver), {txn.id: score})
        if txn.doc_type_id:
            self.redis.zadd(RedisKey.idx_txn_by_doc_type(self.cluster_id, txn.doc_type_id), {txn.id: score})
        if txn.conversation_id:
            self.redis.zadd(RedisKey.idx_txn_by_conv(self.cluster_id, txn.conversation_id), {txn.id: score})
        if txn.group_id:
            self.redis.zadd(RedisKey.idx_txn_by_group(self.cluster_id, txn.group_id), {txn.id: score})

    def _remove_txn_from_indexes(self, txn:'Transaction') -> 'None':
        self.redis.zrem(RedisKey.idx_txn_by_created(self.cluster_id), txn.id)
        status_val = txn.processing_status.value if isinstance(txn.processing_status, ProcessingStatus) else txn.processing_status
        self.redis.zrem(RedisKey.idx_txn_by_status(self.cluster_id, status_val), txn.id)
        if txn.sender:
            self.redis.zrem(RedisKey.idx_txn_by_sender(self.cluster_id, txn.sender), txn.id)
        if txn.receiver:
            self.redis.zrem(RedisKey.idx_txn_by_receiver(self.cluster_id, txn.receiver), txn.id)
        if txn.doc_type_id:
            self.redis.zrem(RedisKey.idx_txn_by_doc_type(self.cluster_id, txn.doc_type_id), txn.id)
        if txn.conversation_id:
            self.redis.zrem(RedisKey.idx_txn_by_conv(self.cluster_id, txn.conversation_id), txn.id)
        if txn.group_id:
            self.redis.zrem(RedisKey.idx_txn_by_group(self.cluster_id, txn.group_id), txn.id)

# ################################################################################################################################
# Transaction search
# ################################################################################################################################

    def search_transactions(
        self,
        date_from:'float | None'=None,
        date_to:'float | None'=None,
        status:'str | None'=None,
        sender:'str | None'=None,
        receiver:'str | None'=None,
        doc_type_id:'str | None'=None,
        limit:'int'=100,
        offset:'int'=0,
    ) -> 'SearchResult':

        if date_from is None:
            date_from = 0
        if date_to is None:
            date_to = float('inf')

        candidate_sets = []

        if status:
            candidate_sets.append(RedisKey.idx_txn_by_status(self.cluster_id, status))
        if sender:
            candidate_sets.append(RedisKey.idx_txn_by_sender(self.cluster_id, sender))
        if receiver:
            candidate_sets.append(RedisKey.idx_txn_by_receiver(self.cluster_id, receiver))
        if doc_type_id:
            candidate_sets.append(RedisKey.idx_txn_by_doc_type(self.cluster_id, doc_type_id))

        if not candidate_sets:
            base_key = RedisKey.idx_txn_by_created(self.cluster_id)
        elif len(candidate_sets) == 1:
            base_key = candidate_sets[0]
        else:
            temp_key = f'{RedisKey.idx_txn_by_created(self.cluster_id)}:temp:{time.time()}'
            self.redis.zinterstore(temp_key, candidate_sets)
            base_key = temp_key

        total = self.redis.zcount(base_key, date_from, date_to)
        txn_ids = self.redis.zrevrangebyscore(base_key, date_to, date_from, start=offset, num=limit)

        if len(candidate_sets) > 1:
            self.redis.delete(base_key)

        transactions = []
        for txn_id in txn_ids:
            if isinstance(txn_id, bytes):
                txn_id = txn_id.decode()
            txn = self.get_transaction(txn_id)
            if txn:
                transactions.append(txn)

        return SearchResult(items=transactions, total=total)

# ################################################################################################################################
# Content storage
# ################################################################################################################################

    def save_content(self, txn_id:'str', content:'bytes') -> 'None':
        key = RedisKey.content(self.cluster_id, txn_id)
        self.redis.set(key, content)

    def get_content(self, txn_id:'str') -> 'bytes | None':
        key = RedisKey.content(self.cluster_id, txn_id)
        return self.redis.get(key)

    def delete_content(self, txn_id:'str') -> 'None':
        key = RedisKey.content(self.cluster_id, txn_id)
        self.redis.delete(key)

# ################################################################################################################################
# Document type CRUD
# ################################################################################################################################

    def create_document_type(self, doc_type:'DocumentType') -> 'None':
        key = RedisKey.doc_type(self.cluster_id, doc_type.id)
        self.redis.hset(key, mapping=doc_type.to_dict())
        self.redis.sadd(RedisKey.set_doc_types(self.cluster_id), doc_type.id)

    def get_document_type(self, dt_id:'str') -> 'DocumentType | None':
        key = RedisKey.doc_type(self.cluster_id, dt_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return DocumentType.from_dict(decoded)

    def update_document_type(self, doc_type:'DocumentType') -> 'None':
        key = RedisKey.doc_type(self.cluster_id, doc_type.id)
        self.redis.hset(key, mapping=doc_type.to_dict())

    def delete_document_type(self, dt_id:'str') -> 'None':
        self.redis.delete(RedisKey.doc_type(self.cluster_id, dt_id))
        self.redis.srem(RedisKey.set_doc_types(self.cluster_id), dt_id)

    def list_document_types(self) -> 'list[DocumentType]':
        dt_ids = self.redis.smembers(RedisKey.set_doc_types(self.cluster_id))
        doc_types = []
        for dt_id in dt_ids:
            if isinstance(dt_id, bytes):
                dt_id = dt_id.decode()
            dt = self.get_document_type(dt_id)
            if dt:
                doc_types.append(dt)
        return doc_types

    def list_enabled_document_types(self) -> 'list[DocumentType]':
        return [dt for dt in self.list_document_types() if dt.is_enabled]

# ################################################################################################################################
# Processing rule CRUD
# ################################################################################################################################

    def create_processing_rule(self, rule:'ProcessingRule') -> 'None':
        key = RedisKey.rule(self.cluster_id, rule.id)
        self.redis.hset(key, mapping=rule.to_dict())
        self.redis.sadd(RedisKey.set_rules(self.cluster_id), rule.id)
        self.redis.zadd(RedisKey.idx_rule_order(self.cluster_id), {rule.id: rule.ordinal})

    def get_processing_rule(self, rule_id:'str') -> 'ProcessingRule | None':
        key = RedisKey.rule(self.cluster_id, rule_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return ProcessingRule.from_dict(decoded)

    def update_processing_rule(self, rule:'ProcessingRule') -> 'None':
        key = RedisKey.rule(self.cluster_id, rule.id)
        self.redis.hset(key, mapping=rule.to_dict())
        self.redis.zadd(RedisKey.idx_rule_order(self.cluster_id), {rule.id: rule.ordinal})

    def delete_processing_rule(self, rule_id:'str') -> 'None':
        self.redis.delete(RedisKey.rule(self.cluster_id, rule_id))
        self.redis.srem(RedisKey.set_rules(self.cluster_id), rule_id)
        self.redis.zrem(RedisKey.idx_rule_order(self.cluster_id), rule_id)

    def list_processing_rules(self) -> 'list[ProcessingRule]':
        rule_ids = self.redis.zrange(RedisKey.idx_rule_order(self.cluster_id), 0, -1)
        rules = []
        for rule_id in rule_ids:
            if isinstance(rule_id, bytes):
                rule_id = rule_id.decode()
            rule = self.get_processing_rule(rule_id)
            if rule:
                rules.append(rule)
        return rules

    def list_enabled_processing_rules(self) -> 'list[ProcessingRule]':
        return [r for r in self.list_processing_rules() if r.is_enabled]

    def reorder_rules(self, ordered_ids:'strlist') -> 'None':
        for idx, rule_id in enumerate(ordered_ids):
            rule = self.get_processing_rule(rule_id)
            if rule:
                rule.ordinal = idx
                self.update_processing_rule(rule)

# ################################################################################################################################
# Task CRUD
# ################################################################################################################################

    def create_task(self, task:'Task') -> 'None':
        key = RedisKey.task(self.cluster_id, task.id)
        self.redis.hset(key, mapping=task.to_dict())
        self._add_task_to_indexes(task)

    def get_task(self, task_id:'str') -> 'Task | None':
        key = RedisKey.task(self.cluster_id, task_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return Task.from_dict(decoded)

    def update_task(self, task:'Task') -> 'None':
        old_task = self.get_task(task.id)
        if old_task:
            self._remove_task_from_indexes(old_task)
        key = RedisKey.task(self.cluster_id, task.id)
        self.redis.hset(key, mapping=task.to_dict())
        self._add_task_to_indexes(task)

    def delete_task(self, task_id:'str') -> 'None':
        task = self.get_task(task_id)
        if task:
            self._remove_task_from_indexes(task)
            self.redis.delete(RedisKey.task(self.cluster_id, task_id))

    def _add_task_to_indexes(self, task:'Task') -> 'None':
        score = task.created
        status_val = task.status.value if isinstance(task.status, TaskStatus) else task.status
        self.redis.zadd(RedisKey.idx_task_by_status(self.cluster_id, status_val), {task.id: score})
        self.redis.zadd(RedisKey.idx_task_by_txn(self.cluster_id, task.transaction_id), {task.id: score})
        if task.next_retry_at:
            self.redis.zadd(RedisKey.idx_task_retry_schedule(self.cluster_id), {task.id: task.next_retry_at})

    def _remove_task_from_indexes(self, task:'Task') -> 'None':
        status_val = task.status.value if isinstance(task.status, TaskStatus) else task.status
        self.redis.zrem(RedisKey.idx_task_by_status(self.cluster_id, status_val), task.id)
        self.redis.zrem(RedisKey.idx_task_by_txn(self.cluster_id, task.transaction_id), task.id)
        self.redis.zrem(RedisKey.idx_task_retry_schedule(self.cluster_id), task.id)

    def get_tasks_for_transaction(self, txn_id:'str') -> 'list[Task]':
        task_ids = self.redis.zrange(RedisKey.idx_task_by_txn(self.cluster_id, txn_id), 0, -1)
        tasks = []
        for task_id in task_ids:
            if isinstance(task_id, bytes):
                task_id = task_id.decode()
            task = self.get_task(task_id)
            if task:
                tasks.append(task)
        return tasks

    def schedule_retry(self, task_id:'str', next_retry_at:'float') -> 'None':
        task = self.get_task(task_id)
        if task:
            task.next_retry_at = next_retry_at
            self.update_task(task)

    def get_due_retries(self, now:'float') -> 'list[Task]':
        task_ids = self.redis.zrangebyscore(RedisKey.idx_task_retry_schedule(self.cluster_id), 0, now)
        tasks = []
        for task_id in task_ids:
            if isinstance(task_id, bytes):
                task_id = task_id.decode()
            task = self.get_task(task_id)
            if task:
                tasks.append(task)
        return tasks

# ################################################################################################################################
# Activity log
# ################################################################################################################################

    def create_log_entry(self, entry:'ActivityLogEntry') -> 'None':
        key = RedisKey.log_entry(self.cluster_id, entry.transaction_id, int(entry.id.split(':')[-1]))
        self.redis.hset(key, mapping=entry.to_dict())
        self.redis.zadd(RedisKey.idx_log_by_txn(self.cluster_id, entry.transaction_id), {entry.id: entry.timestamp})
        activity_class_val = entry.activity_class.value if hasattr(entry.activity_class, 'value') else entry.activity_class
        self.redis.zadd(RedisKey.idx_log_by_class(self.cluster_id, activity_class_val), {entry.id: entry.timestamp})
        severity_val = entry.severity.value if isinstance(entry.severity, Severity) else entry.severity
        self.redis.zadd(RedisKey.idx_log_by_severity(self.cluster_id, severity_val), {entry.id: entry.timestamp})
        self.redis.zadd(RedisKey.idx_log_global(self.cluster_id), {entry.id: entry.timestamp})

    def get_logs_for_transaction(self, txn_id:'str') -> 'list[ActivityLogEntry]':
        entry_ids = self.redis.zrange(RedisKey.idx_log_by_txn(self.cluster_id, txn_id), 0, -1)
        entries = []
        for entry_id in entry_ids:
            if isinstance(entry_id, bytes):
                entry_id = entry_id.decode()
            parts = entry_id.split(':')
            seq = int(parts[-1])
            key = RedisKey.log_entry(self.cluster_id, txn_id, seq)
            data = self.redis.hgetall(key)
            if data:
                decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
                entries.append(ActivityLogEntry.from_dict(decoded))
        return entries

    def search_logs(
        self,
        date_from:'float | None'=None,
        date_to:'float | None'=None,
        activity_class:'str | None'=None,
        severity:'str | None'=None,
        limit:'int'=100,
        offset:'int'=0,
    ) -> 'SearchResult':

        if date_from is None:
            date_from = 0
        if date_to is None:
            date_to = float('inf')

        if activity_class:
            base_key = RedisKey.idx_log_by_class(self.cluster_id, activity_class)
        elif severity:
            base_key = RedisKey.idx_log_by_severity(self.cluster_id, severity)
        else:
            base_key = RedisKey.idx_log_global(self.cluster_id)

        total = self.redis.zcount(base_key, date_from, date_to)
        entry_ids = self.redis.zrevrangebyscore(base_key, date_to, date_from, start=offset, num=limit)

        entries = []
        for entry_id in entry_ids:
            if isinstance(entry_id, bytes):
                entry_id = entry_id.decode()
            parts = entry_id.split(':')
            txn_id = parts[0]
            seq = int(parts[-1])
            key = RedisKey.log_entry(self.cluster_id, txn_id, seq)
            data = self.redis.hgetall(key)
            if data:
                decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
                entries.append(ActivityLogEntry.from_dict(decoded))

        return SearchResult(items=entries, total=total)

# ################################################################################################################################
# PGP key CRUD
# ################################################################################################################################

    def create_pgp_key(self, pgp_key:'PGPKey') -> 'None':
        key = RedisKey.pgp_key(self.cluster_id, pgp_key.id)
        self.redis.hset(key, mapping=pgp_key.to_dict())
        self.redis.sadd(RedisKey.set_pgp_keys(self.cluster_id), pgp_key.id)

    def get_pgp_key(self, key_id:'str') -> 'PGPKey | None':
        key = RedisKey.pgp_key(self.cluster_id, key_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return PGPKey.from_dict(decoded)

    def update_pgp_key(self, pgp_key:'PGPKey') -> 'None':
        key = RedisKey.pgp_key(self.cluster_id, pgp_key.id)
        self.redis.hset(key, mapping=pgp_key.to_dict())

    def delete_pgp_key(self, key_id:'str') -> 'None':
        self.redis.delete(RedisKey.pgp_key(self.cluster_id, key_id))
        self.redis.srem(RedisKey.set_pgp_keys(self.cluster_id), key_id)

    def list_pgp_keys(self) -> 'list[PGPKey]':
        key_ids = self.redis.smembers(RedisKey.set_pgp_keys(self.cluster_id))
        keys = []
        for key_id in key_ids:
            if isinstance(key_id, bytes):
                key_id = key_id.decode()
            pgp_key = self.get_pgp_key(key_id)
            if pgp_key:
                keys.append(pgp_key)
        return keys

# ################################################################################################################################
# Settings
# ################################################################################################################################

    def get_settings(self) -> 'Settings':
        key = RedisKey.settings(self.cluster_id)
        data = self.redis.hgetall(key)
        if not data:
            return Settings()
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return Settings.from_dict(decoded)

    def update_settings(self, settings:'Settings') -> 'None':
        key = RedisKey.settings(self.cluster_id)
        self.redis.hset(key, mapping=settings.to_dict())

# ################################################################################################################################
# User statuses
# ################################################################################################################################

    def get_user_statuses(self) -> 'strlist':
        statuses = self.redis.smembers(RedisKey.set_user_statuses(self.cluster_id))
        return [s.decode() if isinstance(s, bytes) else s for s in statuses]

    def add_user_status(self, status:'str') -> 'None':
        self.redis.sadd(RedisKey.set_user_statuses(self.cluster_id), status)

    def remove_user_status(self, status:'str') -> 'None':
        self.redis.srem(RedisKey.set_user_statuses(self.cluster_id), status)

# ################################################################################################################################
# Deduplication
# ################################################################################################################################

    def check_duplicate(self, doc_id:'str', sender:'str', doc_type_id:'str') -> 'str | None':
        key = RedisKey.dedup(self.cluster_id, doc_id, sender, doc_type_id)
        result = self.redis.get(key)
        if result:
            return result.decode() if isinstance(result, bytes) else result
        return None

    def set_dedup_key(self, doc_id:'str', sender:'str', doc_type_id:'str', txn_id:'str', ttl_seconds:'int') -> 'None':
        key = RedisKey.dedup(self.cluster_id, doc_id, sender, doc_type_id)
        self.redis.set(key, txn_id, ex=ttl_seconds)

# ################################################################################################################################
# Pickup channels
# ################################################################################################################################

    def create_pickup_channel(self, channel:'PickupChannel') -> 'None':
        key = RedisKey.pickup_channel(self.cluster_id, channel.id)
        self.redis.hset(key, mapping=channel.to_dict())
        self.redis.sadd(RedisKey.set_pickup_channels(self.cluster_id), channel.id)

    def get_pickup_channel(self, channel_id:'str') -> 'PickupChannel | None':
        key = RedisKey.pickup_channel(self.cluster_id, channel_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        decoded = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        return PickupChannel.from_dict(decoded)

    def update_pickup_channel(self, channel:'PickupChannel') -> 'None':
        key = RedisKey.pickup_channel(self.cluster_id, channel.id)
        self.redis.hset(key, mapping=channel.to_dict())

    def delete_pickup_channel(self, channel_id:'str') -> 'None':
        self.redis.delete(RedisKey.pickup_channel(self.cluster_id, channel_id))
        self.redis.srem(RedisKey.set_pickup_channels(self.cluster_id), channel_id)

    def list_pickup_channels(self) -> 'list[PickupChannel]':
        channel_ids = self.redis.smembers(RedisKey.set_pickup_channels(self.cluster_id))
        channels = []
        for channel_id in channel_ids:
            if isinstance(channel_id, bytes):
                channel_id = channel_id.decode()
            channel = self.get_pickup_channel(channel_id)
            if channel:
                channels.append(channel)
        return channels

    def list_enabled_pickup_channels(self) -> 'list[PickupChannel]':
        return [c for c in self.list_pickup_channels() if c.is_enabled]

# ################################################################################################################################
# ################################################################################################################################
