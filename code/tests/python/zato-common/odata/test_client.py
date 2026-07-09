# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, NOT_FOUND, OK, PRECONDITION_FAILED, PRECONDITION_REQUIRED

# requests
from requests.exceptions import ReadTimeout, SSLError

# pytest
import pytest

# Zato
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataError, ODataVersion

# ################################################################################################################################
# ################################################################################################################################

def _bc_client(server, **extra):
    """ A client for the Business Central profile - V4, no auth unless a test adds it.
    """
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V4,
        'auth_type': 'none',
    }
    config.update(extra)

    out = ODataClient(config)
    return out

# ################################################################################################################################

def _s4_client(server, **extra):
    """ A client for the S/4HANA profile - V2, basic credentials, sap-client and CSRF.
    """
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V2,
        'auth_type': 'basic',
        'username': 'sap-user',
        'secret': 'sap-pass',
        'custom_query_params': {'sap-client': '100'},
        'needs_csrf_token': True,
    }
    config.update(extra)

    out = ODataClient(config)
    return out

# ################################################################################################################################

def _seed_customers(server):
    """ Loads a small, predictable set of Business Central customers.
    """
    server.reset()
    server.add_entities('customers', 'id', [
        {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum', 'city': 'Atlanta', 'balanceDue': 100},
        {'id': 'aaaa0002-0000-0000-0000-000000000002', 'displayName': 'Trey Research', 'city': 'Chicago', 'balanceDue': 200},
        {'id': 'aaaa0003-0000-0000-0000-000000000003', 'displayName': 'School of Art', 'city': 'Atlanta', 'balanceDue': 300},
    ])

# ################################################################################################################################

def _seed_sales_orders(server):
    """ Loads a small, predictable set of S/4HANA sales orders and enforces the profile's
    credentials and required parameters.
    """
    server.reset()
    server.set_credentials('sap-user', 'sap-pass')
    server.require_query_params({'sap-client': '100'})
    server.add_entities('A_SalesOrder', 'SalesOrder', [
        {'SalesOrder': '1', 'SalesOrderType': 'OR', 'SoldToParty': 'CUST-17', 'TotalNetAmount': 100},
        {'SalesOrder': '2', 'SalesOrderType': 'OR', 'SoldToParty': 'CUST-23', 'TotalNetAmount': 250},
        {'SalesOrder': '3', 'SalesOrderType': 'TA', 'SoldToParty': 'CUST-17', 'TotalNetAmount': 990},
    ])

# ################################################################################################################################
# ################################################################################################################################

class TestReadV4:
    """ Reads against the V4 Business Central profile.
    """

    def test_read_all(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        items = client.read('customers')
        client.close()

        assert len(items) == 3

    def test_read_with_filter(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        items = client.read('customers', filter="city eq 'Atlanta'")
        client.close()

        names = []
        for item in items:
            names.append(item['displayName'])

        assert sorted(names) == ['Adatum', 'School of Art']

        # The filter travels as one $filter parameter.
        assert business_central_server.last_request['query']['$filter'] == "city eq 'Atlanta'"

    def test_read_with_orderby_top_skip(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        items = client.read('customers', orderby='balanceDue desc', top=1, skip=1)
        client.close()

        assert len(items) == 1
        assert items[0]['displayName'] == 'Trey Research'

    def test_read_with_select(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        items = client.read('customers', select=['id', 'displayName'], orderby='displayName')
        client.close()

        assert 'city' not in items[0]
        assert items[0]['displayName'] == 'Adatum'

    def test_get_by_key(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        entity = client.get('customers', 'aaaa0001-0000-0000-0000-000000000001')
        client.close()

        assert entity['displayName'] == 'Adatum'

        # A V4 string key travels quoted inside the parentheses.
        path = business_central_server.last_request['path']
        assert path.endswith("customers('aaaa0001-0000-0000-0000-000000000001')")

    def test_get_missing_is_404(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)

        with pytest.raises(ODataError) as ctx:
            _ = client.get('customers', 'no-such-key')

        client.close()

        assert ctx.value.status_code == NOT_FOUND

    def test_count(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        count = client.count('customers')
        filtered = client.count('customers', filter="city eq 'Atlanta'")
        client.close()

        assert count == 3
        assert filtered == 2

    def test_ping(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        status = client.ping()
        client.close()

        assert status == OK

# ################################################################################################################################
# ################################################################################################################################

class TestReadV2:
    """ Reads against the V2 S/4HANA profile - the 'd' wrapper and V2 spellings.
    """

    def test_read_all(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        items = client.read('A_SalesOrder')
        client.close()

        assert len(items) == 3

        # The configured sap-client parameter rides on every request.
        assert s4hana_server.last_request['query']['sap-client'] == '100'

    def test_read_with_inlinecount(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        items = client.read('A_SalesOrder', count=True)
        client.close()

        assert len(items) == 3

        # V4's $count=true becomes V2's $inlinecount=allpages on the wire.
        assert s4hana_server.last_request['query']['$inlinecount'] == 'allpages'
        assert '$count' not in s4hana_server.last_request['query']

    def test_get_by_key(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        entity = client.get('A_SalesOrder', '2')
        client.close()

        assert entity['TotalNetAmount'] == 250

    def test_count(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        count = client.count('A_SalesOrder', filter="SoldToParty eq 'CUST-17'")
        client.close()

        assert count == 2

# ################################################################################################################################
# ################################################################################################################################

class TestWrites:
    """ Creates, updates and deletes against both versions.
    """

    def test_create_v4(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        created = client.create('customers', {'displayName': 'New Co', 'city': 'Boston'})
        client.close()

        # The server assigned a generated key and stored the entity.
        assert created['displayName'] == 'New Co'
        assert created['id']
        assert created['id'] in business_central_server.entities['customers']

    def test_update_v4_needs_etag(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)

        # Business Central rejects updates that carry no If-Match at all.
        with pytest.raises(ODataError) as ctx:
            _ = client.update('customers', 'aaaa0001-0000-0000-0000-000000000001', {'city': 'Boston'})

        assert ctx.value.status_code == PRECONDITION_REQUIRED

        # A stale ETag is rejected too, with the status the OData specification prescribes.
        with pytest.raises(ODataError) as ctx:
            _ = client.update(
                'customers', 'aaaa0001-0000-0000-0000-000000000001', {'city': 'Boston'}, etag='W/"etag-stale"')

        assert ctx.value.status_code == PRECONDITION_FAILED

        # The current ETag or the wildcard both go through.
        entity = client.get('customers', 'aaaa0001-0000-0000-0000-000000000001')
        _ = client.update(
            'customers', 'aaaa0001-0000-0000-0000-000000000001', {'city': 'Boston'}, etag=entity['@odata.etag'])

        _ = client.update('customers', 'aaaa0001-0000-0000-0000-000000000001', {'city': 'Chicago'}, etag='*')
        client.close()

        stored = business_central_server.entities['customers']['aaaa0001-0000-0000-0000-000000000001']
        assert stored['city'] == 'Chicago'

    def test_update_uses_patch_in_v4(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.update('customers', 'aaaa0002-0000-0000-0000-000000000002', {'city': 'Boston'}, etag='*')
        client.close()

        assert business_central_server.last_request['method'] == 'PATCH'

    def test_delete_v4(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        client.delete('customers', 'aaaa0003-0000-0000-0000-000000000003', etag='*')
        client.close()

        assert 'aaaa0003-0000-0000-0000-000000000003' not in business_central_server.entities['customers']

    def test_create_v2(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        created = client.create('A_SalesOrder', {'SalesOrder': '9', 'SalesOrderType': 'TA'})
        client.close()

        assert created['SalesOrder'] == '9'
        assert '9' in s4hana_server.entities['A_SalesOrder']

    def test_update_uses_merge_in_v2(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        _ = client.update('A_SalesOrder', '1', {'SalesOrderType': 'RE'})
        client.close()

        # V2 partial updates are spelled MERGE, not PATCH.
        update_request = s4hana_server.recorded_requests[-1]
        assert update_request['method'] == 'MERGE'

        assert s4hana_server.entities['A_SalesOrder']['1']['SalesOrderType'] == 'RE'

    def test_delete_v2(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        client.delete('A_SalesOrder', '3')
        client.close()

        assert '3' not in s4hana_server.entities['A_SalesOrder']

# ################################################################################################################################
# ################################################################################################################################

class TestPaging:
    """ Transparent iteration over server-driven pages in both versions.
    """

    def test_iter_v4_follows_next_links(self, business_central_server):
        _seed_customers(business_central_server)
        business_central_server.set_page_size(1)

        client = _bc_client(business_central_server)
        items = list(client.iter('customers'))
        client.close()

        assert len(items) == 3

        # Three pages of one item each means three feed requests went out.
        feed_requests = []
        for request in business_central_server.recorded_requests:
            if request['path'].endswith('/customers'):
                feed_requests.append(request)

        assert len(feed_requests) == 3

    def test_iter_v2_follows_next_links(self, s4hana_server):
        _seed_sales_orders(s4hana_server)
        s4hana_server.set_page_size(2)

        client = _s4_client(s4hana_server)
        items = list(client.iter('A_SalesOrder'))
        client.close()

        assert len(items) == 3

    def test_iter_respects_max_pages(self, business_central_server):
        _seed_customers(business_central_server)
        business_central_server.set_page_size(1)

        client = _bc_client(business_central_server, max_pages=2)
        items = list(client.iter('customers'))
        client.close()

        # Two pages of one item each - the third page was never requested.
        assert len(items) == 2

    def test_iter_sends_maxpagesize_preference(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server, page_size=2)
        _ = list(client.iter('customers'))
        client.close()

        # The page size travels as the V4 Prefer header.
        assert business_central_server.last_request['headers']['Prefer'] == 'odata.maxpagesize=2'

    def test_read_returns_single_page_only(self, business_central_server):
        _seed_customers(business_central_server)
        business_central_server.set_page_size(2)

        client = _bc_client(business_central_server)
        items = client.read('customers')
        client.close()

        # read never follows next links - that is what iter is for.
        assert len(items) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestSubResources:
    """ Business Central style nested paths - companies(guid)/customers(id).
    """

    def test_read_nested(self, business_central_server):
        business_central_server.reset()
        business_central_server.add_entities('companies', 'id', [
            {'id': 'cccc0001-0000-0000-0000-000000000001', 'name': 'CRONUS'},
        ])
        business_central_server.add_entities('customers', 'id', [
            {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        ])

        client = _bc_client(business_central_server)
        items = client.read('companies(cccc0001-0000-0000-0000-000000000001)/customers')
        client.close()

        assert len(items) == 1

    def test_nested_with_unknown_company_is_404(self, business_central_server):
        business_central_server.reset()
        business_central_server.add_entities('companies', 'id', [
            {'id': 'cccc0001-0000-0000-0000-000000000001', 'name': 'CRONUS'},
        ])
        business_central_server.add_entities('customers', 'id', [])

        client = _bc_client(business_central_server)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('companies(no-such-company)/customers')

        client.close()

        assert ctx.value.status_code == NOT_FOUND

    def test_get_nested_entity(self, business_central_server):
        business_central_server.reset()
        business_central_server.add_entities('companies', 'id', [
            {'id': 'cccc0001-0000-0000-0000-000000000001', 'name': 'CRONUS'},
        ])
        business_central_server.add_entities('customers', 'id', [
            {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        ])

        client = _bc_client(business_central_server)
        entity = client.get(
            'companies(cccc0001-0000-0000-0000-000000000001)/customers', 'aaaa0001-0000-0000-0000-000000000001')
        client.close()

        assert entity['displayName'] == 'Adatum'

# ################################################################################################################################
# ################################################################################################################################

class TestErrors:
    """ Error payloads of both versions surface as one exception type.
    """

    def test_v4_error_shape(self, business_central_server):
        business_central_server.reset()
        business_central_server.configure(
            '/v2.0/test-tenant/sandbox/api/v2.0/customers',
            respond_error=(INTERNAL_SERVER_ERROR, 'Internal_ServerError', 'Something went wrong'),
        )

        client = _bc_client(business_central_server)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('customers')

        client.close()

        assert ctx.value.status_code == INTERNAL_SERVER_ERROR
        assert ctx.value.code == 'Internal_ServerError'
        assert ctx.value.message == 'Something went wrong'

    def test_v2_error_shape(self, s4hana_server):
        _seed_sales_orders(s4hana_server)
        s4hana_server.configure(
            '/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder',
            respond_error=(BAD_REQUEST, 'SY/530', 'Order is locked'),
        )

        client = _s4_client(s4hana_server)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('A_SalesOrder')

        client.close()

        # The V2 language-tagged message object surfaces as its plain text.
        assert ctx.value.status_code == BAD_REQUEST
        assert ctx.value.code == 'SY/530'
        assert ctx.value.message == 'Order is locked'

    def test_missing_required_param(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        # A client without the sap-client parameter the profile insists on.
        client = _s4_client(s4hana_server, custom_query_params={})

        with pytest.raises(ODataError) as ctx:
            _ = client.read('A_SalesOrder')

        client.close()

        assert ctx.value.status_code == BAD_REQUEST
        assert ctx.value.code == 'MissingParameter'

    def test_exception_message_carries_all_parts(self, business_central_server):
        business_central_server.reset()

        client = _bc_client(business_central_server)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('no_such_set')

        client.close()

        assert str(ctx.value) == '404 NotFound Entity set no_such_set does not exist'

# ################################################################################################################################
# ################################################################################################################################

class TestTimeouts:
    """ The configured timeout limits how long a response may take.
    """

    def test_timeout_raises(self, business_central_server):
        _seed_customers(business_central_server)
        business_central_server.configure('/v2.0/test-tenant/sandbox/api/v2.0/customers', delay=2)

        client = _bc_client(business_central_server, timeout=0.2)

        with pytest.raises(ReadTimeout):
            _ = client.read('customers')

        client.close()

    def test_slow_response_within_timeout(self, business_central_server):
        _seed_customers(business_central_server)
        business_central_server.configure('/v2.0/test-tenant/sandbox/api/v2.0/customers', delay=0.2)

        client = _bc_client(business_central_server, timeout=5)
        items = client.read('customers')
        client.close()

        assert len(items) == 3

# ################################################################################################################################
# ################################################################################################################################

class TestTLS:
    """ HTTPS connections verify or skip verification per configuration.
    """

    def test_verified_with_ca_bundle(self, business_central_tls_server):
        business_central_tls_server.reset()
        business_central_tls_server.add_entities('customers', 'id', [
            {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        ])

        ca_path = business_central_tls_server.tls_material.ca_path

        client = _bc_client(business_central_tls_server, validate_tls=ca_path)
        items = client.read('customers')
        client.close()

        assert len(items) == 1

    def test_unverified_self_signed_is_rejected(self, business_central_tls_server):
        business_central_tls_server.reset()

        # Verification against the system trust store is the default - the test CA is not in it.
        client = _bc_client(business_central_tls_server)

        with pytest.raises(SSLError):
            _ = client.read('customers')

        client.close()

    def test_verification_disabled(self, business_central_tls_server):
        business_central_tls_server.reset()
        business_central_tls_server.add_entities('customers', 'id', [
            {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        ])

        client = _bc_client(business_central_tls_server, validate_tls=False)
        items = client.read('customers')
        client.close()

        assert len(items) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestOperations:
    """ Function and action calls in both versions.
    """

    def test_v4_function_params_in_path(self, d365fo_server):
        d365fo_server.reset()
        d365fo_server.set_oauth_client('client-1', 'secret-1')
        d365fo_server.configure("/data/GetKeys(entity='CustomersV3')", operation=(OK, {'value': 'dataAreaId'}))

        config = {
            'address': d365fo_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'oauth2',
            'client_id': 'client-1',
            'client_secret': 'secret-1',
            'token_url': d365fo_server.token_url,
        }
        client = ODataClient(config)
        result = client.call_function('GetKeys', {'entity': 'CustomersV3'})
        client.close()

        # V4 function parameters travel inline in the path, inside the parentheses.
        assert result == {'value': 'dataAreaId'}
        assert d365fo_server.last_request['path'] == "/data/GetKeys(entity='CustomersV3')"

    def test_v2_function_params_in_query_string(self, s4hana_server):
        _seed_sales_orders(s4hana_server)
        s4hana_server.configure(
            '/sap/opu/odata/sap/API_SALES_ORDER_SRV/ReleaseApprovalRequest',
            operation=(OK, {'d': {'SalesOrder': '1', 'Released': True}}),
        )

        client = _s4_client(s4hana_server)
        result = client.call_function('ReleaseApprovalRequest', {'SalesOrder': '1'})
        client.close()

        # V2 function parameters travel in the query string, as quoted literals.
        assert result == {'SalesOrder': '1', 'Released': True}
        assert s4hana_server.last_request['query']['SalesOrder'] == "'1'"

    def test_action_posts_json_body(self, d365fo_server):
        d365fo_server.reset()
        d365fo_server.set_oauth_client('client-1', 'secret-1')
        d365fo_server.configure('/data/CalculateBalance', operation=(OK, {'value': 250.5}))

        config = {
            'address': d365fo_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'oauth2',
            'client_id': 'client-1',
            'client_secret': 'secret-1',
            'token_url': d365fo_server.token_url,
        }
        client = ODataClient(config)
        result = client.call_action('CalculateBalance', {'asOfDate': '2026-01-01'})
        client.close()

        assert result == {'value': 250.5}
        assert d365fo_server.last_request['method'] == 'POST'
        assert d365fo_server.last_request['json'] == {'asOfDate': '2026-01-01'}

# ################################################################################################################################
# ################################################################################################################################

class TestRequestShape:
    """ The headers and parameters every request carries.
    """

    def test_v4_version_headers(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.read('customers')
        client.close()

        headers = business_central_server.last_request['headers']

        assert headers['OData-Version'] == '4.0'
        assert headers['OData-MaxVersion'] == '4.0'
        assert headers['Accept'] == 'application/json;odata.metadata=minimal'

    def test_v2_accept_header(self, s4hana_server):
        _seed_sales_orders(s4hana_server)

        client = _s4_client(s4hana_server)
        _ = client.read('A_SalesOrder')
        client.close()

        headers = s4hana_server.last_request['headers']

        assert headers['Accept'] == 'application/json'
        assert 'OData-Version' not in headers

    def test_custom_headers_ride_along(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server, custom_headers={'X-Correlation-ID': 'abc-123'})
        _ = client.read('customers')
        client.close()

        assert business_central_server.last_request['headers']['X-Correlation-ID'] == 'abc-123'

    def test_write_body_is_json(self, business_central_server):
        _seed_customers(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.create('customers', {'displayName': 'New Co'})
        client.close()

        request = business_central_server.last_request

        assert request['headers']['Content-Type'] == 'application/json'
        assert request['json'] == {'displayName': 'New Co'}

# ################################################################################################################################
# ################################################################################################################################

class TestAuditCallback:
    """ The audit callback sees each request and response, including error payloads.
    """

    def test_request_and_response_recorded(self, business_central_server):
        _seed_customers(business_central_server)

        events = []

        def _callback(cid, event, endpoint, outcome, payload):
            events.append((cid, event, endpoint, outcome, payload))

        client = _bc_client(business_central_server)
        client.audit_callback = _callback

        _ = client.read('customers', cid='cid-1')
        client.close()

        assert len(events) == 2

        # The request went out first, then its response arrived.
        assert events[0][0] == 'cid-1'
        assert events[1][0] == 'cid-1'
        assert events[0][2] == events[1][2]

    def test_error_payload_recorded(self, business_central_server):
        business_central_server.reset()

        events = []

        def _callback(cid, event, endpoint, outcome, payload):
            events.append((cid, event, endpoint, outcome, payload))

        client = _bc_client(business_central_server)
        client.audit_callback = _callback

        with pytest.raises(ODataError):
            _ = client.read('no_such_set', cid='cid-2')

        client.close()

        # The error response was captured before the exception was raised.
        response_payload = events[1][4]
        assert b'NotFound' in response_payload

# ################################################################################################################################
# ################################################################################################################################
