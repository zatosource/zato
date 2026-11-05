# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from time import monotonic

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError

# Zato
from cleanup import set_expired
from common import delete_all_rows, get_message_rows
from zato.common.db_env.errors import get_sqlstate, is_transient, SQLState
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

_topic_name = 'pubsub.backend.test.cleanup.postgresql'
_sub_key = 'zpsk.test.cleanup.postgresql'

# How many expired messages each flow publishes and how many of them another transaction holds locked.
_expired_count = 20
_locked_count = 5

# How long a sweep that skips the locked rows may take at most, in seconds.
_skip_deadline_seconds = 10

# How long the sweep may take to start waiting for the locked delivery row, and to complete once it is released.
_wait_deadline_seconds = 30

# How often the flows check the state of the sweep, in seconds.
_poll_seconds = 0.1

# The query that finds the backend of the sweep while it waits for a row lock.
_waiting_backend_query = text("""
    select pid from pg_stat_activity
    where wait_event_type = 'Lock' and datname = current_database() and pid <> pg_backend_pid()
""")

# The address and user of a database that no server listens for.
_unreachable_host = '127.0.0.1'
_unreachable_user = 'zato'

# The query that returns how many deadlocks the database detected so far.
_deadlocks_query = text('select deadlocks from pg_stat_database where datname = current_database()')

# ################################################################################################################################
# ################################################################################################################################

def _publish_expired(backend:'SQLPubSubBackend') -> 'strlist':
    """ Publishes the messages of a flow and marks them as expired.
    """
    out:'strlist' = []

    for index in range(_expired_count):
        result = backend.publish(_topic_name, f'cleanup-postgresql-{index}')
        out.append(result.msg_id)

    set_expired(out)

    return out

# ################################################################################################################################

def _run_locked_rows_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The sweep skips the expired messages that another transaction holds locked instead of waiting for them,
    deletes all the others, and deletes the skipped ones in a later sweep, once they are released.
    """
    delete_all_rows()
    backend.subscribe(_sub_key, _topic_name)

    msg_ids = _publish_expired(backend)
    locked_msg_ids = msg_ids[:_locked_count]

    lock_query = select(message_table.c.id)
    lock_query = lock_query.where(message_table.c.msg_id.in_(locked_msg_ids))
    lock_query = lock_query.with_for_update()

    engine = get_pubsub_engine()
    cleanup = PubSubCleanup()

    with engine.connect() as lock_connection:
        with lock_connection.begin():

            locked_rows = lock_connection.execute(lock_query).fetchall()
            assert len(locked_rows) == _locked_count

            start = monotonic()
            counts = cleanup.sweep_once()
            elapsed = monotonic() - start

            # The sweep did not wait for the locks ..
            assert elapsed < _skip_deadline_seconds, elapsed

            # .. and deleted every message that was not locked.
            assert counts['expired'] == _expired_count - _locked_count, counts

            remaining:'strlist' = []
            for row in get_message_rows(_topic_name):
                remaining.append(row.msg_id)

            assert sorted(remaining) == sorted(locked_msg_ids), remaining

    # Once released, the locked messages are deleted by the next sweep.
    counts = cleanup.sweep_once()
    assert counts['expired'] == _locked_count, counts
    assert get_message_rows(_topic_name) == []

# ################################################################################################################################

def _run_terminated_connection_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The sweep whose connection is terminated while it waits for a row lock postpones itself,
    starts again, and deletes every expired message once the lock is released.
    """
    delete_all_rows()
    backend.subscribe(_sub_key, _topic_name)

    _ = _publish_expired(backend)

    # One delivery row is locked, which the sweep has to wait for when it deletes the deliveries of its batch ..
    lock_query = select(delivery_table.c.id)
    lock_query = lock_query.where(delivery_table.c.sub_key == _sub_key)
    lock_query = lock_query.limit(1)
    lock_query = lock_query.with_for_update()

    engine = get_pubsub_engine()
    cleanup = PubSubCleanup()

    with engine.connect() as lock_connection:
        lock_transaction = lock_connection.begin()
        _ = lock_connection.execute(lock_query).fetchall()

        sweep = gevent.spawn(cleanup.sweep_until_done)

        # .. the backend of the sweep is found once it waits for the lock ..
        deadline = monotonic() + _wait_deadline_seconds
        waiting_pid = None

        with engine.connect() as admin_connection:
            while waiting_pid is None:
                assert monotonic() < deadline, 'The sweep did not start waiting for the lock'
                gevent.sleep(_poll_seconds)
                waiting_pid = admin_connection.execute(_waiting_backend_query).scalar()

            # .. and terminated ..
            _ = admin_connection.execute(text('select pg_terminate_backend(:pid)'), {'pid': waiting_pid})
            admin_connection.commit()

        # .. the sweep is still running, postponed rather than failed ..
        gevent.sleep(_poll_seconds)
        assert not sweep.dead, sweep.exception

        # .. and the lock is released.
        lock_transaction.rollback()

    counts = sweep.get(timeout=_wait_deadline_seconds)

    assert counts['expired'] == _expired_count, counts
    assert get_message_rows(_topic_name) == []

