# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Server-level invocation - outgoing REST connections with Basic Auth and with an OAuth bearer token, imported through
# enmasse into a running server and invoked from a deployed service, with what the test endpoint received and what
# the service returned both asserted.

# stdlib
from base64 import b64encode
from http.client import NOT_FOUND, OK
from json import dumps, loads

# Test support
from endpoint import EndpointResponse
from live_config import Basic_Outconn_Name, Basic_Password, Basic_Username, Invoke_Service_Name, OAuth_Outconn_Name, \
    OAuth_Path, OAuth_Token, OAuth_Token_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    from endpoint import RecordedRequest, TestEndpoint
    from live_config import InvokeClient

# ################################################################################################################################
# ################################################################################################################################

# The Authorization header the Basic Auth connection sends
_basic_authorization = 'Basic ' + b64encode(f'{Basic_Username}:{Basic_Password}'.encode('utf8')).decode('ascii')

# ################################################################################################################################
# ################################################################################################################################

def _invoke(invoke_client:'InvokeClient', conn_name:'str', method:'str', data:'any_'=None, params:'anydict | None'=None) -> 'anydict':
    """ Invokes the connection through the deployed service and returns what the service reported.
    """
    if params is None:
        params = {}

    payload = {
        'conn_name': conn_name,
        'method': method,
        'data': data,
        'params': params,
    }

    out = invoke_client.invoke(Invoke_Service_Name, payload)
    return out

# ################################################################################################################################

def _get_request(endpoint:'TestEndpoint', path:'str', cid:'str') -> 'RecordedRequest':
    """ Returns the only request received for the path under the given correlation ID.
    """
    matching:'list[RecordedRequest]' = []

    for request in endpoint.get_requests(path):
        if request.get_header('X-Zato-CID') == cid:
            matching.append(request)

    out, = matching
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_basic_auth_get(endpoint:'TestEndpoint', invoke_client:'InvokeClient') -> 'None':
    """ A GET of the Basic Auth connection fills its path template, sends the query string and the credentials,
    and the service returns the parsed response.
    """
    path = '/live/basic/customers/123'
    customer = {'customer_id': 123, 'name': 'John Smith'}

    endpoint.set_response(path, EndpointResponse(body=dumps(customer), headers=[('Content-Type', 'application/json')]))

    result = _invoke(invoke_client, Basic_Outconn_Name, 'get', params={'customer_id': 123, 'page': 2})

    assert result['error'] == ''
    assert result['status_code'] == OK
    assert result['data'] == customer

    request = _get_request(endpoint, path, result['cid'])

    assert request.method == 'GET'
    assert request.query == 'page=2'
    assert request.get_header('Authorization') == _basic_authorization

# ################################################################################################################################

def test_basic_auth_post(endpoint:'TestEndpoint', invoke_client:'InvokeClient') -> 'None':
    """ A POST of the Basic Auth connection sends its body as JSON with the credentials.
    """
    path = '/live/basic/customers/456'
    order = {'order_id': 100, 'customer': 'Jane Doe', 'amount': 249.5}

    endpoint.set_response(path, EndpointResponse(body='{"status": "accepted"}', headers=[('Content-Type', 'application/json')]))

    result = _invoke(invoke_client, Basic_Outconn_Name, 'post', data=order, params={'customer_id': 456})

    assert result['error'] == ''
    assert result['status_code'] == OK
    assert result['data'] == {'status': 'accepted'}

    request = _get_request(endpoint, path, result['cid'])

    assert request.method == 'POST'
    assert request.query == ''
    assert loads(request.body) == order
    assert request.get_header('Content-Type') == 'application/json'
    assert request.get_header('Authorization') == _basic_authorization

# ################################################################################################################################

def test_basic_auth_error_response(endpoint:'TestEndpoint', invoke_client:'InvokeClient') -> 'None':
    """ An error response of the endpoint is returned to the service with its status and its body.
    """
    path = '/live/basic/customers/999'
    endpoint.set_response(path, EndpointResponse(NOT_FOUND, 'Customer not found'))

    result = _invoke(invoke_client, Basic_Outconn_Name, 'get', params={'customer_id': 999})

    assert result['error'] == ''
    assert result['status_code'] == NOT_FOUND
    assert result['text'] == 'Customer not found'

# ################################################################################################################################

def test_oauth_get(endpoint:'TestEndpoint', invoke_client:'InvokeClient') -> 'None':
    """ Calls of the OAuth connection send the token obtained from the token endpoint, which is asked for it once.
    """
    orders = [{'order_id': 100, 'amount': 249.5}, {'order_id': 101, 'amount': 99.0}]
    endpoint.set_response(OAuth_Path, EndpointResponse(body=dumps(orders), headers=[('Content-Type', 'application/json')]))

    first = _invoke(invoke_client, OAuth_Outconn_Name, 'get')
    second = _invoke(invoke_client, OAuth_Outconn_Name, 'get', params={'status': 'open'})

    assert first['error'] == ''
    assert second['error'] == ''
    assert first['data'] == orders
    assert second['data'] == orders

    first_request = _get_request(endpoint, OAuth_Path, first['cid'])
    second_request = _get_request(endpoint, OAuth_Path, second['cid'])

    assert first_request.get_header('Authorization') == f'Bearer {OAuth_Token}'
    assert second_request.get_header('Authorization') == f'Bearer {OAuth_Token}'
    assert second_request.query == 'status=open'

    assert len(endpoint.get_requests(OAuth_Token_Path)) == 1

# ################################################################################################################################
# ################################################################################################################################
