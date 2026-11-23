# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError

# Zato - Rust
from zato_server_core.zato_server_core import HTTPTransport

# Test support
from http_endpoint.endpoint import CloseMode, EndpointResponse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from zato.common.typing_ import any_, anytuple, byteslist, bytestuple

    intset = set[int]

# ################################################################################################################################
# ################################################################################################################################

# How many idle connections the transport keeps per endpoint
_pool_size = 4

# How long one wait of the transport may take, in seconds
_timeout = 30.0

# The sizes of the parts that each test sends
_part_sizes = (0, 1, 64 * 1024, 16 * 1024 * 1024)

# The headers of a push
_headers = {
    'Content-Type': 'application/json',
    'X-Zato-Msg-ID': 'zpsm.0192d3a1b2c3d4e5f60718293a4b5c6d',
    'X-Zato-Delivery-Attempt': '1',
}

# The text that the parts repeat
_filler = b'Order "12345" for John Smith\n'

# The network scope of the address of the local endpoint
_loopback_scope = 'loopback'

# What the error of a call names when no address of the host has the scope the call requires
_scope_refused_text = 'required network scope'

# ################################################################################################################################
# ################################################################################################################################

def _new_part(size:'int', index:'int') -> 'bytes':
    """ Returns a part of the given size whose bytes differ from those of the other parts.
    """
    marker = f'part {index} - '
    marker = marker.encode('ascii')

    repeat_count = size // len(_filler) + 1
    out = marker + _filler * repeat_count
    out = out[:size]
    return out

# ################################################################################################################################

def _new_parts() -> 'bytestuple':
    """ Returns one part of each size, in the order of the sizes.
    """
    parts:'byteslist' = []

    for index, size in enumerate(_part_sizes):
        part = _new_part(size, index)
        parts.append(part)

    out = tuple(parts)
    return out

# ################################################################################################################################

def _new_transport(ca_path:'str | None') -> 'any_':
    out = HTTPTransport(_pool_size)
    out.set_timeout(_timeout)
    out.set_tls(ca_path, None, None)
    return out

# ################################################################################################################################

def _invoke(transport:'any_', url:'str', parts:'bytestuple') -> 'anytuple':
    """ Sends the parts as the body of one push and returns what the transport returned.
    """
    out = transport.invoke_parts('POST', url, _headers, parts)
    assert out is not None

    status_code = out[0]
    assert status_code == OK

    return out

# ################################################################################################################################

def _get_base(endpoint:'TestEndpoint', is_tls:'bool') -> 'str':
    if is_tls:
        out = endpoint.https_base
    else:
        out = endpoint.http_base

    return out

# ################################################################################################################################

def _get_ca_path(endpoint:'TestEndpoint', is_tls:'bool') -> 'str | None':
    if is_tls:
        out = endpoint.certificates.ca_path
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('is_tls', [False, True], ids=['plain', 'tls'])
def test_parts_arrive_as_one_body(endpoint:'TestEndpoint', path:'str', is_tls:'bool') -> 'None':

    base = _get_base(endpoint, is_tls)
    ca_path = _get_ca_path(endpoint, is_tls)

    transport = _new_transport(ca_path)
    parts = _new_parts()
    expected = b''.join(parts)

    _ = _invoke(transport, base + path, parts)

    # The body is the parts joined, and its length is the sum of their lengths
    request = endpoint.get_request(path)
    content_length = request.get_header('Content-Length')

    assert request.body == expected
    assert content_length == str(len(expected))

# ################################################################################################################################

@pytest.mark.parametrize('is_tls', [False, True], ids=['plain', 'tls'])
def test_consecutive_pushes_reuse_the_connection(endpoint:'TestEndpoint', path:'str', is_tls:'bool') -> 'None':

    base = _get_base(endpoint, is_tls)
    ca_path = _get_ca_path(endpoint, is_tls)

    transport = _new_transport(ca_path)
    parts = _new_parts()
    expected = b''.join(parts)

    for _ in range(3):
        _ = _invoke(transport, base + path, parts)

    requests = endpoint.get_requests(path)
    connection_ids:'intset' = set()

    for request in requests:
        assert request.body == expected
        connection_ids.add(request.connection_id)

    request_count = len(requests)
    connection_count = len(connection_ids)

    assert request_count == 3
    assert connection_count == 1

# ################################################################################################################################

