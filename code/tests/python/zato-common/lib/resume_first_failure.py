# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A pytest plugin that resumes each pytest run of a make goal after the goal failed or was interrupted.
#
# code/tests/recipe_shell.sh loads it into every pytest run of every recipe line through PYTEST_ADDOPTS
# and keeps one state file per make goal. While the previous run of the goal failed or was interrupted,
# a pytest run that completed in that run is skipped in full, and a pytest run that failed or was interrupted
# starts from the test that failed first or that was running when the run was interrupted. A run of the goal
# that completes, or a run with RESTART=1, makes the next run start from the first test of every pytest run.
#
# A pytest run is identified by its working directory, its command line arguments and the environment variables
# named Zato_Test_* that its recipe line names, so that each pass of a loop over modes or parameters of a recipe line
# resumes on its own, while the variables that the shell of the user exports do not change the identity.
# It imports nothing from Zato, because it is loaded before the suites that patch gevent.

# stdlib
import fcntl
import os
from hashlib import sha1
from typing import cast

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variables that recipe_shell.sh sets for each recipe line
    Env_State_Path = 'Zato_Resume_State_Path'
    Env_Run_Id = 'Zato_Resume_Run_Id'
    Env_Line = 'Zato_Resume_Line'
    Env_Addopts_Original = 'Zato_Resume_Pytest_Addopts'
    Env_Addopts = 'PYTEST_ADDOPTS'

    # The environment variables that are part of the identity of a pytest run, compared case-insensitively ..
    Env_Identity_Prefix = 'zato_test_'

    # .. except for the goal, which differs between a target run on its own and the same target run by test-all.
    Env_Identity_Excluded = {'zato_test_goal'}

    # The entries of the state file that this plugin reads and writes
    Entry_Done = 'done'
    Entry_First = 'first'

    # The suffix of the lock file that recipe_shell.sh and this plugin serialize the state file with
    Lock_Suffix = '.lock'

# ################################################################################################################################
# ################################################################################################################################

class _RunState:
    """ The state of the current pytest run.
    """
    is_active:'bool' = False
    state_path:'str' = ''
    run_id:'str' = ''
    stage_id:'str' = ''
    is_skipped:'bool' = False
    start_nodeid:'str | None' = None
    first_failed:'str | None' = None
    current:'str | None' = None

_run_state = _RunState()

# ################################################################################################################################
# ################################################################################################################################

def _write_line(config:'pytest.Config', text:'str') -> 'None':
    """ Writes a line to the terminal of the session.
    """
    reporter = config.pluginmanager.getplugin('terminalreporter')
    reporter = cast('pytest.TerminalReporter', reporter)
    reporter.write_line(text)

# ################################################################################################################################

def _get_stage_id(config:'pytest.Config', line:'str') -> 'str':
    """ Returns the identity of this pytest run - its directory, its arguments and the Zato_Test_* environment variables
    that its recipe line names.
    """
    hasher = sha1()

    _ = hasher.update(str(config.invocation_params.dir).encode('utf8'))

    for arg in config.invocation_params.args:
        _ = hasher.update(b'\0')
        _ = hasher.update(arg.encode('utf8'))

    for name in sorted(os.environ):
        name_lower = name.lower()
        if name_lower.startswith(ModuleCtx.Env_Identity_Prefix) and name in line:
            if name_lower not in ModuleCtx.Env_Identity_Excluded:
                _ = hasher.update(b'\0')
                _ = hasher.update(f'{name}={os.environ[name]}'.encode('utf8'))

    out = hasher.hexdigest()
    return out

# ################################################################################################################################

def _read_last_entry(state_path:'str', stage_id:'str') -> 'list[str] | None':
    """ Returns the last done or first entry of the state file for the pytest run, split into its fields.
    """
    out = None

    with open(state_path + ModuleCtx.Lock_Suffix, 'a') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_SH)

        with open(state_path) as state_file:
            for line in state_file:
                fields = line.rstrip('\n').split(' ', 3)
                if fields[0] in (ModuleCtx.Entry_Done, ModuleCtx.Entry_First):
                    if fields[2] == stage_id:
                        out = fields

    return out

# ################################################################################################################################

def _append_entry(state_path:'str', entry:'str') -> 'None':
    """ Appends an entry to the state file under the lock that recipe_shell.sh rewrites the file under.
    """
    with open(state_path + ModuleCtx.Lock_Suffix, 'a') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        with open(state_path, 'a') as state_file:
            _ = state_file.write(entry + '\n')

