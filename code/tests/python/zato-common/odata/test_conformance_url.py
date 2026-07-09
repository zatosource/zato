# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK
from uuid import UUID

# abnf
from abnf import Rule

# Zato
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataVersion

# ################################################################################################################################
# ################################################################################################################################

# The official OASIS grammars live in the fixture tree - the aggregation grammar
# extends the construction rules with the $apply vocabulary.
ABNF_Dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'abnf')

# ################################################################################################################################
# ################################################################################################################################

class ODataGrammar(Rule):
    """ The OData 4.01 URL grammar - every rule of the two official OASIS ABNF files.
    """

ODataGrammar.from_file(os.path.join(ABNF_Dir, 'odata-abnf-construction-rules.txt'))
ODataGrammar.from_file(os.path.join(ABNF_Dir, 'odata-aggregation-abnf.txt'))

# ################################################################################################################################
# ################################################################################################################################

class _CapturingResponse:
    """ The canned response the capturing session hands back - just enough of the
    requests response surface for the client to carry on.
    """
    def __init__(self):
        self.status_code = OK
        self.ok = True
        self.content = b'{"value": []}'
        self.text = '{"value": []}'
        self.headers = {}

    def json(self):
        out = {'value': []}
        return out

# ################################################################################################################################

class _CapturingSession:
    """ Stands in for the client's HTTP session - it never talks to any network,
    it only records the URLs the client generates.
    """
    def __init__(self):
        self.urls = []

    def request(self, method, url, **kwargs):
        self.urls.append(url)

        out = _CapturingResponse()
        return out

    def get(self, url, **kwargs):
        out = self.request('GET', url)
        return out

    def close(self):
        pass

# ################################################################################################################################

# Every URL the client generates is relative to this service root.
Service_Root = 'http://host/service/'

# ################################################################################################################################

def _capture(odata_version, invoke, **config_extra):
    """ Runs one client call against the capturing session and returns the generated
    URLs with the service root stripped - the odataRelativeUri of each request.
    """
    config = {
        'address': Service_Root,
        'odata_version': odata_version,
        'auth_type': 'none',
    }
    config.update(config_extra)

    client = ODataClient(config)

    session = _CapturingSession()
    client.session = session

    # Only the generated URLs matter here - the canned JSON body will not satisfy
    # every response parser, e.g. $count expects plain text and $metadata expects XML.
    try:
        invoke(client)
    except Exception:
        pass

    out = []
    for url in session.urls:
        out.append(url[len(Service_Root):])

    return out

# ################################################################################################################################

def _assert_valid(relative_uri):
    """ Parses one relative URI against the normative grammar - a ParseError means
    the client generated something the OData specification does not allow.
    """
    rule = ODataGrammar('odataRelativeUri')

    _ = rule.parse_all(relative_uri)

# ################################################################################################################################
# ################################################################################################################################

