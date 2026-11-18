# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the API clients, the partners and the push receiver of the traffic share one process as greenlets,
# so the patching runs before the modules of the suite are imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_lib_dir = os.path.abspath(os.path.join(_here, '..', '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _lib_dir)

# pytest
import pytest

# Zato
from pubsub_rest.capture import limit_captured_logs
from pubsub_rest.runner import get_duration
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from pubsub_rest.suite import define_traffic
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.direct_sql.pubsub_seed import seed_traces
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-cleanup-load')

# How many delivered-message traces past their retention the cleanup removes during the traffic,
# unless Zato_Test_Retention_Messages says otherwise.
_trace_count = 2_000_000

# How old the traces are, which is past the retention by age.
_trace_age_days = 30

# The topic the traces belong to.
_trace_topic = 'stability.retention'

# ################################################################################################################################
# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

    _ = define_traffic(server, definition)

    trace_count = get_duration('Zato_Test_Retention_Messages', _trace_count)

    # The traces are in the database before the server starts.
    def seed_retention_traces(server_directory:'str') -> 'None':
        server.properties['seed_seconds'] = seed_traces(_trace_topic, trace_count, _trace_age_days)

    server.pre_server_callback = seed_retention_traces
    server.properties['trace_count'] = trace_count
    server.properties['trace_topic'] = _trace_topic

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(**get_fixture_arguments(_server, _setup, scope='module',
    quickstart_parent_dir=get_runtime_dir()))

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def server() -> 'PubSubServer':
    return _server

# ################################################################################################################################

@pytest.fixture(autouse=True)
def captured_log_level(request:'pytest.FixtureRequest', caplog:'pytest.LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of each test.
    """
    yield from limit_captured_logs(request, caplog)

# ################################################################################################################################
# ################################################################################################################################
