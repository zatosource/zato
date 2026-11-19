# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The errors of the database in a batch of the pub/sub writer with an item of every kind - the error that each caller
# of the batch receives, the rows that the batch leaves as they were, the connection that the pool hands out next,
# the next batch on the same pool and the outage that the writer records.

# stdlib
import json
import os
import subprocess
import sys
from time import sleep

# pytest
import pytest

# Zato
from tools import build_fsfault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, strdict

    any_ = any_
    anydict = anydict
    Path = Path
    strdict = strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The process that runs one batch under a fault
    Runner_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batch_fault_runner.py')

    # How long a process may take, in seconds
    Runner_Timeout = 120

    # How long the process that holds the write lock of the file takes to enter its sync, in seconds
    Hold_Enter_Seconds = 1.0

    # The variables of the fault library
    Env_Preload = 'LD_PRELOAD'
    Env_Control = 'ZATO_FSFAULT_CONTROL'

class RunnerCtx:

    # The modes of the runner
    Mode_Sync = 'sync'
    Mode_Full = 'full'
    Mode_Constraint = 'constraint'
    Mode_Hold = 'hold'
    Mode_Locked = 'locked'

    # The lines that a runner prints when it reaches a point that the test waits for
    Line_Prepared = 'prepared'
    Line_Ready = 'ready'
    Line_Writing = 'writing'

    # The subscriber of the publications of a batch
    Sub_Key_Pub = 'zpsk.batch-faults.publish'

# The outcome of the next batch, which commits each of its items once the fault is cleared
_next_batch = {
    'exceptions': ['None', 'None', 'None', 'None', 'None'],
    'subscriber_keys': [RunnerCtx.Sub_Key_Pub],
    'ack_removed_count': 1,
    'atomic_removed_count': 1,
    'attempts': [[2, 1]],
    'leased_count': 2,
    'is_outage_cleared': True,
}

# The outcome of a batch under each fault of the file system
_fault_outcomes = {
    RunnerCtx.Mode_Sync: {
        'error_class': 'OperationalError',
        'error_base': 'DatabaseError',
        'orig_class': 'sqlite3.OperationalError',
        'orig_message': 'disk I/O error',
        'is_every_caller': True,
        'is_rows_unchanged': True,
        'is_in_transaction': False,
        'is_outage_recorded': True,
        'next': _next_batch,
    },
    RunnerCtx.Mode_Full: {
        'error_class': 'OperationalError',
        'error_base': 'DatabaseError',
        'orig_class': 'sqlite3.OperationalError',
        'orig_message': 'database or disk is full',
        'is_every_caller': True,
        'is_rows_unchanged': True,
        'is_in_transaction': False,
        'is_outage_recorded': True,
        'next': _next_batch,
    },
}

# The outcome of a batch whose publication has a value that its table does not accept
_constraint_outcome = {
    'error_class': 'IntegrityError',
    'error_base': 'DatabaseError',
    'orig_class': 'sqlite3.IntegrityError',
    'orig_message': 'NOT NULL constraint failed: pubsub_message.priority',
    'is_every_caller': True,
    'is_rows_unchanged': True,
    'is_in_transaction': False,
}

# The outcome of a batch that waits for a write lock that another process holds for longer than the busy timeout
_locked_outcome = {
    'error_class': 'OperationalError',
    'error_base': 'DatabaseError',
    'orig_class': 'sqlite3.OperationalError',
    'orig_message': 'database is locked',
    'is_every_caller': True,
}

# ################################################################################################################################
# ################################################################################################################################

def _get_env(control_path:'str', needs_fault:'bool') -> 'strdict':
    """ Returns the environment of a runner process, with the fault library preloaded if the process needs it.
    """
    out = dict(os.environ)

    if needs_fault:
        fsfault_path = build_fsfault()

        if current_preload := out.get(ModuleCtx.Env_Preload, ''):
            out[ModuleCtx.Env_Preload] = f'{fsfault_path} {current_preload}'
        else:
            out[ModuleCtx.Env_Preload] = fsfault_path

    out[ModuleCtx.Env_Control] = control_path

    return out

# ################################################################################################################################