@pytest.mark.parametrize('is_tls', [False, True], ids=['plain', 'tls'])
def test_push_on_a_closed_connection_is_sent_again(endpoint:'TestEndpoint', path:'str', is_tls:'bool') -> 'None':

    base = _get_base(endpoint, is_tls)
    ca_path = _get_ca_path(endpoint, is_tls)

    # The endpoint closes the pooled connection after reading the second push, without a response ..
    endpoint.set_responses(path, [
        EndpointResponse(body='First response'),
        EndpointResponse(close_mode=CloseMode.Close_Before_Response),
        EndpointResponse(body='Third response'),
    ])

    transport = _new_transport(ca_path)
    parts = _new_parts()
    expected = b''.join(parts)

    first = _invoke(transport, base + path, parts)
    second = _invoke(transport, base + path, parts)

    assert first[3] == b'First response'
    assert second[3] == b'Third response'

    # .. so the transport sends it once more, on a new connection, with the whole body.
    first_request, closed_request, repeated_request = endpoint.get_requests(path)

    assert first_request.body == expected
    assert closed_request.body == expected
    assert repeated_request.body == expected

    assert closed_request.connection_id == first_request.connection_id
    assert repeated_request.connection_id != first_request.connection_id

# ################################################################################################################################

@pytest.mark.parametrize('host', ['127.0.0.1', 'localhost'])
def test_response_names_the_scope_of_the_peer(endpoint:'TestEndpoint', path:'str', host:'str') -> 'None':

    transport = _new_transport(None)
    parts = _new_parts()

    url = f'http://{host}:{endpoint.http_port}{path}'
    out = _invoke(transport, url, parts)

    tuple_length = len(out)
    peer_scope = out[6]

    assert tuple_length == 7
    assert peer_scope == _loopback_scope

# ################################################################################################################################

def test_required_loopback_scope_is_sent(endpoint:'TestEndpoint', path:'str') -> 'None':

    transport = _new_transport(None)
    parts = _new_parts()
    url = endpoint.http_base + path
    expected = b''.join(parts)

    out = transport.invoke_parts('POST', url, _headers, parts, _loopback_scope)

    status_code = out[0]
    peer_scope = out[6]

    assert status_code == OK
    assert peer_scope == _loopback_scope

    request = endpoint.get_request(path)
    assert request.body == expected

# ################################################################################################################################

@pytest.mark.parametrize('required_scope', ['public', 'private'])
def test_required_scope_of_another_network_is_refused(endpoint:'TestEndpoint', path:'str', required_scope:'str') -> 'None':

    transport = _new_transport(None)
    parts = _new_parts()
    url = endpoint.http_base + path

    with pytest.raises(RequestsConnectionError, match=_scope_refused_text):
        _ = transport.invoke_parts('POST', url, _headers, parts, required_scope)

    requests = endpoint.get_requests(path)
    assert requests == []

# ################################################################################################################################

@pytest.mark.parametrize('required_scope', ['link-local', 'internal', ''])
def test_scope_that_cannot_be_required_is_rejected(endpoint:'TestEndpoint', path:'str', required_scope:'str') -> 'None':

    transport = _new_transport(None)
    parts = _new_parts()
    url = endpoint.http_base + path

    with pytest.raises(ValueError, match='Unknown required network scope'):
        _ = transport.invoke_parts('POST', url, _headers, parts, required_scope)

    requests = endpoint.get_requests(path)
    assert requests == []

# ################################################################################################################################

def test_pooled_connection_of_another_scope_is_not_reused(endpoint:'TestEndpoint', path:'str') -> 'None':

    transport = _new_transport(None)
    parts = _new_parts()
    url = endpoint.http_base + path

    # A call without a required scope leaves its connection in the pool ..
    _ = _invoke(transport, url, parts)

    # .. which a call that requires another scope does not send on, so the call fails before anything is sent ..
    with pytest.raises(RequestsConnectionError, match=_scope_refused_text):
        _ = transport.invoke_parts('POST', url, _headers, parts, 'private')

    # .. and the connection remains in the pool for a call that requires its own scope.
    out = transport.invoke_parts('POST', url, _headers, parts, _loopback_scope)

    status_code = out[0]
    assert status_code == OK

    first_request, second_request = endpoint.get_requests(path)
    assert second_request.connection_id == first_request.connection_id

# ################################################################################################################################
# ################################################################################################################################
