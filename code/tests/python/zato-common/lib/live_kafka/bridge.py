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
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, IO

# Zato
from live_environment.quickstart import Host
from zato.common.test.conftest_base_pubsub import Expected_Record_Marker
from zato.common.test.process_util import kill_process_tree
from zato.common.test.reservation import PortInUse, reserve_port, start_on_reserved_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import PortReservation
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

popen_  = subprocess.Popen[bytes]
nonegen = Generator[None, None, None]

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

    # The variable name both the server and the bridge read the port of the bridge's HTTP query API from
    Bridge_Port_Variable = 'Zato_Queue_Bridge_Port'

    # The purposes of the port reservations of Redis and of the bridge's HTTP query API
    Redis_Port_Purpose       = 'kafka-bridge-redis'
    Bridge_HTTP_Port_Purpose = 'kafka-bridge-http'

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
    """ The Redis and the bridge a suite started, the ports they hold, and the environment its server needs to find them.
    """

    def __init__(
        self,
        redis_reservation:'PortReservation',
        http_reservation:'PortReservation',
        redis:'ProcessPart',
        bridge:'ProcessPart',
        is_expected:'threading.Event',
        ) -> 'None':
        self.redis_reservation = redis_reservation
        self.http_reservation = http_reservation
        self.redis_port = redis_reservation.port
        self.http_port = http_reservation.port
        self.redis = redis
        self.bridge = bridge
        self.is_expected = is_expected

    @property
    def server_environment(self) -> 'strstrdict':
        out = {
            ModuleCtx.Bridge_Redis_Port_Variable: str(self.redis_port),
            ModuleCtx.Bridge_Port_Variable: str(self.http_port),
        }
        return out

    def restart_bridge(self) -> 'None':
        """ Ends the bridge and starts it again on the same Redis - what a bridge restart in production is.
        """
        self.bridge.stop()
        self.bridge = ProcessPart(start_bridge(self.redis_port, self.http_port, self.is_expected))

    @contextmanager
    def expected_errors(self) -> 'nonegen':
        """ Marks each line of the output of the bridge as expected while the block runs,
        for a test that makes the bridge report errors deliberately, e.g. by stopping Kafka.
        """
        self.is_expected.set()

        try:
            yield
        finally:
            self.is_expected.clear()

    def stop_redis(self) -> 'None':
        """ Ends Redis and releases its port.
        """
        self.redis.stop()
        self.redis_reservation.release()

    def stop_bridge(self) -> 'None':
        """ Ends the bridge and releases the port of its HTTP query API.
        """
        self.bridge.stop()
        self.http_reservation.release()

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_tcp_port(port:'int', process:'popen_') -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after the timeout. Raises PortInUse
    when the process listening on it exits first, which is what Redis does when it cannot bind the port.
    """
    deadline = time.monotonic() + ModuleCtx.Redis_Wait_Timeout
    address = (Host, port)

    while time.monotonic() < deadline:

        if process.poll() is not None:
            raise PortInUse(f'Process exited with code {process.returncode} before port {port} accepted connections')

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
    _wait_for_tcp_port(port, out)

    return out

# ################################################################################################################################

def _relay_output(process:'popen_', is_expected:'threading.Event') -> 'None':
    """ Writes each line of the output of the bridge to the output of the tests, with the expected record marker
    while a test makes the bridge report errors deliberately.
    """
    stdout = cast_('IO[bytes]', process.stdout)

    for line in iter(stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()

        if is_expected.is_set():
            text = f'{Expected_Record_Marker} {text}'

        print(text, flush=True)

# ################################################################################################################################

def start_bridge(redis_port:'int', http_port:'int', is_expected:'threading.Event') -> 'popen_':
    """ Starts the queue bridge binary pointed at the test Redis, with its HTTP query API on the given port,
    and relays its output to the output of the tests.
    """
    env = dict(os.environ)
    env[ModuleCtx.Bridge_Redis_Port_Variable] = str(redis_port)
    env[ModuleCtx.Bridge_Port_Variable] = str(http_port)

    out = subprocess.Popen(
        [str(ModuleCtx.Bridge_Binary)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    relay = threading.Thread(target=_relay_output, args=(out, is_expected), daemon=True)
    relay.start()

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
    """ Starts a Redis on a reserved port and the bridge on it, with its HTTP query API on another reserved port.
    """
    # Redis binds its port as it starts, so a port taken by a process that does not reserve ports is replaced ..
    redis_started = start_on_reserved_port(ModuleCtx.Redis_Port_Purpose, start_redis)
    redis = ProcessPart(redis_started.result)

    # .. while the bridge binds its HTTP query API only after the server's first reload, so its port is reserved up front.
    http_reservation = reserve_port(ModuleCtx.Bridge_HTTP_Port_Purpose)
    is_expected = threading.Event()
    bridge = ProcessPart(start_bridge(redis_started.reservation.port, http_reservation.port, is_expected))

    out = BridgeParts(redis_started.reservation, http_reservation, redis, bridge, is_expected)
    return out

# ################################################################################################################################
# ################################################################################################################################
