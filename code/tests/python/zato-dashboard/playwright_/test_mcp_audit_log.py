# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from urllib.parse import quote

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - test helpers - the page helpers and the group propagation patterns
# are shared with the response controls suite, which also wires up the MCP client import.
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

from test_mcp_response_controls import (
    _create_basic_auth, _wait_until_authenticated, _Echo_Service, _Group_Edit_Log_Patterns, _Group_Log_Patterns,
    _MCP_Page_Url)
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form

from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist, any_

# ################################################################################################################################
# ################################################################################################################################

import pytest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# The section title of the MCP source, compared lowercase because the heading is styled with CSS
_MCP_Title = 'mcp audit log'

# What each MCP request audits as
_Event_Initialize = 'mcp-initialize'
_Event_Tools_Call = 'mcp-tools-call'

_Outcome_OK = 'ok'

# What the audit page renders empty cells as
_Empty_Cell = '---'

# Column indexes: Time, CID, Event, Tool, Caller, Outcome, Size, Data preview
_Column_Time    = 0
_Column_CID     = 1
_Column_Event   = 2
_Column_Tool    = 3
_Column_Caller  = 4
_Column_Outcome = 5
_Column_Size    = 6
_Column_Data    = 7

# ################################################################################################################################
# ################################################################################################################################

def _create_mcp_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', definition_name:'str') -> 'None':
    """ Creates an MCP gateway via the UI with the echo service and the given security definition assigned,
    verifying on the way that the audit log checkbox is on by default for new gateways.
    """

    # Navigate to the MCP gateways page ..
    navigate_to_page(page, base_url, _MCP_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the basic fields ..
    page.fill('#id_name', gateway_name)
    page.fill('#id_url_path', url_path)

    # .. the audit log checkbox is checked by default for new gateways ..
    assert page.is_checked('#id_is_audit_log_active'), 'Expected the audit log checkbox to be checked by default'

    # .. assign the echo service via its badge ..
    badge_selector = f'#badge-zone-available-create .badge-zone-body .security-badge[data-name="{_Echo_Service}"]'
    badge = page.wait_for_selector(badge_selector, state='visible', timeout=10000)
    badge.click()

    # .. assign the credentials via the security badge picker - the view auto-creates
    # the gateway's security group with this definition as its member ..
    security_badge_selector = f'#badge-zone-available-sec-create .security-badge[data-name="{definition_name}"]'
    security_badge = page.wait_for_selector(security_badge_selector, state='visible', timeout=10000)
    security_badge.click()

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{gateway_name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _run_one_conversation(mcp_url:'str', auth:'tuple') -> 'None':
    """ Runs one initialize plus tools/call round trip against the live gateway.
    """

    client = MCPClient(mcp_url, auth=auth)
    session_id = client.initialize().session_id

    params = {'name': _Echo_Service, 'arguments': {'customer': 'Customer name here'}}
    response = client.jsonrpc('tools/call', params=params, session_id=session_id)

    data = response.json()
    assert 'error' not in data, f'Expected a successful call, got: {data}'

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events.
    """
    _ = page.wait_for_function(
        '''() => {
            let body = document.querySelector('#audit-log-table-body');
            if (!body) return false;
            let rows = body.querySelectorAll('tr');
            if (!rows.length) return false;
            return !body.querySelector('tr.detail-loading-row');
        }''',
        timeout=10000)

# ################################################################################################################################

def _get_row_cells(row:'any_') -> 'anylist':
    """ Returns the text of each cell in one audit log row.
    """
    out = [] # type: anylist

    for cell in row.query_selector_all('td'):
        out.append(cell.inner_text().strip())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPAuditLog:
    """ End-to-end test for the MCP audit log page - the gateway is created through the dashboard
    with the audit checkbox on, a live MCP client drives real calls and the audit page shows them.
    """

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_audit_events_render_on_the_audit_page(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        gateway_name = _Test_Name_Prefix + 'gateway'
        url_path = '/mcp/test/audit/' + CryptoManager.generate_hex_string()

        mcp_url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (username, password)

        # Create the credentials the MCP client will use ..
        _create_basic_auth(page, base_url, definition_name, username, password)

        # .. create the gateway with the audit log checkbox on, which is its default ..
        _create_mcp_gateway(page, base_url, gateway_name, url_path, definition_name)

        # .. wait until the gateway reaches live enforcement ..
        _wait_until_authenticated(mcp_url, auth)

        # .. drive one real MCP conversation through the gateway ..
        _run_one_conversation(mcp_url, auth)

        # .. go back to the MCP gateways page and click this gateway's Audit log link ..
        navigate_to_page(page, base_url, _MCP_Page_Url)

        row_selector = f'#data-table tbody tr:has(td:text-is("{gateway_name}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the MCP audit log of this gateway ..
        assert 'source=mcp' in page.url, f'Expected source=mcp in the URL, got: "{page.url}"'
        assert quote(gateway_name) in page.url, f'Expected the gateway name in the URL, got: "{page.url}"'

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_MCP_Title), f'Expected the title to start with "{_MCP_Title}", got: "{title_text}"'

        # .. the table shows the MCP columns, compared case-insensitively
        # .. because the headers are uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'tool' in header_text, f'Expected a Tool column, got: "{header_text}"'
        assert 'caller' in header_text, f'Expected a Caller column, got: "{header_text}"'
        assert 'outcome' in header_text, f'Expected an Outcome column, got: "{header_text}"'

        # .. the polling loop that waited for enforcement produced its own initialize events,
        # .. so the newest two rows are what matters - the conversation's call and its initialize ..
        rows = page.query_selector_all('#audit-log-table-body tr')
        row_count = len(rows)
        assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        tools_call_cells = _get_row_cells(rows[0])
        initialize_cells = _get_row_cells(rows[1])

        # .. events come newest first - the tools/call of the conversation tops the list ..
        assert tools_call_cells[_Column_Event] == _Event_Tools_Call, \
            f'Expected event "{_Event_Tools_Call}", got: "{tools_call_cells[_Column_Event]}"'
        assert initialize_cells[_Column_Event] == _Event_Initialize, \
            f'Expected event "{_Event_Initialize}", got: "{initialize_cells[_Column_Event]}"'

        # .. only the tools/call row names the tool ..
        assert tools_call_cells[_Column_Tool] == _Echo_Service, \
            f'Expected tool "{_Echo_Service}", got: "{tools_call_cells[_Column_Tool]}"'
        assert initialize_cells[_Column_Tool] == _Empty_Cell, \
            f'Expected no tool for initialize, got: "{initialize_cells[_Column_Tool]}"'

        # .. every row names the caller and the outcome ..
        for cells in (tools_call_cells, initialize_cells):
            assert cells[_Column_Caller] == definition_name, \
                f'Expected caller "{definition_name}", got: "{cells[_Column_Caller]}"'
            assert cells[_Column_Outcome] == _Outcome_OK, \
                f'Expected outcome "{_Outcome_OK}", got: "{cells[_Column_Outcome]}"'
            assert cells[_Column_CID] != '', 'Expected a CID in every row'
            assert cells[_Column_Time] != '', 'Expected a time in every row'

        # .. the response size is recorded ..
        size = int(tools_call_cells[_Column_Size])
        assert size > 0, f'Expected a positive size, got {size}'

        # .. and the payload itself never reaches the audit log.
        assert 'Customer name here' not in tools_call_cells[_Column_Data], \
            f'Expected no payload in the data preview, got: "{tools_call_cells[_Column_Data]}"'

# ################################################################################################################################
# ################################################################################################################################