class TestSystemQueryOptions:
    """ Every $-option the client can generate, proven against the normative grammar.
    """

    def test_filter(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', filter="City eq 'Berlin'"))
        _assert_valid(urls[0])

    def test_filter_with_functions(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', filter="startswith(CompanyName,'A') and Value gt 7"))
        _assert_valid(urls[0])

    def test_select(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', select=['ID', 'CompanyName']))
        _assert_valid(urls[0])

    def test_expand(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', expand='Orders'))
        _assert_valid(urls[0])

    def test_orderby(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', orderby=['City desc', 'CompanyName']))
        _assert_valid(urls[0])

    def test_top_and_skip(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', top=10, skip=20))
        _assert_valid(urls[0])

    def test_count(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', count=True))
        _assert_valid(urls[0])

    def test_search(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', search='blue OR green'))
        _assert_valid(urls[0])

    def test_apply(self):
        apply_text = 'groupby((Country),aggregate(Amount with sum as Total))'
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', apply=apply_text))
        _assert_valid(urls[0])

    def test_everything_at_once(self):
        def invoke(client):
            _ = client.read(
                'Customers',
                filter="City eq 'Berlin'",
                select=['ID', 'CompanyName'],
                expand='Orders',
                orderby='CompanyName',
                top=10,
                skip=20,
                count=True,
            )

        urls = _capture(ODataVersion.V4, invoke)
        _assert_valid(urls[0])

# ################################################################################################################################
# ################################################################################################################################

class TestKeyFormats:
    """ Every key format the client can generate in a resource path.
    """

    def test_string_key(self):
        urls = _capture(ODataVersion.V4, lambda c: c.get('Customers', 'ALFKI'))
        _assert_valid(urls[0])

    def test_int_key(self):
        urls = _capture(ODataVersion.V4, lambda c: c.get('Orders', 10248))
        _assert_valid(urls[0])

    def test_guid_key(self):
        key = UUID('11111111-2222-3333-4444-555555555555')
        urls = _capture(ODataVersion.V4, lambda c: c.get('Customers', key))
        _assert_valid(urls[0])

    def test_composite_key(self):
        key = {'SalesOrder': '1', 'SalesOrderItem': 10}
        urls = _capture(ODataVersion.V4, lambda c: c.get('SalesOrderItems', key))
        _assert_valid(urls[0])

    def test_key_with_embedded_quote(self):
        urls = _capture(ODataVersion.V4, lambda c: c.get('Customers', "O'Brien"))
        _assert_valid(urls[0])

# ################################################################################################################################
# ################################################################################################################################

class TestEscaping:
    """ Characters that need percent-encoding survive it in grammar-valid form.
    """

    def test_spaces(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', filter="CompanyName eq 'Alfreds Futterkiste'"))

        assert ' ' not in urls[0]
        _assert_valid(urls[0])

    def test_unicode(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', filter="City eq 'Łódź'"))

        assert 'Łódź' not in urls[0]
        _assert_valid(urls[0])

    def test_ampersand_inside_a_literal(self):
        urls = _capture(ODataVersion.V4, lambda c: c.read('Customers', filter="CompanyName eq 'B&B'"))

        # The ampersand was encoded away, so it cannot split the query string.
        assert urls[0].count('&') == 0
        _assert_valid(urls[0])

# ################################################################################################################################
# ################################################################################################################################

class TestOperationsAndSegments:
    """ Functions, actions and the special path segments.
    """

    def test_function_with_parameters(self):
        urls = _capture(ODataVersion.V4, lambda c: c.call_function('GetNearestAirport', {'lat': 33, 'lon': -118.41}))
        _assert_valid(urls[0])

    def test_function_with_string_parameter(self):
        urls = _capture(ODataVersion.V4, lambda c: c.call_function('GetKeys', {'entity': 'CustomersV3'}))
        _assert_valid(urls[0])

    def test_action(self):
        urls = _capture(ODataVersion.V4, lambda c: c.call_action('ResetDataSource'))
        _assert_valid(urls[0])

    def test_count_segment(self):
        urls = _capture(ODataVersion.V4, lambda c: c.count('Customers', filter="City eq 'Berlin'"))
        _assert_valid(urls[0])

    def test_batch_segment(self):
        urls = _capture(ODataVersion.V4, lambda c: c.batch([]))
        _assert_valid(urls[0])

    def test_metadata_segment(self):
        urls = _capture(ODataVersion.V4, lambda c: c.metadata())
        _assert_valid(urls[0])

    def test_nested_path(self):
        entity_set = 'companies(11111111-2222-3333-4444-555555555555)/customers'
        urls = _capture(ODataVersion.V4, lambda c: c.read(entity_set, top=5))
        _assert_valid(urls[0])

# ################################################################################################################################
# ################################################################################################################################

class TestCustomParameters:
    """ System-specific parameters ride along without breaking grammar validity.
    """

    def test_custom_query_params(self):
        urls = _capture(
            ODataVersion.V4,
            lambda c: c.read('Customers', top=5),
            custom_query_params={'cross-company': 'true'},
        )
        _assert_valid(urls[0])

    def test_write_paths(self):
        def invoke(client):
            _ = client.create('Customers', {'CompanyName': 'New Co'})
            _ = client.update('Customers', 'ALFKI', {'City': 'Berlin'}, etag='*')
            client.delete('Customers', 'ALFKI', etag='*')

        urls = _capture(ODataVersion.V4, invoke)

        for url in urls:
            _assert_valid(url)

# ################################################################################################################################
# ################################################################################################################################

class TestV2URLs:
    """ V2 predates the OASIS grammar, so only its grammar-compatible parts are provable -
    resource paths and the $-options V2 shares with V4.
    """

    def test_paths_and_shared_options(self):
        def invoke(client):
            _ = client.read('Customers', filter="City eq 'Berlin'", top=10, skip=20)
            _ = client.get('Customers', 'ALFKI')
            _ = client.count('Customers')

        urls = _capture(ODataVersion.V2, invoke)

        for url in urls:
            _assert_valid(url)

# ################################################################################################################################
# ################################################################################################################################
