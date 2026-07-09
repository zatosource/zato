# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import NOT_IMPLEMENTED, PRECONDITION_FAILED
from json import loads

# pytest
import pytest

# Zato
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataError, ODataVersion, extract_entity, extract_items, extract_next_link, parse_error

# ################################################################################################################################
# ################################################################################################################################

# The normative payload examples live in the fixture tree.
Payloads_Dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'payloads')

# ################################################################################################################################
# ################################################################################################################################

def _load_payload(file_name):
    """ Reads one normative payload example from the fixture tree.
    """
    path = os.path.join(Payloads_Dir, file_name)

    with open(path, 'rb') as payload_file:
        out = loads(payload_file.read())

    return out

# ################################################################################################################################

def _bc_client(server, **extra):
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V4,
        'auth_type': 'none',
    }
    config.update(extra)

    out = ODataClient(config)
    return out

# ################################################################################################################################

def _seed(server):
    server.reset()
    server.add_entities('customers', 'id', [
        {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        {'id': 'aaaa0002-0000-0000-0000-000000000002', 'displayName': 'Trey Research'},
        {'id': 'aaaa0003-0000-0000-0000-000000000003', 'displayName': 'School of Art'},
    ])

# ################################################################################################################################
# ################################################################################################################################

class TestMustClauses:
    """ OASIS OData 4.01 Part 1, section 13.3 'Interoperable OData Clients' - one test
    per numbered MUST requirement.
    """

    def test_13_3_1_odata_maxversion_header(self, business_central_server):
        """ 13.3 clause 1 - clients MUST specify the OData-MaxVersion header in requests
        (section 8.2.7).
        """
        _seed(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.read('customers')
        client.close()

        assert business_central_server.last_request['headers']['OData-MaxVersion'] == '4.0'

    def test_13_3_2_odata_version_and_content_type_with_payload(self, business_central_server):
        """ 13.3 clause 2 - clients MUST specify OData-Version (section 8.1.5) and
        Content-Type (section 8.1.1) in any request with a payload.
        """
        _seed(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.create('customers', {'displayName': 'New Co'})
        client.close()

        headers = business_central_server.last_request['headers']

        assert headers['OData-Version'] == '4.0'
        assert headers['Content-Type'] == 'application/json'

    def test_13_3_3_conforming_json_consumer(self):
        """ 13.3 clause 3 - clients MUST be a conforming consumer of OData as defined
        in [OData-JSON]. The normative spec examples parse into the expected shapes.
        """
        feed = _load_payload('v4-feed.json')
        items = extract_items(feed, ODataVersion.V4)

        assert len(items) == 2
        assert items[0]['ID'] == 'ALFKI'
        assert items[0]['Address']['City'] == 'Berlin'

        entity_payload = _load_payload('v4-entity.json')
        entity = extract_entity(entity_payload, ODataVersion.V4)

        assert entity['CompanyName'] == 'Alfreds Futterkiste'
        assert entity['@odata.etag'] == 'W/"MjAxMy0wNS0yN1QxMTo1OFo="'

    def test_13_3_4_follows_redirects(self, business_central_server):
        """ 13.3 clause 4 - clients MUST follow redirects (section 9.1.5).
        """
        _seed(business_central_server)

        # The old path redirects to where the entities really are.
        target = business_central_server.service_root + '/customers'
        business_central_server.configure(
            '/v2.0/test-tenant/sandbox/api/v2.0/customersOld', redirect=target)

        client = _bc_client(business_central_server)
        items = client.read('customersOld')
        client.close()

        assert len(items) == 3

    def test_13_3_5_handles_next_links(self, business_central_server):
        """ 13.3 clause 5 - clients MUST correctly handle next links (section 11.2.6.7),
        proven both against the normative example and against a live paging server.
        """
        feed = _load_payload('v4-feed-next-link.json')

        next_link = extract_next_link(feed, ODataVersion.V4)
        assert next_link == 'http://host/service/Customers?$skiptoken=ANATR'

        _seed(business_central_server)
        business_central_server.set_page_size(1)

        client = _bc_client(business_central_server)
        items = list(client.iter('customers'))
        client.close()

        assert len(items) == 3

    def test_13_3_6_tolerates_unknown_properties_and_annotations(self):
        """ 13.3 clause 6 - clients MUST support instances returning properties and
        navigation properties not specified in metadata (section 11.2). Unknown
        annotations and extra properties pass through parsing untouched.
        """
        feed = _load_payload('v4-feed-delta-link.json')
        items = extract_items(feed, ODataVersion.V4)

        # The delta link annotation did not disturb item extraction ..
        assert len(items) == 2

        # .. and neither do arbitrary annotations or never-declared properties.
        entity_payload = _load_payload('v4-entity.json')
        entity = extract_entity(entity_payload, ODataVersion.V4)

        assert entity['Orders@odata.navigationLink'] == "Customers('ALFKI')/Orders"
        assert entity['@odata.editLink'] == "Customers('ALFKI')"

    def test_13_3_7_updates_use_patch(self, business_central_server):
        """ 13.3 clause 7 - clients that support updates MUST generate PATCH requests
        (section 11.4.3).
        """
        _seed(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.update('customers', 'aaaa0001-0000-0000-0000-000000000001', {'displayName': 'Renamed'}, etag='*')
        client.close()

        assert business_central_server.last_request['method'] == 'PATCH'

# ################################################################################################################################
# ################################################################################################################################

class TestShouldClauses:
    """ The section 13.3 SHOULD requirement.
    """

    def test_13_3_8_basic_authentication_over_https(self, business_central_tls_server):
        """ 13.3 clause 8 - clients SHOULD support basic authentication as defined in
        [RFC7617] over HTTPS.
        """
        business_central_tls_server.reset()
        business_central_tls_server.set_credentials('bc-user', 'bc-pass')
        business_central_tls_server.add_entities('customers', 'id', [
            {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        ])

        ca_path = business_central_tls_server.tls_material.ca_path

        client = _bc_client(
            business_central_tls_server,
            auth_type='basic',
            username='bc-user',
            secret='bc-pass',
            validate_tls=ca_path,
        )
        items = client.read('customers')
        client.close()

        assert len(items) == 1
        assert business_central_tls_server.last_request['headers']['Authorization'].startswith('Basic ')

# ################################################################################################################################
# ################################################################################################################################

class TestMayClauses:
    """ The section 13.3 MAY requirements this client chooses to support.
    """

    def test_13_3_13_search_query_option(self, business_central_server):
        """ 13.3 clause 13 - clients MAY support the $search system query option
        (section 11.2.5.6).
        """
        _seed(business_central_server)

        client = _bc_client(business_central_server)
        _ = client.read('customers', search='Adatum')
        client.close()

        assert business_central_server.last_request['query']['$search'] == 'Adatum'

# ################################################################################################################################
# ################################################################################################################################

class TestErrorFormat:
    """ Section 9.4 - error responses of both versions parse into one exception type,
    proven against the normative examples.
    """

    def test_v4_error_example(self):
        payload = _load_payload('v4-error.json')

        error = parse_error(NOT_IMPLEMENTED, payload)

        assert error.status_code == NOT_IMPLEMENTED
        assert error.code == '501'
        assert error.message == 'Unsupported functionality'
        assert error.details[0]['target'] == '$search'

    def test_v2_error_example(self):
        payload = _load_payload('v2-error.json')

        error = parse_error(NOT_IMPLEMENTED, payload)

        # The V2 language-tagged message surfaces as its plain text.
        assert error.code == 'SY/530'
        assert error.message == 'Maintain the business partner for sales organization 1710'

# ################################################################################################################################
# ################################################################################################################################

class TestV2Payloads:
    """ The V2 verbose-JSON examples - feeds, entities and paging links.
    """

    def test_verbose_feed(self):
        payload = _load_payload('v2-feed-verbose.json')

        items = extract_items(payload, ODataVersion.V2)

        assert len(items) == 2
        assert items[0]['CustomerID'] == 'ALFKI'

        # The deferred navigation property and the __metadata object pass through untouched.
        assert items[0]['__metadata']['type'] == 'NorthwindModel.Customer'
        assert items[0]['Orders']['__deferred']['uri'] == "http://host/service/Customers('ALFKI')/Orders"

        next_link = extract_next_link(payload, ODataVersion.V2)
        assert next_link == "http://host/service/Customers?$skiptoken='ANATR'"

    def test_plain_feed(self):
        payload = _load_payload('v2-feed-plain.json')

        # Older V2 servers return the list directly under 'd', with no paging possible.
        items = extract_items(payload, ODataVersion.V2)
        assert len(items) == 2

        next_link = extract_next_link(payload, ODataVersion.V2)
        assert next_link is None

    def test_entity(self):
        payload = _load_payload('v2-entity.json')

        entity = extract_entity(payload, ODataVersion.V2)

        assert entity['CustomerID'] == 'ALFKI'
        assert entity['__metadata']['etag'] == 'W/"X\'00000000000007D1\'"'

# ################################################################################################################################
# ################################################################################################################################

class TestETagHandling:
    """ Sections 8.2.4 and 11.4.1.1 - the ETag a response carries goes back in If-Match,
    and a stale one is rejected with 412.
    """

    def test_etag_round_trip(self, business_central_server):
        _seed(business_central_server)

        client = _bc_client(business_central_server)

        entity = client.get('customers', 'aaaa0001-0000-0000-0000-000000000001')
        etag = entity['@odata.etag']

        _ = client.update('customers', 'aaaa0001-0000-0000-0000-000000000001', {'displayName': 'Renamed'}, etag=etag)

        # The ETag traveled back in If-Match, exactly as received.
        assert business_central_server.last_request['headers']['If-Match'] == etag

        # The update rotated the ETag server-side, so the old one is now stale.
        with pytest.raises(ODataError) as ctx:
            _ = client.update('customers', 'aaaa0001-0000-0000-0000-000000000001', {'displayName': 'Again'}, etag=etag)

        client.close()

        assert ctx.value.status_code == PRECONDITION_FAILED

# ################################################################################################################################
# ################################################################################################################################
