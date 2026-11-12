# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Timeouts - the timeout of a connection applied to establishing a connection and to waiting for a response,
# over plain HTTP and over TLS.

# stdlib
from http.client import OK
from time import monotonic

# pytest
import pytest

# Zato
from zato.common.audit_log.common import TransportStatus
from zato.common.exception import BackendInvocationError

# Test support
from endpoint import EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint, UnresponsiveListener
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The timeout of the connections that are expected to time out, in seconds
_timeout = 1

# How long the endpoint waits before it answers, longer than the timeout
_delay = 1.5

# ################################################################################################################################
# ################################################################################################################################

def test_read_timeout(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An endpoint that does not answer within the timeout raises BackendInvocationError with the timeout transport status.
    """
    endpoint.set_response(path, EndpointResponse(delay=_delay))

    connection = new_connection(server, endpoint.http_base, path, timeout=_timeout)

    start = monotonic()

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    elapsed = monotonic() - start

    assert info.value.transport_status == TransportStatus.Timeout
    assert info.value.args[0].startswith('Timeout error: ')

    assert elapsed >= _timeout
    assert elapsed < _delay

    assert len(endpoint.get_requests(path)) == 1

# ################################################################################################################################

def test_read_timeout_tls(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An endpoint that does not answer over TLS within the timeout raises BackendInvocationError with the timeout transport status.
    """
    endpoint.set_response(path, EndpointResponse(delay=_delay))

    connection = new_connection(
        server, endpoint.https_base, path, timeout=_timeout, ca_certs_path=endpoint.certificates.ca_path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Timeout

# ################################################################################################################################

def test_connect_timeout(unresponsive_listener:'UnresponsiveListener', server:'ServerStub', path:'str') -> 'None':
    """ A connection that cannot be established within the timeout raises BackendInvocationError with the timeout transport status.
    """
    connection = new_connection(server, unresponsive_listener.base, path, timeout=_timeout)

    start = monotonic()

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    elapsed = monotonic() - start

    assert info.value.transport_status == TransportStatus.Timeout
    assert info.value.args[0].startswith('Timeout error: ')

    assert elapsed >= _timeout
    assert elapsed < _timeout * 3

# ################################################################################################################################

def test_response_within_timeout(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An endpoint that answers more slowly than usual but within the timeout returns its response.
    """
    endpoint.set_response(path, EndpointResponse(body='Delayed response', delay=0.3))

    connection = new_connection(server, endpoint.http_base, path, timeout=2)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert response.text == 'Delayed response'

# ################################################################################################################################

def test_no_timeout_configured(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection with no timeout configured waits for a response as long as the endpoint takes to send it.
    """
    endpoint.set_response(path, EndpointResponse(body='Response without a timeout', delay=_delay))

    connection = new_connection(server, endpoint.http_base, path, timeout=0)

    response = connection.get(Test_CID)

    assert connection.config['timeout'] is None
    assert response.status_code == OK
    assert response.text == 'Response without a timeout'

# ################################################################################################################################

def test_connection_usable_after_timeout(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection whose previous call timed out serves the next call normally.
    """
    endpoint.set_responses(path, [EndpointResponse(delay=_delay), EndpointResponse(body='After timeout')])

    connection = new_connection(server, endpoint.http_base, path, timeout=_timeout)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert response.text == 'After timeout'

# ################################################################################################################################
# ################################################################################################################################
