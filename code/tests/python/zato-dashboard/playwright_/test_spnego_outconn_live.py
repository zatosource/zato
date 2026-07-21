# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# pytest
import pytest

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from http_test_server import SPNEGOTestServer
from live_kerberos.containers import start_kdc, stop_kdc, ModuleCtx as KerberosCtx
from rest_channel import create_spnego_definition
from rest_outconn import create_outconn, invoke_outconn_via_overlay, ping_outconn_until_success

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.spnego.' + rand_string() + '.'

# Log patterns produced when GSSAPI cannot acquire credentials for a principal absent from the keytab
_SPNEGO_Failure_Log_Patterns = ('MissingCredentialsError', 'No credentials were supplied', \
    'Can\'t find client principal', 'no suitable keys')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def kerberos_kdc() -> 'any_':
    """ A live MIT KDC container with the test realm, keytabs and krb5.conf in place,
    for the duration of the module.
    """

    start_kdc()

    # This process performs the accept side of the negotiation, so its own GSSAPI calls
    # must resolve the realm through the same configuration.
    os.environ['KRB5_CONFIG'] = KerberosCtx.Krb5_Config_Path

    yield KerberosCtx

    stop_kdc()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def spnego_test_server(kerberos_kdc:'any_') -> 'any_':
    """ A live recording server protected with SPNEGO, for the duration of a single test.
    """

    server = SPNEGOTestServer(kerberos_kdc.Service_SPN, kerberos_kdc.Service_Keytab_Path)
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestSPNEGOOutconnLive:
    """ End-to-end tests for Kerberos (SPNEGO) security on outgoing REST connections,
    against a live KDC and a live SPNEGO-protected endpoint.
    """

    def test_spnego_live_negotiate(
        self, logged_in_page:'Page', zato_dashboard:'anydict', spnego_test_server:'SPNEGOTestServer') -> 'None':
        """ Creates a Kerberos definition backed by the KDC's client keytab, assigns it
        to a connection and verifies the endpoint authenticated the expected principal
        through the full 401-negotiate-retry dance.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'live'
        url_path = '/test/outconn/spnego-live/' + rand_string()

        # Create the security definition pointing at the live keytab ..
        definition = create_spnego_definition(page, base_url, _Test_Name_Prefix + 'live-def', {
            'principal': KerberosCtx.Client_Principal,
            'keytab_path': KerberosCtx.Client_Keytab_Path,
            'target_spn': KerberosCtx.Service_SPN,
        })

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, spnego_test_server.address, {
            'url_path': url_path,
            'security': f'Kerberos (SPNEGO)/{definition["name"]}',
        })

        # .. the ping succeeds only once the negotiation works end to end,
        # which also covers the propagation delay of the new definition ..
        ping_result = ping_outconn_until_success(page, outconn_name)
        assert ping_result['is_success'], f'Expected a successful ping with Kerberos credentials, got: {ping_result}'

        # .. invoke it ..
        spnego_test_server.clear_requests()
        _ = invoke_outconn_via_overlay(page, outconn_id, request_body='{"check": "spnego"}')

        requests = spnego_test_server.wait_for_request_count(1)
        request = requests[0]

        logger.info('[test_spnego_live_negotiate] request=%s', request)

        # .. the request reached the endpoint with a Negotiate token ..
        auth_header = request['headers'].get('Authorization', '')
        assert auth_header.startswith('Negotiate '), f'Expected a Negotiate token, got: {request}'

        # .. and the endpoint verified the expected principal.
        assert request['spnego_principal'] == KerberosCtx.Client_Principal, \
            f'Expected principal "{KerberosCtx.Client_Principal}", got: {request}'

# ################################################################################################################################

    def test_spnego_live_wrong_principal(
        self, logged_in_page:'Page', zato_dashboard:'anydict', spnego_test_server:'SPNEGOTestServer') -> 'None':
        """ A definition whose principal is absent from the keytab cannot authenticate -
        the credential acquisition fails and the endpoint records no authenticated requests.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'wrong-principal'
        url_path = '/test/outconn/spnego-neg/' + rand_string()

        # Create a definition with a principal the KDC has never heard of ..
        definition = create_spnego_definition(page, base_url, _Test_Name_Prefix + 'wrong-def', {
            'principal': KerberosCtx.Wrong_Principal,
            'keytab_path': KerberosCtx.Client_Keytab_Path,
            'target_spn': KerberosCtx.Service_SPN,
        })

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, spnego_test_server.address, {
            'url_path': url_path,
            'security': f'Kerberos (SPNEGO)/{definition["name"]}',
        })

        # .. invoke it through the overlay ..
        spnego_test_server.clear_requests()
        result = invoke_outconn_via_overlay(page, outconn_id, request_body='{"check": "spnego-neg"}')

        logger.info('[test_spnego_live_wrong_principal] result=%s', result)

        # .. the overlay itself returns OK because the invoking service responded, so the failed
        # credential acquisition shows up in the response text rather than in the status line ..
        response_text = result['response']

        has_spnego_failure = False
        for pattern in _SPNEGO_Failure_Log_Patterns:
            if pattern in response_text:
                has_spnego_failure = True
                break

        assert has_spnego_failure, f'Expected a credential acquisition failure in the response, got: {result}'

        # .. and no authenticated request made it through.
        recorded = spnego_test_server.recorded_requests
        assert not recorded, f'Expected no recorded requests, got: {recorded}'

# ################################################################################################################################
# ################################################################################################################################
