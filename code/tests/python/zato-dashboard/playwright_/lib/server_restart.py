# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import tempfile
import time
from http.client import OK
from urllib.request import Request, urlopen

# Zato
from zato.common.test.process_util import kill_process_tree

# The conftest's atexit cleanup reads this dict, so handing the new process over here means it will be killed at exit
from cleanup_refs import cleanup_refs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

# How long to wait for the restarted server to answer pings
_Restart_Timeout = 180

# How often the orphan watchdog checks whether the test process is still alive
_Watchdog_Interval_Seconds = 5

# ################################################################################################################################
# ################################################################################################################################

def start_orphan_watchdog(watched_pid:'int', server_group_pid:'int') -> 'None':
    """ Starts a detached watchdog that kills the restarted server's process group once the
    test process is gone. The atexit cleanup never runs when pytest is killed hard, and the
    restarted server is detached, so without the watchdog it would run forever,
    filling its log file in /tmp without bounds.
    """
    watchdog_script = (
        f'while kill -0 {watched_pid} 2>/dev/null; do sleep {_Watchdog_Interval_Seconds}; done; '
        f'kill -- -{server_group_pid} 2>/dev/null'
    )
    _ = subprocess.Popen(['/bin/sh', '-c', watchdog_script], start_new_session=True)

# ################################################################################################################################
# ################################################################################################################################

def read_process_environment(pid:'int') -> 'dict':
    """ Reads the environment of a running process so the restarted one gets the same variables,
    including the dynamic ports the fixture chose at startup.
    """
    with open(f'/proc/{pid}/environ', 'rb') as environ_file:
        raw = environ_file.read()

    out = {} # type: dict

    for entry in raw.decode('utf8', errors='replace').split('\0'):
        if '=' in entry:
            key, _, value = entry.partition('=')
            out[key] = value

    return out

# ################################################################################################################################

def restart_server(zato_dashboard:'anydict') -> 'None':
    """ Stops the server subprocess and starts a new one with the same environment,
    then waits until it answers pings again.
    """
    server_process = zato_dashboard['server_process']
    server_dir = zato_dashboard['server_dir']
    server_port = zato_dashboard['server_port']
    host = zato_dashboard['host']

    # Capture the environment before the process goes away ..
    server_environment = read_process_environment(server_process.pid)

    # .. stop the server along with its whole process group - terminating just
    # the launcher would leave the actual server running and holding the port ..
    kill_process_tree(server_process)

    # .. start a new one with the same environment ..
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    restarted_log_path = os.path.join(tempfile.gettempdir(), f'zato_restarted_server_{server_port}.log')
    restarted_log_file = open(restarted_log_path, 'wb')

    new_process = subprocess.Popen(
        [zato_bin, 'start', server_dir, '--fg'],
        env=server_environment,
        stdout=restarted_log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    logger.info('[restart_server] started new server pid=%s port=%s stdout=%r',
        new_process.pid, server_port, restarted_log_path)

    # .. hand the new process over to the conftest so its cleanup kills it at exit ..
    zato_dashboard['server_process'] = new_process
    cleanup_refs['server_process'] = new_process

    # .. and arm the watchdog that reaps the server if this test process dies
    # without running its atexit cleanup.
    start_orphan_watchdog(os.getpid(), new_process.pid)

    # .. and wait until the server answers pings again.
    # .. The browser is intentionally idle during this wait, the server is restarting ..
    logger.info('The server was stopped on purpose, waiting up to %ss for it to come back after the restart', _Restart_Timeout)

    url = f'http://{host}:{server_port}/zato/ping'
    deadline = time.monotonic() + _Restart_Timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == OK:
                    return
        except Exception:
            time.sleep(1)

    raise RuntimeError(f'The server did not come back within {_Restart_Timeout}s after the restart')

# ################################################################################################################################
# ################################################################################################################################
