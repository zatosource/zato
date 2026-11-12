# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Pass-through arguments - keyword arguments of the requests library given to a call reaching the transport
# and producing the request and the response the requests library produces for them.

# stdlib
from http.client import OK
from json import loads

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

# The content type a connection without a data format sends when the caller names none
_default_content_type = 'text/plain'

# ################################################################################################################################
# ################################################################################################################################

def test_stream(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A streamed response is returned with its whole body.
    """
    endpoint.set_response(path, EndpointResponse(body='Streamed response body', is_chunked=True))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, stream=True)

    assert response.status_code == OK
    assert response.text == 'Streamed response body'
    assert response.content == b'Streamed response body'

    request = endpoint.get_request(path)
    assert request.method == 'GET'

# ################################################################################################################################

def test_cookies(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Cookies given to a call are sent in the Cookie header.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, cookies={'session_id': 'session.9e7d1a5c', 'region': 'eu-central'})

    request = endpoint.get_request(path)
    assert request.get_header('Cookie') == 'session_id=session.9e7d1a5c; region=eu-central'

# ################################################################################################################################

def test_files(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Files given to a call are sent in a multipart body along with the fields of the data, under the content type
    of the connection.
    """
    connection = new_connection(server, endpoint.http_base, path)

    files = {'document': ('report.txt', b'Quarterly report content', 'text/plain')}
    _ = connection.post(Test_CID, {'title': 'Quarterly report'}, files=files)

    request = endpoint.get_request(path)

    assert request.get_header('Content-Type') == _default_content_type
    assert b'Content-Disposition: form-data; name="title"' in request.body
    assert b'Quarterly report\r\n' in request.body
    assert b'Content-Disposition: form-data; name="document"; filename="report.txt"' in request.body
    assert b'Quarterly report content' in request.body

# ################################################################################################################################

def test_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A JSON document given to a call without a body is sent as the body, under the content type of the connection.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.post(Test_CID, json={'customer_id': 123, 'name': 'John Smith'})

    request = endpoint.get_request(path)

    assert request.get_header('Content-Type') == _default_content_type
    assert loads(request.body) == {'customer_id': 123, 'name': 'John Smith'}

# ################################################################################################################################

def test_proxies(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A request of a call given a proxy is sent to the proxy with the absolute address of the endpoint as its target.
    """
    address_host = 'http://customers.example.invalid'
    connection = new_connection(server, address_host, path)

    response = connection.get(Test_CID, {'page': 2}, proxies={'http': endpoint.http_base})

    assert response.status_code == OK

    target_path = address_host + path
    request = endpoint.get_request(target_path)

    assert request.target == f'{target_path}?page=2'
    assert request.get_header('Host') == 'customers.example.invalid'

# ################################################################################################################################
# ################################################################################################################################
