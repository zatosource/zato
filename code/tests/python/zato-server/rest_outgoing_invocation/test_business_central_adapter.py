# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# BusinessCentralAdapter - the connection and the base URL of an adapter, static or built by a method, placeholders
# in the endpoint and the base URL filled from the input and from a configuration file, the response returned as JSON
# or mapped to a model, and an error response raised as an exception.

# stdlib
from http.client import NOT_FOUND
from json import dumps

# pytest
import pytest

# requests
from requests import Session

# Zato
from zato.server.service import BusinessCentralAdapter

# Test support
from adapter_support import new_adapter
from endpoint import EndpointResponse
from models import Customer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict
    from endpoint import TestEndpoint

# ################################################################################################################################
# ################################################################################################################################

# The name the adapters look their connection up under
_conn_name = 'test.business.central'

# A customer document as an endpoint returns it
_customer = {'customer_id': 123, 'name': 'John Smith'}

# A list of customer documents under the key the endpoint returns them in
_customer_list = {'value': [
    {'customer_id': 123, 'name': 'John Smith'},
    {'customer_id': 456, 'name': 'Jane Doe'},
]}

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_') -> 'EndpointResponse':
    out = EndpointResponse(body=dumps(data), headers=[('Content-Type', 'application/json')])
    return out

# ################################################################################################################################

def _run(adapter_class:'any_', *, data:'strdict | None'=None, config:'anydict | None'=None) -> 'any_':
    """ Runs the handle method of an adapter whose connection is a client of its own and returns the adapter.
    """
    out = new_adapter(adapter_class, data=data, cloud={_conn_name: Session()}, config=config)
    out.handle()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_static_configuration(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ An adapter with a static connection, base URL and endpoint reads the endpoint and assigns the JSON as its payload.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'customers'

    endpoint.set_response(path + '/customers', _json_response(_customer))

    adapter = _run(CustomerAdapter)

    assert adapter.response.payload == _customer

    request = endpoint.get_request(path + '/customers')
    assert request.method == 'GET'

# ################################################################################################################################

def test_get_conn_name_and_get_base_url(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ An adapter that builds its connection name and its base URL reads the endpoint under that base URL.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        base_url = ''
        endpoint = 'customers'

        def get_conn_name(self) -> 'str':
            return _conn_name

        def get_base_url(self) -> 'str':
            return address

    endpoint.set_response(path + '/customers', _json_response(_customer))

    adapter = _run(CustomerAdapter)
    assert adapter.response.payload == _customer

# ################################################################################################################################

def test_endpoint_placeholders_from_input(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ Placeholders in the endpoint are filled from the input.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'companies({company_id})/customers({customer_id})'

    _ = _run(CustomerAdapter, data={'company_id': 'eu-central', 'customer_id': 123})

    request = endpoint.get_request(path + '/companies(eu-central)/customers(123)')
    assert request.method == 'GET'

# ################################################################################################################################

def test_placeholders_from_config_file(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ A base URL and an endpoint that are placeholders of a configuration file are read from that file.
    """
    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = '{business_central.ini:api.base_url}'
        endpoint = '{business_central.ini:api.customers}'

    config = {
        'business_central': {
            'api': {
                'base_url': endpoint.http_base + path,
                'customers': 'companies(eu-central)/customers',
            }
        }
    }

    _ = _run(CustomerAdapter, config=config)

    request = endpoint.get_request(path + '/companies(eu-central)/customers')
    assert request.method == 'GET'

# ################################################################################################################################

def test_missing_input_elements(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ Input elements missing for the placeholders raise an exception naming them in sorted order.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'companies({company_id})/customers({customer_id})'

    with pytest.raises(Exception) as info:
        _ = _run(CustomerAdapter, data={'region': 'eu-central'})

    assert info.value.args[0] == "Elements missing on input -> `['company_id', 'customer_id']` "

    with pytest.raises(Exception) as info:
        _ = _run(CustomerAdapter, data={'company_id': 'eu-central'})

    assert info.value.args[0] == "Element missing on input -> `['customer_id']` "

# ################################################################################################################################

def test_missing_config_key(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ A key missing from the configuration file raises an exception naming the placeholder, the key and the keys available.
    """
    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = '{business_central.ini:api.base_url}'
        endpoint = '{business_central.ini:api.vendors}'

    config = {
        'business_central': {
            'api': {
                'base_url': endpoint.http_base + path,
                'customers': 'customers',
            }
        }
    }

    with pytest.raises(Exception) as info:
        _ = _run(CustomerAdapter, config=config)

    expected = "Key not found -> `business_central.ini:api.vendors` -> `vendors` in `['base_url', 'customers']`"
    assert info.value.args[0] == expected

# ################################################################################################################################

def test_value_list_mapped_to_model(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ A list under the `value` key is mapped to a list of the model of the adapter.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'customers'
        model = Customer

    endpoint.set_response(path + '/customers', _json_response(_customer_list))

    adapter = _run(CustomerAdapter)
    first, second = adapter.response.payload

    assert isinstance(first, Customer)
    assert isinstance(second, Customer)
    assert first.name == 'John Smith'
    assert second.customer_id == 456

# ################################################################################################################################

def test_single_object_mapped_with_get_model(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ A single object is mapped to the model the adapter builds, which becomes the payload as a dict.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'customers(123)'

        def get_model(self) -> 'any_':
            return Customer

    endpoint.set_response(path + '/customers(123)', _json_response(_customer))

    adapter = _run(CustomerAdapter)
    assert adapter.response.payload == _customer

# ################################################################################################################################

def test_error_response(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ A response other than 200 OK raises an exception with its status and its body.
    """
    address = endpoint.http_base + path

    class CustomerAdapter(BusinessCentralAdapter):
        conn_name = _conn_name
        base_url = address
        endpoint = 'customers(999)'

    endpoint.set_response(path + '/customers(999)', EndpointResponse(NOT_FOUND, 'Customer not found'))

    with pytest.raises(Exception) as info:
        _ = _run(CustomerAdapter)

    assert info.value.args[0] == 'Endpoint invocation error (404) -> Customer not found'

# ################################################################################################################################
# ################################################################################################################################