# ################################################################################################################################

def _wait_for_waiting_backend(engine:'any_') -> 'None':
    """ Waits until a backend other than the caller's waits for a lock.
    """
    deadline = monotonic() + _wait_deadline_seconds

    with engine.connect() as admin_connection:
        while admin_connection.execute(_waiting_backend_query).scalar() is None:
            assert monotonic() < deadline, 'The sweep did not start waiting for the lock'
            gevent.sleep(_poll_seconds)

# ################################################################################################################################

def _run_deadlock_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The sweep that PostgreSQL rolls back as part of a deadlock starts again and deletes every expired message.
    Another transaction locks a delivery row, the sweep locks its message and waits for the delivery row,
    and the other transaction then waits for the message, which closes the cycle.
    """
    delete_all_rows()
    backend.subscribe(_sub_key, _topic_name)

    _ = _publish_expired(backend)

    delivery_query = select(delivery_table.c.id, delivery_table.c.message_id)
    delivery_query = delivery_query.where(delivery_table.c.sub_key == _sub_key)
    delivery_query = delivery_query.limit(1)
    delivery_query = delivery_query.with_for_update()

    engine = get_pubsub_engine()
    cleanup = PubSubCleanup()

    with engine.connect() as connection:
        deadlocks_before = connection.execute(_deadlocks_query).scalar_one()

    with engine.connect() as lock_connection:
        lock_transaction = lock_connection.begin()

        # The delivery row is locked ..
        delivery_row = lock_connection.execute(delivery_query).one()

        # .. the sweep locks the message and waits for the delivery row ..
        sweep = gevent.spawn(cleanup.sweep_until_done)
        _wait_for_waiting_backend(engine)

        # .. and the message is requested, which PostgreSQL resolves by rolling back one of the two transactions.
        message_query = select(message_table.c.id)
        message_query = message_query.where(message_table.c.id == delivery_row.message_id)
        message_query = message_query.with_for_update()

        try:
            _ = lock_connection.execute(message_query).fetchall()
        except DBAPIError as e:
            assert get_sqlstate(e) == SQLState.Deadlock_Detected, e

        lock_transaction.rollback()

    counts = sweep.get(timeout=_wait_deadline_seconds)

    assert counts['expired'] == _expired_count, counts
    assert get_message_rows(_topic_name) == []

    with engine.connect() as connection:
        deadlocks_after = connection.execute(_deadlocks_query).scalar_one()

    assert deadlocks_after > deadlocks_before, (deadlocks_before, deadlocks_after)

# ################################################################################################################################

def _run_unreachable_database_flow() -> 'None':
    """ A connection that cannot be opened, as during a failover, is a transient condition after which
    the sweep starts again.
    """

    # A port that was free a moment ago has no listener ..
    with socket.socket() as probe:
        probe.bind((_unreachable_host, 0))
        port = probe.getsockname()[1]

    engine = create_engine(f'postgresql+pg8000://{_unreachable_user}@{_unreachable_host}:{port}/{_unreachable_user}')

    # .. so the connection is refused ..
    try:
        with engine.connect():
            pass
    except DBAPIError as e:
        error = e
    else:
        raise AssertionError(f'A connection to port {port} was opened')
    finally:
        engine.dispose()

    # .. which the sweep treats as transient.
    assert is_transient(error), error

# ################################################################################################################################

def run_cleanup_postgresql_scenario() -> 'None':
    """ The cleanup process on PostgreSQL under row locks held by other transactions, a terminated connection,
    a deadlock and a database that cannot be reached.
    """
    backend = SQLPubSubBackend()

    _run_locked_rows_flow(backend)
    _run_terminated_connection_flow(backend)
    _run_deadlock_flow(backend)
    _run_unreachable_database_flow()

# ################################################################################################################################
# ################################################################################################################################
