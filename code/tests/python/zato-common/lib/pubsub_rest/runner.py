# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess
import sys
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.test.conftest_base_pubsub import get_process_environment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.monitor import Monitor
    from zato.common.typing_ import callable_, strstrdict

    process = subprocess.Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

# The cleanup process of pub/sub, started as an installation starts it, sweeping as often as its schedule does, in seconds.
_cleanup_module = 'zato.common.pubsub.sql.cleanup'
_cleanup_interval_seconds = 300

# How long the cleanup process may take to stop after it was asked to, in seconds.
_cleanup_stop_timeout = 120

# How often a run checks whether it is done, in seconds.
_tick_seconds = 1

# ################################################################################################################################
# ################################################################################################################################

def get_duration(env_name:'str', default_seconds:'int') -> 'int':
    """ How long a suite runs, which the given variable may override, in seconds.
    """
    if value := os.environ.get(env_name, ''):
        out = int(value)
    else:
        out = default_seconds

    return out

# ################################################################################################################################

def run_for(
    monitor:'Monitor',
    duration_seconds:'float',
    on_tick:'callable_ | None' = None,
    is_done:'callable_ | None' = None,
    is_done_interval:'float' = 1.0,
    ) -> 'None':
    """ Lets the traffic run for the given time, calling on_tick with the elapsed seconds once a second,
    and stops early when the disk runs low or when is_done, called every is_done_interval seconds, returns True.
    """
    start = monotonic()
    next_is_done = start + is_done_interval

    while True:
        now = monotonic()
        elapsed = now - start

        if elapsed >= duration_seconds or monitor.is_disk_low:
            break

        if is_done and now >= next_is_done:
            if is_done():
                break
            next_is_done = now + is_done_interval

        if on_tick:
            on_tick(elapsed)

        sleep(_tick_seconds)

# ################################################################################################################################

def start_cleanup_process(extra_env:'strstrdict | None'=None) -> 'process':
    """ Starts the cleanup process against the database of the server, with the environment of a process
    of an installation, to which the given variables are added.
    """
    env = get_process_environment()

    if extra_env:
        env.update(extra_env)

    command = [sys.executable, '-m', _cleanup_module, '--interval', str(_cleanup_interval_seconds)]

    out = subprocess.Popen(command, env=env)
    return out

# ################################################################################################################################

def run_cleanup_once() -> 'None':
    """ Runs one sweep of the cleanup process, as the scheduled job of an installation runs it.
    """
    command = [sys.executable, '-m', _cleanup_module, '--once']
    _ = subprocess.run(command, env=get_process_environment(), check=True)

# ################################################################################################################################

def stop_cleanup_process(cleanup:'process') -> 'None':
    cleanup.send_signal(signal.SIGTERM)
    _ = cleanup.wait(timeout=_cleanup_stop_timeout)

# ################################################################################################################################
# ################################################################################################################################
