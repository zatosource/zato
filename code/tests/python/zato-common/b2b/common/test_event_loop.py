# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys

# gevent
from gevent import joinall, sleep, spawn
from gevent.monkey import get_original

# psutil
from psutil import Process

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from gevent_monitor import get_monitor, Lag_Interval
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.db_env.engine import needs_thread_pool
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import new_identity, new_memory_engine, new_stored_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from gevent import Greenlet
    Greenlet = Greenlet
    Path = Path

greenlet_list = list['Greenlet']

# ################################################################################################################################
# ################################################################################################################################

_native_sleep = get_original('time', 'sleep')

# How long a greenlet holds the event loop without yielding, in seconds.
_blocking_seconds = 0.3

# How long a shorter blocking holds the event loop, in seconds, so that the lag greenlet wakes up late.
_short_blocking_seconds = 0.2

# How long the cooperative greenlets run, in seconds - longer than two sample intervals,
# so that at least one interval lies entirely within the window.
_cooperative_seconds = 2.5

# How many cooperative greenlets run, and how long each of them sleeps between two switches, in seconds.
_cooperative_count = 5
_cooperative_sleep = 0.005

# The switches per second the cooperative greenlets make at least.
_min_switch_rate = 500

# How long the cooperative greenlets run before one of them blocks the event loop, in seconds.
_blocker_delay = 1.0

# The network databases, whose drivers yield to the event loop - no connection is opened to them.
_network_urls = (
    'mysql+pymysql://zato:password@localhost/zato',
    'postgresql+pg8000://zato:password@localhost/zato',
)

# The directory with the test library that the monitor is part of.
_lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

# The conftest and the tests of a run under the monitor in a process of its own.
_monitored_conftest = """
from gevent import monkey
_ = monkey.patch_all()

from gevent_monitor import pytest_pyfunc_call as pytest_pyfunc_call
"""

_monitored_tests = """
from gevent import sleep, spawn
from gevent.monkey import get_original

_native_sleep = get_original('time', 'sleep')

def hold_event_loop():
    _native_sleep(0.3)

def test_blocking():
    spawn(hold_event_loop).join()

def test_cooperative():
    sleep(0.3)
"""

# ################################################################################################################################
# ################################################################################################################################

def _hold_event_loop() -> 'None':
    _native_sleep(_blocking_seconds)

# ################################################################################################################################

def _hold_event_loop_briefly() -> 'None':
    _native_sleep(_short_blocking_seconds)

# ################################################################################################################################

def _cooperate() -> 'None':
    iterations = int(_cooperative_seconds / _cooperative_sleep)

    for _ in range(iterations):
        sleep(_cooperative_sleep)

# ################################################################################################################################
# ################################################################################################################################

class TestWriterUnderGevent:
    """ Under gevent, the commit loop of the writer is a greenlet and adds no thread of the operating system.
    """

    def test_commit_loop(self) -> 'None':
        process = Process()
        engine = new_memory_engine()

        threads_before = process.num_threads()
        writer = GroupCommitWriter(engine, interval_ms=0)
        threads_after = process.num_threads()

        store = MessageStore(writer)
        is_claimed = store.claim(new_identity('message-1'), new_stored_message())

        writer.stop()

        assert threads_after == threads_before
        assert is_claimed

    def test_thread_pool(self) -> 'None':
        """ Only the calls of SQLite, whose driver does not yield, run in the thread pool of the hub.
        """
        sqlite_engine = new_memory_engine()

        assert needs_thread_pool(sqlite_engine)

        for url in _network_urls:
            engine = create_engine(url)
            assert not needs_thread_pool(engine)

# ################################################################################################################################
# ################################################################################################################################

class TestEventLoopMonitor:
    """ The monitor records each greenlet run that blocks the event loop, the lag of the loop, the switch rate
    and the live greenlets, and a test that blocks the loop fails with the stack of the blocking greenlet.
    """

    def test_blocking(self) -> 'None':
        monitor = get_monitor()
        monitor.begin()

        worker = spawn(_hold_event_loop)
        _ = worker.join()

        summary = monitor.end()

        # A new window begins, so that the blocking this test causes is not reported for the test itself.
        monitor.begin()

        assert len(summary.blockings) == 1

        blocking = summary.blockings[0]

        assert blocking.duration >= _blocking_seconds
        assert ', in _hold_event_loop\n' in blocking.stack

    def test_lag_and_switches(self) -> 'None':
        monitor = get_monitor()
        monitor.begin()

        workers:'greenlet_list' = []

        for _ in range(_cooperative_count):
            worker = spawn(_cooperate)
            workers.append(worker)

        sleep(_blocker_delay)

        blocker = spawn(_hold_event_loop_briefly)
        workers.append(blocker)

        _ = joinall(workers)

        summary = monitor.end()

        # A new window begins, so that the blocking this test causes is not reported for the test itself.
        monitor.begin()

        assert len(summary.blockings) == 1
        assert summary.lag_p50 < Lag_Interval
        assert summary.lag_max >= _short_blocking_seconds - Lag_Interval
        assert summary.switches_per_second >= _min_switch_rate
        assert summary.greenlets_max >= _cooperative_count

    def test_failure_report(self, tmp_path:'Path') -> 'None':

        conftest_path = tmp_path / 'conftest.py'
        tests_path = tmp_path / 'test_monitored.py'

        _ = conftest_path.write_text(_monitored_conftest)
        _ = tests_path.write_text(_monitored_tests)

        env = dict(os.environ)
        env['PYTHONPATH'] = _lib_dir

        command = [sys.executable, '-m', 'gevent.monkey', '--module', 'pytest', str(tmp_path), '-q',
            '-p', 'no:cacheprovider', '-p', 'no:randomly']

        result = subprocess.run(command, capture_output=True, text=True, env=env, cwd=tmp_path)

        assert result.returncode == 1
        assert '1 failed, 1 passed' in result.stdout
        assert 'test_monitored.py::test_blocking' in result.stdout
        assert 'The event loop was blocked 1 time for longer than 100 ms' in result.stdout
        assert ', in hold_event_loop\n' in result.stdout

# ################################################################################################################################
# ################################################################################################################################
