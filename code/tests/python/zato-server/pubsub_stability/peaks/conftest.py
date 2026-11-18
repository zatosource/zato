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
from pubsub_rest.server import get_fixture_arguments, PubSubServer
from pubsub_rest.suite import define_traffic
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

_server = PubSubServer('pubsub-peaks')

# ################################################################################################################################
# ################################################################################################################################

def _setup(server:'PubSubServer', definition:'Definition') -> 'None':
    _ = define_traffic(server, definition)

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
