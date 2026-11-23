# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

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
# ################################################################################################################################
