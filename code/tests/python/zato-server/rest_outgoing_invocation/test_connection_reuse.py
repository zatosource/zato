# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Connection reuse - one TCP connection kept open across sequential calls, a connection the endpoint closed
# replaced transparently, and the pool size of a connection bounding how many TCP connections are kept.

# stdlib
from http.client import OK

# gevent
from gevent import joinall, spawn

# Test support
from endpoint import CloseMode, EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

def _get_connection_ids(endpoint:'TestEndpoint', path:'str') -> 'list[int]':
    """ Returns the IDs of the TCP connections the requests for the path arrived on, oldest first.
    """
    out:'list[int]' = []

    for request in endpoint.get_requests(path):
        out.append(request.connection_id)

    return out

# ################################################################################################################################

def _invoke_concurrently(connection:'HTTPSOAPWrapper', count:'int') -> 'None':
    """ Invokes the connection from the given number of greenlets at the same time and waits for all of them.
    """
    greenlets = []

    for _ in range(count):
        greenlet = spawn(connection.get, Test_CID)
        greenlets.append(greenlet)

    _ = joinall(greenlets, raise_error=True)

# ################################################################################################################################
# ################################################################################################################################

def test_sequential_calls_reuse_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Sequential calls are sent over one TCP connection.
    """
    connection = new_connection(server, endpoint.http_base, path)

    for _ in range(5):
        response = connection.get(Test_CID)
        assert response.status_code == OK

    connection_ids = _get_connection_ids(endpoint, path)

    assert len(connection_ids) == 5
    assert len(set(connection_ids)) == 1

# ################################################################################################################################

def test_sequential_calls_reuse_tls_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Sequential calls over TLS are sent over one TCP connection.
    """
    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    for _ in range(5):
        _ = connection.get(Test_CID)

    connection_ids = _get_connection_ids(endpoint, path)
    assert len(set(connection_ids)) == 1

# ################################################################################################################################

def test_connection_closed_by_endpoint(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A TCP connection the endpoint closed after a response is replaced with a new one by the next call, which succeeds.
    """
    endpoint.set_responses(path, [
        EndpointResponse(body='First response', close_mode=CloseMode.Close_After_Response),
        EndpointResponse(body='Second response'),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    first = connection.get(Test_CID)
    second = connection.get(Test_CID)

    assert first.text == 'First response'
    assert second.text == 'Second response'

    first_id, second_id = _get_connection_ids(endpoint, path)
    assert first_id != second_id

# ################################################################################################################################

def test_connection_close_header(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A response with `Connection: close` makes the next call open a new TCP connection.
    """
    endpoint.set_responses(path, [
        EndpointResponse(body='First response', needs_close=True),
        EndpointResponse(body='Second response'),
        EndpointResponse(body='Third response'),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    for _ in range(3):
        _ = connection.get(Test_CID)

    first_id, second_id, third_id = _get_connection_ids(endpoint, path)

    assert first_id != second_id
    assert second_id == third_id

# ################################################################################################################################

def test_response_without_length(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A response without a length is read until the endpoint closes the connection, and the next call opens a new one.
    """
    endpoint.set_responses(path, [
        EndpointResponse(body='Response without a length', has_no_length=True),
        EndpointResponse(body='Second response'),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    first = connection.get(Test_CID)
    second = connection.get(Test_CID)

    assert first.text == 'Response without a length'
    assert second.text == 'Second response'

    first_id, second_id = _get_connection_ids(endpoint, path)
    assert first_id != second_id

# ################################################################################################################################

def test_pool_size_bounds_kept_connections(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Of the TCP connections opened by concurrent calls, as many as the pool size are kept and reused by the next concurrent calls.
    """
    pool_size = 2
    concurrency = 4

    endpoint.set_response(path, EndpointResponse(delay=0.3))

    connection = new_connection(server, endpoint.http_base, path, pool_size=pool_size)

    _invoke_concurrently(connection, concurrency)
    first_ids = set(_get_connection_ids(endpoint, path))

    _invoke_concurrently(connection, concurrency)
    all_ids = set(_get_connection_ids(endpoint, path))

    second_new_ids = all_ids - first_ids

    assert len(first_ids) == concurrency
    assert len(second_new_ids) == concurrency - pool_size

# ################################################################################################################################
# ################################################################################################################################
