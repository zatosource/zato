# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from pubsub_rest.capture import limit_captured_logs
from pubsub_rest.receiver import PushReceiver
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition
    from pubsub_rest.receiver import Push
    from zato.common.typing_ import callable_

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-failing-partners')

# The partners, each with a push endpoint of its own, whose subscriber and topic are named after it.
_partner_names = ['healthy', 'slow', 'flaky', 'failing', 'unresponsive']

_partner_prefix = 'stability.partners'

# ################################################################################################################################
# ################################################################################################################################

def _reject(push:'Push') -> 'bool':
    return False

# ################################################################################################################################

class _Endpoints:
    """ The push endpoints of all the partners, which hand each push to the behavior of the test,
    and reject every push until a test gives them one.
    """
    def __init__(self) -> 'None':
        self.handler:'callable_' = _reject

    def on_push(self, push:'Push') -> 'bool':
        out = self.handler(push)
        return out

# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

    endpoints = _Endpoints()

    receiver = PushReceiver(endpoints.on_push)
    server.add_receiver(receiver)

    for name in _partner_names:
        partner = f'{_partner_prefix}.{name}'
        _ = definition.add_push_subscriber(partner, [partner], receiver.port, f'/{name}')

    server.properties['endpoints'] = endpoints
    server.properties['partner_prefix'] = _partner_prefix
    server.properties['partner_names'] = _partner_names

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
