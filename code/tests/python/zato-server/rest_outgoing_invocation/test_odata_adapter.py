# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ODataAdapter - an entity set read whole or by a key, both with placeholders filled from the input, the query options
# of the adapter with placeholders, static or built by a method, and the entities mapped to a model.

# stdlib
from json import dumps
from urllib.parse import parse_qsl

# Zato
from zato.server.service import ODataAdapter

# Test support
from adapter_support import new_adapter, new_odata_client
from endpoint import EndpointResponse
from models import Customer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict
    from endpoint import TestEndpoint

# ################################################################################################################################
# ################################################################################################################################

# The name the adapters look their connection up under
_conn_name = 'test.odata'

# The entities of a set as an OData 4.0 service returns them
_customer_set = {'value': [
    {'customer_id': 123, 'name': 'John Smith'},
    {'customer_id': 456, 'name': 'Jane Doe'},
]}

# One entity as an OData 4.0 service returns it
_customer = {'customer_id': 123, 'name': 'John Smith'}

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_') -> 'EndpointResponse':
    out = EndpointResponse(body=dumps(data), headers=[('Content-Type', 'application/json')])
    return out

# ################################################################################################################################

def _run(adapter_class:'any_', endpoint:'TestEndpoint', path:'str', *, data:'strdict | None'=None) -> 'any_':
    """ Runs the handle method of an adapter whose connection is a client of the service under the path and returns the adapter.
    """
    client = new_odata_client(endpoint, path)

    out = new_adapter(adapter_class, data=data, odata={_conn_name: client})
    out.handle()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_read_set(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ An adapter without a key reads the whole set and assigns its entities as the payload.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = 'Customers'

    endpoint.set_response(path + '/Customers', _json_response(_customer_set))

    adapter = _run(CustomerAdapter, endpoint, path)

    assert adapter.response.payload == _customer_set['value']

    request = endpoint.get_request(path + '/Customers')

    assert request.method == 'GET'
    assert request.query == ''

# ################################################################################################################################

def test_read_entity_by_key(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ An adapter with a key reads one entity, the entity set and the key filled from the input.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = '{entity_set}'
        key = '{customer_id}'

    entity_path = path + "/Customers('ALFKI')"
    endpoint.set_response(entity_path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, path, data={'entity_set': 'Customers', 'customer_id': 'ALFKI'})

    assert adapter.response.payload == _customer
    assert endpoint.get_request(entity_path).method == 'GET'

# ################################################################################################################################

def test_query_options(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ The static query options of an adapter are sent, the placeholders in them filled from the input.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = 'Customers'
        filter = "City eq '{city}'" # noqa: A003
        select = 'customer_id,name'
        expand = 'Orders'
        orderby = 'name desc'
        top = 10
        skip = 20

    endpoint.set_response(path + '/Customers', _json_response(_customer_set))

    _ = _run(CustomerAdapter, endpoint, path, data={'city': 'Berlin'})

    request = endpoint.get_request(path + '/Customers')

    assert dict(parse_qsl(request.query)) == {
        '$filter': "City eq 'Berlin'",
        '$select': 'customer_id,name',
        '$expand': 'Orders',
        '$orderby': 'name desc',
        '$top': '10',
        '$skip': '20',
    }

# ################################################################################################################################

def test_get_query(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ The query options an adapter builds win over its static ones.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = 'Customers'
        filter = "City eq 'Berlin'" # noqa: A003
        top = 10

        def get_query(self) -> 'strdict':
            return {'filter': "Country eq 'Germany'", 'top': 5}

    endpoint.set_response(path + '/Customers', _json_response(_customer_set))

    _ = _run(CustomerAdapter, endpoint, path)

    request = endpoint.get_request(path + '/Customers')
    assert dict(parse_qsl(request.query)) == {'$filter': "Country eq 'Germany'", '$top': '5'}

# ################################################################################################################################

def test_model_maps_set(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ The entities of a set are mapped to a list of the model of the adapter.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = 'Customers'
        model = Customer

    endpoint.set_response(path + '/Customers', _json_response(_customer_set))

    adapter = _run(CustomerAdapter, endpoint, path)
    first, second = adapter.response.payload

    assert isinstance(first, Customer)
    assert isinstance(second, Customer)
    assert first.customer_id == 123
    assert second.name == 'Jane Doe'

# ################################################################################################################################

def test_model_maps_entity(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ One entity is mapped to the model of the adapter, which becomes the payload as a dict.
    """
    class CustomerAdapter(ODataAdapter):
        conn_name = _conn_name
        entity_set = 'Customers'
        key = '123'
        model = Customer

    entity_path = path + "/Customers('123')"
    endpoint.set_response(entity_path, _json_response(_customer))

    adapter = _run(CustomerAdapter, endpoint, path)
    assert adapter.response.payload == _customer

# ################################################################################################################################
# ################################################################################################################################
