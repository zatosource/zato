# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.process_util import kill_process_tree

# Live environment
from live_environment.parts import Parts, skip_or_fail, tear_down
from live_environment.quickstart import find_free_port, Host, ZatoEnvironment

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx
from live_fabric.state import describe, missing_requirements

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_fabric.state import FabricEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import iterator_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

popen_ = subprocess.Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The connection with valid credentials
    Connection_Name = 'test.fabric.main'

    # The connection whose client secret the token endpoint rejects
    Bad_Credentials_Connection_Name = 'test.fabric.bad-credentials'

    # The bridge binary, relative to the repository root the tests are run from
    Bridge_Binary = Path(os.environ['ZATO_TEST_BASE_DIR']) / 'code' / 'bin' / '_zato_queue_bridge'

    # The services the tests drive and the connections they use
    Services_File = Path(__file__).parent / '_services.py'
    Template_File = Path(__file__).parent / '_enmasse_template.yaml'

    # How long a freshly started Redis has to open its port
    Redis_Wait_Timeout  = 30
    Redis_Poll_Interval = 0.2
    Connect_Timeout     = 1

    # The variable name both the server and the bridge read the Redis port from
    Bridge_Redis_Port_Variable = 'Zato_Queue_Bridge_Redis_Port'

    # The service whose answer tells the deployed services are in place
    Ping_Service = 'test.fabric.ping'

    # How long the deployed services have to appear
    Deploy_Timeout       = 60
    Deploy_Poll_Interval = 1

# ################################################################################################################################
# ################################################################################################################################

class FabricLiveEnvironment(NamedTuple):
    """ Everything a test case needs - the server to invoke and the Fabric environment to reach.
    """
    zato: 'ZatoEnvironment'
    fabric: 'FabricEnvironment'

# ################################################################################################################################
# ################################################################################################################################

class ProcessPart:
    """ One started process, stopped along with everything it spawned.
    """

    def __init__(self, process:'popen_') -> 'None':
        self.process = process

# ################################################################################################################################

    def stop(self) -> 'None':
        kill_process_tree(self.process)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_tcp_port(port:'int') -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after the timeout.
    """
    now = time.monotonic()
    deadline = now + ModuleCtx.Redis_Wait_Timeout
    address = (Host, port)

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(address, timeout=ModuleCtx.Connect_Timeout):
                return
        except OSError:
            time.sleep(ModuleCtx.Redis_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {ModuleCtx.Redis_Wait_Timeout}s')

# ################################################################################################################################

def _start_redis(port:'int') -> 'popen_':
    """ Starts a throwaway Redis with no persistence in its own session.
    """
    command = ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no']
    out = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    _wait_for_tcp_port(port)

    return out

# ################################################################################################################################

def _start_bridge(env:'strstrdict') -> 'popen_':
    """ Starts the queue bridge binary pointed at the test Redis.
    """
    command = [str(ModuleCtx.Bridge_Binary)]

    out = subprocess.Popen(command, env=env, start_new_session=True)
    return out

# ################################################################################################################################

def _local_requirements() -> 'strlist':
    """ What this machine lacks besides the Fabric side.
    """
    out:'strlist' = []

    if not shutil.which('redis-server'):
        out.append('redis-server is not installed')

    if not ModuleCtx.Bridge_Binary.exists():
        out.append(f'Bridge binary {ModuleCtx.Bridge_Binary} is missing')

    return out

# ################################################################################################################################

def _render_template(fabric:'FabricEnvironment') -> 'str':
    """ The connections under test, with the real credentials and one wrong secret.
    """
    template = ModuleCtx.Template_File.read_text()

    invalid_client_secret = 'test.invalid.secret.' + CryptoManager.generate_hex_string()

    out = template.format(
        connection_name=ModuleCtx.Connection_Name,
        bad_credentials_connection_name=ModuleCtx.Bad_Credentials_Connection_Name,
        tenant_id=fabric.tenant_id,
        client_id=fabric.client_id,
        client_secret=fabric.client_secret,
        invalid_client_secret=invalid_client_secret,
    )

    return out

# ################################################################################################################################

def _wait_until_deployed(client:'AdminClient') -> 'None':
    """ Waits for the hot-deployed services to answer.
    """
    now = time.monotonic()
    deadline = now + ModuleCtx.Deploy_Timeout
    request = {'conn_name': ModuleCtx.Connection_Name}

    while time.monotonic() < deadline:
        try:
            _ = client.invoke(ModuleCtx.Ping_Service, request)
        except Exception:
            time.sleep(ModuleCtx.Deploy_Poll_Interval)
        else:
            return

    raise Exception(f'The test services did not deploy within {ModuleCtx.Deploy_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def fabric_live() -> 'iterator_':
    """ One Redis, one queue bridge and one Zato server for the whole session.
    """
    # Skip or fail when anything the suite needs is missing ..
    missing_fabric = missing_requirements()
    missing_local = _local_requirements()
    missing = missing_fabric + missing_local
    skip_or_fail(missing, FabricCtx.Required_Variable)

    parts = Parts()

    try:
        # .. read what the setup recorded ..
        fabric = describe()

        # .. start Redis ..
        redis_port = find_free_port()
        redis_port_text = str(redis_port)
        redis_process = _start_redis(redis_port)
        redis_part = ProcessPart(redis_process)
        parts.add('redis-server', redis_part.stop)

        # .. start the bridge pointed at it ..
        bridge_env = dict(os.environ)
        bridge_env[ModuleCtx.Bridge_Redis_Port_Variable] = redis_port_text
        bridge_process = _start_bridge(bridge_env)
        bridge_part = ProcessPart(bridge_process)
        parts.add('queue bridge', bridge_part.stop)

        # .. start the server pointed at the same Redis ..
        directory = tempfile.mkdtemp(prefix='zato_fabric_live_')
        zato = ZatoEnvironment(directory, password_prefix='test.fabric')
        parts.add('zato environment', zato.stop)
        zato.create()

        extra_environment = {ModuleCtx.Bridge_Redis_Port_Variable: redis_port_text}
        zato.start(extra_environment)

        # .. import the connections under test ..
        _ = zato.import_yaml('fabric_live.yaml', _render_template(fabric))

        # .. deploy the services the tests drive ..
        file_name = ModuleCtx.Services_File.name
        source = ModuleCtx.Services_File.read_text()
        zato.deploy(file_name, source)

        # .. hand everything to the tests ..
        out = FabricLiveEnvironment(zato=zato, fabric=fabric)
        yield out

    # .. and stop whatever was started.
    finally:
        tear_down(parts)

# ################################################################################################################################

@pytest.fixture(scope='session')
def deployed_client(fabric_live:'FabricLiveEnvironment') -> 'AdminClient':
    """ A client of the test server, handed over once the deployed services answer.
    """
    out = fabric_live.zato.client()
    _wait_until_deployed(out)

    return out

# ################################################################################################################################
# ################################################################################################################################
