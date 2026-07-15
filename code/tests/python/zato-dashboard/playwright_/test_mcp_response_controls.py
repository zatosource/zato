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
from http.client import OK

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form, submit_edit_form

# Zato - test helpers - the live MCP client lives in the mcp_live suite
_mcp_live_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-server', 'mcp_live'))

if _mcp_live_directory not in sys.path:
    sys.path.insert(0, _mcp_live_directory)

from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

import pytest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.controls.' + CryptoManager.generate_hex_string(32) + '.'

_MCP_Page_Url = '/zato/gateway/mcp/?cluster=1'
_Basic_Auth_Page_Url = '/zato/security/basic-auth/?cluster=1'

_Echo_Service = 'demo.echo'

# The token cap the test configures - it must stay above the minimum usable byte budget
# for graceful trimming, i.e. 1000 tokens at 4 characters each.
_Max_Response_Tokens = '2048'

# How many echo rows make a response that is comfortably over the cap above
_Oversized_Row_Count = 500

# How long to wait for a UI change to propagate to live MCP enforcement, in seconds
_Propagation_Timeout = 20

# How long to wait between the polling attempts above, in seconds
_Propagation_Poll_Interval = 0.5

# Log patterns produced by the server while the group membership is still propagating
_Group_Log_Patterns = (
    'Invalid bearer token (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
)

# The group-name uniqueness probe queries a groups table missing from the quickstart ODB,
# so the dashboard middleware logs this warning whenever a group is edited via the UI
_Group_Edit_Log_Patterns = ('nDetails: ··· Error ···',)

# ################################################################################################################################
# ################################################################################################################################

