# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from dataclasses import dataclass

# Zato
from zato.common.marshal_.api import Model
from zato.server.service import ODataAdapter, Service

# ################################################################################################################################
# ################################################################################################################################

class ODataTestRead(Service):
    """ Reads an entity set through a named OData connection.
    """
    name = 'test.odata.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        entity_set = self.request.raw_request['entity_set']
        query = self.request.raw_request.get('query') or {}

        conn = self.odata[conn_name]
        items = conn.read(entity_set, **query)

        self.response.payload = json.dumps({'items': items})

# ################################################################################################################################
# ################################################################################################################################

class ODataTestGet(Service):
    """ Reads a single entity by key.
    """
    name = 'test.odata.get'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        entity_set = self.request.raw_request['entity_set']
        key = self.request.raw_request['key']

        conn = self.odata[conn_name]
        entity = conn.get(entity_set, key)

        self.response.payload = json.dumps({'entity': entity})

# ################################################################################################################################
# ################################################################################################################################

class ODataTestCreate(Service):
    """ Creates a new entity.
    """
    name = 'test.odata.create'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        entity_set = self.request.raw_request['entity_set']
        data = self.request.raw_request['data']

        conn = self.odata[conn_name]
        created = conn.create(entity_set, data)

        self.response.payload = json.dumps({'created': created})

# ################################################################################################################################
# ################################################################################################################################

class ODataTestCount(Service):
    """ Counts the members of an entity set.
    """
    name = 'test.odata.count'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        entity_set = self.request.raw_request['entity_set']

        conn = self.odata[conn_name]
        count = conn.count(entity_set)

        self.response.payload = json.dumps({'count': count})

# ################################################################################################################################
# ################################################################################################################################

class ODataTestPing(Service):
    """ Pings an OData connection and returns the status code.
    """
    name = 'test.odata.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.odata[conn_name]
        status_code = conn.ping()

        self.response.payload = json.dumps({'status_code': status_code})

# ################################################################################################################################
# ################################################################################################################################

class ODataAdapterCustomersByCity(ODataAdapter):
    """ An adapter with a placeholder-driven filter - {city} comes from the input payload.
    """
    name = 'test.odata.adapter.customers-by-city'

    conn_name  = 'test.odata.bc'
    entity_set = 'customers'
    filter     = "city eq '{city}'" # noqa: A003
    orderby    = 'displayName'

    def handle(self):
        items = self._invoke_odata()
        self.response.payload = json.dumps({'items': items})

# ################################################################################################################################
# ################################################################################################################################

class ODataAdapterCustomerByKey(ODataAdapter):
    """ An adapter reading a single entity - the key placeholder comes from the input payload.
    """
    name = 'test.odata.adapter.customer-by-key'

    conn_name  = 'test.odata.bc'
    entity_set = 'customers'
    key        = '{customer_id}'

    def handle(self):
        entity = self._invoke_odata()
        self.response.payload = json.dumps({'entity': entity})

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Customer(Model):
    id: 'str'
    displayName: 'str'
    city: 'str'

# ################################################################################################################################
# ################################################################################################################################

class ODataAdapterCustomersWithModel(ODataAdapter):
    """ An adapter mapping each returned item through a model.
    """
    name = 'test.odata.adapter.customers-with-model'

    model      = Customer
    conn_name  = 'test.odata.bc'
    entity_set = 'customers'
    select     = 'id,displayName,city'
    orderby    = 'displayName'

    def handle(self):
        customers = self._invoke_odata()

        items = []
        for customer in customers:
            items.append(customer.to_dict())

        self.response.payload = json.dumps({'items': items})

# ################################################################################################################################
# ################################################################################################################################
