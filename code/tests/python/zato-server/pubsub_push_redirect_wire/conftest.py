# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import sys
import tempfile

# The support module of the suite is in its own directory, and the test endpoint and the connection stubs
# are shared with other suites
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, '..', '..', 'zato-common', 'lib'))

# pytest
import pytest # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager # noqa: E402

# Test support
from http_endpoint.addresses import get_non_loopback_address # noqa: E402
from http_endpoint.endpoint import Host, TestEndpoint # noqa: E402
from rest_outgoing_stub.connection import ServerStub # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    endpointgen = Iterator[TestEndpoint]

# ################################################################################################################################
# ################################################################################################################################

# What a test name is reduced to before it becomes a part of a path
_path_unsafe = re.compile(r'[^a-zA-Z0-9]+')

# ################################################################################################################################
# ################################################################################################################################

def _run_endpoint(name:'str', host:'str') -> 'endpointgen':
    """ Starts an endpoint on the host with its certificates in a directory of their own, and stops it afterwards.
    """
    directory = tempfile.mkdtemp(prefix=f'zato-pubsub-push-redirect-{name}-')
    certificates_directory = os.path.join(directory, 'certificates')

    endpoint = TestEndpoint(certificates_directory, host)
    endpoint.start()

    yield endpoint

    endpoint.stop()
    os.rmdir(directory)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def loopback_first() -> 'endpointgen':
    """ The first endpoint on the loopback address.
    """
    yield from _run_endpoint('loopback-first', Host)

# ################################################################################################################################

@pytest.fixture(scope='session')
def loopback_second() -> 'endpointgen':
    """ The second endpoint on the loopback address, with ports of its own.
    """
    yield from _run_endpoint('loopback-second', Host)

# ################################################################################################################################

@pytest.fixture(scope='session')
def non_loopback_address() -> 'str':
    """ The address of this machine outside the loopback range.
    """
    out = get_non_loopback_address()
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def remote_first(non_loopback_address:'str') -> 'endpointgen':
    """ The first endpoint on the address outside the loopback range.
    """
    yield from _run_endpoint('remote-first', non_loopback_address)

# ################################################################################################################################

@pytest.fixture(scope='session')
def remote_second(non_loopback_address:'str') -> 'endpointgen':
    """ The second endpoint on the address outside the loopback range, with ports of its own.
    """
    yield from _run_endpoint('remote-second', non_loopback_address)

# ################################################################################################################################

@pytest.fixture
def server() -> 'ServerStub':
    """ The part of a server that the outgoing connections of a test read.
    """
    out = ServerStub()
    return out

# ################################################################################################################################

@pytest.fixture
def path(request:'pytest.FixtureRequest') -> 'str':
    """ A path that no other test uses, so that each test reads only the requests that it sent.
    """
    name = _path_unsafe.sub('-', request.node.name)
    suffix = CryptoManager.generate_hex_string(32)

    out = f'/test/{name}/{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################