# ################################################################################################################################

def pytest_configure(config:'pytest.Config') -> 'None':
    """ Finds where this pytest run starts from and hides the plugin from any pytest run that the tests start themselves.
    """
    environ = os.environ

    # A pytest run that the tests start themselves, or one started outside of make, is not resumed ..
    if ModuleCtx.Env_State_Path not in environ:
        return

    _run_state.is_active = True
    _run_state.state_path = environ.pop(ModuleCtx.Env_State_Path)
    _run_state.run_id = environ.pop(ModuleCtx.Env_Run_Id)
    line = environ.pop(ModuleCtx.Env_Line)

    # .. so the options of pytest go back to what they were before recipe_shell.sh added the plugin to them ..
    addopts_original = environ.pop(ModuleCtx.Env_Addopts_Original)
    if addopts_original:
        environ[ModuleCtx.Env_Addopts] = addopts_original
    else:
        del environ[ModuleCtx.Env_Addopts]

    # .. the identity is computed without the variables of the plugin ..
    _run_state.stage_id = _get_stage_id(config, line)

    # .. and the last entry for this pytest run tells where it starts from.
    entry = _read_last_entry(_run_state.state_path, _run_state.stage_id)

    if entry is None:
        return

    entry_type, entry_run_id = entry[0], entry[1]

    # An entry of the current run of the goal belongs to an earlier pass of the same pytest run, which does not resume it
    if entry_run_id == _run_state.run_id:
        return

    if entry_type == ModuleCtx.Entry_Done:
        _run_state.is_skipped = True
    else:
        _run_state.start_nodeid = entry[3]

# ################################################################################################################################

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config:'pytest.Config', items:'list[pytest.Item]') -> 'None':
    """ Deselects every test of a pytest run that completed in the previous run of the goal, or the tests
    that precede the test that the previous run failed first in or was interrupted in.
    """
    if _run_state.is_skipped:
        _write_line(config, '>>> Skipping the suite, which completed in the previous run of the goal')
        config.hook.pytest_deselected(items=items[:])
        del items[:]
        return

    start_nodeid = _run_state.start_nodeid

    if start_nodeid is None:
        return

    start_index = None

    for index, item in enumerate(items):
        if item.nodeid == start_nodeid:
            start_index = index
            break

    if start_index is None:
        _write_line(config, f'>>> Test {start_nodeid} not collected, starting the suite from its first test')
        return

    deselected = items[:start_index]

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        del items[:start_index]

    _write_line(config, f'>>> Resuming the suite from {start_nodeid}')

# ################################################################################################################################

def pytest_runtest_logstart(nodeid:'str', location:'tuple[str, int | None, str]') -> 'None':
    """ Records the test that is running, which the next run starts from if this run is interrupted in it.
    """
    _run_state.current = nodeid

# ################################################################################################################################

def pytest_runtest_logreport(report:'pytest.TestReport') -> 'None':
    """ Records the first test of the run that failed in its setup, its call or its teardown.
    """
    if report.failed:
        if _run_state.first_failed is None:
            _run_state.first_failed = report.nodeid

# ################################################################################################################################

def pytest_sessionfinish(session:'pytest.Session', exitstatus:'int') -> 'None':
    """ Records where the next run of the goal starts this pytest run from. A pytest run that ends in any other way,
    such as with a module that failed to import, keeps what the previous run recorded.
    """
    if not _run_state.is_active:
        return

    # A pytest run skipped in full has no tests, which is a success, and it stays recorded as completed
    if _run_state.is_skipped:
        session.exitstatus = pytest.ExitCode.OK
        return

    prefix = f'{_run_state.run_id} {_run_state.stage_id}'

    if _run_state.first_failed is not None:
        _append_entry(_run_state.state_path, f'{ModuleCtx.Entry_First} {prefix} {_run_state.first_failed}')

    elif exitstatus == pytest.ExitCode.INTERRUPTED:
        if _run_state.current is not None:
            _append_entry(_run_state.state_path, f'{ModuleCtx.Entry_First} {prefix} {_run_state.current}')

    elif exitstatus == pytest.ExitCode.OK:
        _append_entry(_run_state.state_path, f'{ModuleCtx.Entry_Done} {prefix}')

# ################################################################################################################################
# ################################################################################################################################
