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
import time
from http.client import FORBIDDEN, OK

# pytest
import pytest

# requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form

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
    from zato.common.typing_ import anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

from bearer_token import create_dynamic_definition, edit_group_members

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.bearer.mcp.' + CryptoManager.generate_hex_string(32) + '.'

_MCP_Page_Url = '/zato/gateway/mcp/?cluster=1'

_Echo_Service = 'demo.echo'

# MCP gateways auto-create their security group under this prefix followed by the gateway name
_MCP_Group_Name_Prefix = 'mcp.'

# How long to wait for a UI change to propagate to live MCP enforcement, in seconds
_Propagation_Timeout = 10

# How long to wait between the polling attempts above, in seconds
_Propagation_Poll_Interval = 0.5

# Log patterns produced by the server when group credentials are rejected
_Group_Log_Patterns = (
    'Invalid bearer token (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
)

# The group-name uniqueness probe queries a groups table missing from the quickstart ODB,
# so the dashboard middleware logs this warning whenever a group is edited via the UI
_Group_Edit_Log_Patterns = ('nDetails: ··· Error ···',)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def keycloak() -> 'None':
    keycloak_.ensure_keycloak()

# ################################################################################################################################

def _post_jsonrpc(server_port:'int', url_path:'str', body:'str', token:'strnone'=None, session_id:'strnone'=None) -> 'Response':
    """ Posts a JSON-RPC request to the given MCP URL path, optionally with a bearer token and a session ID.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'
    headers = {'Content-Type': 'application/json'}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    if session_id:
        headers['Mcp-Session-Id'] = session_id

    out = requests.post(url, data=body, headers=headers, timeout=10)

    logger.info('[_post_jsonrpc] POST %s session=%s -> status=%d', url_path, session_id, out.status_code)

    return out

# ################################################################################################################################

def _initialize_until_status(server_port:'int', url_path:'str', token:'strnone', expected_status:'int') -> 'Response':
    """ Sends initialize requests until the expected status arrives, which covers the short window
    between a UI change and its propagation to the server. Returns the last response.
    """

    body = make_jsonrpc_initialize()
    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = _post_jsonrpc(server_port, url_path, body, token)

        # Stop as soon as we see the expected status ..
        if out.status_code == expected_status:
            break

        # .. or when the deadline passes, in which case the caller's assertion will fail with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################

def _create_mcp_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str') -> 'None':
    """ Creates an MCP gateway via the UI with the echo service assigned through the badge picker.
    """

    # Navigate to the MCP gateways page ..
    navigate_to_page(page, base_url, _MCP_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the basic fields ..
    page.fill('#id_name', gateway_name)
    page.fill('#id_url_path', url_path)

    # .. assign the echo service via its badge ..
    badge_selector = f'#badge-zone-available-create .badge-zone-body .security-badge[data-name="{_Echo_Service}"]'
    badge = page.wait_for_selector(badge_selector, state='visible', timeout=10000)
    badge.click()

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{gateway_name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestBearerTokenMCPGateway:
    """ Tests for Bearer token definitions enforced on MCP gateways through security groups,
    with a live MCP client authenticated by Keycloak-issued JWTs.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_gateway_with_keycloak_token(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Puts a claim-filtered definition into an MCP gateway's security group and verifies
        the full initialize and tools/call flow with a matching Keycloak JWT,
        then a claim-filter rejection with a non-matching one.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'accounting'
        gateway_name = _Test_Name_Prefix + 'gateway'
        url_path = '/mcp/test/bearer/' + CryptoManager.generate_hex_string()

        # Create the definition pointing to Keycloak, filtered to the Accounting department ..
        _ = create_dynamic_definition(page, base_url, definition_name, {
            'username': keycloak_.Client_Accounting,
            'secret': keycloak_.Secret_Accounting,
            'auth_server_url': keycloak_.get_token_url(),
            'issuer': keycloak_.get_issuer(),
            'audience': keycloak_.Audience_Main,
            'claims': f'{keycloak_.Claim_Department}={keycloak_.Department_Accounting}',
        })

        # .. create the gateway, which auto-creates its own security group ..
        _create_mcp_gateway(page, base_url, gateway_name, url_path)

        # .. and put the definition into that group.
        group_name = _MCP_Group_Name_Prefix + gateway_name
        edit_group_members(page, base_url, group_name, add_names=[definition_name])

        # A matching token now completes the initialize flow ..
        accounting_token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)

        initialize_response = _initialize_until_status(server_port, url_path, accounting_token, OK)
        assert initialize_response.status_code == OK, \
            f'Expected OK for a matching token, got {initialize_response.status_code}: {initialize_response.text}'

        session_id = initialize_response.headers['Mcp-Session-Id']

        # .. and a tools/call runs through with the session ..
        tools_call_body = json.dumps({
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 2,
            'params': {
                'name': _Echo_Service,
                'arguments': {'hello': 'world'},
            },
        })

        tools_call_response = _post_jsonrpc(server_port, url_path, tools_call_body, accounting_token, session_id)
        assert tools_call_response.status_code == OK, \
            f'Expected OK for tools/call, got {tools_call_response.status_code}: {tools_call_response.text}'

        # .. the echo service returns the arguments unchanged ..
        json_body = tools_call_response.json()
        result = json_body['result']
        content = result['content']

        first_content = content[0]
        parsed = json.loads(first_content['text'])
        assert parsed['hello'] == 'world', f'Expected the echoed arguments, got: {parsed}'

        # .. a token from the same IdP with the same audience but a different department claim is rejected ..
        sales_token = keycloak_.get_token(keycloak_.Client_Sales, keycloak_.Secret_Sales)

        initialize_body = make_jsonrpc_initialize()
        response = _post_jsonrpc(server_port, url_path, initialize_body, sales_token)
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for a claim mismatch, got {response.status_code}: {response.text}'

        # .. and so is an anonymous client.
        response = _post_jsonrpc(server_port, url_path, initialize_body)
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for an anonymous client, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################
