# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import threading
from collections import Counter
from datetime import datetime
from tempfile import gettempdir
from typing import cast

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_, strlist

    nonegen = generator_[None, None, None]
    reportgen = generator_[None, pytest.TestReport, pytest.TestReport]
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The modules whose process-wide state owns background threads, each with the function that stops them. The modules
    # are imported by the tests that use them, not by this conftest, which is loaded before the suites that patch gevent
    # before anything else is imported.
    Stop_Functions = (
        ('zato.common.db_env.engine', 'dispose_cached_engines'),
        ('zato.common.util.memory_trim', 'stop_memory_trimmer'),
        ('zato.common.audit_log.search_index_merge', 'stop_search_index_merger'),
        ('zato.common.audit_log.retention_runner', 'stop_retention_runner'),
    )

    # How long a thread that remains after a test may take to end, in seconds, such as a thread of a receiver
    # of the session that answers a delivery in flight when the test ends
    Thread_End_Timeout = 5.0

    # The file that each failure is appended to the moment it occurs, and the line that opens each failure,
    # in that file and in the output of the session
    Failures_Path = os.path.join(gettempdir(), 'zato-test-failures.txt')
    Failure_Marker = '>>> ZATO TEST FAILURE'

# ################################################################################################################################
# ################################################################################################################################

def _stop_process_wide_threads() -> 'None':
    """ Disposes every cached engine of this process, which stops the background WAL checkpointers, and stops
    the memory trimmer that the pub/sub backend starts, the flushers, the retention runner and the merger of the search indexes
    of the audit log, and the worker threads of the thread pool of the gevent hub.
    """
    for module_name, function_name in ModuleCtx.Stop_Functions:
        if module := sys.modules.get(module_name):
            stop = getattr(module, function_name)
            stop()

    # The worker threads of the thread pool of the gevent hub end as well, and the pool starts new ones when it is next used
    if hub_local := sys.modules.get('gevent._hub_local'):
        if hub := hub_local.get_hub_if_exists():
            hub.threadpool.size = 0

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

@pytest.fixture(autouse=True)
def no_thread_outlives_its_test() -> 'nonegen':
    """ Fails a test that leaves a thread running in this process. Later tests fork workers from this process,
    and a forked worker inherits in their locked state the locks that such a thread holds at the time of the fork.
    The threads of the engines and of the memory trimmer that the test started are stopped first,
    and a test that needs an engine again receives a new one. Threads are compared by name, so a test that stops
    a thread of its session and starts it again under the same name leaves nothing behind.
    """
    threads_before = Counter(thread.name for thread in threading.enumerate())

    yield

    _stop_process_wide_threads()

    threads_after = Counter(thread.name for thread in threading.enumerate())
    remaining = threads_after - threads_before

    # A thread that ends shortly after the test is not left behind
    for thread in threading.enumerate():
        if thread.name in remaining:
            thread.join(ModuleCtx.Thread_End_Timeout)

    threads_after = Counter(thread.name for thread in threading.enumerate())

    remaining_names:'strlist' = sorted((threads_after - threads_before).elements())

    assert remaining_names == []

# ################################################################################################################################
# ################################################################################################################################
