# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue bridge a Kafka suite runs next to its server - a throwaway Redis and the bridge binary pointed at it.

# stdlib
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

# Zato
from live_environment.quickstart import find_free_port, Host
from zato.common.test.process_util import kill_process_tree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

popen_ = subprocess.Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The bridge binary, relative to the repository root the tests are run from
    Bridge_Binary = Path(os.environ['ZATO_TEST_BASE_DIR']) / 'code' / 'bin' / '_zato_queue_bridge'

    # How long a freshly started Redis has to open its port
    Redis_Wait_Timeout  = 30
    Redis_Poll_Interval = 0.2
    Connect_Timeout     = 1

    # The variable name both the server and the bridge read the Redis port from
    Bridge_Redis_Port_Variable = 'Zato_Queue_Bridge_Redis_Port'

# ################################################################################################################################
# ################################################################################################################################

class ProcessPart:
    """ One started process, stopped along with everything it spawned.
    """

    def __init__(self, process:'popen_') -> 'None':
        self.process = process

    def stop(self) -> 'None':
        kill_process_tree(self.process)

# ################################################################################################################################
# ################################################################################################################################

class BridgeParts:
    """ The Redis and the bridge a suite started, and the environment its server needs to find them.
    """

    def __init__(self, redis_port:'int', redis:'ProcessPart', bridge:'ProcessPart') -> 'None':
        self.redis_port = redis_port
        self.redis = redis
        self.bridge = bridge

    @property
    def server_environment(self) -> 'strstrdict':
        out = {ModuleCtx.Bridge_Redis_Port_Variable: str(self.redis_port)}
        return out

    def restart_bridge(self) -> 'None':
        """ Ends the bridge and starts it again on the same Redis - what a bridge restart in production is.
        """
        self.bridge.stop()
        self.bridge = ProcessPart(start_bridge(self.redis_port))

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_tcp_port(port:'int') -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after the timeout.
    """
    deadline = time.monotonic() + ModuleCtx.Redis_Wait_Timeout
    address = (Host, port)

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(address, timeout=ModuleCtx.Connect_Timeout):
                return
        except OSError:
            time.sleep(ModuleCtx.Redis_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {ModuleCtx.Redis_Wait_Timeout}s')

# ################################################################################################################################

def start_redis(port:'int') -> 'popen_':
    """ Starts a throwaway Redis with no persistence in its own session.
    """
    command = ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no']
    out = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    _wait_for_tcp_port(port)

    return out

# ################################################################################################################################

def start_bridge(redis_port:'int') -> 'popen_':
    """ Starts the queue bridge binary pointed at the test Redis.
    """
    env = dict(os.environ)
    env[ModuleCtx.Bridge_Redis_Port_Variable] = str(redis_port)

    out = subprocess.Popen([str(ModuleCtx.Bridge_Binary)], env=env, start_new_session=True)
    return out

# ################################################################################################################################

def local_requirements() -> 'strlist':
    """ What this machine lacks for the bridge to run.
    """
    out:'strlist' = []

    if not shutil.which('redis-server'):
        out.append('redis-server is not installed')

    if not ModuleCtx.Bridge_Binary.exists():
        out.append(f'Bridge binary {ModuleCtx.Bridge_Binary} is missing')

    return out

# ################################################################################################################################

def start_bridge_parts() -> 'BridgeParts':
    """ Starts a Redis on a free port and the bridge on it.
    """
    redis_port = find_free_port()
    redis = ProcessPart(start_redis(redis_port))
    bridge = ProcessPart(start_bridge(redis_port))

    out = BridgeParts(redis_port, redis, bridge)
    return out

# ################################################################################################################################
# ################################################################################################################################
