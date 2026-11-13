# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How the response a service produces is serialized and sent.

# stdlib
import json
from http.client import CREATED, OK, UNPROCESSABLE_ENTITY

# Zato
from channel_definitions import Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_customer = {
    'customer_id': 123,
    'name': 'John Smith',
    'city': 'Zürich',
    'is_active': True,
    'balance': 1.5,
    'note': None,
    'tags': ['retail', 'priority'],
    'address': {'street': 'Main Street', 'number': 10},
}

_customer_list = [{'customer_id': 1, 'name': 'John Smith'}, {'customer_id': 2, 'name': 'Mary Johnson'}]

_customer_model_list = [
    {'customer_id': 1, 'name': 'John Smith', 'is_active': True},
    {'customer_id': 2, 'name': 'Mary Johnson', 'is_active': False},
]

# ################################################################################################################################
# ################################################################################################################################

def _json_bytes(value:'any_') -> 'bytes':
    """ Returns the bytes a value is serialized to in a JSON response.
    """
    out = json.dumps(value, indent=4).encode('utf-8')
    return out

# ################################################################################################################################

def _assert_response(response:'HTTPResponse', status:'int', reason:'str', content_type:'str', body:'bytes') -> 'None':
    assert response.status == status, response.body
    assert response.reason == reason
    assert response.headers['content-type'] == content_type
    assert response.headers['content-length'] == str(len(body))
    assert response.body == body

# ################################################################################################################################
# ################################################################################################################################

def test_dict(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Dict)
    _assert_response(response, OK, 'OK', 'application/json', _json_bytes(_customer))

# ################################################################################################################################

def test_list(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_List)
    _assert_response(response, OK, 'OK', 'application/json', _json_bytes(_customer_list))

# ################################################################################################################################

def test_string(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_String)
    _assert_response(response, OK, 'OK', 'application/json', b'Customer record accepted')

# ################################################################################################################################

def test_bytes(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Bytes)
    _assert_response(response, OK, 'OK', 'application/json', b'"Customer record accepted"')

# ################################################################################################################################

def test_none(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_None)
    _assert_response(response, OK, 'OK', 'application/json', b'')

# ################################################################################################################################

def test_dot_access(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Dot_Access)
    expected = {'customer': {'details': {'customer_id': 123}}}

    _assert_response(response, OK, 'OK', 'application/json', _json_bytes(expected))

# ################################################################################################################################

def test_model(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Model)
    expected = {'customer_id': 123, 'name': 'John Smith', 'is_active': True}

    _assert_response(response, OK, 'OK', 'application/json', _json_bytes(expected))

# ################################################################################################################################

def test_model_list(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Model_List)
    _assert_response(response, OK, 'OK', 'application/json', _json_bytes(_customer_model_list))

# ################################################################################################################################

def test_status_and_headers(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Status_Headers)

    _assert_response(response, CREATED, 'Created', 'application/json', _json_bytes({'customer_id': 123}))
    assert response.get_header_values('X-Customer-ID') == ['123']
    assert response.get_header_values('Location') == ['/customers/123']

# ################################################################################################################################

def test_content_type_set_by_service(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Content_Type)
    _assert_response(response, OK, 'OK', 'application/xml', b'<customer><id>123</id></customer>')

# ################################################################################################################################

def test_error_status_set_by_service(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Error_Status)
    expected = _json_bytes({'error': 'Customer ID is invalid'})

    _assert_response(response, UNPROCESSABLE_ENTITY, 'Unprocessable Entity', 'application/json', expected)

# ################################################################################################################################

def test_default_content_type_per_data_format(client:'ChannelClient') -> 'None':

    for path in (Paths.Response_Dict_XML, Paths.Response_Dict_No_Format):
        response = client.get(path)
        _assert_response(response, OK, 'OK', 'text/plain', _json_bytes(_customer))

# ################################################################################################################################

def test_response_header_names(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Response_Dict)
    names = []

    for name, _ in response.header_list:
        names.append(name)

    assert names == ['content-type', 'content-length', 'connection']
    assert response.headers['connection'] == 'close'

# ################################################################################################################################
# ################################################################################################################################
