# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A pytest plugin, loaded with -p resume_first_failure, that runs every test of a suite and starts the next run
# of the suite from the test that failed first, or from the test that was running when the run was interrupted.
# A run that completes without a failure makes the next run start from the first test, as does --resume-reset.
# It imports nothing from Zato, because it is loaded before the suites that patch gevent.

# stdlib
from typing import cast

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The key of the pytest cache with the test that the next run of the suite starts from
    Cache_Key = 'zato/resume_first_failure'

    # The command line option that starts a run from the first test of the suite, and its destination
    Reset_Option = '--resume-reset'
    Reset_Dest = 'resume_reset'

# ################################################################################################################################
# ################################################################################################################################

class _RunState:
    """ The tests of the current run that the next run may start from.
    """
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

def pytest_configure(config:'pytest.Config') -> 'None':
    """ Rejects a run without the pytest cache, which stores the test that the next run starts from.
    """
    if not config.pluginmanager.has_plugin('cacheprovider'):
        raise Exception('Plugin resume_first_failure requires the cacheprovider plugin of pytest')

# ################################################################################################################################

def pytest_addoption(parser:'pytest.Parser') -> 'None':
    group = parser.getgroup('resume_first_failure')
    group.addoption(ModuleCtx.Reset_Option, action='store_true', dest=ModuleCtx.Reset_Dest,
        help='Start the suite from its first test instead of the test that failed first in the previous run')

# ################################################################################################################################

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config:'pytest.Config', items:'list[pytest.Item]') -> 'None':
    """ Deselects the tests that precede the test that the previous run failed first in or was interrupted in.
    """
    cache = config.cache

    if config.getoption(ModuleCtx.Reset_Dest):
        _write_line(config, '>>> Starting the suite from its first test')
        return

    start_nodeid = cache.get(ModuleCtx.Cache_Key, None)

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
    """ Stores the test that the next run starts from. A run that ends in any other way, such as with a module
    that failed to import, keeps the test that the previous run stored.
    """
    cache = session.config.cache

    if _run_state.first_failed is not None:
        cache.set(ModuleCtx.Cache_Key, _run_state.first_failed)

    elif exitstatus == pytest.ExitCode.INTERRUPTED:
        if _run_state.current is not None:
            cache.set(ModuleCtx.Cache_Key, _run_state.current)

    elif exitstatus == pytest.ExitCode.OK:
        cache.set(ModuleCtx.Cache_Key, None)

# ################################################################################################################################
# ################################################################################################################################
