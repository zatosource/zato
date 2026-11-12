# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The declarative profile of a connection - the method, the query string, the path parameters, the headers
# and the body a request takes from the connection's configuration for whatever the caller did not give,
# with JSONata values evaluated against the data the caller gave.

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import DATA_FORMAT, HTTP_SOAP

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_text = _invocation.ValueMode.Text
_jsonata = _invocation.ValueMode.JSONata

# ################################################################################################################################
# ################################################################################################################################

def _rows(*rows:'tuple[str, str, str]') -> 'str':
    """ Returns the JSON of declarative rows, each given as a key, a value and a mode.
    """
    items:'anylist' = []

    for key, value, mode in rows:
        item = {
            'key': key,
            'value': value,
            'mode': mode,
        }
        items.append(item)

    out = dumps(items)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_everything_from_profile(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A call that gives nothing takes the method, the query string, the path parameters, the headers and the body from the profile.
    """
    profile = {
        _invocation.Field_Request_Method: 'POST',
        _invocation.Field_Request_Query_String: _rows(('page', '1', _text), ('limit', '10', _text)),
        _invocation.Field_Request_Path_Params: _rows(('customer_id', 'C-100', _text)),
        _invocation.Field_Request_Headers: _rows(('X-Tenant', 'tenant-a', _text)),
        _invocation.Field_Request_Data: 'Test profile body',
    }

    connection = new_connection(server, endpoint.http_base, path + '/customers/{customer_id}', **profile)

    _ = connection.rest_invoke(Test_CID)

    request = endpoint.get_request(path + '/customers/C-100')

    assert request.method == 'POST'
    assert request.query == 'page=1&limit=10'
    assert request.get_header('X-Tenant') == 'tenant-a'
    assert request.body == b'Test profile body'

# ################################################################################################################################

def test_explicit_arguments_win_per_key(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An explicit query parameter, header or body wins over the profile's one, and the profile fills in the rest.
    """
    profile = {
        _invocation.Field_Request_Query_String: _rows(('page', '1', _text), ('limit', '10', _text)),
        _invocation.Field_Request_Headers: _rows(('X-Tenant', 'tenant-a', _text), ('X-Source', 'profile', _text)),
        _invocation.Field_Request_Data: 'Test profile body',
    }

    connection = new_connection(server, endpoint.http_base, path, **profile)

    params = {'page': '5'}
    headers = {'X-Source': 'caller'}

    _ = connection.post(Test_CID, 'Test caller body', params, headers=headers)

    request = endpoint.get_request(path)

    assert request.query == 'page=5&limit=10'
    assert request.get_header('X-Tenant') == 'tenant-a'
    assert request.get_header('X-Source') == 'caller'
    assert request.body == b'Test caller body'

    assert params == {'page': '5'}
    assert headers == {'X-Source': 'caller'}

# ################################################################################################################################

def test_explicit_method_wins(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A method of the connection named in the call wins over the method of the profile.
    """
    profile = {
        _invocation.Field_Request_Method: 'POST',
    }

    connection = new_connection(server, endpoint.http_base, path, **profile)

    _ = connection.put(Test_CID, 'Test caller body')

    request = endpoint.get_request(path)
    assert request.method == 'PUT'

# ################################################################################################################################

def test_jsonata_values(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ JSONata values of the query string and of the headers are evaluated against the data the caller gave.
    """
    profile = {
        _invocation.Field_Request_Query_String: _rows(('customer', 'customer.name', _jsonata), ('source', 'api', _text)),
        _invocation.Field_Request_Headers: _rows(('X-Customer-ID', 'customer.id', _jsonata)),
    }

    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON, **profile)
    data = {'customer': {'id': 'C-200', 'name': 'John Smith'}}

    _ = connection.post(Test_CID, data)

    request = endpoint.get_request(path)

    assert request.query == 'customer=John+Smith&source=api'
    assert request.get_header('X-Customer-ID') == 'C-200'
    assert loads(request.body) == data

# ################################################################################################################################

def test_jsonata_body(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A JSONata body reshapes the data the caller gave on every call.
    """
    profile = {
        _invocation.Field_Request_Data: '{"id": customer.id, "full_name": customer.name}',
        _invocation.Field_Request_Data_Mode: _jsonata,
    }

    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON, **profile)

    _ = connection.post(Test_CID, {'customer': {'id': 'C-300', 'name': 'Maria Johnson'}})
    _ = connection.post(Test_CID, {'customer': {'id': 'C-301', 'name': 'Anna Miller'}})

    first, second = endpoint.get_requests(path)

    assert loads(first.body) == {'id': 'C-300', 'full_name': 'Maria Johnson'}
    assert loads(second.body) == {'id': 'C-301', 'full_name': 'Anna Miller'}

# ################################################################################################################################

def test_text_body_fills_in_empty_one_only(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A text body of the profile is sent when the caller gave no body and the caller's body is sent otherwise.
    """
    profile = {
        _invocation.Field_Request_Data: 'Test profile body',
        _invocation.Field_Request_Data_Mode: _text,
    }

    connection = new_connection(server, endpoint.http_base, path, **profile)

    _ = connection.post(Test_CID)
    _ = connection.post(Test_CID, 'Test caller body')

    first, second = endpoint.get_requests(path)

    assert first.body == b'Test profile body'
    assert second.body == b'Test caller body'

# ################################################################################################################################
# ################################################################################################################################
