# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How the body of a request reaches a service, per data format and per input declaration.

# stdlib
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, OK

# Zato
from channel_definitions import Paths
from channel_suite import assert_json_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_json_headers = {'Content-Type': 'application/json'}
_xml_headers = {'Content-Type': 'application/xml'}
_form_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# ################################################################################################################################
# ################################################################################################################################

def _post(client:'ChannelClient', path:'str', body:'bytes', headers:'anydict | None' = None) -> 'anydict':
    response = client.request('POST', path, headers=headers, body=body)
    assert response.status == OK, response.body

    out = response.json()
    return out

# ################################################################################################################################

def _bytes_value(text:'str') -> 'anydict':
    out = {'type': 'bytes', 'value': text}
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_json_object(client:'ChannelClient') -> 'None':
    body = b'{"customer_id": 123, "name": "John Smith", "city": "Z\\u00fcrich", "is_active": true, "note": null}'
    data = _post(client, Paths.Echo, body, _json_headers)

    expected_fields = {
        'customer_id': {'type': 'int', 'value': 123},
        'name': {'type': 'str', 'value': 'John Smith'},
        'city': {'type': 'str', 'value': 'Zürich'},
        'is_active': {'type': 'bool', 'value': True},
        'note': {'type': 'NoneType', 'value': None},
    }

    assert data['payload'] == {'type': 'dict', 'value': expected_fields}
    assert data['input'] == {'type': 'ServiceInput', 'value': expected_fields}
    assert data['raw_request'] == _bytes_value(body.decode('utf-8'))
    assert data['POST'] == {}

# ################################################################################################################################

def test_json_list(client:'ChannelClient') -> 'None':
    body = b'[1, "two", {"three": 3}]'
    data = _post(client, Paths.Echo, body, _json_headers)

    expected = {'type': 'list', 'value': [
        {'type': 'int', 'value': 1},
        {'type': 'str', 'value': 'two'},
        {'type': 'dict', 'value': {'three': {'type': 'int', 'value': 3}}},
    ]}

    assert data['payload'] == expected
    assert data['input'] == expected

# ################################################################################################################################

def test_json_string(client:'ChannelClient') -> 'None':
    data = _post(client, Paths.Echo, b'"Customer record"', _json_headers)

    assert data['payload'] == {'type': 'str', 'value': 'Customer record'}
    assert data['input'] == {'type': 'str', 'value': 'Customer record'}

# ################################################################################################################################

def test_empty_body(client:'ChannelClient') -> 'None':
    data = _post(client, Paths.Echo, b'', _json_headers)

    assert data['payload'] == {'type': 'str', 'value': ''}
    assert data['input'] == {'type': 'ServiceInput', 'value': {}}
    assert data['raw_request'] == _bytes_value('')

# ################################################################################################################################

def test_invalid_json(client:'ChannelClient') -> 'None':
    body = b'{"customer_id": '
    data = _post(client, Paths.Echo, body, _json_headers)

    assert data['payload'] == _bytes_value('{"customer_id": ')
    assert data['input'] == _bytes_value('{"customer_id": ')
    assert data['raw_request'] == _bytes_value('{"customer_id": ')

# ################################################################################################################################

def test_non_utf8_body(client:'ChannelClient') -> 'None':
    body = b'\xff\xfe\x00customer'
    data = _post(client, Paths.Echo, body, _json_headers)

    expected = _bytes_value('\ufffd\ufffd\x00customer')

    assert data['payload'] == expected
    assert data['raw_request'] == expected

# ################################################################################################################################

def test_form_body_on_json_channel(client:'ChannelClient') -> 'None':
    data = _post(client, Paths.Echo, b'customer_id=123', _form_headers)

    assert data['payload'] == _bytes_value('customer_id=123')
    assert data['POST'] == {}

# ################################################################################################################################

def test_xml_body(client:'ChannelClient') -> 'None':
    body = b'<customer><id>123</id><name>John Smith</name></customer>'
    data = _post(client, Paths.Echo_XML, body, _xml_headers)

    assert data['payload'] == _bytes_value(body.decode('utf-8'))
    assert data['input'] == _bytes_value(body.decode('utf-8'))
    assert data['data_format'] == 'xml'

# ################################################################################################################################

def test_malformed_xml_body(client:'ChannelClient') -> 'None':
    data = _post(client, Paths.Echo_XML, b'<customer><id>123', _xml_headers)
    assert data['payload'] == _bytes_value('<customer><id>123')

# ################################################################################################################################

