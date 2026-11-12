# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Responses - the status, headers, body and metadata of a response, its body parsed according to the data format
# of the connection or the content type of the response, and the attributes describing the request it answers.

# stdlib
from datetime import timedelta
from http.client import CREATED, INTERNAL_SERVER_ERROR, NO_CONTENT, NOT_FOUND
from json import dumps

# pytest
import pytest

# requests
from requests.exceptions import HTTPError

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.exception import BadRequest

# Test support
from endpoint import EndpointResponse
from models import Customer
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# A customer document as an endpoint returns it
_customer = {'customer_id': 123, 'name': 'John Smith'}
_customer_json = dumps(_customer)

# The content types of the responses
_json_content_type = ('Content-Type', 'application/json')
_text_content_type = ('Content-Type', 'text/plain; charset=utf-8')

# ################################################################################################################################
# ################################################################################################################################

def test_status_reason_and_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The status code, the reason, the text and the bytes of the body are what the endpoint sent.
    """
    endpoint.set_response(path, EndpointResponse(CREATED, 'Customer created', headers=[_text_content_type]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.status_code == CREATED
    assert response.ok is True
    assert response.reason == 'Created'
    assert response.text == 'Customer created'
    assert response.content == b'Customer created'

# ################################################################################################################################

def test_custom_reason(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A reason phrase other than the standard one is returned as the endpoint sent it.
    """
    endpoint.set_response(path, EndpointResponse(NOT_FOUND, reason='Customer Not Found'))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.status_code == NOT_FOUND
    assert response.ok is False
    assert response.reason == 'Customer Not Found'

# ################################################################################################################################

