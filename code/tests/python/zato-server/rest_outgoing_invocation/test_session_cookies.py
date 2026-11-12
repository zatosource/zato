# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Session cookies - a cookie an endpoint sets sent back on the following calls of the same connection, and an explicit
# Cookie header of the caller sent in place of the cookies of the session.

# Test support
from endpoint import EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def _set_cookie(value:'str') -> 'EndpointResponse':
    out = EndpointResponse(headers=[('Set-Cookie', f'{value}; Path=/')])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_cookie_sent_back(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A cookie an endpoint sets is sent back on every following call of the connection.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.5c2f4e8b'), EndpointResponse()])

    connection = new_connection(server, endpoint.http_base, path)

    for _ in range(3):
        _ = connection.get(Test_CID)

    first, second, third = endpoint.get_requests(path)

    assert first.get_header('Cookie') is None
    assert second.get_header('Cookie') == 'session_id=session.5c2f4e8b'
    assert third.get_header('Cookie') == 'session_id=session.5c2f4e8b'

# ################################################################################################################################

def test_cookie_updated(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A cookie an endpoint sets again replaces its previous value in the following calls.
    """
    endpoint.set_responses(path, [
        _set_cookie('session_id=session.first'),
        _set_cookie('session_id=session.second'),
        EndpointResponse(),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    for _ in range(3):
        _ = connection.get(Test_CID)

    _, second, third = endpoint.get_requests(path)

    assert second.get_header('Cookie') == 'session_id=session.first'
    assert third.get_header('Cookie') == 'session_id=session.second'

# ################################################################################################################################

def test_cookie_sent_with_other_methods(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A cookie set in a response to one method is sent with requests of other methods.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.7e3f5b2d'), EndpointResponse()])

    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.post(Test_CID, 'Request body')
    _ = connection.delete(Test_CID)

    _, post, delete = endpoint.get_requests(path)

    assert post.get_header('Cookie') == 'session_id=session.7e3f5b2d'
    assert delete.get_header('Cookie') == 'session_id=session.7e3f5b2d'

# ################################################################################################################################

def test_cookies_not_shared_between_connections(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A cookie set in a response to one connection is not sent by another connection.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.3f5b2d8a'), EndpointResponse()])

    first_connection = new_connection(server, endpoint.http_base, path)
    second_connection = new_connection(server, endpoint.http_base, path)

    _ = first_connection.get(Test_CID)
    _ = second_connection.get(Test_CID)

    _, second = endpoint.get_requests(path)
    assert second.get_header('Cookie') is None

# ################################################################################################################################

def test_explicit_cookie_header(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An explicit Cookie header of the caller is sent in place of the cookies of the session.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.9a7f1c4e'), EndpointResponse()])

    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, headers={'Cookie': 'tenant=customers.eu'})

    _, second = endpoint.get_requests(path)
    assert second.get_header_list('Cookie') == ['tenant=customers.eu']

# ################################################################################################################################

def test_explicit_empty_cookie_header(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An explicit empty Cookie header of the caller is sent as an empty header in place of the cookies of the session.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.2b5d9a7f'), EndpointResponse()])

    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, headers={'Cookie': ''})

    _, second = endpoint.get_requests(path)
    assert second.get_header_list('Cookie') == ['']

# ################################################################################################################################

def test_session_cookie_kept_after_explicit_header(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A call with an explicit Cookie header leaves the cookies of the session in place for the following calls.
    """
    endpoint.set_responses(path, [_set_cookie('session_id=session.6d8a2b5c'), EndpointResponse()])

    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, headers={'Cookie': 'tenant=customers.eu'})
    _ = connection.get(Test_CID)

    _, _, third = endpoint.get_requests(path)
    assert third.get_header('Cookie') == 'session_id=session.6d8a2b5c'

# ################################################################################################################################
# ################################################################################################################################
