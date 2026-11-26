# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Live environment
from live_environment.parts import Parts, skip_or_fail, tear_down
from live_environment.quickstart import ZatoEnvironment

# Live Kafka
from live_kafka.bridge import local_requirements, start_bridge_parts

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx
from live_fabric.state import describe, missing_requirements

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_fabric.state import FabricEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import iterator_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The connection with valid credentials
    Connection_Name = 'test.fabric.main'

    # The connection whose client secret the token endpoint rejects
    Bad_Credentials_Connection_Name = 'test.fabric.bad-credentials'

    # The services the tests drive and the connections they use
    Services_File = Path(__file__).parent / '_services.py'
    Template_File = Path(__file__).parent / '_enmasse_template.yaml'

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
    missing_local = local_requirements()
    missing = missing_fabric + missing_local
    skip_or_fail(missing, FabricCtx.Required_Variable)

    parts = Parts()

    try:
        # .. read what the setup recorded ..
        fabric = describe()

        # .. start Redis and the bridge pointed at it ..
        bridge = start_bridge_parts()
        parts.add('redis-server', bridge.stop_redis)
        parts.add('queue bridge', bridge.stop_bridge)

        # .. start the server pointed at the same Redis and at the bridge's HTTP query API ..
        directory = tempfile.mkdtemp(prefix='zato_fabric_live_')
        zato = ZatoEnvironment(directory, password_prefix='test.fabric')
        parts.add('zato environment', zato.stop)
        zato.create()

        zato.start(dict(bridge.server_environment))

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
