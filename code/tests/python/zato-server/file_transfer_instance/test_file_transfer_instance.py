# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import threading

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditOutcome
from zato.common.audit_log.file_transfer_run import find_running_runs, Phase_Reading, Run_Status_Interrupted, \
    Run_Status_Running
from zato.common.audit_log.sqlite_writes import env_config as audit_env_config
from zato.common.db_env import dispose_env_engine
from zato.server import process_instance
from zato.server.process_instance import bind_process_instance
from zato.server.service.internal.outgoing.file_transfer.run import close_interrupted_runs, open_run
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_READY, STATE_STOPPED

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import anylist, generator_, stranydict
    from zato.server.service.internal.outgoing.file_transfer.run import RunContext

    anylist = anylist
    Path = Path
    RunContext = RunContext
    stranydict = stranydict

    nonegen = generator_[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Server_Name = 'test.server'
    Conn_Name = 'test.sftp'
    Schedule_Name = 'test.schedule'
    File_Name = 'invoice.csv'
    Other_File_Name = 'orders.csv'

    Start_ID = 1_794_000_000
    Earlier_Start_ID = 1_793_000_000
    Slot_Count = 2

    # The environment variables that point the audit log at a database
    Env_DB_Type = 'Zato_Audit_Log_DB_Type'
    Env_DB_Name = 'Zato_Audit_Log_DB_Name'

    # The thread that checkpoints the write-ahead log of the audit database
    Checkpoint_Thread_Name = 'sqlite-wal-checkpoint'

    # How long the test waits for that thread to end, in seconds
    Join_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

_claim_suffix = FileTransfer.Scheduler.Claim_Suffix

# ################################################################################################################################
# ################################################################################################################################

class LocalConn:
    """ The remote directory as a local one, with the two calls that a claim and its release make.
    """
    def exists(self, path:'str') -> 'bool':
        out = os.path.exists(path)
        return out

    def move(self, source:'str', target:'str') -> 'None':
        os.rename(source, target)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db(tmp_path:'Path', monkeypatch:'pytest.MonkeyPatch') -> 'nonegen':
    """ Points the audit log at a database of the test, and after the test closes it and leaves the process unbound.
    """
    threads_before = set(threading.enumerate())

    monkeypatch.setenv(ModuleCtx.Env_DB_Type, AuditLogCtx.Type_SQLite)
    monkeypatch.setenv(ModuleCtx.Env_DB_Name, str(tmp_path / 'audit.db'))

    yield

    # The engine of the database is closed and its checkpoints end ..
    dispose_env_engine(audit_env_config)

    for thread in threading.enumerate():
        if thread not in threads_before and thread.name == ModuleCtx.Checkpoint_Thread_Name:
            thread.join(ModuleCtx.Join_Timeout)

    # .. and the next test starts in a process that no arbiter bound.
    process_instance._state.binding = None

# ################################################################################################################################

def _new_region(start_id:'int') -> 'SharedRegion':
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
        'lock_capacity': 0,
        'start_id': start_id,
    })

    for slot in range(ModuleCtx.Slot_Count):
        _ = out.next_slot_generation(slot)
        out.set_slot_state(slot, STATE_READY)

    return out

# ################################################################################################################################

def _bind(region:'SharedRegion', slot:'int') -> 'None':
    bind_process_instance(region, slot, region.slot_generation(slot))

# ################################################################################################################################

def _new_directory(tmp_path:'Path') -> 'str':
    """ Returns the remote directory of the tests, with the two files that the runs claim.
    """
    out = tmp_path / 'remote'
    out.mkdir()

    for name in (ModuleCtx.File_Name, ModuleCtx.Other_File_Name):
        _ = (out / name).write_text('a,b\n')

    return str(out)

# ################################################################################################################################

