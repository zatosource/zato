# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timedelta, timezone
from importlib import import_module

# Zato
from zato.common import worker_slot as worker_slot_module
from zato.common.audit_log.retention import _Archiver, Env_Archive_Dir
from zato.common.worker_slot import is_singleton_owner

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anylist, intnone

    any_ = any_
    anylist = anylist
    intnone = intnone
    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The moment at which the runs start, and how far apart within one second
    Run_Start = datetime(2026, 11, 14, 3, 0, 0, tzinfo=timezone.utc)
    Run_Offset = timedelta(milliseconds=1)

    # How many runs start within the one second
    Run_Count = 3

    # The slots of the workers of a server with three workers
    Other_Slots = (1, 2)

# ################################################################################################################################
# ################################################################################################################################

class _RecordingRunner:
    """ Records the engines whose retention was requested, in place of the runner of the process.
    """
    def __init__(self) -> 'None':
        self.requested:'anylist' = []

    def request(self, engine:'any_') -> 'None':
        self.requested.append(engine)

# ################################################################################################################################
# ################################################################################################################################

def test_runs_within_one_second_write_files_of_their_own(monkeypatch:'MonkeyPatch', tmp_path:'Path') -> 'None':

    archive_dir = os.path.join(tmp_path, 'archive')
    monkeypatch.setenv(Env_Archive_Dir, archive_dir)

    # Several runs start within the same second, each one archiving a row of its own ..
    for index in range(ModuleCtx.Run_Count):
        archiver = _Archiver(ModuleCtx.Run_Start + ModuleCtx.Run_Offset * index)
        archiver.write_rows('event', [{'id': index}])
        archiver.write_rows('body', [{'id': index}])

    # .. and each of them wrote to a file of its own, whose name the runs after the first one number.
    expected_names = [
        'audit-archive-20261114-030000-2.jsonl',
        'audit-archive-20261114-030000-3.jsonl',
        'audit-archive-20261114-030000.jsonl',
    ]
    assert sorted(os.listdir(archive_dir)) == expected_names

    for name in expected_names:
        with open(os.path.join(archive_dir, name), encoding='utf-8') as archive_file:
            lines = archive_file.readlines()

        assert len(lines) == 2
        assert lines[0].startswith('{"kind": "event"')
        assert lines[1].startswith('{"kind": "body"')

# ################################################################################################################################

def test_a_run_with_nothing_to_archive_creates_no_file(monkeypatch:'MonkeyPatch', tmp_path:'Path') -> 'None':

    archive_dir = os.path.join(tmp_path, 'archive')
    monkeypatch.setenv(Env_Archive_Dir, archive_dir)

    archiver = _Archiver(ModuleCtx.Run_Start)
    archiver.write_rows('event', [])

    assert archiver.archive_path is None
    assert not os.path.exists(archive_dir)

# ################################################################################################################################

def test_retention_is_requested_only_in_the_worker_of_the_first_slot(monkeypatch:'MonkeyPatch') -> 'None':

    retention_runner = import_module('zato.common.audit_log.retention_runner')

    runner = _RecordingRunner()
    monkeypatch.setattr(retention_runner, '_runner', runner)

    engine = object()

    # A process that is not a worker, and the worker of the first slot, run retention ..
    for slot in (None, worker_slot_module.ModuleCtx.Singleton_Slot):
        monkeypatch.setattr(worker_slot_module, '_worker_slot', slot)
        assert is_singleton_owner()
        retention_runner.request_retention(engine)

    # .. while the workers of the other slots do not.
    for slot in ModuleCtx.Other_Slots:
        monkeypatch.setattr(worker_slot_module, '_worker_slot', slot)
        assert not is_singleton_owner()
        retention_runner.request_retention(engine)

    assert runner.requested == [engine, engine]

# ################################################################################################################################
# ################################################################################################################################
