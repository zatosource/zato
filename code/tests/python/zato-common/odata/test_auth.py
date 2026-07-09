# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from http.client import UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataError, ODataException, ODataVersion

# ################################################################################################################################
# ################################################################################################################################

def _seed_people(server):
    """ Loads a predictable set of SuccessFactors person records and enforces the
    profile's credentials and the $format parameter the real system insists on.
    """
    server.reset()
    server.set_credentials('sfadmin@COMPANY', 'sf-pass')
    server.require_query_params({'$format': 'json'})
    server.add_entities('PerPerson', 'personIdExternal', [
        {'personIdExternal': 'emp-1', 'countryOfBirth': 'PL'},
        {'personIdExternal': 'emp-2', 'countryOfBirth': 'DE'},
    ])

# ################################################################################################################################

def _sf_client(server, **extra):
    """ A client for the SuccessFactors profile - V2, basic credentials with a company id.
    """
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V2,
        'auth_type': 'basic',
        'username': 'sfadmin@COMPANY',
        'secret': 'sf-pass',
        'custom_query_params': {'$format': 'json'},
    }
    config.update(extra)

    out = ODataClient(config)
    return out

# ################################################################################################################################

def _d365_client(server, **extra):
    """ A client for the Dynamics profile - V4, OAuth2 client credentials.
    """
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V4,
        'auth_type': 'oauth2',
        'client_id': 'client-1',
        'client_secret': 'secret-1',
        'token_url': server.token_url,
    }
    config.update(extra)

    out = ODataClient(config)
    return out

# ################################################################################################################################

def _seed_vendors(server):
    """ Loads a predictable set of Dynamics vendors and configures the token endpoint.
    """
    server.reset()
    server.set_oauth_client('client-1', 'secret-1')
    server.add_entities('VendorsV2', 'VendorAccountNumber', [
        {'dataAreaId': 'usmf', 'VendorAccountNumber': 'V-001', 'VendorGroupId': '10'},
    ])

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuth:
    """ Basic credentials against the SuccessFactors profile.
    """

    def test_valid_credentials(self, successfactors_server):
        _seed_people(successfactors_server)

        client = _sf_client(successfactors_server)
        items = client.read('PerPerson')
        client.close()

        assert len(items) == 2

        # The credentials traveled as one Basic Authorization header.
        expected = b64encode(b'sfadmin@COMPANY:sf-pass').decode('ascii')
        assert successfactors_server.last_request['headers']['Authorization'] == f'Basic {expected}'

    def test_wrong_password(self, successfactors_server):
        _seed_people(successfactors_server)

        client = _sf_client(successfactors_server, secret='wrong')

        with pytest.raises(ODataError) as ctx:
            _ = client.read('PerPerson')

        client.close()

        assert ctx.value.status_code == UNAUTHORIZED

    def test_wrong_username(self, successfactors_server):
        _seed_people(successfactors_server)

        client = _sf_client(successfactors_server, username='other@COMPANY')

        with pytest.raises(ODataError) as ctx:
            _ = client.read('PerPerson')

        client.close()

        assert ctx.value.status_code == UNAUTHORIZED

    def test_missing_credentials(self, successfactors_server):
        _seed_people(successfactors_server)

        config = {
            'address': successfactors_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
            'custom_query_params': {'$format': 'json'},
        }
        client = ODataClient(config)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('PerPerson')

        client.close()

        assert ctx.value.status_code == UNAUTHORIZED

# ################################################################################################################################
# ################################################################################################################################

class TestBearerAuth:
    """ A static bearer token - the Dynamics profile accepts only tokens its endpoint issued.
    """

    def test_issued_token_is_accepted(self, d365fo_server):
        _seed_vendors(d365fo_server)

        # A token obtained out of band, e.g. by an external token manager.
        token = d365fo_server._httpd.issue_bearer_token()

        config = {
            'address': d365fo_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'bearer',
            'secret': token,
        }
        client = ODataClient(config)
        items = client.read('VendorsV2')
        client.close()

        assert len(items) == 1
        assert d365fo_server.last_request['headers']['Authorization'] == f'Bearer {token}'

    def test_unknown_token_is_rejected(self, d365fo_server):
        _seed_vendors(d365fo_server)

        config = {
            'address': d365fo_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'bearer',
            'secret': 'made-up-token',
        }
        client = ODataClient(config)

        with pytest.raises(ODataError) as ctx:
            _ = client.read('VendorsV2')

        client.close()

        assert ctx.value.status_code == UNAUTHORIZED

# ################################################################################################################################
# ################################################################################################################################

