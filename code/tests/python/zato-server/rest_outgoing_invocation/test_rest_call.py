# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rest_call method - the data and the response of a successful call, a non-2xx response raised as an exception
# describing the request, the data mapped to a model or a list of models and handed to a callback.

# stdlib
import socket
from http.client import BAD_REQUEST, OK
from json import dumps, loads

# pytest
import pytest

# Zato
from zato.common.api import DATA_FORMAT, NotGiven
from zato.common.exception import BackendInvocationError
from zato.common.typing_ import list_
from zato.common.util import http_retry

# Test support
from endpoint import CloseMode, EndpointResponse, Host
from models import Customer
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# A customer document as an endpoint returns it
_customer = {'customer_id': 123, 'name': 'John Smith'}

# A list of customer documents as an endpoint returns it
_customer_list = [
    {'customer_id': 123, 'name': 'John Smith'},
    {'customer_id': 456, 'name': 'Jane Doe'},
]

# The model of a list of customers
_customer_list_model:'any_' = list_[Customer]

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_', status:'int'=OK) -> 'EndpointResponse':
    out = EndpointResponse(status, dumps(data), headers=[('Content-Type', 'application/json')])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_data_and_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A successful call returns the parsed data and the response.
    """
    endpoint.set_response(path, _json_response(_customer))

    connection = new_connection(server, endpoint.http_base, path)

    data, response = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven)

    assert data == _customer
    assert response.status_code == OK
    assert response.data == _customer

    request = endpoint.get_request(path)
    assert request.method == 'GET'

# ################################################################################################################################

def test_arguments_sent(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The method, the body, the query string and the headers of the call are sent to the endpoint.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    _ = connection.rest_call(
        cid=Test_CID,
        callback=None,
        sec_def_name=NotGiven,
        method='POST',
        data=_customer,
        params={'page': 2},
        headers={'X-Request-Source': 'rest-call'},
    )

    request = endpoint.get_request(path)

    assert request.method == 'POST'
    assert request.query == 'page=2'
    assert loads(request.body) == _customer
    assert request.get_header('X-Request-Source') == 'rest-call'
    assert request.get_header('X-Zato-CID') == Test_CID

# ################################################################################################################################

def test_error_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A non-2xx response raises BackendInvocationError naming the connection, the method, the address with its query string and the data.
    """
    endpoint.set_response(path, EndpointResponse(BAD_REQUEST, 'Invalid customer ID'))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, params={'customer_id': 'abc'})

    address = endpoint.http_base + path
    expected = f'Error calling outgoing connection: test.rest.outgoing -> GET {address}?customer_id=abc -> Invalid customer ID'

    assert info.value.msg == expected

# ################################################################################################################################

def test_error_response_without_query_string(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A non-2xx response to a call without a query string raises BackendInvocationError naming the address alone.
    """
    endpoint.set_response(path, EndpointResponse(BAD_REQUEST, 'Invalid request'))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, method='DELETE')

    address = endpoint.http_base + path
    assert info.value.msg == f'Error calling outgoing connection: test.rest.outgoing -> DELETE {address} -> Invalid request'

# ################################################################################################################################

def test_needs_exception_off(server:'ServerStub', path:'str') -> 'None':
    """ A call that fails before a response arrives returns None instead of raising when exceptions are not needed.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((Host, 0))
    port = sock.getsockname()[1]
    sock.close()

    connection = new_connection(server, f'http://{Host}:{port}', path)

    result = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, needs_exception=False)
    assert result is None

# ################################################################################################################################

def test_needs_exception_on(server:'ServerStub', path:'str') -> 'None':
    """ A call that fails before a response arrives raises by default.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((Host, 0))
    port = sock.getsockname()[1]
    sock.close()

    connection = new_connection(server, f'http://{Host}:{port}', path)

    with pytest.raises(BackendInvocationError):
        _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven)

# ################################################################################################################################

def test_model(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data is mapped to the model the call names.
    """
    endpoint.set_response(path, _json_response(_customer))

    connection = new_connection(server, endpoint.http_base, path)

    data, _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, model=Customer)

    assert isinstance(data, Customer)
    assert data.customer_id == 123
    assert data.name == 'John Smith'

# ################################################################################################################################

def test_list_of_models(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A list in the data is mapped to a list of the model the call names.
    """
    endpoint.set_response(path, _json_response(_customer_list))

    connection = new_connection(server, endpoint.http_base, path)

    data, _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, model=_customer_list_model)

    assert len(data) == 2

    first, second = data

    assert isinstance(first, Customer)
    assert isinstance(second, Customer)

    assert first.customer_id == 123
    assert second.name == 'Jane Doe'

# ################################################################################################################################

def test_callback(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A callback receives the mapped data with the call's details, and what it returns is the data of the call.
    """
    endpoint.set_response(path, _json_response(_customer))

    connection = new_connection(server, endpoint.http_base, path)

    received:'any_' = []

    def callback(data:'any_', **kwargs:'any_') -> 'any_':
        received.append((data, kwargs))
        out = {'customer_name': data.name}
        return out

    data, _ = connection.rest_call(cid=Test_CID, callback=callback, model=Customer, sec_def_name=NotGiven)

    assert data == {'customer_name': 'John Smith'}

    callback_data, callback_kwargs = received[0]

    assert isinstance(callback_data, Customer)
    assert callback_kwargs['cid'] == Test_CID
    assert callback_kwargs['model'] is Customer
    assert callback_kwargs['callback'] is callback

# ################################################################################################################################

def test_retry_arguments(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    """ The retry arguments of the call win over the retry settings of the connection.
    """
    sleeps:'list[int]' = []
    monkeypatch.setattr(http_retry, 'sleep', sleeps.append)

    endpoint.set_responses(path, [
        EndpointResponse(close_mode=CloseMode.Reset_Before_Response),
        _json_response(_customer),
    ])

    connection = new_connection(server, endpoint.http_base, path)

    data, _ = connection.rest_call(cid=Test_CID, callback=None, sec_def_name=NotGiven, max_retries=1, retry_sleep_time=3)

    assert data == _customer
    assert sleeps == [3]
    assert len(endpoint.get_requests(path)) == 2

# ################################################################################################################################
# ################################################################################################################################
