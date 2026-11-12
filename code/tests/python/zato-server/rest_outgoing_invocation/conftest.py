# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - outgoing connections run under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import re
import sys
import tempfile

# The test support modules live next to the tests and are imported flat
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato_server_core.zato_server_core import init_rest_log

# Test support
from endpoint import TestEndpoint, UnresponsiveListener
from support import configure_rest_log, ServerStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    endpointgen = Iterator[TestEndpoint]
    listenergen = Iterator[UnresponsiveListener]
    strgen      = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

# What a test name is reduced to before it becomes a part of a path
_path_unsafe = re.compile(r'[^a-zA-Z0-9]+')

# The size at which the REST log rotates, large enough for it not to rotate during a run
_rest_log_max_bytes = 1_000_000_000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def endpoint() -> 'endpointgen':
    """ The local endpoint of the session, with its certificates in a directory of their own.
    """
    directory = tempfile.mkdtemp(prefix='zato-rest-outgoing-')
    certificates_directory = os.path.join(directory, 'certificates')

    out = TestEndpoint(certificates_directory)
    out.start()

    yield out

    out.stop()
    os.rmdir(directory)

# ################################################################################################################################

@pytest.fixture(scope='session')
def unresponsive_listener() -> 'listenergen':
    """ A listener that never completes a connection, for connect timeouts.
    """
    out = UnresponsiveListener()
    out.start()

    yield out

    out.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def rest_log_path() -> 'strgen':
    """ The file both the zato_rest logger and the server's REST log writer write to.
    """
    directory = tempfile.mkdtemp(prefix='zato-rest-outgoing-log-')
    out = os.path.join(directory, 'rest.log')

    configure_rest_log(out)
    init_rest_log(out, _rest_log_max_bytes)

    yield out

# ################################################################################################################################

@pytest.fixture
def server() -> 'ServerStub':
    """ A new server for each test, so no test sees the definitions or the cached tokens of another one.
    """
    out = ServerStub()
    return out

# ################################################################################################################################

@pytest.fixture
def path(request:'pytest.FixtureRequest') -> 'str':
    """ A path no other test uses, so each test reads only the requests it sent.
    """
    name = _path_unsafe.sub('-', request.node.name)
    suffix = CryptoManager.generate_hex_string(32)

    out = f'/test/{name}/{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################
