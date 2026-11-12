# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SAPAdapter - the OData adapter reading through the SAP connections of a service instead of its OData connections.

# stdlib
from json import dumps
from urllib.parse import parse_qsl

# Zato
from zato.server.service import SAPAdapter

# Test support
from adapter_support import new_adapter, new_odata_client
from endpoint import EndpointResponse
from models import Customer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint

# ################################################################################################################################
# ################################################################################################################################

# The name the adapters look their connection up under
_conn_name = 'test.sap'

# The entities of a set as the service returns them
_sales_orders = {'value': [
    {'customer_id': 123, 'name': 'John Smith'},
    {'customer_id': 456, 'name': 'Jane Doe'},
]}

# ################################################################################################################################
# ################################################################################################################################

def test_read_through_sap_connections(endpoint:'TestEndpoint', path:'str') -> 'None':
    """ An adapter reads through the SAP connection of its name, with its query options and its model,
    and the OData connections are not consulted.
    """
    class SalesOrderAdapter(SAPAdapter):
        conn_name = _conn_name
        entity_set = 'A_SalesOrder'
        filter = "SoldToParty eq '{customer_id}'" # noqa: A003
        top = 2
        model = Customer

    endpoint.set_response(path + '/A_SalesOrder', EndpointResponse(
        body=dumps(_sales_orders), headers=[('Content-Type', 'application/json')]))

    client = new_odata_client(endpoint, path)

    adapter = new_adapter(SalesOrderAdapter, data={'customer_id': '123'}, sap={_conn_name: client})
    adapter.handle()

    first, second = adapter.response.payload

    assert isinstance(first, Customer)
    assert isinstance(second, Customer)
    assert adapter.odata == {}

    request = endpoint.get_request(path + '/A_SalesOrder')
    assert dict(parse_qsl(request.query)) == {'$filter': "SoldToParty eq '123'", '$top': '2'}

# ################################################################################################################################
# ################################################################################################################################
