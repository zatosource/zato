# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import threading
from datetime import date, datetime
from multiprocessing import get_context
from types import SimpleNamespace

# pytest
import pytest

# Zato
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.sqlite_writes import env_config as audit_env_config
from zato.common.db_env import dispose_env_engine
from zato.server import process_instance
from zato.server.process_instance import bind_process_instance
from zato.server.service.internal.outgoing.file_transfer import run as run_module
from zato.server.service.internal.outgoing.file_transfer.run import add_delivered_today, close_run, get_delivered_today, \
    note_listing, open_run
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_READY

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.queues import SimpleQueue
    from pathlib import Path
    from zato.common.typing_ import any_, anylist, anytuple, callable_, generator_, strlist
    from zato.server.service.internal.outgoing.file_transfer.run import RunContext

    any_ = any_
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    Path = Path
    RunContext = RunContext
    SimpleQueue = SimpleQueue
    strlist = strlist

    nonegen = generator_[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Server_Name = 'test.server'
    Conn_Name = 'test.sftp'
    Schedule_Name = 'test.schedule'
    Other_Schedule_Name = 'test.other-schedule'
    Remote_Path = '/inbox'

    Start_ID = 1_794_000_000
    Slot_Count = 3
    Lock_Capacity = 8

    # The count of the deliveries of the day that another worker set first
    Preceding_Count = 7

    # The environment variables that point the audit log at a database
    Env_DB_Type = 'Zato_Audit_Log_DB_Type'
    Env_DB_Name = 'Zato_Audit_Log_DB_Name'

    # The thread that checkpoints the write-ahead log of the audit database
    Checkpoint_Thread_Name = 'sqlite-wal-checkpoint'

    # How long the test waits for a thread or a process, in seconds
    Join_Timeout = 60.0

_context = get_context('fork')

# The listings of the runs of the tests, as the names of their files
_first_listing = ('invoice.csv',)
_second_listing = ('invoice.csv', 'orders.csv')

# ################################################################################################################################
# ################################################################################################################################

def _dispose_audit_engine() -> 'None':
    """ Closes the engine of the audit database of this process and waits for its checkpoints to end.
    """
    dispose_env_engine(audit_env_config)

    for thread in threading.enumerate():
        if thread.name == ModuleCtx.Checkpoint_Thread_Name:
            thread.join(ModuleCtx.Join_Timeout)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db(tmp_path:'Path', monkeypatch:'pytest.MonkeyPatch') -> 'nonegen':
    """ Points the audit log at a database of the test, and after the test closes it and leaves the process unbound.
    """
    monkeypatch.setenv(ModuleCtx.Env_DB_Type, AuditLogCtx.Type_SQLite)
    monkeypatch.setenv(ModuleCtx.Env_DB_Name, str(tmp_path / 'audit.db'))

    yield

    _dispose_audit_engine()

    process_instance._state.binding = None
    run_module._delivered_today.clear()

# ################################################################################################################################

def _new_region(lock_capacity:'int'=ModuleCtx.Lock_Capacity) -> 'SharedRegion':
    """ Returns the region of a server whose every slot has a worker that is ready.
    """
    out = SharedRegion({
        'slot_count': ModuleCtx.Slot_Count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': lock_capacity,
        'start_id': ModuleCtx.Start_ID,
    })

    for slot in range(ModuleCtx.Slot_Count):
        _ = out.next_slot_generation(slot)
        out.set_slot_state(slot, STATE_READY)

    return out

# ################################################################################################################################

def _bind(region:'SharedRegion', slot:'int') -> 'None':
    bind_process_instance(region, slot, region.slot_generation(slot))

# ################################################################################################################################

def _run_in_child(target:'callable_', args:'anytuple') -> 'anylist':
    """ Runs a function in a forked process and returns what it put in its queue,
    with the engine of the audit database of this process closed first, so the child opens its own.
    """
    _dispose_audit_engine()

    results:'SimpleQueue' = _context.SimpleQueue()

    process = _context.Process(target=target, args=(results, *args))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    out:'anylist' = []

    while not results.empty():
        out.append(results.get())

    return out

# ################################################################################################################################

def _record_delivery(schedule_name:'str') -> 'None':
    """ Writes the audit event of one file that a schedule delivered.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)
    _ = record_schedule_event(audit_log, ModuleCtx.Conn_Name, AuditEvent.Delivered, ModuleCtx.Remote_Path,
        cid='file-1', correl_id='run-1', schedule=schedule_name, outcome=AuditOutcome.OK)

# ################################################################################################################################

def _get_today() -> 'int':
    now = datetime.now()
    today = now.astimezone().date()

    out = today.toordinal()
    return out

# ################################################################################################################################

def _get_delivered_entry(region:'SharedRegion') -> 'int':
    key = f'{run_module._delivered_today_key_prefix}{ModuleCtx.Conn_Name}|{ModuleCtx.Schedule_Name}'

    out = region.lock_entry(key)
    return out

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################

def _deliver(results:'SimpleQueue', region:'SharedRegion', slot:'int') -> 'None':
    """ Delivers one file of the schedule in a worker bound to its slot.
    """
    _bind(region, slot)
    results.put(add_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name))

# ################################################################################################################################

def test_each_delivery_carries_the_count_of_every_worker() -> 'None':
    region = _new_region()

    # Two deliveries were recorded today before any worker counted them, and one of another schedule ..
    _record_delivery(ModuleCtx.Schedule_Name)
    _record_delivery(ModuleCtx.Schedule_Name)
    _record_delivery(ModuleCtx.Other_Schedule_Name)

    # .. so the first delivery of a worker counts them, and every later one adds to the deliveries of every worker.
    assert _run_in_child(_deliver, (region, 1)) == [3]
    assert _run_in_child(_deliver, (region, 2)) == [4]
    assert _run_in_child(_deliver, (region, 1)) == [5]

    _bind(region, 0)
    assert get_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 5

# ################################################################################################################################

def test_the_first_run_of_a_day_counts_the_day_anew() -> 'None':
    region = _new_region()
    entry = _get_delivered_entry(region)

    yesterday = _get_today() - 1
    assert region.lock_counter_replace(entry, 0, run_module._pack_day_count(yesterday, ModuleCtx.Preceding_Count))

    _record_delivery(ModuleCtx.Schedule_Name)

    _bind(region, 1)

    assert get_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 1
    assert run_module._unpack_day_count(region.lock_counter(entry)) == (_get_today(), 1)

# ################################################################################################################################

def test_a_worker_preceded_by_another_one_in_counting_the_day_uses_its_count(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    region = _new_region()
    entry = _get_delivered_entry(region)

    def count_while_another_worker_sets_the_day(*_args:'any_') -> 'int':
        """ Another worker counts the day and sets it while this one is still counting.
        """
        value = run_module._pack_day_count(_get_today(), ModuleCtx.Preceding_Count)
        _ = region.lock_counter_replace(entry, region.lock_counter(entry), value)

        return 0

    monkeypatch.setattr(run_module, 'count_delivered_since', count_while_another_worker_sets_the_day)

    _bind(region, 1)

    assert get_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == ModuleCtx.Preceding_Count
    assert add_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == ModuleCtx.Preceding_Count + 1

# ################################################################################################################################

def test_with_the_lock_table_full_a_worker_counts_its_own_deliveries(caplog:'pytest.LogCaptureFixture') -> 'None':
    region = _new_region(lock_capacity=0)
    _bind(region, 1)

    with caplog.at_level(logging.ERROR):
        assert add_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 1
        assert add_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 2

    assert 'the lock table is full' in caplog.text

# ################################################################################################################################

def test_a_process_that_no_arbiter_started_counts_its_own_deliveries() -> 'None':
    _record_delivery(ModuleCtx.Schedule_Name)

    assert add_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 2
    assert get_delivered_today(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name) == 2

    today = date.today().isoformat()
    key = f'{ModuleCtx.Conn_Name}|{ModuleCtx.Schedule_Name}'

    assert run_module._delivered_today[key] == {'day': today, 'count': 2}

# ################################################################################################################################
# ################################################################################################################################

def _list_and_close(results:'SimpleQueue', region:'SharedRegion | None', slot:'int', file_names:'strlist') -> 'None':
    """ Runs the schedule over a listing in a worker bound to its slot, or in a process that no arbiter bound,
    and reports the run's id and whether its listing is unchanged.
    """
    if region:
        _bind(region, slot)

    audit_log = AuditLog(ModuleCtx.Server_Name)
    schedule = {'name': ModuleCtx.Schedule_Name, 'expected_files': 0, 'expected_by': ''}
    scheduler_context = {'job_id': 1, 'current_run': 1}

    run = open_run(audit_log, ModuleCtx.Conn_Name, ModuleCtx.Remote_Path, 'run', schedule, scheduler_context)

    entries = [SimpleNamespace(name=name, size=1, last_modified_iso='2026-11-15T10:00:00') for name in file_names]
    note_listing(run, entries, 0)

    if 'unchanged_since_event_id' in run.data:
        unchanged_since = run.data['unchanged_since_event_id']
    else:
        unchanged_since = None

    close_run(run)

    results.put((run.event_id, run.is_unchanged, unchanged_since))

# ################################################################################################################################

def test_a_run_compares_its_listing_with_the_previous_run_through_any_worker() -> 'None':
    region = _new_region()

    # The first run through one worker sees a listing ..
    [(first_id, first_unchanged, _)] = _run_in_child(_list_and_close, (region, 1, _first_listing))

    # .. which a run through another worker sees unchanged since then ..
    [(_, second_unchanged, second_since)] = _run_in_child(_list_and_close, (region, 2, _first_listing))

    # .. and a run through the first worker sees changed after a run through the second one saw it change.
    [(third_id, third_unchanged, _)] = _run_in_child(_list_and_close, (region, 2, _second_listing))
    [(_, fourth_unchanged, _)] = _run_in_child(_list_and_close, (region, 1, _first_listing))

    assert not first_unchanged
    assert second_unchanged
    assert second_since == first_id

    assert not third_unchanged
    assert not fourth_unchanged
    assert third_id != first_id

# ################################################################################################################################

def test_an_unchanged_run_leaves_the_reference_listing_in_place() -> 'None':
    region = _new_region()

    [(first_id, _, _)] = _run_in_child(_list_and_close, (region, 1, _first_listing))
    _ = _run_in_child(_list_and_close, (region, 2, _first_listing))

    [(_, third_unchanged, third_since)] = _run_in_child(_list_and_close, (region, 1, _first_listing))

    assert third_unchanged
    assert third_since == first_id

# ################################################################################################################################

def test_processes_that_no_arbiter_started_compare_with_the_previous_run_of_the_server() -> 'None':
    [(first_id, _, _)] = _run_in_child(_list_and_close, (None, 0, _first_listing))
    [(_, second_unchanged, second_since)] = _run_in_child(_list_and_close, (None, 0, _first_listing))

    assert second_unchanged
    assert second_since == first_id

# ################################################################################################################################
# ################################################################################################################################
