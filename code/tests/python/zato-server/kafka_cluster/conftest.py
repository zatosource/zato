# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A Kafka cluster of several instances, one Redis, one queue bridge and one Zato server for the whole session -
# the connections point at the first instance alone, so discovering the rest is under test from the first message on.

# stdlib
import os
import sys
import tempfile
from contextlib import ExitStack

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_environment.parts import missing_requirements, Parts, skip_or_fail, tear_down
from live_environment.quickstart import ZatoEnvironment
from live_kafka.bridge import local_requirements, start_bridge_parts
from live_kafka.containers import start_kafka_cluster
from live_kafka.suite import KafkaSuite, ModuleCtx
from zato.common.test.pubsub_database import pubsub_db_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_kafka.containers import KafkaCluster
    from zato.common.typing_ import any_, anylist, iterator_

# ################################################################################################################################
# ################################################################################################################################

class ClusterSuite(KafkaSuite):
    """ The single-instance suite's helpers over a cluster, plus the cluster itself under its own name.
    """

    @property
    def cluster(self) -> 'KafkaCluster':
        out:'KafkaCluster' = self.kafka # type: ignore[assignment]
        return out

# ################################################################################################################################

    @property
    def bootstrap(self) -> 'str':
        """ Every instance that can answer right now - what the test's own clients use to look at the topics.
        """
        out = ','.join(elem.address for elem in self.cluster.running_instances())
        return out

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
    skip_or_fail(_requirements(), ModuleCtx.Required_Variable)

    parts = Parts()

    try:
        # .. the cluster ..
        cluster = start_kafka_cluster()
        parts.add('kafka cluster', cluster.stop)

        # .. Redis and the bridge ..
        bridge = start_bridge_parts()
        parts.add('redis-server', bridge.stop_redis)
        parts.add('queue bridge', bridge.stop_bridge)

        # .. the server pointed at the same Redis ..
        directory = tempfile.mkdtemp(prefix='zato_kafka_cluster_')
        zato = ZatoEnvironment(directory, password_prefix='test.kafka.cluster')
        parts.add('zato environment', zato.stop)
        zato.create()

        # .. the tests read the audit log of the server, so this process uses the server's database too ..
        database_scope = ExitStack()
        parts.add('database environment', database_scope.close)
        database_scope.enter_context(pubsub_db_env(zato.database_env))

        # The server gets a Zato database of its own, so nothing of an earlier session's DLQs is restored into it
        environment = dict(bridge.server_environment)

        zato.start(environment)

        # .. the services the tests drive ..
        zato.deploy(ModuleCtx.Shared_Services_File.name, ModuleCtx.Shared_Services_File.read_text())
        zato.deploy(ModuleCtx.Services_File.name, ModuleCtx.Services_File.read_text())

        suite = ClusterSuite(zato, cluster, bridge, environment)
        suite.wait_until_deployed()

        yield suite

    finally:
        tear_down(parts)

# ################################################################################################################################

def pytest_configure(config:'any_') -> 'None':
    config.addinivalue_line('markers', 'bridge_errors_expected: the test stops, kills or pauses instances deliberately')

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_slate(request:'any_') -> 'iterator_':
    """ Every test starts with no recorded invocations, receivers that behave and every instance up and running,
    and leaves the cluster whole for the next one whatever it did to it. A test that takes instances down deliberately
    has the output of the bridge marked as expected until the cluster is whole again.
    """
    used_suite:'ClusterSuite | None' = None
    scope = ExitStack()

    if 'kafka_suite' in request.fixturenames:
        suite:'ClusterSuite' = request.getfixturevalue('kafka_suite')
        suite.cluster.restore_all()
        suite.clear_received()
        suite.reset_behaviour()
        used_suite = suite

        if request.node.get_closest_marker('bridge_errors_expected'):
            scope.enter_context(suite.bridge.expected_errors())

    with scope:

        yield

        if used_suite:
            used_suite.cluster.restore_all()

# ################################################################################################################################
# ################################################################################################################################
