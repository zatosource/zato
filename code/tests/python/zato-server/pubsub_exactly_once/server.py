# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess
import time

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port, start_server_process, wait_for_server
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import release
from zato.common.test.process_util import get_process_tree_pids
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

# The process name of the worker of a server
_worker_process_name = 'zato-worker'

# The process ID returned when the server has no worker
_no_worker_pid = 0

# How long the arbiter is given to start a new worker, in seconds
Worker_Timeout = 120.0

# How long a stopped server is given to exit, in seconds
_stop_timeout = 120

# How often the processes of the server are looked at, in seconds
_poll_seconds = 0.2

# The time between the request to stop the server and the release of the held key, in seconds
_stop_release_delay = 1.0

# The address that the server listens on
_server_host = '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

def _get_server_process() -> 'Popen[bytes]':
    """ Returns the process that started the server of the session, which a running server always has.
    """
    out = cast_('Popen[bytes]', TestConfig.session_state.server_process)
    return out

# ################################################################################################################################

def get_server_pids() -> 'intlist':
    """ Returns the processes of the server of the session, which descend from the process that started it.
    """
    server_process = _get_server_process()

    out = get_process_tree_pids(server_process.pid)
    return out

# ################################################################################################################################

def _get_worker_pid() -> 'int':
    """ Returns the process ID of the worker of the server, or zero if the server has no worker.
    """
    server_pids = get_server_pids()

    for pid in server_pids:

        try:
            with open(f'/proc/{pid}/comm') as process_name_file:
                process_name = process_name_file.read()
        except FileNotFoundError:
            continue

        process_name = process_name.strip()

        if process_name == _worker_process_name:
            out = pid
            break

    else:
        out = _no_worker_pid

    return out

# ################################################################################################################################

def find_worker_pid() -> 'int':
    """ Returns the process ID of the worker of the server.
    """
    out = _get_worker_pid()

    if out == _no_worker_pid:
        raise Exception('No worker process of the server found')

    return out

# ################################################################################################################################

def kill_worker() -> 'None':
    """ Kills the worker of the server with SIGKILL and waits until the arbiter has started a new one that responds.
    """
    old_pid = find_worker_pid()
    os.kill(old_pid, signal.SIGKILL)

    deadline = time.monotonic() + Worker_Timeout

    # Wait for a worker with another process ID ..
    while True:

        if time.monotonic() > deadline:
            raise Exception(f'No new worker within {Worker_Timeout}s')

        new_pid = _get_worker_pid()

        if new_pid != _no_worker_pid:
            if new_pid != old_pid:
                break

        time.sleep(_poll_seconds)

    # .. and until it responds.
    wait_for_server(TestConfig.logger, _server_host, TestConfig.server_port)

# ################################################################################################################################

def start_server() -> 'None':
    """ Starts the server of the session again and waits until its worker is ready.
    """
    broker_port = find_free_port()

    _ = start_server_process(
        state=TestConfig.session_state,
        logger=TestConfig.logger,
        zato_bin=TestConfig.zato_bin,
        server_directory=TestConfig.server_directory,
        server_port=TestConfig.server_port,
        broker_port=broker_port,
        extra_server_env=TestConfig.extra_server_env,
        patch_server_conf_bind=True,
    )

# ################################################################################################################################

def stop_server_releasing(key:'str') -> 'None':
    """ Stops the server with `zato stop`, releases the held key while the server drains its deliveries,
    and waits until the server has exited.
    """
    command = [TestConfig.zato_bin, 'stop', TestConfig.server_directory]
    stop_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # The held invocation is released only after the server has been told to stop ..
    time.sleep(_stop_release_delay)
    release(key)

    # .. and the test continues once the server has exited.
    _ = stop_process.wait(timeout=_stop_timeout)

    server_process = _get_server_process()
    _ = server_process.wait(timeout=_stop_timeout)

# ################################################################################################################################

def kill_server() -> 'None':
    """ Kills the arbiter and the worker of the server with SIGKILL.
    """
    server_process = _get_server_process()
    server_pids = get_server_pids()

    for pid in server_pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    _ = server_process.wait(timeout=_stop_timeout)

# ################################################################################################################################
# ################################################################################################################################
