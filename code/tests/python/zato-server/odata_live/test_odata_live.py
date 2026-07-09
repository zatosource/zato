# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.odata_live')

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        from base64 import b64encode
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestODataRead:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_read_all(self, zato_server:'anydict') -> 'None':
        """ A plain read returns all the seeded Business Central customers.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.read', {
            'conn_name': 'test.odata.bc',
            'entity_set': 'customers',
        })

        items = result['items']
        assert len(items) == 3

# ################################################################################################################################

    def test_read_with_filter(self, zato_server:'anydict') -> 'None':
        """ Query options travel through the facade to the OData server.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.read', {
            'conn_name': 'test.odata.bc',
            'entity_set': 'customers',
            'query': {'filter': "city eq 'Atlanta'"},
        })

        items = result['items']
        names = []
        for item in items:
            names.append(item['displayName'])

        assert sorted(names) == ['Adatum', 'School of Art']

        # The filter must have arrived as one $filter parameter.
        bc_server = zato_server['bc_server']
        assert bc_server.last_request['query']['$filter'] == "city eq 'Atlanta'"

# ################################################################################################################################

    def test_read_v2(self, zato_server:'anydict') -> 'None':
        """ A V2 read against the S/4HANA profile parses the d-wrapped payload.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.read', {
            'conn_name': 'test.odata.s4',
            'entity_set': 'A_SalesOrder',
        })

        items = result['items']
        assert len(items) == 2
        assert items[0]['SalesOrder'] == '1'

# ################################################################################################################################

    def test_get_by_key(self, zato_server:'anydict') -> 'None':
        """ A single entity is read by key.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.get', {
            'conn_name': 'test.odata.bc',
            'entity_set': 'customers',
            'key': 'aaaa0002-0000-0000-0000-000000000002',
        })

        entity = result['entity']
        assert entity['displayName'] == 'Trey Research'

# ################################################################################################################################

    def test_count(self, zato_server:'anydict') -> 'None':
        """ $count returns the size of the seeded set.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.count', {
            'conn_name': 'test.odata.bc',
            'entity_set': 'customers',
        })

        assert result['count'] == 3

# ################################################################################################################################
# ################################################################################################################################

class TestODataWrite:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_create(self, zato_server:'anydict') -> 'None':
        """ A create through the facade adds an entity to the server's store.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.create', {
            'conn_name': 'test.odata.bc',
            'entity_set': 'customers',
            'data': {'id': 'bbbb0001-0000-0000-0000-000000000001', 'displayName': 'Contoso', 'city': 'Boston'},
        })

        created = result['created']
        assert created['displayName'] == 'Contoso'

        bc_server = zato_server['bc_server']
        assert 'bbbb0001-0000-0000-0000-000000000001' in bc_server.entities['customers']

# ################################################################################################################################

    def test_create_v2_with_csrf(self, zato_server:'anydict') -> 'None':
        """ A V2 write against S/4HANA proves the CSRF fetch-then-write flow works
        through the pooled connection.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.create', {
            'conn_name': 'test.odata.s4',
            'entity_set': 'A_SalesOrder',
            'data': {'SalesOrder': '900', 'SalesOrderType': 'OR', 'SoldToParty': 'CUST-99', 'TotalNetAmount': 750},
        })

        created = result['created']
        assert created['SalesOrder'] == '900'

        s4_server = zato_server['s4_server']
        assert '900' in s4_server.entities['A_SalesOrder']

# ################################################################################################################################
# ################################################################################################################################

class TestODataPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() returns a successful status code against the live server.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.ping', {
            'conn_name': 'test.odata.bc',
        })

        assert result['status_code'] < 400

# ################################################################################################################################
# ################################################################################################################################

class TestODataAdapter:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_adapter_placeholder_filter(self, zato_server:'anydict') -> 'None':
        """ The adapter fills the {city} placeholder from the input payload.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.adapter.customers-by-city', {
            'city': 'Atlanta',
        })

        items = result['items']
        names = []
        for item in items:
            names.append(item['displayName'])

        assert names == ['Adatum', 'School of Art']

        bc_server = zato_server['bc_server']
        assert bc_server.last_request['query']['$filter'] == "city eq 'Atlanta'"
        assert bc_server.last_request['query']['$orderby'] == 'displayName'

# ################################################################################################################################

    def test_adapter_key_placeholder(self, zato_server:'anydict') -> 'None':
        """ The adapter reads a single entity through a key placeholder.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.adapter.customer-by-key', {
            'customer_id': 'aaaa0003-0000-0000-0000-000000000003',
        })

        entity = result['entity']
        assert entity['displayName'] == 'School of Art'

# ################################################################################################################################

    def test_adapter_with_model(self, zato_server:'anydict') -> 'None':
        """ Each returned item is mapped through the adapter's model.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.odata.adapter.customers-with-model', {})

        items = result['items']
        assert len(items) >= 3

        first = items[0]
        assert sorted(first) == ['city', 'displayName', 'id']

        bc_server = zato_server['bc_server']
        assert bc_server.last_request['query']['$select'] == 'id,displayName,city'

# ################################################################################################################################
# ################################################################################################################################
