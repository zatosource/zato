# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the monkey patching must run before every other import, the same order the server uses
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import json
import sys
import time

# gevent
import gevent
from gevent.event import Event

# oracledb
import oracledb

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.odb.api import SQLConnectionPool
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many connections the pool holds and how many greenlets contend for them
_pool_size    = 25
_worker_count = 40

# How long the workload runs, in seconds
_workload_duration = 30.0

# How long the heartbeat greenlet sleeps between wake-ups, in seconds
_heartbeat_sleep = 0.05

# The rows the workload table is filled with
_bulk_row_count = 5000
_clob_row_id    = 0
_clob_size      = 200_000

# The id inserted and rolled back by every iteration, outside the bulk range
_scratch_row_id = _bulk_row_count + 1

# ################################################################################################################################
# ################################################################################################################################

_sid_query      = "select sys_context('userenv', 'sid') from dual"
_bulk_query     = f'select id from pool_workload where id between 1 and {_bulk_row_count}'
_clob_query     = 'select payload from pool_workload where id = :id'
_missing_query  = 'select id from pool_workload where id = :id'
_insert_query   = 'insert into pool_workload (id) values (:id)'
_delete_query   = 'delete from pool_workload where id = :id'

# How many statements one iteration of the worker loop runs
_queries_per_iteration = 6

# ################################################################################################################################
# ################################################################################################################################

class _WorkloadState:
    """ What the workers and the heartbeat greenlet observed.
    """

    def __init__(self) -> 'None':
        self.query_count = 0
        self.session_ids:'set[str]' = set()
        self.errors:'strlist' = []
        self.max_heartbeat_gap_ms = 0.0

# ################################################################################################################################
# ################################################################################################################################

def _create_workload_table(session_factory:'any_') -> 'None':
    """ Creates and fills the table the workload queries - the table may exist
    when the container is reused between runs, so it is dropped first.
    """
    session = session_factory()

    try:
        _ = session.execute(text("""
            begin
                execute immediate 'drop table pool_workload';
            exception
                when others then null;
            end;
        """))

        _ = session.execute(text('create table pool_workload (id number, payload clob)'))
        _ = session.execute(text(f'insert into pool_workload (id) select level from dual connect by level <= {_bulk_row_count}'))

        clob_payload = 'z' * _clob_size
        _ = session.execute(
            text('insert into pool_workload (id, payload) values (:id, :payload)'),
            {'id': _clob_row_id, 'payload': clob_payload},
        )

        session.commit()

    finally:
        session.close()

# ################################################################################################################################

def _run_worker(state:'_WorkloadState', session_factory:'any_', deadline:'float') -> 'None':
    """ One worker greenlet - runs the mixed workload on its own sessions until the deadline.
    """
    while time.monotonic() < deadline:

        session = session_factory()

        try:
            # The database session id shows which pooled connection served this iteration ..
            sid_row = session.execute(text(_sid_query)).one()
            state.session_ids.add(sid_row[0])

            # .. a query returning the full bulk of rows ..
            rows = session.execute(text(_bulk_query)).all()
            row_count = len(rows)

            if row_count != _bulk_row_count:
                state.errors.append(f'Expected {_bulk_row_count} rows, found {row_count}')
                return

            # .. a large CLOB read ..
            payload = session.execute(text(_clob_query), {'id': _clob_row_id}).scalar()
            payload_length = len(payload)

            if payload_length != _clob_size:
                state.errors.append(f'Expected a payload of {_clob_size}, found {payload_length}')
                return

            # .. a query matching nothing ..
            missing = session.execute(text(_missing_query), {'id': -1}).one_or_none()

            if missing is not None:
                state.errors.append(f'Expected no row for id -1, found {missing}')
                return

            # .. an insert that commits ..
            _ = session.execute(text(_insert_query), {'id': _scratch_row_id})
            session.commit()

            # .. and a delete that rolls back.
            _ = session.execute(text(_delete_query), {'id': _scratch_row_id})
            session.rollback()

            state.query_count += _queries_per_iteration

        except Exception as e:
            state.errors.append(repr(e))
            return

        finally:
            session.close()

# ################################################################################################################################

def _run_heartbeat(state:'_WorkloadState', stop_event:'Event') -> 'None':
    """ Sleeps in short intervals and records the largest gap between wake-ups -
    a call that blocks every greenlet shows up as a gap of seconds.
    """
    previous = time.monotonic()

    while not stop_event.is_set():
        gevent.sleep(_heartbeat_sleep)

        now = time.monotonic()
        gap_ms = (now - previous) * 1000

        if gap_ms > state.max_heartbeat_gap_ms:
            state.max_heartbeat_gap_ms = gap_ms

        previous = now

# ################################################################################################################################

def _get_processes_parameter(session_factory:'any_') -> 'str':
    """ Reads the database's processes parameter so a session limit is visible
    in the output rather than guessed at.
    """
    try:
        session = session_factory()
        out = session.execute(text("select value from v$parameter where name = 'processes'")).scalar()
        session.close()
    except Exception as e:
        out = f'unavailable: {e!r}'

    return out

# ################################################################################################################################

def main() -> 'None':

    details = json.loads(sys.argv[1])

    config = {
        'engine':    'oracle',
        'username':  details['username'],
        'password':  details['password'],
        'host':      details['host'],
        'port':      details['port'],
        'db_name':   details['name'],
        'name':      'test.oracle.db.pool',
        'extra':     'max_overflow=0\npool_timeout=90',
        'pool_size': _pool_size,
    }

    pool = SQLConnectionPool('test.oracle.db.pool', config, config)

    if pool.engine is None:
        print(json.dumps({'errors': ['The pool did not create an engine']}), flush=True)
        sys.exit(1)

    engine = cast_('any_', pool.engine)
    session_factory = sessionmaker(bind=engine)

    _create_workload_table(session_factory)

    state = _WorkloadState()
    stop_event = Event()
    deadline = time.monotonic() + _workload_duration

    # Run the workload with the heartbeat alongside it ..
    heartbeat = gevent.spawn(_run_heartbeat, state, stop_event)

    workers = []

    for _ in range(_worker_count):
        worker = gevent.spawn(_run_worker, state, session_factory, deadline)
        workers.append(worker)

    _ = gevent.joinall(workers)

    stop_event.set()
    _ = heartbeat.join()

    # .. and report what happened in one line the parent parses.
    result = {
        'query_count':            state.query_count,
        'distinct_session_count': len(state.session_ids),
        'max_heartbeat_gap_ms':   round(state.max_heartbeat_gap_ms, 2),
        'checked_out':            engine.pool.checkedout(),
        'checked_in':             engine.pool.checkedin(),
        'is_thin_mode':           oracledb.is_thin_mode(),
        'errors':                 state.errors,
    }

    if state.errors:
        result['processes_parameter'] = _get_processes_parameter(session_factory)

    # Close every pooled connection so the interpreter exits cleanly
    engine.dispose()

    print(json.dumps(result), flush=True)

    if state.errors:
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
