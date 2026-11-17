# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
from pubsub_rest.definition import Delivery_Pull
from pubsub_rest.runner import get_duration
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from pubsub_rest.suite import define_traffic
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.direct_sql.pubsub_seed import seed_queues, SeededQueue
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-laggard')

# How many messages the partner is behind, unless Zato_Test_Laggard_Messages says otherwise.
_backlog_messages = 20_000_000

# The partner of the traffic that is behind.
_laggard_index = 0

# ################################################################################################################################
# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

    traffic = define_traffic(server, definition)

    backlog_messages = get_duration('Zato_Test_Laggard_Messages', _backlog_messages)
    partner_name = traffic.get_partner_name(_laggard_index)

    # The backlog of the partner is in its queue before the server starts.
    queue = SeededQueue(partner_name, Delivery_Pull, partner_name, backlog_messages)

    def seed_backlog(server_directory:'str') -> 'None':
        server.properties['seed_seconds'] = seed_queues([queue])

    server.pre_server_callback = seed_backlog
    server.properties['backlog_messages'] = backlog_messages
    server.properties['laggard_index'] = _laggard_index

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
