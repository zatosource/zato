# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn
from gevent.pool import Pool

# Zato
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx as ConfigCtx
from zato.common.test.pubsub_database import pubsub_db_env
from zato.common.test.pubsub_replication import connect_active, kill_primary, promote_standby

# local
from environment import replicated_environment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Callable
    from zato.common.test.pubsub_replication import ReplicatedDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber whose data each operation removes.
_topic_name = 'replication.admin'
_sub_key = 'zpsk.replication.admin'

# How many messages the queue holds before the operation starts, and how many publish at once while it is filled.
_message_count = 30_000
_fill_concurrency = 50

# How many rows one batch of an operation touches, small enough for the operation to span many transactions.
_batch_size = '100'

# How long an operation may take, and how often its progress is checked, in seconds.
_operation_timeout = 300
_poll_interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _count(database:'ReplicatedDatabase', query:'str') -> 'int':
    connection = connect_active(database)

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _count_deliveries(database:'ReplicatedDatabase') -> 'int':
    out = _count(database, f"select count(*) from pubsub_delivery where sub_key = '{_sub_key}'")
    return out

# ################################################################################################################################

def _fill_queue(backend:'SQLPubSubBackend', expiration:'int') -> 'None':
    """ Publishes the messages that the operation is to remove.
    """
    pool = Pool(_fill_concurrency)

    def publish(index:'int') -> 'None':
        _ = backend.publish(_topic_name, f'admin.{index:06d}', expiration=expiration)

    for index in range(_message_count):
        _ = pool.spawn(publish, index)

    _ = pool.join(raise_error=True)

# ################################################################################################################################

def _fail_over_during(database:'ReplicatedDatabase', operation:'Callable[[], any_]') -> 'list[Exception]':
    """ Starts an operation, loses the primary once the operation has committed part of its work, promotes
    the standby and returns what the operation raised, if anything.
    """
    errors:'list[Exception]' = []

    def run() -> 'None':
        try:
            _ = operation()
        except Exception as e:
            errors.append(e)

    greenlet = spawn(run)

    # The primary is lost once the operation has committed at least one of its batches ..
    deadline = monotonic() + _operation_timeout

    while _count_deliveries(database) == _message_count:
        assert monotonic() < deadline, 'The operation committed nothing'
        sleep(_poll_interval)

    assert not greenlet.ready(), 'The operation completed before the primary was lost'

    kill_primary(database)
    _ = promote_standby(database)

    # .. and the operation either ends with an error or completes on the new primary.
    _ = greenlet.join(timeout=_operation_timeout)
    assert greenlet.ready(), 'The operation did not end after the failover'

    return errors

# ################################################################################################################################
# ################################################################################################################################

def _clear_queue_operation(backend:'SQLPubSubBackend') -> 'Callable[[], any_]':
    def operation() -> 'any_':
        out = backend.clear_queue(_sub_key)
        return out
    return operation

# ################################################################################################################################

def _delete_topic_operation(backend:'SQLPubSubBackend') -> 'Callable[[], any_]':
    def operation() -> 'None':
        backend.delete_topic(_topic_name)
    return operation

# ################################################################################################################################

def _check_counts(backend:'SQLPubSubBackend', database:'ReplicatedDatabase') -> 'None':
    depths = backend.get_pending_depths([(_sub_key, _topic_name)])
    rows = _count_deliveries(database)
    assert depths[_sub_key] == rows, f'Depth {depths[_sub_key]} != rows {rows}'

# ################################################################################################################################
# ################################################################################################################################

def test_failover_during_clear_queue() -> 'None':
    """ Clearing a queue that the failover interrupts is repeated on the new primary and leaves no partial state.
    """
    with replicated_environment('clear', True) as database, pubsub_db_env({ConfigCtx.Env_Batch_Size: _batch_size}):

        backend = SQLPubSubBackend()
        backend.subscribe(_sub_key, _topic_name)
        _fill_queue(backend, 86_400)

        errors = _fail_over_during(database, _clear_queue_operation(backend))
        print(f'\nClear queue interrupted by the failover -> errors {errors[:1]}')

        _ = backend.clear_queue(_sub_key)

        assert _count_deliveries(database) == 0
        assert _count(database, f"select count(*) from pubsub_message where topic_name = '{_topic_name}' " +
            'and payload is not null') == 0

        _check_counts(backend, database)

# ################################################################################################################################

def test_failover_during_delete_topic() -> 'None':
    """ Deleting a topic that the failover interrupts is repeated on the new primary and leaves nothing of the topic.
    """
    with replicated_environment('delete', True) as database, pubsub_db_env({ConfigCtx.Env_Batch_Size: _batch_size}):

        backend = SQLPubSubBackend()
        backend.subscribe(_sub_key, _topic_name)
        _fill_queue(backend, 86_400)

        errors = _fail_over_during(database, _delete_topic_operation(backend))
        print(f'\nTopic deletion interrupted by the failover -> errors {errors[:1]}')

        backend.delete_topic(_topic_name)

        for table_name in ('pubsub_message', 'pubsub_delivery', 'pubsub_topic_sub'):
            count = _count(database, f"select count(*) from {table_name} where topic_name = '{_topic_name}'")
            assert count == 0, f'{table_name} has {count} rows of the deleted topic'

        _check_counts(backend, database)

# ################################################################################################################################

def test_failover_during_retention_sweep() -> 'None':
    """ A retention sweep that the failover interrupts continues on the new primary until nothing expired is left.
    """
    with replicated_environment('sweep', True) as database, pubsub_db_env({ConfigCtx.Env_Batch_Size: _batch_size}):

        backend = SQLPubSubBackend()
        backend.subscribe(_sub_key, _topic_name)
        _fill_queue(backend, 1)

        # Every message expires before the sweep starts ..
        sleep(2)

        cleanup = PubSubCleanup()
        errors = _fail_over_during(database, cleanup.sweep_until_done)

        # .. and the sweep itself waits for the new primary rather than failing.
        assert not errors, errors

        assert _count_deliveries(database) == 0
        assert _count(database, f"select count(*) from pubsub_message where topic_name = '{_topic_name}' " +
            'and payload is not null') == 0

        _check_counts(backend, database)

# ################################################################################################################################
# ################################################################################################################################
