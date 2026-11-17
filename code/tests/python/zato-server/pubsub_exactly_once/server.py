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
from zato.common.test.conftest_base_pubsub import find_free_port, get_server_pids, kill_server_worker, \
    start_server_process
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import release
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen

# ################################################################################################################################
# ################################################################################################################################

# How long a stopped server is given to exit, in seconds
_stop_timeout = 120

# The time between the request to stop the server and the release of the held key, in seconds
_stop_release_delay = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _get_server_process() -> 'Popen[bytes]':
    """ Returns the process that started the server of the session, which a running server always has.
    """
    out = cast_('Popen[bytes]', TestConfig.session_state.server_process)
    return out

# ################################################################################################################################

def kill_worker() -> 'None':
    """ Kills the worker of the server with SIGKILL and waits until the arbiter has started a new one that responds.
    """
    kill_server_worker(TestConfig.logger, TestConfig.session_state, TestConfig.server_port)

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
    server_pids = get_server_pids(TestConfig.session_state)

    for pid in server_pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    _ = server_process.wait(timeout=_stop_timeout)

# ################################################################################################################################
# ################################################################################################################################
