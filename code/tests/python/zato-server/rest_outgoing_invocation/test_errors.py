# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Transport errors - a refused connection, a host name that does not resolve and a connection ended by the endpoint
# before or during its response, each raised as the exception and with the transport status a caller expects.

# stdlib
import socket
from http.client import OK

# pytest
import pytest

# requests
from requests.exceptions import ChunkedEncodingError

# Zato
from zato.common.audit_log.common import TransportStatus
from zato.common.exception import BackendInvocationError

# Test support
from endpoint import CloseMode, EndpointResponse, Host
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The body of the responses that are cut by the endpoint
_body = 'Customer list response body'

# ################################################################################################################################
# ################################################################################################################################

def _get_closed_port() -> 'int':
    """ Returns a port on the loopback address that nothing listens on.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((Host, 0))

    out = sock.getsockname()[1]
    sock.close()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_connection_refused(server:'ServerStub', path:'str') -> 'None':
    """ A port nothing listens on raises BackendInvocationError with the connection error transport status.
    """
    port = _get_closed_port()
    connection = new_connection(server, f'http://{Host}:{port}', path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Connection_Error
    assert info.value.args[0].startswith('Connection error: ')

# ################################################################################################################################

def test_unknown_host_name(server:'ServerStub', path:'str') -> 'None':
    """ A host name that does not resolve raises BackendInvocationError with the connection error transport status.
    """
    connection = new_connection(server, 'http://unknown-host.invalid', path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Connection_Error
    assert info.value.args[0].startswith('Connection error: ')

# ################################################################################################################################

@pytest.mark.parametrize('close_mode', [CloseMode.Reset_Before_Response, CloseMode.Close_Before_Response])
def test_connection_ended_before_response(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    close_mode:'str',
    ) -> 'None':
    """ A connection the endpoint resets or closes after the request and before the response raises BackendInvocationError
    with the connection error transport status.
    """
    endpoint.set_response(path, EndpointResponse(close_mode=close_mode))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Connection_Error
    assert info.value.args[0].startswith('Connection error: ')

    assert len(endpoint.get_requests(path)) == 1

# ################################################################################################################################

def test_connection_reset_during_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection the endpoint resets after part of the body raises ChunkedEncodingError unchanged.
    """
    endpoint.set_response(path, EndpointResponse(body=_body, close_mode=CloseMode.Reset_During_Response))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(ChunkedEncodingError):
        _ = connection.get(Test_CID)

# ################################################################################################################################

def test_chunked_response_cut(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A chunked response the endpoint cuts before its last chunk raises ChunkedEncodingError unchanged.
    """
    endpoint.set_response(path, EndpointResponse(body=_body, is_chunked=True, close_mode=CloseMode.Reset_During_Response))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(ChunkedEncodingError):
        _ = connection.get(Test_CID)

# ################################################################################################################################

def test_connection_usable_after_error(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection whose previous call was reset by the endpoint serves the next call normally.
    """
    endpoint.set_responses(path, [
        EndpointResponse(close_mode=CloseMode.Reset_Before_Response),
        EndpointResponse(body=_body),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert response.text == _body

    first, second = endpoint.get_requests(path)
    assert first.connection_id != second.connection_id

# ################################################################################################################################

def test_tls_connection_reset_before_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A TLS connection the endpoint resets before the response raises BackendInvocationError with a connection-level transport status.
    """
    endpoint.set_response(path, EndpointResponse(close_mode=CloseMode.Reset_Before_Response))

    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status in (TransportStatus.Connection_Error, TransportStatus.TLS_Error)

# ################################################################################################################################
# ################################################################################################################################
