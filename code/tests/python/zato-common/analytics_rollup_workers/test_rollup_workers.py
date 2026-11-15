# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import time
from multiprocessing import get_context

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from live_sql.env import database_env
from zato.common.analytics import rollup
from zato.common.analytics.api import get_analytics_engine, usage_table, ModuleCtx as AnalyticsCtx
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditCtx
from zato.common.audit_log.bulk_insert import insert_events
from zato.common.audit_log.common import AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from live_sql.containers import DatabaseServer
    from pytest import MonkeyPatch
    from zato.common.typing_ import anytuple, callable_, stranydict

    anytuple = anytuple
    callable_ = callable_
    DatabaseServer = DatabaseServer
    MonkeyPatch = MonkeyPatch
    Path = Path
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Event_Count = 2

    Audit_Env_Prefix = 'Zato_Audit_Log_DB_'
    Server_Name = 'test.analytics.workers'
    Channel = 'test.analytics.channel'

    First_Thread = 'first'

    # How long the second rollup runs alone, in seconds, before the first one continues
    Overlap_Seconds = 1.0

    # How long the writer of the first event keeps its transaction open after the rollup started, in seconds
    Commit_Delay = 1.0

    # How long the test waits for the process that runs its body, in seconds
    Join_Timeout = 60.0

# The body of each test runs in a forked process, as the workers of a server run
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _get_counted() -> 'int':
    """ Returns how many requests the hourly rows count in total.
    """
    statement = select(func.sum(usage_table.c.request_count))

    with get_analytics_engine().connect() as connection:
        result = connection.execute(statement)
        out = result.scalar_one()

    return out

# ################################################################################################################################

def _new_row(audit_log:'AuditLog', label:'str') -> 'dict':
    pending = audit_log.new_pending_event(AuditSource.REST_Channel, AuditEvent.Response_Sent, ModuleCtx.Channel, data=label)
    out = pending.values
    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_reinitialized(target:'callable_', args:'anytuple') -> 'None':
    """ Gives the forked process an event loop of its own before the test body runs, as the arbiter does for its workers.
    """
    gevent.reinit()
    target(*args)

# ################################################################################################################################

def _run_in_child(target:'callable_', args:'anytuple') -> 'None':
    """ Runs one test body in a forked process, so that the engines and the checkpoint threads it starts
    remain in that process and no process that a later test forks inherits them.
    """
    process = _context.Process(target=_run_reinitialized, args=(target, args))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

# ################################################################################################################################

def _overlapping_rollups() -> 'None':

    # The watermark row exists before the overlapping runs begin
    _ = rollup.run_rollup()

    audit_log = AuditLog(ModuleCtx.Server_Name)

    for index in range(ModuleCtx.Event_Count):
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, ModuleCtx.Channel, data=f'event-{index}')

    load_new_events = rollup._load_new_events
    first_reached = threading.Event()
    first_released = threading.Event()

    # The first rollup holds the analytics file from its watermark update until it commits ..
    def paused_load(last_event_id:'int') -> 'list':
        if threading.current_thread().name == ModuleCtx.First_Thread:
            first_reached.set()
            _ = first_released.wait()
        out = load_new_events(last_event_id)
        return out

    rollup._load_new_events = paused_load

    first = threading.Thread(target=rollup.run_rollup, name=ModuleCtx.First_Thread)
    second = threading.Thread(target=rollup.run_rollup)

    first.start()
    _ = first_reached.wait()

    # .. the second one begins meanwhile and waits for the file ..
    second.start()
    time.sleep(ModuleCtx.Overlap_Seconds)

    # .. and both commit.
    first_released.set()
    first.join()
    second.join()

    assert _get_counted() == ModuleCtx.Event_Count

# ################################################################################################################################

def _event_committed_after_a_higher_one(server_details:'stranydict') -> 'None':

    with database_env(ModuleCtx.Audit_Env_Prefix, server_details):

        audit_log = AuditLog(ModuleCtx.Server_Name)
        engine = audit_log.engine

        # The writer of one worker inserts its event and has not committed yet ..
        first_connection = engine.connect()
        first_transaction = first_connection.begin()
        first_ids = insert_events(first_connection, [_new_row(audit_log, 'first')], 'test-first')

        # .. the writer of another worker inserts and commits its own, which receives the higher id ..
        with engine.begin() as second_connection:
            second_ids = insert_events(second_connection, [_new_row(audit_log, 'second')], 'test-second')

        assert first_ids[0] < second_ids[0]

        # .. the first writer commits while a rollup runs ..
        def commit_first() -> 'None':
            time.sleep(ModuleCtx.Commit_Delay)
            first_transaction.commit()
            first_connection.close()

        committer = threading.Thread(target=commit_first)
        committer.start()

        first_result = rollup.run_rollup()
        committer.join()

        second_result = rollup.run_rollup()

    # .. and the two rollups together count each event once.
    assert first_result.event_count + second_result.event_count == ModuleCtx.Event_Count
    assert _get_counted() == ModuleCtx.Event_Count

# ################################################################################################################################
# ################################################################################################################################

def test_overlapping_rollups_count_each_event_once(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(AuditCtx.Env_Type, AuditCtx.Type_SQLite)
    monkeypatch.setenv(AuditCtx.Env_Name, str(tmp_path / 'audit.db'))
    monkeypatch.setenv(AnalyticsCtx.Env_Path, str(tmp_path / 'analytics.db'))

    _run_in_child(_overlapping_rollups, ())

# ################################################################################################################################

def test_an_event_committed_after_a_higher_one_is_counted(
    postgresql_server:'DatabaseServer',
    tmp_path:'Path',
    monkeypatch:'MonkeyPatch',
    ) -> 'None':

    monkeypatch.setenv(AnalyticsCtx.Env_Path, str(tmp_path / 'analytics.db'))

    _run_in_child(_event_committed_after_a_higher_one, (postgresql_server.details,))

# ################################################################################################################################
# ################################################################################################################################
