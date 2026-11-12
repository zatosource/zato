# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The body of a request - serialized by the data format of the connection, sent as it is when it already is
# what goes on the wire, and left to the transport for form-urlencoded connections.

# stdlib
from json import loads

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import ContentType, DATA_FORMAT

# Test support
from models import Order
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_dict_serialized_to_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A dict is serialized to JSON for a connection whose data format is JSON, with its length in Content-Length.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)
    data = {'customer_id': 123, 'name': 'John Smith', 'tags': ['first', 'second']}

    _ = connection.post(Test_CID, data)

    request = endpoint.get_request(path)

    assert loads(request.body) == data
    assert request.get_header('Content-Length') == str(len(request.body))

# ################################################################################################################################

def test_list_serialized_to_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A list is serialized to JSON for a connection whose data format is JSON.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)
    data = [{'order_id': 1}, {'order_id': 2}]

    _ = connection.post(Test_CID, data)

    request = endpoint.get_request(path)
    assert loads(request.body) == data

# ################################################################################################################################

def test_model_serialized_to_json(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A model is turned into a dict and serialized to JSON.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)
    order = Order.from_dict({'order_id': 100, 'customer': 'Maria Johnson', 'amount': 249.5})

    _ = connection.post(Test_CID, order)

    request = endpoint.get_request(path)
    assert loads(request.body) == {'order_id': 100, 'customer': 'Maria Johnson', 'amount': 249.5}

# ################################################################################################################################

def test_form_data_url_encoded(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A dict is URL-encoded for a connection whose data format is form data.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.FORM_DATA)

    _ = connection.post(Test_CID, {'name': 'John Smith', 'city': 'Zürich'})

    request = endpoint.get_request(path)
    assert request.body == b'name=John+Smith&city=Z%C3%BCrich'

# ################################################################################################################################

def test_text_sent_as_utf8(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Text is sent as it is, encoded as UTF-8, whatever the data format.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)
    data = '{"name": "Zażółć gęślą jaźń"}'

    _ = connection.post(Test_CID, data)

    request = endpoint.get_request(path)

    assert request.body == data.encode('utf8')
    assert request.get_header('Content-Length') == str(len(data.encode('utf8')))

# ################################################################################################################################

def test_bytes_sent_as_they_are(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Bytes are sent exactly as they are by a connection without a data format.
    """
    connection = new_connection(server, endpoint.http_base, path)
    data = b'\x00\x01\x02 Test binary content \xff\xfe'

    _ = connection.post(Test_CID, data)

    request = endpoint.get_request(path)
    assert request.body == data

# ################################################################################################################################

def test_multipart_encoder_sent_as_it_is(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A multipart encoder is an encoded body already and it is sent as it is, with its own content type.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    fields = {
        'description': 'Test file description',
        'document': ('document.txt', b'Test document content', 'text/plain'),
    }

    encoder = MultipartEncoder(fields=fields)
    content_type = encoder.content_type

    _ = connection.post(Test_CID, encoder, headers={'Content-Type': content_type})

    request = endpoint.get_request(path)

    assert request.get_header('Content-Type') == content_type
    assert b'Test file description' in request.body
    assert b'Test document content' in request.body
    assert b'filename="document.txt"' in request.body

# ################################################################################################################################

def test_form_urlencoded_connection_dict(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A form-urlencoded connection gives a dict to the transport, which encodes it as a form.
    """
    connection = new_connection(server, endpoint.http_base, path, content_type=ContentType.FormURLEncoded)

    _ = connection.post(Test_CID, {'name': 'John Smith', 'customer_id': 123})

    request = endpoint.get_request(path)

    assert request.body == b'name=John+Smith&customer_id=123'
    assert request.get_header_list('Content-Type') == [ContentType.FormURLEncoded]

# ################################################################################################################################

def test_form_urlencoded_connection_text(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A form-urlencoded connection sends text as it is.
    """
    connection = new_connection(server, endpoint.http_base, path, content_type=ContentType.FormURLEncoded)

    _ = connection.post(Test_CID, 'grant_type=client_credentials&scope=read')

    request = endpoint.get_request(path)
    assert request.body == b'grant_type=client_credentials&scope=read'

# ################################################################################################################################

def test_empty_body_on_get(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A GET request has no body and no Content-Length.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)

    assert request.body == b''
    assert request.get_header('Content-Length') is None
    assert request.get_header('Transfer-Encoding') is None

# ################################################################################################################################

def test_empty_body_on_post(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A POST request without a body says that its length is zero.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.post(Test_CID)

    request = endpoint.get_request(path)

    assert request.body == b''
    assert request.get_header('Content-Length') == '0'

# ################################################################################################################################
# ################################################################################################################################