def _open_claiming_run(directory:'str', run_cid:'str', file_name:'str') -> 'RunContext':
    """ Opens a run that claims one file and is in the middle of reading it.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)
    schedule = {'name': ModuleCtx.Schedule_Name, 'expected_files': 0, 'expected_by': ''}
    scheduler_context = {'job_id': 1, 'current_run': 1}

    out = open_run(audit_log, ModuleCtx.Conn_Name, directory, run_cid, schedule, scheduler_context)

    full_path = os.path.join(directory, file_name)
    os.rename(full_path, full_path + _claim_suffix)
    out.set_phase(Phase_Reading, file_name)

    return out

# ################################################################################################################################

def _close_interrupted_runs() -> 'None':
    audit_log = AuditLog(ModuleCtx.Server_Name)
    close_interrupted_runs(audit_log, ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name, LocalConn())

# ################################################################################################################################

def _get_running_files() -> 'anylist':
    """ The current files of the runs of the schedule that are marked as running, oldest first.
    """
    running = find_running_runs(ModuleCtx.Conn_Name, ModuleCtx.Schedule_Name, ModuleCtx.Server_Name)

    out:'anylist' = []

    for _event_id, data in running:
        out.append(data['current_file'])

    return out

# ################################################################################################################################

def _is_claimed(directory:'str', file_name:'str') -> 'bool':
    out = os.path.exists(os.path.join(directory, file_name + _claim_suffix))
    return out

# ################################################################################################################################

def _get_row(run:'RunContext') -> 'stranydict':
    """ The outcome and the status of the row of a run.
    """
    statement = select(event_table.c.outcome, event_table.c.status)
    statement = statement.where(event_table.c.id == run.event_id)

    with get_audit_engine().connect() as connection:
        outcome, status = connection.execute(statement).one()

    out = {'outcome': outcome, 'status': status}
    return out

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################

def test_a_run_records_the_process_instance_of_its_worker(tmp_path:'Path') -> 'None':
    region = _new_region(ModuleCtx.Start_ID)
    _bind(region, 1)

    run = _open_claiming_run(_new_directory(tmp_path), 'run-1', ModuleCtx.File_Name)

    assert run.data['process_instance'] == {
        'start_id': ModuleCtx.Start_ID,
        'slot': 1,
        'generation': region.slot_generation(1),
    }

# ################################################################################################################################

def test_a_run_of_a_process_that_no_arbiter_started_records_no_instance(tmp_path:'Path') -> 'None':
    run = _open_claiming_run(_new_directory(tmp_path), 'run-1', ModuleCtx.File_Name)
    assert 'process_instance' not in run.data

# ################################################################################################################################

def test_a_run_of_another_live_worker_stays_running_with_its_claim(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)
    region = _new_region(ModuleCtx.Start_ID)

    # The worker of slot 0 is in the middle of a file ..
    _bind(region, 0)
    run = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    # .. when the worker of slot 1 starts a run of the same schedule.
    _bind(region, 1)
    _close_interrupted_runs()

    assert _get_running_files() == [ModuleCtx.File_Name]
    assert _get_row(run) == {'outcome': AuditOutcome.Running, 'status': Run_Status_Running}
    assert _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################

def test_another_run_of_the_same_worker_stays_running(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)
    region = _new_region(ModuleCtx.Start_ID)
    _bind(region, 0)

    _ = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)
    _close_interrupted_runs()

    assert _get_running_files() == [ModuleCtx.File_Name]
    assert _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################

def test_a_run_of_a_stopped_worker_is_interrupted_and_its_claim_released(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)
    region = _new_region(ModuleCtx.Start_ID)

    _bind(region, 0)
    stopped = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    # The worker of slot 0 terminates, and its slot has no replacement yet ..
    region.set_slot_state(0, STATE_STOPPED)

    # .. while the worker of slot 1 is itself in the middle of another file.
    _bind(region, 1)
    live = _open_claiming_run(directory, 'run-2', ModuleCtx.Other_File_Name)

    _close_interrupted_runs()

    assert _get_running_files() == [ModuleCtx.Other_File_Name]
    assert _get_row(stopped) == {'outcome': AuditOutcome.Error, 'status': Run_Status_Interrupted}
    assert _get_row(live) == {'outcome': AuditOutcome.Running, 'status': Run_Status_Running}

    assert not _is_claimed(directory, ModuleCtx.File_Name)
    assert _is_claimed(directory, ModuleCtx.Other_File_Name)

# ################################################################################################################################

def test_a_run_of_a_replaced_worker_is_interrupted(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)
    region = _new_region(ModuleCtx.Start_ID)

    _bind(region, 0)
    replaced = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    # A new worker runs in slot 0 ..
    _ = region.next_slot_generation(0)
    region.set_slot_state(0, STATE_READY)

    # .. and it starts a run of the schedule.
    _bind(region, 0)
    _close_interrupted_runs()

    assert _get_running_files() == []
    assert _get_row(replaced) == {'outcome': AuditOutcome.Error, 'status': Run_Status_Interrupted}
    assert not _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################

def test_a_run_of_an_earlier_arbiter_is_interrupted(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)

    # A worker of the previous arbiter of the server opened the run ..
    _bind(_new_region(ModuleCtx.Earlier_Start_ID), 0)
    earlier = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    # .. and the worker of the same slot and generation of the current arbiter starts a run of the schedule.
    _bind(_new_region(ModuleCtx.Start_ID), 0)
    _close_interrupted_runs()

    assert _get_running_files() == []
    assert _get_row(earlier) == {'outcome': AuditOutcome.Error, 'status': Run_Status_Interrupted}
    assert not _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################

def test_a_run_without_an_instance_is_interrupted_by_a_worker(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)

    # A process that no arbiter started opened the run ..
    without = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    # .. and a worker starts a run of the schedule.
    _bind(_new_region(ModuleCtx.Start_ID), 0)
    _close_interrupted_runs()

    assert _get_row(without) == {'outcome': AuditOutcome.Error, 'status': Run_Status_Interrupted}
    assert not _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################

def test_a_process_that_no_arbiter_started_interrupts_every_running_run(tmp_path:'Path') -> 'None':
    directory = _new_directory(tmp_path)

    _bind(_new_region(ModuleCtx.Start_ID), 0)
    with_instance = _open_claiming_run(directory, 'run-1', ModuleCtx.File_Name)

    process_instance._state.binding = None
    _close_interrupted_runs()

    assert _get_row(with_instance) == {'outcome': AuditOutcome.Error, 'status': Run_Status_Interrupted}
    assert not _is_claimed(directory, ModuleCtx.File_Name)

# ################################################################################################################################
# ################################################################################################################################
