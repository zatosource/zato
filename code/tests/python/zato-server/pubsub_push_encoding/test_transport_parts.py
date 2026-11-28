# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# Zato
from zato.server.base.parallel.push_engine_client import PushEngineClient

# Test support
from http_endpoint.endpoint import CloseMode, EndpointResponse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from zato.common.typing_ import anytuple, byteslist, bytestuple

    intset = set[int]

# ################################################################################################################################
# ################################################################################################################################

# The threads of the push engine of each test, one, so that consecutive pushes use one keep-alive connection in order
_thread_count = 1

# How many idle connections the push engine keeps per endpoint
_pool_size = 4

# How long one connect or one read of the push engine may take, in seconds
_timeout = 30.0

# How long a stop of the push engine waits for its threads, in seconds
_stop_timeout = 5.0

# The sizes of the parts that each test sends
_part_sizes = (0, 1, 64 * 1024, 16 * 1024 * 1024)

# The ID of the message of each push
_msg_id = 'zpsm.0192d3a1b2c3d4e5f60718293a4b5c6d'

# The headers of a push
_headers = {
    'Content-Type': 'application/json',
    'X-Zato-Msg-ID': _msg_id,
    'X-Zato-Delivery-Attempt': '1',
}

# The text that the parts repeat
_filler = b'Order "12345" for John Smith\n'

# The network scope of the address of the local endpoint
_loopback_scope = 'loopback'

# The positions of the fields of the outcome of a request of the push engine
_outcome_status = 1
_outcome_concluded = 3
_outcome_scope = 5
_outcome_error_kind = 6

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

class _Engine:
    """ A push engine with the TLS settings of one test, stopped by the test once it completes.
    """

    def __init__(self, ca_path:'str | None') -> 'None':
        self.client = PushEngineClient(_thread_count, _pool_size, _stop_timeout)
        self.tls = (ca_path, None, None, 0)

    def push(self, url:'str', parts:'bytestuple') -> 'anytuple':
        """ Sends the parts as the body of one push and returns the outcome of its request.
        """
        request = (url, _headers, parts, [_msg_id], False)
        internal_error, outcomes = self.client.run([request], _timeout, self.tls)

        assert internal_error is None, internal_error

        out = outcomes[0]
        return out

    def push_ok(self, url:'str', parts:'bytestuple') -> 'anytuple':
        """ Sends one push and confirms that it concluded its message with a 200.
        """
        out = self.push(url, parts)

        assert out[_outcome_error_kind] is None, out
        assert out[_outcome_status] == OK, out
        assert out[_outcome_concluded] == [_msg_id], out

        return out

    def stop(self) -> 'None':
        is_stopped = self.client.stop()
        assert is_stopped

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
    engine = _Engine(_get_ca_path(endpoint, is_tls))

    parts = _new_parts()
    expected = b''.join(parts)

    try:
        _ = engine.push_ok(base + path, parts)
    finally:
        engine.stop()

    # The body is the parts joined, and its length is the sum of their lengths
    request = endpoint.get_request(path)
    content_length = request.get_header('Content-Length')

    assert request.body == expected
    assert content_length == str(len(expected))

# ################################################################################################################################

@pytest.mark.parametrize('is_tls', [False, True], ids=['plain', 'tls'])
def test_consecutive_pushes_reuse_the_connection(endpoint:'TestEndpoint', path:'str', is_tls:'bool') -> 'None':

    base = _get_base(endpoint, is_tls)
    engine = _Engine(_get_ca_path(endpoint, is_tls))

    parts = _new_parts()
    expected = b''.join(parts)

    try:
        for _ in range(3):
            _ = engine.push_ok(base + path, parts)
    finally:
        engine.stop()

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

    # The endpoint closes the pooled connection after reading the second push, without a response ..
    endpoint.set_responses(path, [
        EndpointResponse(body='First response'),
        EndpointResponse(close_mode=CloseMode.Close_Before_Response),
        EndpointResponse(body='Third response'),
    ])

    engine = _Engine(_get_ca_path(endpoint, is_tls))

    parts = _new_parts()
    expected = b''.join(parts)

    try:
        _ = engine.push_ok(base + path, parts)
        _ = engine.push_ok(base + path, parts)
    finally:
        engine.stop()

    # .. so the engine sends it once more, on a new connection, with the whole body.
    first_request, closed_request, repeated_request = endpoint.get_requests(path)

    assert first_request.body == expected
    assert closed_request.body == expected
    assert repeated_request.body == expected

    assert closed_request.connection_id == first_request.connection_id
    assert repeated_request.connection_id != first_request.connection_id

# ################################################################################################################################

@pytest.mark.parametrize('host', ['127.0.0.1', 'localhost'])
def test_outcome_names_the_scope_of_the_peer(endpoint:'TestEndpoint', path:'str', host:'str') -> 'None':

    engine = _Engine(None)
    parts = _new_parts()
    url = f'http://{host}:{endpoint.http_port}{path}'

    try:
        out = engine.push_ok(url, parts)
    finally:
        engine.stop()

    peer_scope = out[_outcome_scope]
    assert peer_scope == _loopback_scope

# ################################################################################################################################
# ################################################################################################################################
