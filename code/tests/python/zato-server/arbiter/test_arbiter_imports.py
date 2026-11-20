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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The process that imports the modules as the arbiter does, in an interpreter that imported nothing before it
    Process_Path = os.path.join(os.path.dirname(__file__), 'internal_imports_process.py')

    # How long the process may run, in seconds
    Process_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _run_process() -> 'anydict':
    """ Runs the process and returns what it reported.
    """
    result = subprocess.run(
        [sys.executable, ModuleCtx.Process_Path],
        capture_output=True,
        text=True,
        timeout=ModuleCtx.Process_Timeout,
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_arbiter_imports_internal_service_modules_and_stays_ready_for_the_fork() -> 'None':

    result = _run_process()

    # Every module of the internal services is imported ..
    assert result['module_count'] > 0
    assert result['missing_modules'] == []

    # .. and nothing that the import opened stops the fork.
    assert result['fork_ready_error'] == ''

# ################################################################################################################################
# ################################################################################################################################