def _create_basic_auth(page:'Page', base_url:'str', name:'str', username:'str', password:'str') -> 'None':
    """ Creates a Basic Auth definition via the UI so the MCP client has credentials to use.
    """

    # Navigate to the basic auth page ..
    navigate_to_page(page, base_url, _Basic_Auth_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form ..
    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _create_mcp_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', definition_name:'str') -> 'str':
    """ Creates an MCP gateway via the UI with the echo service and the given security definition
    assigned, and the response shaping fields configured on the create dialog's Response shaping tab.
    Returns the gateway's ID.
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

    # .. assign the credentials via the security badge picker - the view auto-creates
    # the gateway's security group with this definition as its member ..
    security_badge_selector = f'#badge-zone-available-sec-create .security-badge[data-name="{definition_name}"]'
    security_badge = page.wait_for_selector(security_badge_selector, state='visible', timeout=10000)
    security_badge.click()

    # .. switch to the Response shaping tab ..
    page.click('#create-div .dashboard-tab[data-tab="response_shaping"]')
    _ = page.wait_for_selector('#mcp-create-tab-panel-response_shaping', state='visible', timeout=5000)

    # .. set a token cap in the default truncate mode and turn null stripping on ..
    page.fill('#id_max_response_size', _Max_Response_Tokens)
    page.check('#id_safeguards_strip_nulls')

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{gateway_name}"))'
    row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

    # .. and read the gateway's ID out of its hidden cell.
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.text_content().strip()
    return out

# ################################################################################################################################

def _call_echo(mcp_url:'str', auth:'tuple', arguments:'anydict') -> 'anydict':
    """ Runs one initialize plus tools/call round trip against the live gateway
    and returns the result object of the JSON-RPC response.
    """

    client = MCPClient(mcp_url, auth=auth)
    session_id = client.initialize().session_id

    params = {'name': _Echo_Service, 'arguments': arguments}
    response = client.jsonrpc('tools/call', params=params, session_id=session_id)

    data = response.json()

    out = data['result']
    return out

# ################################################################################################################################

def _get_text(result:'anydict') -> 'str':
    """ Extracts the text of the first content element of a tools/call result.
    """

    content = result['content']
    first_content = content[0]

    out = first_content['text']
    return out

# ################################################################################################################################

def _wait_until_authenticated(mcp_url:'str', auth:'tuple') -> 'None':
    """ Polls the gateway with an initialize request until the group membership added via the UI
    reaches live enforcement and the credentials are accepted.
    """

    client = MCPClient(mcp_url, auth=auth)
    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        response = client.jsonrpc('initialize', params={
            'protocolVersion': '2025-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
        })

        # Stop as soon as the credentials go through ..
        if response.status_code == OK:
            return

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Credentials were not accepted within {_Propagation_Timeout}s, ' + \
                f'last status: {response.status_code}, body: {response.text}')

        time.sleep(_Propagation_Poll_Interval)

# ################################################################################################################################

def _wait_until_rejected_as_too_large(mcp_url:'str', auth:'tuple', arguments:'anydict') -> 'anydict':
    """ Polls the gateway with an oversized call until block mode, configured via the UI a moment earlier,
    starts refusing it. Returns the refusing result.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = _call_echo(mcp_url, auth, arguments)

        # Stop as soon as the response is refused ..
        if 'isError' in out:
            return out

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Block mode did not take effect within {_Propagation_Timeout}s, last result: {out}')

        time.sleep(_Propagation_Poll_Interval)

# ################################################################################################################################

def _make_rows(count:'int') -> 'list':
    out = []
    for index in range(count):
        row = {'id': f'inv-{index:05}', 'customer': 'Customer name here'}
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPResponseControls:
    """ End-to-end tests for response size and content controls - the gateway is configured
    entirely through the dashboard and a live MCP client asserts the enforcement.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_response_controls_configured_via_the_ui(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway with a token cap and null stripping on the create dialog, verifies
        both run live, verifies the edit dialog round-trips the values, then switches
        the cap to block mode via the edit dialog and verifies the refusal.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        gateway_name = _Test_Name_Prefix + 'gateway'
        url_path = '/mcp/test/controls/' + CryptoManager.generate_hex_string()

        mcp_url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (username, password)

        # Create the credentials the MCP client will use ..
        _create_basic_auth(page, base_url, definition_name, username, password)

        # .. create the gateway with the credentials assigned and the shaping fields
        # set on the create dialog ..
        gateway_id = _create_mcp_gateway(page, base_url, gateway_name, url_path, definition_name)

        # .. and wait until it all reaches live enforcement.
        _wait_until_authenticated(mcp_url, auth)

        # Null stripping configured at create time runs live - null keys disappear while real values survive ..
        result = _call_echo(mcp_url, auth, {'customer': 'Customer name here', 'middle_name': None, 'fax': None})
        echoed = json.loads(_get_text(result))

        assert 'isError' not in result, f'Expected no error, got: {result}'
        assert echoed == {'customer': 'Customer name here'}, f'Expected nulls to be stripped, got: {echoed}'

        # .. and so does the token cap - an oversized response is gracefully trimmed to fit.
        result = _call_echo(mcp_url, auth, {'status': 'ok', 'rows': _make_rows(_Oversized_Row_Count)})
        echoed = json.loads(_get_text(result))

        assert 'isError' not in result, f'Expected no error, got: {result}'
        assert echoed['status'] == 'ok', f'Expected the scalar field to survive, got: {echoed}'
        assert len(echoed['rows']) < _Oversized_Row_Count, f'Expected fewer than {_Oversized_Row_Count} rows'

        # The edit dialog round-trips the values saved at create time ..
        navigate_to_page(page, base_url, _MCP_Page_Url)
        page.evaluate(f'$.fn.zato.gateway.mcp.edit("{gateway_id}")')
        _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. on its Response shaping tab ..
        page.click('#edit-div .dashboard-tab[data-tab="response_shaping"]')
        _ = page.wait_for_selector('#mcp-edit-tab-panel-response_shaping', state='visible', timeout=5000)

        max_response_size = page.input_value('#id_edit-max_response_size')
        assert max_response_size == _Max_Response_Tokens, f'Expected {_Max_Response_Tokens}, got: {max_response_size}'

        assert page.is_checked('#id_edit-safeguards_strip_nulls'), 'Expected the strip nulls checkbox to be checked'

        cap_mode = page.input_value('#id_edit-size_cap_mode')
        assert cap_mode == 'truncate', f'Expected the truncate mode, got: {cap_mode}'

        # .. switching the cap to block mode through the same dialog, but only once the badge pickers
        # have loaded the assigned service and credentials, so the submit does not wipe them -
        # the badges sit on the Access control tab, which is hidden now, hence the attached state ..
        service_badge = f'#badge-zone-assigned-edit .security-badge[data-name="{_Echo_Service}"]'
        _ = page.wait_for_selector(service_badge, state='attached', timeout=10000)

        security_badge = f'#badge-zone-assigned-sec-edit .security-badge[data-name="{definition_name}"]'
        _ = page.wait_for_selector(security_badge, state='attached', timeout=10000)

        page.select_option('#id_edit-size_cap_mode', 'block')
        submit_edit_form(page)

        # .. makes the gateway refuse an oversized response outright, naming the size and the cap.
        result = _wait_until_rejected_as_too_large(mcp_url, auth, {'status': 'ok', 'rows': _make_rows(_Oversized_Row_Count)})

        text = _get_text(result)
        assert 'Response too large:' in text, f'Expected a size refusal, got: {text}'
        assert f'cap is {_Max_Response_Tokens}' in text, f'Expected the cap to be named, got: {text}'

# ################################################################################################################################
# ################################################################################################################################
