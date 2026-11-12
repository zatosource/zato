# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The methods of a connection - each one sends its HTTP method, with the body and the query string given
# positionally or by keyword, alone or together with the caller's headers.

# stdlib
from json import loads

# pytest
import pytest

# Zato
from zato.common.api import DATA_FORMAT

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The methods that take a body, each with the HTTP method it sends
_methods_with_body = [
    ('post', 'POST'),
    ('send', 'POST'),
    ('put', 'PUT'),
    ('patch', 'PATCH'),
    ('delete', 'DELETE'),
    ('options', 'OPTIONS'),
]

# The methods whose body and query string can be given positionally
_methods_positional = [
    ('post', 'POST'),
    ('put', 'PUT'),
    ('patch', 'PATCH'),
    ('delete', 'DELETE'),
]

# What the combination tests send
_body = 'Test request body'
_params = {'page': '2', 'filter': 'active'}
_query = 'page=2&filter=active'
_headers = {'X-Custom-Header': 'Test value'}

# ################################################################################################################################
# ################################################################################################################################

def test_get(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ get sends a GET request.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.method == 'GET'

# ################################################################################################################################

@pytest.mark.parametrize(('method_name', 'http_method'), _methods_with_body)
def test_method_with_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method_name:'str', http_method:'str') -> 'None':
    """ Each method that takes a body sends its HTTP method with the body.
    """
    connection = new_connection(server, endpoint.http_base, path)
    method = getattr(connection, method_name)

    _ = method(Test_CID, _body)

    request = endpoint.get_request(path)

    assert request.method == http_method
    assert request.body == _body.encode('utf8')

# ################################################################################################################################

def test_rest_invoke_method_from_profile(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ rest_invoke takes the HTTP method from the declarative profile of the connection.
    """
    connection = new_connection(server, endpoint.http_base, path, request_method='PUT')

    _ = connection.rest_invoke(Test_CID, _body)

    request = endpoint.get_request(path)

    assert request.method == 'PUT'
    assert request.body == _body.encode('utf8')

# ################################################################################################################################

def test_rest_invoke_method_of_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ rest_invoke without a method in the declarative profile uses the method of the connection.
    """
    connection = new_connection(server, endpoint.http_base, path, method='DELETE')

    _ = connection.rest_invoke(Test_CID)

    request = endpoint.get_request(path)
    assert request.method == 'DELETE'

# ################################################################################################################################

def test_get_positional_query_string(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The query string given as the second positional argument of get is the same as one given by keyword.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, _params)
    _ = connection.get(Test_CID, params=_params)

    positional, keyword = endpoint.get_requests(path)

    assert positional.query == _query
    assert keyword.query == _query

# ################################################################################################################################

@pytest.mark.parametrize(('method_name', 'http_method'), _methods_positional)
def test_positional_body_and_query_string(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    method_name:'str',
    http_method:'str',
    ) -> 'None':
    """ The body given as the second positional argument and the query string given as the third one
    are the same as the ones given by keyword.
    """
    connection = new_connection(server, endpoint.http_base, path)
    method = getattr(connection, method_name)

    _ = method(Test_CID, _body, _params)
    _ = method(Test_CID, data=_body, params=_params)

    positional, keyword = endpoint.get_requests(path)

    for item in (positional, keyword):
        assert item.method == http_method
        assert item.query == _query
        assert item.body == _body.encode('utf8')

# ################################################################################################################################

@pytest.mark.parametrize(('method_name', 'http_method'), _methods_with_body)
def test_combinations_with_body(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    method_name:'str',
    http_method:'str',
    ) -> 'None':
    """ Each method that takes a body is invoked with the CID only, with the body, the query string and the headers
    one at a time, and with all three together.
    """
    connection = new_connection(server, endpoint.http_base, path)
    method = getattr(connection, method_name)

    _ = method(Test_CID)
    _ = method(Test_CID, data=_body)
    _ = method(Test_CID, params=_params)
    _ = method(Test_CID, headers=_headers)
    _ = method(Test_CID, data=_body, params=_params, headers=_headers)

    cid_only, body_only, params_only, headers_only, everything = endpoint.get_requests(path)

    for item in (cid_only, body_only, params_only, headers_only, everything):
        assert item.method == http_method

    assert cid_only.body == b''
    assert cid_only.query == ''
    assert cid_only.get_header('X-Custom-Header') is None

    assert body_only.body == _body.encode('utf8')
    assert body_only.query == ''

    assert params_only.body == b''
    assert params_only.query == _query

    assert headers_only.body == b''
    assert headers_only.get_header('X-Custom-Header') == 'Test value'

    assert everything.body == _body.encode('utf8')
    assert everything.query == _query
    assert everything.get_header('X-Custom-Header') == 'Test value'

# ################################################################################################################################

def test_get_combinations(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ get is invoked with the CID only, with the query string, with the headers and with both.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID, params=_params)
    _ = connection.get(Test_CID, headers=_headers)
    _ = connection.get(Test_CID, params=_params, headers=_headers)

    cid_only, params_only, headers_only, everything = endpoint.get_requests(path)

    assert cid_only.target == path
    assert params_only.query == _query
    assert headers_only.query == ''
    assert headers_only.get_header('X-Custom-Header') == 'Test value'
    assert everything.query == _query
    assert everything.get_header('X-Custom-Header') == 'Test value'

# ################################################################################################################################

def test_patch_json_with_query_string(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ patch sends a JSON body together with a query string.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    _ = connection.patch(Test_CID, data={'status': 'shipped'}, params={'object_suffix': 'orders'})

    request = endpoint.get_request(path)

    assert request.method == 'PATCH'
    assert request.query == 'object_suffix=orders'
    assert loads(request.body) == {'status': 'shipped'}

# ################################################################################################################################

def test_put_and_get_without_body_or_query_string(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ put and get invoked with nothing but the CID send no body and no query string.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.put(Test_CID)
    _ = connection.get(Test_CID)

    put_request, get_request = endpoint.get_requests(path)

    assert put_request.method == 'PUT'
    assert put_request.target == path
    assert put_request.body == b''
    assert put_request.get_header('Content-Length') == '0'

    assert get_request.method == 'GET'
    assert get_request.target == path
    assert get_request.body == b''

# ################################################################################################################################
# ################################################################################################################################
