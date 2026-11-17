# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sqlite3
import subprocess
import sys
from uuid import uuid4

# pytest
import pytest

# Zato
from tools import build_fsfault
from write_apis import Write_APIs
from zato.common.db_env.database_env import DatabaseEnv

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The process that runs one write API under the fault
    Runner_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fault_runner.py')

    # How long the process may take, in seconds
    Runner_Timeout = 120

    # The variables of the fault library
    Env_Preload = 'LD_PRELOAD'
    Env_Control = 'ZATO_FSFAULT_CONTROL'

    # What the integrity check of SQLite returns for a sound database
    Integrity_OK = 'ok'

# ################################################################################################################################
# ################################################################################################################################

def _get_runner_env(control_path:'str') -> 'dict[str, str]':
    """ Returns the environment of the process that runs a write API, with the fault library preloaded.
    """
    fsfault_path = build_fsfault()

    out = dict(os.environ)

    if current_preload := out.get(ModuleCtx.Env_Preload, ''):
        out[ModuleCtx.Env_Preload] = f'{fsfault_path} {current_preload}'
    else:
        out[ModuleCtx.Env_Preload] = fsfault_path

    out[ModuleCtx.Env_Control] = control_path

    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_integrity(db_path:'str') -> 'str':
    """ Returns the result of the integrity check of a SQLite file, as a new connection runs it.
    """
    connection = sqlite3.connect(db_path)

    try:
        row = connection.execute('pragma integrity_check').fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('name', sorted(Write_APIs))
def test_failed_sync_raises(tmp_path:'Path', name:'str') -> 'None':
    """ A write API whose commit cannot be synced raises rather than acknowledges, and once the fault is cleared
    and the process is started again, the database is sound. The frames of the failed commit were written before
    the sync failed, so whether the restarted process finds the write is not determined, as for any database.
    """
    token = uuid4().hex

    database_dir = os.path.join(tmp_path, 'database')
    os.makedirs(database_dir)

    control_path = os.path.join(tmp_path, 'fsfault-control')
    db_path = os.path.join(database_dir, DatabaseEnv.File_Name)

    env = _get_runner_env(control_path)
    command = [sys.executable, ModuleCtx.Runner_Path, name, token, database_dir, control_path]

    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=ModuleCtx.Runner_Timeout,
        check=False)

    assert result.returncode == 0, result.stderr

    # The last line of the output is the outcome of the write ..
    lines = result.stdout.strip().splitlines()
    outcome = json.loads(lines[-1])

    assert outcome['is_raised'], f'{name} returned while every sync of its commit failed'

    # .. and this process, which opens the database anew, finds it sound.
    integrity = _check_integrity(db_path)
    assert integrity == ModuleCtx.Integrity_OK, f'{name} -> {integrity}'

# ################################################################################################################################
# ################################################################################################################################