def _get_paths(tmp_path:'Path') -> 'tuple[str, str]':
    """ Returns the directory of the database of a test and the control file of its fault library.
    """
    database_dir = os.path.join(tmp_path, 'database')
    os.makedirs(database_dir)

    control_path = os.path.join(tmp_path, 'fsfault-control')

    out = database_dir, control_path
    return out

# ################################################################################################################################

def _run(mode:'str', tmp_path:'Path', needs_fault:'bool') -> 'anydict':
    """ Runs the runner in one mode to its end and returns what it reported.
    """
    database_dir, control_path = _get_paths(tmp_path)

    env = _get_env(control_path, needs_fault)
    command = [sys.executable, ModuleCtx.Runner_Path, mode, database_dir, control_path]

    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=ModuleCtx.Runner_Timeout,
        check=False)

    assert result.returncode == 0, result.stderr

    lines = result.stdout.strip().splitlines()

    out = json.loads(lines[-1])
    return out

# ################################################################################################################################

def _start(mode:'str', database_dir:'str', control_path:'str', needs_fault:'bool') -> 'subprocess.Popen[str]':
    """ Starts the runner in one mode, with its input and output connected to the test.
    """
    env = _get_env(control_path, needs_fault)
    command = [sys.executable, ModuleCtx.Runner_Path, mode, database_dir, control_path]

    out = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True)

    return out

# ################################################################################################################################

def _wait_for_line(process:'subprocess.Popen[str]', expected:'str') -> 'None':
    """ Reads the output of a process until it prints the expected line.
    """
    stdout:'any_' = process.stdout
    stderr:'any_' = process.stderr

    while True:
        line = stdout.readline()
        assert line, stderr.read()

        if line.strip() == expected:
            break

# ################################################################################################################################

def _resume(process:'subprocess.Popen[str]') -> 'None':
    """ Tells a process that waits for its input to continue.
    """
    stdin:'any_' = process.stdin
    _ = stdin.write('\n')
    stdin.flush()

# ################################################################################################################################

def _finish(process:'subprocess.Popen[str]') -> 'anydict':
    """ Waits for a process to end and returns what it reported.
    """
    stdout, stderr = process.communicate(timeout=ModuleCtx.Runner_Timeout)
    assert process.returncode == 0, stderr

    lines = stdout.strip().splitlines()

    out = json.loads(lines[-1])
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('mode', sorted(_fault_outcomes))
def test_batch_fault(tmp_path:'Path', mode:'str') -> 'None':
    """ A batch that a failed sync or a full disk fails reaches every caller with the same error, leaves every row
    as it was and no transaction open, and the next batch on the same pool commits each of its items.
    """
    outcome = _run(mode, tmp_path, True)
    assert outcome == _fault_outcomes[mode], outcome

# ################################################################################################################################

def test_batch_constraint(tmp_path:'Path') -> 'None':
    """ A batch with a value that its table does not accept reaches every caller with the same error
    and leaves every row as it was.
    """
    outcome = _run(RunnerCtx.Mode_Constraint, tmp_path, False)
    assert outcome == _constraint_outcome, outcome

# ################################################################################################################################

def test_batch_locked(tmp_path:'Path') -> 'None':
    """ A batch that waits for the write lock of the file longer than the busy timeout reaches every caller
    with the same error.
    """
    database_dir, control_path = _get_paths(tmp_path)

    # The holder prepares the database and the waiting process opens it before the lock is taken ..
    holder = _start(RunnerCtx.Mode_Hold, database_dir, control_path, True)
    _wait_for_line(holder, RunnerCtx.Line_Prepared)

    waiting = _start(RunnerCtx.Mode_Locked, database_dir, control_path, False)
    _wait_for_line(waiting, RunnerCtx.Line_Ready)

    # .. the holder enters its delayed sync with the lock held ..
    _resume(holder)
    _wait_for_line(holder, RunnerCtx.Line_Writing)
    sleep(ModuleCtx.Hold_Enter_Seconds)

    # .. and the batch of the waiting process gives up while it waits for the lock.
    _resume(waiting)

    outcome = _finish(waiting)
    assert outcome == _locked_outcome, outcome

    holder_outcome = _finish(holder)
    assert holder_outcome == {'is_written': True}, holder_outcome

# ################################################################################################################################
# ################################################################################################################################
