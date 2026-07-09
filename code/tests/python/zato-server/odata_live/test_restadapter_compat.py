# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The compatibility suite - it re-creates the logic of existing RESTAdapter-based
Business Central services with anonymized orders-and-invoices names and asserts,
for each service, both the mapped output and the recorded wire request, so any
change in RESTAdapter behavior fails loudly.
"""

# stdlib
import json
import logging
import os
import sys

# PyPI
import pytest

sys.path.insert(0, os.path.dirname(__file__))

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.odata_live.compat')

_company = 'cccc0001-0000-0000-0000-000000000001'
_env = 'sandbox'
_service_root_path = '/v2.0/test-tenant/sandbox/api/v2.0'

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

@pytest.fixture(scope='module')
def compat_data(zato_server:'anydict') -> 'anydict':
    """ Seeds the Business Central profile with the entities the compat services read.
    """
    bc_server = zato_server['bc_server']

    bc_server.add_entities('companies', 'id', [
        {'id': _company, 'name': 'Compat Test Company'},
    ])

    bc_server.add_entities('discounts', 'id', [
        {'id': 'd1', 'code': 'PCT10', 'blocked': False, 'currency': '', 'postingGroup': 'DOMESTIC'},
        {'id': 'd2', 'code': 'PCT25', 'blocked': False, 'currency': 'GBP', 'postingGroup': 'FOREIGN'},
        {'id': 'd3', 'code': 'PCT50', 'blocked': True, 'currency': '', 'postingGroup': 'DOMESTIC'},
        {'id': 'd4', 'code': 'PCT15', 'blocked': False, 'currency': '', 'postingGroup': 'EXPORT'},
    ])

    bc_server.add_entities('invoiceRates', 'id', [
        {'id': 'r1', 'currencyCode': 'EUR', 'rate': 1.1, 'startingDate': '2026-01-01'},
        {'id': 'r2', 'currencyCode': 'EUR', 'rate': 1.2, 'startingDate': '2026-03-01'},
        {'id': 'r3', 'currencyCode': 'GBP', 'rate': 0.9, 'startingDate': '2026-02-01'},
    ])

    bc_server.add_entities('salesOrders', 'number', [])

    return {
        'client': _AdminClient(zato_server['base_url'], zato_server['invoke_password']),
        'bc_server': bc_server,
    }

# ################################################################################################################################
# ################################################################################################################################

class TestLookupAdapter:

    def test_value_list_mapping(self, compat_data:'anydict') -> 'None':
        """ 9.4.2 - a 'value' list maps into models, blocked records are skipped,
        percentages come from the prefixed code and currencies default by posting group.
        """
        client = compat_data['client']
        bc_server = compat_data['bc_server']

        result = client.invoke('test.compat.get-discounts', {
            'env': _env,
            'company': _company,
        })

        items = result['items']
        by_code = {}
        for item in items:
            by_code[item['code']] = item

        # The blocked PCT50 record is skipped.
        assert sorted(by_code) == ['PCT10', 'PCT15', 'PCT25']

        # The percentage comes out of the prefixed code.
        assert by_code['PCT10']['percentage'] == 10.0
        assert by_code['PCT25']['percentage'] == 25.0

        # Currencies default by posting group when the record has none.
        assert by_code['PCT10']['currency'] == 'EUR'
        assert by_code['PCT15']['currency'] == 'USD'
        assert by_code['PCT25']['currency'] == 'GBP'

        # Business keys are composite and each model carries a hash.
        assert by_code['PCT10']['key'] == f'{_company}-PCT10'
        assert len(by_code['PCT10']['record_hash']) == 64

        # The wire request went to the placeholder-filled path.
        request = bc_server.last_request
        assert request['method'] == 'GET'
        assert request['path'] == f'{_service_root_path}/companies({_company})/discounts'

# ################################################################################################################################

    def test_filter_pass_through(self, compat_data:'anydict') -> 'None':
        """ 9.4.1 - the optional filter travels through as one $filter parameter.
        """
        client = compat_data['client']
        bc_server = compat_data['bc_server']

        result = client.invoke('test.compat.get-discounts', {
            'env': _env,
            'company': _company,
            'filter': "code eq 'PCT10'",
        })

        items = result['items']
        assert len(items) == 1
        assert items[0]['code'] == 'PCT10'

        request = bc_server.last_request
        assert request['query']['$filter'] == "code eq 'PCT10'"

# ################################################################################################################################

    def test_single_entry_mapping(self, compat_data:'anydict') -> 'None':
        """ 9.4.2 - a single-entry response, not a 'value' list, maps into one model
        through the optional {entry} placeholder.
        """
        client = compat_data['client']
        bc_server = compat_data['bc_server']

        result = client.invoke('test.compat.get-discount-entry', {
            'env': _env,
            'company': _company,
            'entry': 'd2',
        })

        entry = result['entry']
        assert entry['code'] == 'PCT25'
        assert entry['percentage'] == 25.0
        assert entry['currency'] == 'GBP'
        assert entry['key'] == f'{_company}-PCT25'

        request = bc_server.last_request
        assert request['method'] == 'GET'
        assert request['path'] == f'{_service_root_path}/companies({_company})/discounts(d2)'

# ################################################################################################################################

    def test_latest_record_per_key(self, compat_data:'anydict') -> 'None':
        """ 9.4.2 - exchange-rate style dedup keeps only the latest record per key by date.
        """
        client = compat_data['client']

        result = client.invoke('test.compat.get-invoice-rates', {
            'env': _env,
            'company': _company,
        })

        items = result['items']
        by_currency = {}
        for item in items:
            by_currency[item['currency_code']] = item

        assert sorted(by_currency) == ['EUR', 'GBP']

        # Only the latest EUR record survived.
        assert by_currency['EUR']['rate'] == 1.2
        assert by_currency['EUR']['starting_date'] == '2026-03-01'

        assert by_currency['GBP']['rate'] == 0.9

# ################################################################################################################################
# ################################################################################################################################

class TestCreateOrder:

    def test_create_order(self, compat_data:'anydict') -> 'None':
        """ 9.4.3 - a POST with a nested payload of order lines, each optionally carrying
        dimension-like sub-lines, maps to the number of the created order.
        """
        client = compat_data['client']
        bc_server = compat_data['bc_server']

        result = client.invoke('test.compat.create-order', {
            'env': _env,
            'company': _company,
            'number': 'ORD-1001',
            'customer_number': 'CUST-42',
            'lines': [
                {'item_number': 'ITEM-1', 'quantity': 3, 'dimensions': [
                    {'code': 'DEPT', 'value': 'SALES'},
                    {'code': 'AREA', 'value': 'NORTH'},
                ]},
                {'item_number': 'ITEM-2', 'quantity': 1},
            ],
        })

        assert result['order_number'] == 'ORD-1001'

        # The wire request carried the nested payload as JSON.
        request = bc_server.last_request
        assert request['method'] == 'POST'
        assert request['path'] == f'{_service_root_path}/companies({_company})/salesOrders'

        body = request['json']
        assert body['number'] == 'ORD-1001'
        assert body['customerNumber'] == 'CUST-42'

        lines = body['salesLines']
        assert len(lines) == 2

        assert lines[0]['itemNumber'] == 'ITEM-1'
        assert lines[0]['quantity'] == 3
        assert lines[0]['dimensions'] == [
            {'code': 'DEPT', 'value': 'SALES'},
            {'code': 'AREA', 'value': 'NORTH'},
        ]

        # The second line has no dimension sub-lines at all.
        assert lines[1] == {'itemNumber': 'ITEM-2', 'quantity': 1}

        # The order made it into the server's store.
        assert 'ORD-1001' in bc_server.entities['salesOrders']

# ################################################################################################################################
# ################################################################################################################################

class TestImportXML:

    def test_import_xml(self, compat_data:'anydict') -> 'None':
        """ 9.4.4 - an XML document goes out as application/xml with the SOAPAction
        header taken from the input and the body passed through unchanged.
        """
        client = compat_data['client']
        bc_server = compat_data['bc_server']

        # The import endpoint is not an entity set - it responds with a canned document.
        bc_server.configure(f'{_service_root_path}/xmlImport', respond_json=(200, {'status': 'imported'}))

        xml_body = '<?xml version="1.0"?><Import><Order number="ORD-1001"/></Import>'

        result = client.invoke('test.compat.import-xml', {
            'env': _env,
            'soap_action': 'urn:import-orders',
            'body': xml_body,
        })

        assert result['result'] == {'status': 'imported'}

        # The wire request carried the XML through unchanged, with the right headers.
        request = bc_server.last_request
        assert request['method'] == 'POST'
        assert request['path'] == f'{_service_root_path}/xmlImport'
        assert request['headers']['Content-Type'] == 'application/xml'
        assert request['headers']['SOAPAction'] == 'urn:import-orders'
        assert request['raw_body'].decode('utf8') == xml_body

# ################################################################################################################################
# ################################################################################################################################
