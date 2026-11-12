# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Connection attributes - the configuration of a connection, its requests session reachable through the connection
# and invoked directly, and the cookies that session keeps shared by direct invocations and by the connection's own calls.

# stdlib
from http.client import OK

# requests
from requests import Session

# Test support
from endpoint import EndpointResponse
from support import Basic_Password, Basic_Username, new_basic_auth_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_config(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The configuration of a connection holds its address and its credentials.
    """
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    assert connection.config['address_host'] == endpoint.http_base
    assert connection.config['address_url_path'] == path
    assert connection.config['username'] == Basic_Username
    assert connection.config['password'] == Basic_Password
    assert connection.address == endpoint.http_base + path

# ################################################################################################################################

def test_impl_is_session(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The implementation of a connection is its requests session.
    """
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    assert isinstance(connection.impl, Session)
    assert connection.impl is connection.session

# ################################################################################################################################

def test_impl_invoked_directly(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A method of the session obtained by name and invoked with a full address sends exactly what it is given.
    """
    endpoint.set_response(path, EndpointResponse(body='Direct response'))

    connection = new_basic_auth_connection(server, endpoint.https_base, path)

    address = endpoint.https_base + path
    func = getattr(connection.impl, 'post')

    response = func(address, data='name=John+Smith', headers={'X-Request-Source': 'direct'}, verify=False)

    assert response.status_code == OK
    assert response.text == 'Direct response'

    request = endpoint.get_request(path)

    assert request.method == 'POST'
    assert request.body == b'name=John+Smith'
    assert request.get_header('X-Request-Source') == 'direct'
    assert request.get_header('X-Zato-CID') is None
    assert request.get_header('Authorization') is None

# ################################################################################################################################

def test_impl_login_cookie(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A cookie set by a login response to a direct invocation is readable through the response, is sent on the following
    direct invocations and on the connection's own calls.
    """
    login_path = path + '/login'
    endpoint.set_response(login_path, EndpointResponse(headers=[('Set-Cookie', 'session_id=session.8b3b9e7d; Path=/')]))

    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    login_response = connection.impl.post(endpoint.http_base + login_path, data='username=john.smith')
    assert login_response.cookies['session_id'] == 'session.8b3b9e7d'

    _ = connection.impl.get(endpoint.http_base + path)
    _ = connection.get(Test_CID)

    direct, own = endpoint.get_requests(path)

    assert direct.get_header('Cookie') == 'session_id=session.8b3b9e7d'
    assert own.get_header('Cookie') == 'session_id=session.8b3b9e7d'
    assert own.get_header('X-Zato-CID') == Test_CID

# ################################################################################################################################
# ################################################################################################################################
