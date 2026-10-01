# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import missing_requirements, Parts, skip_or_fail, tear_down
from live_environment.quickstart import ZatoEnvironment
from live_kafka.bridge import local_requirements, start_bridge_parts
from live_kafka.containers import start_kafka, stop_container
from live_kafka.suite import KafkaSuite, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, iterator_

# ################################################################################################################################
# ################################################################################################################################

def _requirements() -> 'anylist':
    out = missing_requirements(wants_docker=True, wants_haproxy=False)
    out.extend(local_requirements())

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def kafka_suite() -> 'iterator_':
    """ One broker, one Redis, one queue bridge and one Zato server for the whole session.
    """
    skip_or_fail(_requirements(), ModuleCtx.Required_Variable)

    parts = Parts()

    try:
        # .. the broker ..
        kafka = start_kafka()
        parts.add('kafka', lambda: stop_container(kafka.container_name))

        # .. Redis and the bridge ..
        bridge = start_bridge_parts()
        parts.add('redis-server', bridge.redis.stop)
        parts.add('queue bridge', lambda: bridge.bridge.stop())

        # .. the server pointed at the same Redis ..
        directory = tempfile.mkdtemp(prefix='zato_kafka_')
        zato = ZatoEnvironment(directory, password_prefix='test.kafka')
        parts.add('zato environment', zato.stop)
        zato.create()

        # The server gets a pub/sub database of its own, so nothing of an earlier session's DLQs is restored into it
        environment = dict(bridge.server_environment)
        environment[ModuleCtx.PubSub_DB_Type_Variable] = ModuleCtx.PubSub_DB_Type
        environment[ModuleCtx.PubSub_DB_Name_Variable] = os.path.join(directory, ModuleCtx.PubSub_DB_File_Name)

        zato.start(environment)

        # The tests read the audit log the server writes
        os.environ[ModuleCtx.Audit_DB_Variable] = zato.audit_db_path

        # .. the services the tests drive ..
        zato.deploy(ModuleCtx.Shared_Services_File.name, ModuleCtx.Shared_Services_File.read_text())
        zato.deploy(ModuleCtx.Services_File.name, ModuleCtx.Services_File.read_text())

        suite = KafkaSuite(zato, kafka, bridge, environment)
        suite.wait_until_deployed()

        yield suite

    finally:
        tear_down(parts)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def _clean_slate(request:'any_') -> 'iterator_':
    """ Every test starts with no recorded invocations and receivers that behave.
    """
    if 'kafka_suite' in request.fixturenames:
        suite:'KafkaSuite' = request.getfixturevalue('kafka_suite')
        suite.clear_received()
        suite.reset_behaviour()

    yield

# ################################################################################################################################
# ################################################################################################################################
