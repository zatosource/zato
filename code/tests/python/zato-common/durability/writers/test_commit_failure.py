# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys
from uuid import uuid4

# pytest
import pytest

# Zato
from tools import build_fsfault
from write_apis import count_rows, is_written, Write_APIs
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

@pytest.mark.parametrize('name', sorted(Write_APIs))
def test_failed_sync_raises_and_writes_nothing(tmp_path:'Path', name:'str') -> 'None':
    """ A write API whose commit cannot be synced raises, and once the fault is cleared and the process
    is started again, nothing of what it was to write is found in the database.
    """
    token = uuid4().hex
    check = Write_APIs[name](token).get_check()

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

    # .. and this process, which opens the database anew, finds nothing of the write.
    assert not is_written(db_path, check), f'{name} -> {check} -> {count_rows(db_path, check)}'

# ################################################################################################################################
# ################################################################################################################################
