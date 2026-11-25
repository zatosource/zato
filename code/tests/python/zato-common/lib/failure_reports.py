# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A pytest plugin, loaded by the root conftest of the Zato tests and with -p failure_reports by the suites
# of linked repositories. It imports nothing from Zato, because it is loaded before the suites that patch gevent.

# stdlib
import os
from datetime import datetime
from typing import cast

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_

    collectgen = generator_[None, pytest.CollectReport, pytest.CollectReport]
    reportgen = generator_[None, pytest.TestReport, pytest.TestReport]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The file that each failure is appended to the moment it occurs, and the line that opens each failure,
    # in that file and in the output of the session. The path is fixed rather than taken from the temporary directory,
    # which the root conftest moves for the processes that the tests start, because recipe_shell.sh of the Makefile
    # appends the failures of the recipe lines to the same file.
    Failures_Path = '/tmp/zato-test-failures.txt'
    Failure_Marker = '>>> ZATO TEST FAILURE'

    # The environment variables through which zato.common.test.kept_dirs learns of the failures of the session,
    # to keep the directories of the environments that the failed tests ran in
    Env_Failure_Count = 'Zato_Test_Failure_Count'
    Env_Failures_Path = 'Zato_Test_Failures_Path'

    # The number of failures of the session so far
    failure_count = 0

# ################################################################################################################################
# ################################################################################################################################

def pytest_configure(config:'pytest.Config') -> 'None':
    """ Makes the failures file known to the directories of the test environments, which name themselves in it when kept.
    """
    os.environ[ModuleCtx.Env_Failures_Path] = ModuleCtx.Failures_Path

# ################################################################################################################################

def _report_failure(config:'pytest.Config', name:'str', longreprtext:'str') -> 'None':
    """ Writes the reason of a failure to the terminal of the session and appends it to the failures file.
    The terminal reporter of pytest writes to the original output, which the capture of pytest does not hold back.
    """
    ModuleCtx.failure_count += 1
    os.environ[ModuleCtx.Env_Failure_Count] = str(ModuleCtx.failure_count)

    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
    text = f'\n{ModuleCtx.Failure_Marker} {timestamp} {name}\n{longreprtext}\n'

    reporter = config.pluginmanager.getplugin('terminalreporter')
    reporter = cast('pytest.TerminalReporter', reporter)
    reporter.write_line(text)

    with open(ModuleCtx.Failures_Path, 'a') as failures_file:
        _ = failures_file.write(text + '\n')

# ################################################################################################################################

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item:'pytest.Item', call:'pytest.CallInfo[None]') -> 'reportgen':
    """ Reports a failure the moment a test fails in its setup, its call or its teardown,
    rather than only in the summary at the end of the session.
    """
    report = yield

    if report.failed:
        _report_failure(item.config, f'{report.nodeid} ({report.when})', report.longreprtext)

    return report

# ################################################################################################################################

@pytest.hookimpl(wrapper=True)
def pytest_make_collect_report(collector:'pytest.Collector') -> 'collectgen':
    """ Reports a module that could not be collected, such as one that fails to import, the moment it happens.
    """
    report = yield

    if report.failed:
        _report_failure(collector.config, f'{report.nodeid} (collection)', report.longreprtext)

    return report

# ################################################################################################################################
# ################################################################################################################################