def test_form_channel(client:'ChannelClient') -> 'None':
    body = b'customer_id=123&name=John+Smith&tag=retail&tag=priority'
    data = _post(client, Paths.Echo_Form, body, _form_headers)

    expected_fields = {
        'customer_id': {'type': 'str', 'value': '123'},
        'name': {'type': 'str', 'value': 'John Smith'},
        'tag': {'type': 'str', 'value': 'priority'},
    }

    assert data['payload'] == {'type': 'dict', 'value': expected_fields}
    assert data['input'] == {'type': 'ServiceInput', 'value': expected_fields}
    assert data['POST'] == {'customer_id': '123', 'name': 'John Smith', 'tag': 'priority'}

# ################################################################################################################################

def test_channel_without_data_format(client:'ChannelClient') -> 'None':

    data = _post(client, Paths.Echo_No_Format, b'{"customer_id": 123}', _json_headers)
    assert data['payload'] == _bytes_value('{"customer_id": 123}')
    assert data['input'] == _bytes_value('{"customer_id": 123}')
    assert data['POST'] == {'{"customer_id": 123}': ''}

    data = _post(client, Paths.Echo_No_Format, b'Customer record', {'Content-Type': 'text/plain'})
    assert data['payload'] == _bytes_value('Customer record')

# ################################################################################################################################

def test_declared_input(client:'ChannelClient') -> 'None':

    # All elements given ..
    body = b'{"customer_id": 123, "name": "John Smith", "segment": "retail"}'
    data = _post(client, Paths.Input_Declared, body, _json_headers)
    assert data == {
        'customer_id': {'type': 'int', 'value': 123},
        'name': {'type': 'str', 'value': 'John Smith'},
        'segment': {'type': 'str', 'value': 'retail'},
    }

    # .. a typed element converted and an optional one absent ..
    body = b'{"customer_id": "123", "name": "John Smith"}'
    data = _post(client, Paths.Input_Declared, body, _json_headers)
    assert data == {
        'customer_id': {'type': 'int', 'value': 123},
        'name': {'type': 'str', 'value': 'John Smith'},
        'segment': {'type': 'NoneType', 'value': None},
    }

    # .. and the elements given in the query string.
    response = client.get(Paths.Input_Declared + '?customer_id=5&name=Mary+Johnson')
    assert response.json() == {
        'customer_id': {'type': 'int', 'value': 5},
        'name': {'type': 'str', 'value': 'Mary Johnson'},
        'segment': {'type': 'NoneType', 'value': None},
    }

# ################################################################################################################################

def test_declared_input_missing_element(client:'ChannelClient') -> 'None':

    for body in (b'{"name": "John Smith"}', b'{}'):
        response = client.request('POST', Paths.Input_Declared, headers=_json_headers, body=body)
        _ = assert_json_error(response, INTERNAL_SERVER_ERROR, ['Missing required input element: customer_id'])

# ################################################################################################################################

def test_declared_input_invalid_type(client:'ChannelClient') -> 'None':
    body = b'{"customer_id": "abc", "name": "John Smith"}'
    response = client.request('POST', Paths.Input_Declared, headers=_json_headers, body=body)

    _ = assert_json_error(response, INTERNAL_SERVER_ERROR, ["invalid literal for int() with base 10: 'abc'"])

# ################################################################################################################################

def test_model_input(client:'ChannelClient') -> 'None':

    for body in (b'{"customer_id": 123, "name": "John Smith"}', b'{"customer_id": "123", "name": "John Smith"}'):
        data = _post(client, Paths.Input_Model, body, _json_headers)
        assert data == {
            'type': 'CustomerRequest',
            'customer_id': {'type': 'int', 'value': 123},
            'name': {'type': 'str', 'value': 'John Smith'},
        }

# ################################################################################################################################

def test_model_input_missing_field(client:'ChannelClient') -> 'None':
    response = client.request('POST', Paths.Input_Model, headers=_json_headers, body=b'{"name": "John Smith"}')
    _ = assert_json_error(response, BAD_REQUEST, 'Element missing: /customer_id')

# ################################################################################################################################

def test_model_input_invalid_type(client:'ChannelClient') -> 'None':
    body = b'{"customer_id": "abc", "name": "John Smith"}'
    response = client.request('POST', Paths.Input_Model, headers=_json_headers, body=body)

    reason = "invalid literal for int() with base 10: 'abc'"
    expected = f"Value `'abc'` of field customer_id could not be parsed -> {reason} -> {{'customer_id': 'abc', 'name': 'John Smith'}}"

    _ = assert_json_error(response, INTERNAL_SERVER_ERROR, [expected])

# ################################################################################################################################
# ################################################################################################################################
