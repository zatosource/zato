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
    _create_basic_auth, _wait_until_authenticated, _Echo_Service, _Group_Edit_Log_Patterns, _Group_Log_Patterns)

from _client import MCPClient

import _mcp_wizard as wizard_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

import pytest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

# How long to wait for a UI element to show, in milliseconds
_UI_Timeout = 5000

# How long to wait for the audit log table to finish loading, in milliseconds
_Table_Timeout = 10000

# The section title of the MCP source, compared lowercase because the heading is styled with CSS
_MCP_Title = 'mcp audit log'

# How each MCP request reads on its row - the event labels the page renders
_Event_Initialize_Label = 'MCP initialize'
_Event_Tools_Call_Label = 'MCP tools call'

_Outcome_OK = 'ok'

# The audit page is a list-detail layout - each event is one row, everything
# else the event says is read in the detail pane beside the list
_Row_Selector = '#audit-log-table-body tr.audit-log-row'
_Row_Event_Selector = '.audit-log-row-event'
_Row_Main_Cell_Selector = '.audit-log-cell-main'
_Pane_Head_Selector = '.audit-log-pane-head'
_Details_Tab_Selector = '.audit-log-pane-tab[data-tab="details"]'
_Details_Panel_Selector = '#audit-log-pane-panel-details .audit-log-pane-details'

# ################################################################################################################################
# ################################################################################################################################

def _create_mcp_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', definition_name:'str') -> 'None':
    """ Creates an MCP gateway through the wizard with the echo service and the given security definition assigned,
    verifying on the way that the audit log flag is on by default for new gateways.
    """

    # Open the create wizard and answer step 1 ..
    wizard_page.open_wizard_create(page, base_url)

    page.fill('#id_name', gateway_name)
    page.fill('#id_url_path', url_path)

    # .. the audit log flag is on by default for new gateways - the wizard keeps it
    # in a hidden field the gateway options popover edits in place ..
    assert page.is_checked('#id_is_audit_log_active'), 'Expected the audit log flag to be on by default'

    # .. assign the echo service via its badge ..
    wizard_page.assign_badge(page, 'services', _Echo_Service)

    # .. assign the credentials via the security badge picker - the view auto-creates
    # the gateway's security group with this definition as its member ..
    wizard_page.assign_badge(page, 'security', definition_name)

    # .. save from the review step ..
    wizard_page.save_create(page)

    # .. and confirm the row is on the list.
    _ = wizard_page.go_to_list(page, base_url, gateway_name)

# ################################################################################################################################

def _run_one_conversation(mcp_url:'str', auth:'anytuple') -> 'None':
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
        timeout=_Table_Timeout)

# ################################################################################################################################

def _get_row_event_label(row:'any_') -> 'str':
    """ What kind of event one row says it is - MCP events play no request-response role,
    so each row names its kind in a label of its own. The text is read through text_content
    because a narrow list hides the label with CSS while the detail pane is open.
    """
    event_element = row.query_selector(_Row_Event_Selector)

    out = event_element.text_content().strip()
    return out

# ################################################################################################################################

def _get_row_main_text(row:'any_') -> 'str':
    """ Everything one row's main cell says - the event label and the chips the row wears,
    which for an MCP event are the tool and the caller. The text is read through text_content
    because a narrow list hides the chips with CSS while the detail pane is open.
    """
    main_cell = row.query_selector(_Row_Main_Cell_Selector)

    out = main_cell.text_content()
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
        _ = wizard_page.go_to_list(page, base_url, gateway_name)

        row_selector = wizard_page.row_selector(gateway_name)
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the MCP audit log of this gateway ..
        assert 'source=mcp' in page.url, f'Expected source=mcp in the URL, got: "{page.url}"'
        assert quote(gateway_name) in page.url, f'Expected the gateway name in the URL, got: "{page.url}"'

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_MCP_Title), f'Expected the title to start with "{_MCP_Title}", got: "{title_text}"'

        # .. the polling loop that waited for enforcement produced its own initialize events,
        # .. so the newest two rows are what matters - the conversation's call and its initialize ..
        rows = page.query_selector_all(_Row_Selector)
        row_count = len(rows)
        assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        tools_call_row = rows[0]
        initialize_row = rows[1]

        # .. events come newest first - the tools/call of the conversation tops the list ..
        event_label = _get_row_event_label(tools_call_row)
        assert event_label == _Event_Tools_Call_Label, \
            f'Expected event "{_Event_Tools_Call_Label}", got: "{event_label}"'

        event_label = _get_row_event_label(initialize_row)
        assert event_label == _Event_Initialize_Label, \
            f'Expected event "{_Event_Initialize_Label}", got: "{event_label}"'

        # .. the tools/call row wears the tool and the caller as its chips ..
        main_text = _get_row_main_text(tools_call_row)
        assert _Echo_Service in main_text, f'Expected the tool "{_Echo_Service}" on the row, got: "{main_text}"'
        assert definition_name in main_text, f'Expected the caller "{definition_name}" on the row, got: "{main_text}"'

        # .. while the initialize row names no tool, only the caller ..
        main_text = _get_row_main_text(initialize_row)
        assert _Echo_Service not in main_text, f'Expected no tool on the initialize row, got: "{main_text}"'
        assert definition_name in main_text, f'Expected the caller "{definition_name}" on the row, got: "{main_text}"'

        # .. selecting the newest row opens the detail pane on it,
        # with the head reporting the outcome ..
        tools_call_row.click()

        _ = page.wait_for_selector(f'{_Pane_Head_Selector} .audit-log-outcome-filter', state='visible', timeout=_UI_Timeout)

        outcome_text = page.inner_text(f'{_Pane_Head_Selector} .audit-log-outcome-filter')
        outcome_text = outcome_text.strip().lower()
        assert outcome_text == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome_text}"'

        # .. the Details tab reads everything the event says ..
        page.click(_Details_Tab_Selector)
        _ = page.wait_for_selector(_Details_Panel_Selector, state='visible', timeout=_UI_Timeout)

        # The fact labels are uppercased with CSS, so the whole text is compared lowercase,
        # each label together with the value standing right under it
        details_text = page.inner_text(_Details_Panel_Selector)
        details_text = details_text.lower()

        # .. the CID leads, the tool, the caller and the size all follow ..
        cid_text = page.inner_text(f'{_Details_Panel_Selector} .audit-log-cid-link')
        assert cid_text.strip() != '', 'Expected a CID in the detail pane'

        tool_line = f'tool\n{_Echo_Service}'
        assert tool_line in details_text, f'Expected a Tool line in the detail pane, got: "{details_text}"'

        caller_line = f'caller\n{definition_name}'
        assert caller_line in details_text, f'Expected a Caller line in the detail pane, got: "{details_text}"'

        assert 'size\n' in details_text, f'Expected a Size line in the detail pane, got: "{details_text}"'

        # .. and the payload itself never reaches the audit log.
        assert 'customer name here' not in details_text, \
            f'Expected no payload in the detail pane, got: "{details_text}"'

# ################################################################################################################################
# ################################################################################################################################
