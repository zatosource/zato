# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# RESTAdapter - the connection, the method, the body, the query string, the path parameters, the headers and
# the credentials of an adapter, each static or built by a method, the response mapped to a model or by a callback,
# and the result assigned as the payload of the service.

# stdlib
from http.client import OK
from json import dumps, loads
from urllib.parse import parse_qsl

# pytest
import pytest

# Zato
from zato.common.api import DATA_FORMAT, RESTAdapterResponse
from zato.common.util import http_retry
from zato.server.service import RESTAdapter

# Test support
from adapter_support import new_adapter
from endpoint import CloseMode, EndpointResponse
from models import Customer
from support import new_connection, read_log_lines, Test_CID, Token_Path_Suffix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The name the adapters look their connection up under
_conn_name = 'test.rest.adapter'

# A customer document as an endpoint returns it
_customer = {'customer_id': 123, 'name': 'John Smith'}

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_') -> 'EndpointResponse':
    out = EndpointResponse(body=dumps(data), headers=[('Content-Type', 'application/json')])
    return out

# ################################################################################################################################

def _run(
    adapter_class:'any_',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    *,
    data:'strdict | None'=None,
    **connection_kwargs:'any_',
    ) -> 'any_':
    """ Runs the handle method of an adapter against a connection to the path and returns the adapter.
    """
    connection = new_connection(server, endpoint.http_base, path, **connection_kwargs)

    out = new_adapter(adapter_class, data=data, rest={_conn_name: connection})
    out.handle()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_conn_name(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An adapter with a static connection name invokes that connection with GET and assigns the data as its payload.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name

    endpoint.set_response(path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, server, path)

    assert adapter.response.payload == _customer

    request = endpoint.get_request(path)

    assert request.method == 'GET'
    assert request.query == ''
    assert request.get_header('X-Zato-CID') == Test_CID

# ################################################################################################################################

def test_get_conn_name(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An adapter that builds its connection name invokes the connection of that name.
    """
    class CustomerAdapter(RESTAdapter):
        def get_conn_name(self) -> 'str':
            return _conn_name

    endpoint.set_response(path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, server, path)

    assert adapter.response.payload == _customer
    assert len(endpoint.get_requests(path)) == 1

# ################################################################################################################################

def test_method(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A static method given in lowercase is sent in uppercase.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        method = 'delete'

    _ = _run(CustomerAdapter, endpoint, server, path)

    request = endpoint.get_request(path)
    assert request.method == 'DELETE'

# ################################################################################################################################

def test_get_method_and_get_request(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A method and a body built by the adapter are sent, the method in uppercase.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name

        def get_method(self) -> 'str':
            return 'put'

        def get_request(self) -> 'any_':
            return {'customer_id': 123, 'name': 'John Smith'}

    _ = _run(CustomerAdapter, endpoint, server, path, data_format=DATA_FORMAT.JSON)

    request = endpoint.get_request(path)

    assert request.method == 'PUT'
    assert loads(request.body) == _customer

# ################################################################################################################################

def test_query_string_id_default(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An adapter with a query string ID sends the `id` element of its input in the query string.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        has_query_string_id = True

    _ = _run(CustomerAdapter, endpoint, server, path, data={'id': 123})

    request = endpoint.get_request(path)
    assert request.query == 'id=123'

# ################################################################################################################################

def test_query_string_id_param(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An adapter with a named query string ID sends the input element of that name in the query string.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        has_query_string_id = True
        query_string_id_param = 'customer_id'

    _ = _run(CustomerAdapter, endpoint, server, path, data={'customer_id': 456})

    request = endpoint.get_request(path)
    assert request.query == 'customer_id=456'

# ################################################################################################################################

def test_query_string_and_path_params(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The query string and the path parameters an adapter builds are merged with the query string ID, the path parameters
    filling the address template and the rest sent in the query string.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        has_query_string_id = True

        def get_query_string(self, params:'strdict') -> 'strdict':
            return {'page': 2, 'source': f'id-{params["id"]}'}

        def get_path_params(self, params:'strdict') -> 'strdict':
            return {'region': 'eu-central'}

    _ = _run(CustomerAdapter, endpoint, server, path + '/{region}/customers', data={'id': 123})

    request = endpoint.get_request(path + '/eu-central/customers')
    assert dict(parse_qsl(request.query)) == {'id': '123', 'page': '2', 'source': 'id-123'}

# ################################################################################################################################

def test_get_auth_bearer(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A bearer token the adapter builds is sent in the Authorization header.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name

        def get_auth_bearer(self) -> 'str':
            return 'adapter.token.2f4e8b3b'

    _ = _run(CustomerAdapter, endpoint, server, path)

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == 'Bearer adapter.token.2f4e8b3b'

# ################################################################################################################################

def test_sec_def_name(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The bearer token definition an adapter names provides the Authorization header.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        sec_def_name = 'test.adapter.static'

    server.add_static_token('test.adapter.static', 'adapter.static.token.8b3b9e7d')

    _ = _run(CustomerAdapter, endpoint, server, path)

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == 'Bearer adapter.static.token.8b3b9e7d'

# ################################################################################################################################

def test_get_sec_def_name(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The bearer token definition an adapter builds the name of provides the Authorization header.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name

        def get_sec_def_name(self) -> 'str':
            return 'test.adapter.dynamic'

    server.add_static_token('test.adapter.dynamic', 'adapter.dynamic.token.3b9e7d1a')

    _ = _run(CustomerAdapter, endpoint, server, path)

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == 'Bearer adapter.dynamic.token.3b9e7d1a'

# ################################################################################################################################

def _assert_auth_scopes(adapter_class:'any_', endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Runs an adapter whose scopes are `customers.write` and checks that these scopes were requested from the token endpoint.
    """
    token_path = path + Token_Path_Suffix
    token_body = {'access_token': 'adapter.oauth.token.9e7d1a5c', 'token_type': 'Bearer', 'expires_in': 3600}
    endpoint.set_response(token_path, _json_response(token_body))

    server.add_oauth('test.adapter.oauth', endpoint.http_base + token_path, scopes='orders.read')

    _ = _run(adapter_class, endpoint, server, path)

    token_request = endpoint.get_request(token_path)
    assert loads(token_request.body)['scope'] == 'customers.write'

    request = endpoint.get_request(path)
    assert request.get_header('Authorization') == 'Bearer adapter.oauth.token.9e7d1a5c'

# ################################################################################################################################

def test_auth_scopes(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The scopes an adapter names are requested from the token endpoint of its definition.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        sec_def_name = 'test.adapter.oauth'
        auth_scopes = 'customers.write'

    _assert_auth_scopes(CustomerAdapter, endpoint, server, path)

# ################################################################################################################################

def test_get_auth_scopes(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The scopes an adapter builds are requested from the token endpoint of its definition.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        sec_def_name = 'test.adapter.oauth'

        def get_auth_scopes(self) -> 'str':
            return 'customers.write'

    _assert_auth_scopes(CustomerAdapter, endpoint, server, path)

# ################################################################################################################################

def test_get_headers(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The headers an adapter builds are sent along with the bearer token it builds.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name

        def get_headers(self) -> 'strdict':
            return {'X-Tenant': 'customers.eu'}

        def get_auth_bearer(self) -> 'str':
            return 'adapter.token.5c2f4e8b'

    _ = _run(CustomerAdapter, endpoint, server, path)

    request = endpoint.get_request(path)

    assert request.get_header('X-Tenant') == 'customers.eu'
    assert request.get_header('Authorization') == 'Bearer adapter.token.5c2f4e8b'

# ################################################################################################################################

def test_model(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The data is mapped to the model of the adapter, which becomes the payload as a dict.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        model = Customer

    endpoint.set_response(path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, server, path)
    assert adapter.response.payload == _customer

# ################################################################################################################################

def test_map_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The callback of the adapter receives the model instance and what it returns becomes the payload.
    """
    received:'any_' = []

    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        model = Customer

        def map_response(self, data:'any_', **kwargs:'any_') -> 'any_':
            received.append(data)
            out = {'customer_name': data.name}
            return out

    endpoint.set_response(path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, server, path)

    assert adapter.response.payload == {'customer_name': 'John Smith'}
    assert isinstance(received[0], Customer)

# ################################################################################################################################

def test_needs_raw_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An adapter that needs the raw response has a payload holding both the data and the response.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        needs_raw_response = True

    endpoint.set_response(path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, server, path)
    payload = adapter.response.payload

    assert isinstance(payload, RESTAdapterResponse)
    assert payload.data == _customer
    assert payload.raw_response.status_code == OK
    assert payload.raw_response.json() == _customer

# ################################################################################################################################

def test_retry_attributes(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    """ The retry attributes of the adapter win over the retry settings of the connection.
    """
    sleeps:'list[int]' = []
    monkeypatch.setattr(http_retry, 'sleep', sleeps.append)

    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        max_retries = 2
        retry_sleep_time = 1
        retry_backoff_multiplier = 3

    endpoint.set_responses(path, [
        EndpointResponse(close_mode=CloseMode.Reset_Before_Response),
        EndpointResponse(close_mode=CloseMode.Reset_Before_Response),
        _json_response(_customer),
    ])

    adapter = _run(CustomerAdapter, endpoint, server, path, max_retries=0)

    assert adapter.response.payload == _customer
    assert sleeps == [1, 3]
    assert len(endpoint.get_requests(path)) == 3

# ################################################################################################################################

def test_log_response(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ An adapter that logs its responses writes the text of the response.
    """
    class CustomerAdapter(RESTAdapter):
        conn_name = _conn_name
        log_response = True

    suffix = path.rsplit('/', 1)[1]
    body = f'Logged response body {suffix}'

    endpoint.set_response(path, EndpointResponse(body=body))

    _ = _run(CustomerAdapter, endpoint, server, path)

    lines = read_log_lines(rest_log_path, f'REST call response received -> {body}')
    assert len(lines) == 1

# ################################################################################################################################
# ################################################################################################################################