def test_headers(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The headers of a response are looked up regardless of case, and repeated headers are joined into one value.
    """
    headers = [
        ('X-Request-Id', 'request.7d1a5c2f'),
        ('X-Item', 'first'),
        ('X-Item', 'second'),
    ]
    endpoint.set_response(path, EndpointResponse(headers=headers))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.headers['X-Request-Id'] == 'request.7d1a5c2f'
    assert response.headers['x-request-id'] == 'request.7d1a5c2f'
    assert response.headers['X-REQUEST-ID'] == 'request.7d1a5c2f'
    assert response.headers['X-Item'] == 'first, second'
    assert response.headers.get('X-Missing') is None

# ################################################################################################################################

def test_json_method(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The json method parses a JSON body.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[_json_content_type]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.json() == _customer

# ################################################################################################################################

def test_elapsed(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The elapsed time covers the time the endpoint took to answer.
    """
    endpoint.set_response(path, EndpointResponse(delay=0.2))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert isinstance(response.elapsed, timedelta)
    assert response.elapsed >= timedelta(seconds=0.2)

# ################################################################################################################################

def test_raise_for_status(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ raise_for_status raises HTTPError for an error response and does nothing for a successful one.
    """
    endpoint.set_responses(path, [EndpointResponse(), EndpointResponse(INTERNAL_SERVER_ERROR)])

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    response.raise_for_status()

    response = connection.get(Test_CID)

    with pytest.raises(HTTPError) as info:
        response.raise_for_status()

    assert info.value.response is response

# ################################################################################################################################

def test_cookies(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The cookies an endpoint sets are available through the cookies of the response.
    """
    headers = [
        ('Set-Cookie', 'session_id=session.4e8b3b9e; Path=/'),
        ('Set-Cookie', 'region=eu-central; Path=/'),
    ]
    endpoint.set_response(path, EndpointResponse(headers=headers))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.cookies['session_id'] == 'session.4e8b3b9e'
    assert response.cookies['region'] == 'eu-central'

# ################################################################################################################################

def test_url(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The URL of a response is the address the request was sent to, with its query string.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, {'page': 2, 'name': 'John Smith'})

    assert response.url == f'{endpoint.http_base}{path}?page=2&name=John+Smith'

# ################################################################################################################################

@pytest.mark.parametrize(('content_type', 'encoding'), [
    ('text/plain; charset=utf-8', 'utf-8'),
    ('text/plain; charset=iso-8859-2', 'iso-8859-2'),
    ('text/plain', 'ISO-8859-1'),
    ('application/json', 'utf-8'),
])
def test_encoding(endpoint:'TestEndpoint', server:'ServerStub', path:'str', content_type:'str', encoding:'str') -> 'None':
    """ The encoding of a response is the one its content type names, or the default of that content type.
    """
    endpoint.set_response(path, EndpointResponse(headers=[('Content-Type', content_type)]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.encoding == encoding

# ################################################################################################################################

def test_non_utf8_charset(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body in a charset other than UTF-8 is decoded according to that charset.
    """
    text = 'Łódź, Kraków, Gdańsk'
    body = text.encode('iso-8859-2')

    endpoint.set_response(path, EndpointResponse(body=body, headers=[('Content-Type', 'text/plain; charset=iso-8859-2')]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.content == body
    assert response.text == text
    assert response.data == text

# ################################################################################################################################

def test_data_as_text(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data of a response that is not JSON is its text.
    """
    endpoint.set_response(path, EndpointResponse(body='Plain text response', headers=[_text_content_type]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.data == 'Plain text response'

# ################################################################################################################################

def test_data_parsed_by_data_format(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data of a response of a JSON connection is parsed as JSON whatever its content type.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[_text_content_type]))

    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    response = connection.get(Test_CID)
    assert response.data == _customer

# ################################################################################################################################

def test_data_parsed_by_content_type(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data of a JSON response is parsed as JSON whatever the data format of the connection.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[('Content-Type', 'application/json; charset=utf-8')]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.data == _customer

# ################################################################################################################################

def test_invalid_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A JSON response whose body is not JSON raises BadRequest naming the body.
    """
    endpoint.set_response(path, EndpointResponse(body='Not a JSON document', headers=[_json_content_type]))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BadRequest) as info:
        _ = connection.get(Test_CID)

    assert info.value.args[0].startswith('Could not parse JSON response `Not a JSON document`; e:`')

# ################################################################################################################################

def test_empty_json_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An empty body of a JSON connection is parsed into an empty string.
    """
    endpoint.set_response(path, EndpointResponse())

    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    response = connection.get(Test_CID)

    assert response.content == b''
    assert response.data == ''

# ################################################################################################################################

def test_no_content(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A response without content has an empty body.
    """
    endpoint.set_response(path, EndpointResponse(NO_CONTENT))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.status_code == NO_CONTENT
    assert response.content == b''
    assert response.text == ''

# ################################################################################################################################

def test_model(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data of a response is mapped to the model the call names.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[_json_content_type]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, model=Customer)

    assert isinstance(response.data, Customer)
    assert response.data.customer_id == 123
    assert response.data.name == 'John Smith'

# ################################################################################################################################

def test_request_attributes(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A response names the method, the address and the query string of the request it answers.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.post(Test_CID, 'Request body', {'page': 2})

    assert response.zato_method == 'POST'
    assert response.zato_address == endpoint.http_base + path
    assert response.zato_qs_params == {'page': 2}

# ################################################################################################################################

def test_chunked_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body sent with chunked transfer encoding is returned whole.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[_json_content_type], is_chunked=True))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.headers['Transfer-Encoding'] == 'chunked'
    assert response.text == _customer_json
    assert response.data == _customer

# ################################################################################################################################

def test_gzip_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body compressed with gzip is returned decompressed.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, headers=[_json_content_type], is_gzip=True))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.headers['Content-Encoding'] == 'gzip'
    assert response.text == _customer_json
    assert response.data == _customer

# ################################################################################################################################

def test_gzip_chunked_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body compressed with gzip and sent with chunked transfer encoding is returned decompressed and whole.
    """
    endpoint.set_response(path, EndpointResponse(body=_customer_json, is_gzip=True, is_chunked=True))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.text == _customer_json

# ################################################################################################################################

def test_large_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body larger than one read of a socket is returned whole.
    """
    body = b'0123456789abcdef' * 131072
    endpoint.set_response(path, EndpointResponse(body=body))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.content == body

# ################################################################################################################################

def test_large_body_tls(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body larger than one TLS record is returned whole.
    """
    body = b'0123456789abcdef' * 131072
    endpoint.set_response(path, EndpointResponse(body=body))

    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    response = connection.get(Test_CID)
    assert response.content == body

# ################################################################################################################################
# ################################################################################################################################
