# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from http.client import OK, UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - test helpers
_keycloak_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'test'))

if _keycloak_directory not in sys.path:
    sys.path.insert(0, _keycloak_directory)

import keycloak_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from requests import Response
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from bearer_token import create_dynamic_definition, edit_definition
from rest_channel import create_channel, invoke_channel, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.bearer.rest.' + CryptoManager.generate_hex_string(32) + '.'

_Echo_Service = 'demo.echo'

# Log patterns produced by the server when a security definition rejects credentials
_Auth_Log_Patterns = ('401 Unauthorized path_info', 'Unauthorized; path_info')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def keycloak() -> 'None':
    keycloak_.ensure_keycloak()

# ################################################################################################################################

def _bearer_headers(token:'str') -> 'anydict':
    """ Returns HTTP headers carrying the given bearer token.
    """

    out = {'Authorization': f'Bearer {token}'}
    return out

# ################################################################################################################################

def _assert_bearer_challenge(response:'Response') -> 'None':
    """ Asserts that a response is a 401 with the RFC 6750 Bearer challenge.
    """

    assert response.status_code == UNAUTHORIZED, f'Expected 401, got {response.status_code} -> {response.text}'

    challenge = response.headers['WWW-Authenticate']
    assert challenge == 'Bearer', f'Expected a Bearer challenge, got: {challenge}'

# ################################################################################################################################

def _create_keycloak_definition(page:'Page', base_url:'str', name:'str', claims:'str') -> 'str':
    """ Creates a Bearer token definition pointing to the test Keycloak instance and returns its ID.
    The client ID is unique per definition because the database enforces unique usernames
    and these tests verify inbound tokens only, never fetching any outbound ones themselves.
    """

    out = create_dynamic_definition(page, base_url, name, {
        'username': 'client.' + name,
        'secret': keycloak_.Secret_Accounting,
        'auth_server_url': keycloak_.get_token_url(),
        'issuer': keycloak_.get_issuer(),
        'audience': keycloak_.Audience_Main,
        'claims': claims,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBearerTokenRESTChannel:
    """ Tests for Bearer token definitions assigned to REST channels via the web admin UI,
    with live calls authenticated by Keycloak-issued JWTs.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_channel_with_keycloak_token(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition and a REST channel with it, then verifies a valid Keycloak
        token passes while a wrong-audience token and an anonymous call get 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'live'
        channel_name = _Test_Name_Prefix + 'channel-live'
        url_path = '/test/bearer/live/' + CryptoManager.generate_hex_string()

        # Create the definition pointing to Keycloak ..
        _ = _create_keycloak_definition(
            page, base_url, definition_name, f'{keycloak_.Claim_Department}={keycloak_.Department_Accounting}')

        # .. create the channel with the definition assigned directly ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Bearer token/{definition_name}',
        })

        # .. a valid Keycloak token passes ..
        token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
        headers = _bearer_headers(token)

        response = invoke_until_status(server_port, url_path, OK, data='{"bearer": "live"}', headers=headers)
        assert response.status_code == OK, f'Expected OK for a valid token, got {response.status_code}: {response.text}'

        # .. a wrong-audience token is rejected with the Bearer challenge ..
        wrong_audience_token = keycloak_.get_token(keycloak_.Client_Wrong_Audience, keycloak_.Secret_Wrong_Audience)
        wrong_audience_headers = _bearer_headers(wrong_audience_token)

        response = invoke_channel(server_port, url_path, data='{"bearer": "wrong-audience"}', headers=wrong_audience_headers)
        _assert_bearer_challenge(response)

        # .. a token with the right audience but a mismatched claim is rejected too ..
        sales_token = keycloak_.get_token(keycloak_.Client_Sales, keycloak_.Secret_Sales)
        sales_headers = _bearer_headers(sales_token)

        response = invoke_channel(server_port, url_path, data='{"bearer": "claim-mismatch"}', headers=sales_headers)
        _assert_bearer_challenge(response)

        # .. and so is an anonymous call.
        response = invoke_channel(server_port, url_path, data='{"bearer": null}')
        _assert_bearer_challenge(response)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_audience_edit_propagates(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition and a channel, then breaks the audience via the edit dialog
        and verifies a previously valid token now gets 401, all without a server restart.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'edit'
        channel_name = _Test_Name_Prefix + 'channel-edit'
        url_path = '/test/bearer/edit/' + CryptoManager.generate_hex_string()

        # Create the definition and its channel ..
        definition_id = _create_keycloak_definition(
            page, base_url, definition_name, f'{keycloak_.Claim_Department}={keycloak_.Department_Accounting}')

        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Bearer token/{definition_name}',
        })

        # .. the token passes with the correct audience in place ..
        token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
        headers = _bearer_headers(token)

        response = invoke_until_status(server_port, url_path, OK, data='{"audience": "good"}', headers=headers)
        assert response.status_code == OK, f'Expected OK before the edit, got {response.status_code}: {response.text}'

        # .. break the audience via the edit dialog ..
        edit_definition(page, base_url, definition_id, {
            'audience': 'audience-that-matches-nothing',
        })

        # .. the same token is now rejected ..
        response = invoke_until_status(server_port, url_path, UNAUTHORIZED, data='{"audience": "broken"}', headers=headers)
        _assert_bearer_challenge(response)

        # .. restore the audience ..
        edit_definition(page, base_url, definition_id, {
            'audience': keycloak_.Audience_Main,
        })

        # .. and the token passes again, still without a restart.
        response = invoke_until_status(server_port, url_path, OK, data='{"audience": "restored"}', headers=headers)
        assert response.status_code == OK, f'Expected OK after the restore, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################