class TestOAuth2:
    """ The client-credentials grant against the profile's Azure AD style token endpoint.
    """

    def test_token_is_obtained_and_used(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server)
        items = client.read('VendorsV2')
        client.close()

        assert len(items) == 1
        assert len(d365fo_server.issued_tokens) == 1

        # The data request carried the token the endpoint had just issued.
        token = d365fo_server.issued_tokens[0]
        assert d365fo_server.last_request['headers']['Authorization'] == f'Bearer {token}'

    def test_token_is_cached_between_requests(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server)
        _ = client.read('VendorsV2')
        _ = client.read('VendorsV2')
        _ = client.read('VendorsV2')
        client.close()

        # Three reads, one token - the cache did its job.
        assert len(d365fo_server.issued_tokens) == 1

    def test_expired_token_is_refreshed_on_401(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server)
        _ = client.read('VendorsV2')

        # The server forgets the token, as if it had expired server-side.
        d365fo_server.issued_tokens.clear()

        items = client.read('VendorsV2')
        client.close()

        # The read succeeded through one transparent refresh.
        assert len(items) == 1
        assert len(d365fo_server.issued_tokens) == 1

    def test_wrong_client_secret(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server, client_secret='wrong')

        with pytest.raises(ODataException):
            _ = client.read('VendorsV2')

        client.close()

    def test_scopes_travel_space_separated(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server, scopes='https://example.com/.default\noffline_access')
        _ = client.read('VendorsV2')
        client.close()

        # The token request carried the scopes as one space-separated value.
        token_request = d365fo_server.recorded_requests[0]
        assert b'scope=https%3A%2F%2Fexample.com%2F.default+offline_access' in token_request['raw_body']

    def test_missing_token_url_and_tenant(self, d365fo_server):
        _seed_vendors(d365fo_server)

        client = _d365_client(d365fo_server, token_url=None)

        with pytest.raises(ODataException) as ctx:
            _ = client.read('VendorsV2')

        client.close()

        assert 'token_url or tenant_id' in str(ctx.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCSRF:
    """ The SAP CSRF exchange against the S/4HANA profile.
    """

    def test_token_fetched_before_first_write(self, s4hana_server):
        s4hana_server.reset()
        s4hana_server.add_entities('A_SalesOrder', 'SalesOrder', [])

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
            'needs_csrf_token': True,
        }
        client = ODataClient(config)
        _ = client.create('A_SalesOrder', {'SalesOrder': '1'})
        client.close()

        # The fetch went to the service root with the Fetch marker, before the write.
        fetch_request = s4hana_server.recorded_requests[0]
        assert fetch_request['method'] == 'GET'
        assert fetch_request['headers']['X-CSRF-Token'] == 'Fetch'

        # The write then carried the token the fetch obtained.
        write_request = s4hana_server.recorded_requests[1]
        assert write_request['method'] == 'POST'
        assert write_request['headers']['X-CSRF-Token'] == s4hana_server._httpd.csrf_token

    def test_token_reused_across_writes(self, s4hana_server):
        s4hana_server.reset()
        s4hana_server.add_entities('A_SalesOrder', 'SalesOrder', [])

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
            'needs_csrf_token': True,
        }
        client = ODataClient(config)
        _ = client.create('A_SalesOrder', {'SalesOrder': '1'})
        _ = client.create('A_SalesOrder', {'SalesOrder': '2'})
        client.close()

        # One fetch served both writes.
        fetches = []
        for request in s4hana_server.recorded_requests:
            if request['headers'].get('X-CSRF-Token') == 'Fetch':
                fetches.append(request)

        assert len(fetches) == 1

    def test_stale_token_is_refetched_once(self, s4hana_server):
        s4hana_server.reset()
        s4hana_server.add_entities('A_SalesOrder', 'SalesOrder', [])

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
            'needs_csrf_token': True,
        }
        client = ODataClient(config)
        _ = client.create('A_SalesOrder', {'SalesOrder': '1'})

        # The server rotates its token, so the client's cached one goes stale.
        _ = s4hana_server._httpd.issue_csrf_token()

        created = client.create('A_SalesOrder', {'SalesOrder': '2'})
        client.close()

        # The write succeeded through one transparent refetch.
        assert created['SalesOrder'] == '2'
        assert '2' in s4hana_server.entities['A_SalesOrder']

    def test_reads_never_fetch_a_token(self, s4hana_server):
        s4hana_server.reset()
        s4hana_server.add_entities('A_SalesOrder', 'SalesOrder', [])

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
            'needs_csrf_token': True,
        }
        client = ODataClient(config)
        _ = client.read('A_SalesOrder')
        client.close()

        # One request only - no fetch preceded the read.
        assert len(s4hana_server.recorded_requests) == 1

# ################################################################################################################################
# ################################################################################################################################
