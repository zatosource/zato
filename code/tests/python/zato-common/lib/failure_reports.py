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
from tempfile import gettempdir
from typing import cast

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_

    reportgen = generator_[None, pytest.TestReport, pytest.TestReport]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The file that each failure is appended to the moment it occurs, and the line that opens each failure,
    # in that file and in the output of the session
    Failures_Path = os.path.join(gettempdir(), 'zato-test-failures.txt')
    Failure_Marker = '>>> ZATO TEST FAILURE'

# ################################################################################################################################
# ################################################################################################################################

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item:'pytest.Item', call:'pytest.CallInfo[None]') -> 'reportgen':
    """ Writes the reason of a failure the moment a test fails in its setup, its call or its teardown, to the terminal
    of the session and to the failures file, rather than only in the summary at the end of the session.
    The terminal reporter of pytest writes to the original output, which the capture of pytest does not hold back.
    """
    report = yield

    if report.failed:
        timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
        text = f'\n{ModuleCtx.Failure_Marker} {timestamp} {report.nodeid} ({report.when})\n{report.longreprtext}\n'

        reporter = item.config.pluginmanager.getplugin('terminalreporter')
        reporter = cast('pytest.TerminalReporter', reporter)
        reporter.write_line(text)

        with open(ModuleCtx.Failures_Path, 'a') as failures_file:
            _ = failures_file.write(text + '\n')

    return report

# ################################################################################################################################
# ################################################################################################################################
