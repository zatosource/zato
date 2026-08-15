# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import sys
import tempfile
from http.client import OK
from urllib.parse import quote

# PyYAML
from yaml import safe_load

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - test helpers - the page helpers, the shared echo service and the group
# propagation patterns come from the response controls suite.
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

# The agent loop and the Ollama container helpers come from the LLM-driven MCP suite -
# appended at the end of the path so this suite's own modules keep their names.
_llm_live_directory = os.path.abspath(
    os.path.join(_this_directory, '..', '..', 'zato-server', 'mcp_llm_live'))

if _llm_live_directory not in sys.path:
    sys.path.append(_llm_live_directory)

from test_mcp_response_controls import (
    _create_basic_auth, _wait_until_authenticated, _Echo_Service, _Group_Edit_Log_Patterns, _Group_Log_Patterns)

from _client import MCPClient

import _agent
import _mcp_wizard as wizard_page
import containers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

import pytest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.agent.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

# How long to wait for a UI element to show, in milliseconds
_UI_Timeout = 5000

# How long to wait for the audit log table to finish loading, in milliseconds
_Table_Timeout = 10000

# How long the enmasse subprocesses may run, in seconds
_Enmasse_Timeout = 120

# The suffix no audit page may ever show a count with
_Plural_Suffix = '(s)'

# The audit page is a list-detail layout - each event is one row, everything
# else the event says is read in the detail pane beside the list
_Row_Selector = '#audit-log-table-body tr.audit-log-row'
_Row_Event_Selector = '.audit-log-row-event'
_Details_Tab_Selector = '.audit-log-pane-tab[data-tab="details"]'
_Details_Panel_Selector = '#audit-log-pane-panel-details .audit-log-pane-details'

# How a tool call reads on its row - the one event kind whose pane carries a duration
_Event_Tools_Call_Label = 'MCP tools call'

# The fields that identify one gateway rather than describe its options -
# two gateways made from the same values differ in exactly these
_Gateway_Identifying_Fields = ('name', 'url_path', 'security_groups')

# The window flag the markup in the stored values below names - the assertions
# check it stays unset after every render
_Probe_Var = '__zato_markup_probe'

# The element id of the image the markup names - the page never gets such a node
_Probe_Img_Id = 'zato-markup-img'

# The stored values a caller controls - a method with a script tag, both kinds of quotes
# and a control character, a tool name with an image error handler, and a filter expression
# that is a valid JSONata string literal wrapping a script tag, so the filter applies
# and its raw text lands in the event's trace
_Markup_Method = '<script>window.__zato_markup_probe=1</script>/\'"\x07method'
_Markup_Tool = '<img src=x id="zato-markup-img" onerror="window.__zato_markup_probe=1">tool'
_Markup_Filter = '"<script>window.__zato_markup_probe=1</script>"'

# ################################################################################################################################
# ################################################################################################################################

def _create_echo_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', definition_name:'str') -> 'None':
    """ Creates an MCP gateway through the wizard with the echo service
    and the given security definition assigned.
    """

    # Open the create wizard and answer step 1 ..
    wizard_page.open_wizard_create(page, base_url)

    page.fill('#id_name', gateway_name)
    page.fill('#id_url_path', url_path)

    # .. assign the echo service and the credentials via their badges ..
    wizard_page.assign_badge(page, 'services', _Echo_Service)
    wizard_page.assign_badge(page, 'security', definition_name)

    # .. save from the review step ..
    wizard_page.save_create(page)

    # .. and confirm the row is on the list.
    _ = wizard_page.go_to_list(page, base_url, gateway_name)

# ################################################################################################################################

def _run_agent_conversation(mcp_url:'str', auth:'any_') -> 'any_':
    """ Runs one whole agent conversation against the live gateway,
    with the model deciding the echo tool call itself.
    """

    containers.ensure_ollama()
    containers.ensure_model()

    client = MCPClient(mcp_url, auth=auth)

    task = 'Use the echo tool to send back the message: Quarterly report ready.'
    out = _agent.run_agent(client, task)

    assert out.tool_calls, out.messages
    return out

# ################################################################################################################################

def _open_conversation_page(page:'Page', base_url:'str', gateway_name:'str', session_id:'str') -> 'None':
    """ Opens the MCP audit page narrowed down to one gateway and one conversation's session.
    """

    gateway_quoted = quote(gateway_name)
    session_quoted = quote(session_id)

    url = f'{base_url}{_Audit_Log_URL_Prefix}?source=mcp&object_name={gateway_quoted}&query={session_quoted}'

    _ = page.goto(url)
    _wait_for_table(page)

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

def _run_enmasse(server_dir:'str', arguments:'list') -> 'None':
    """ Runs one enmasse command against the live server and expects it to succeed.
    """

    zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base_dir, 'code', 'bin', 'zato')

    enmasse_env = os.environ.copy()
    _ = enmasse_env.pop('COVERAGE_PROCESS_START', None)

    command = [zato_bin, 'enmasse', server_dir, '--verbose'] + arguments
    result = subprocess.run(command, capture_output=True, text=True, timeout=_Enmasse_Timeout, env=enmasse_env)

    assert result.returncode == 0, f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################
# ################################################################################################################################

class TestMCPAgentAudit:
    """ The dashboard against the audit trail a real agent conversation produced -
    every event renders whole, filtering finds exactly the conversation,
    and both creation paths make the same gateway.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_a_conversations_audit_trail_renders_whole(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'render-basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        gateway_name = _Test_Name_Prefix + 'render-gateway'
        url_path = '/mcp/test/agent/render/' + CryptoManager.generate_hex_string()

        mcp_url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (username, password)

        # Create the credentials and the gateway, then wait for live enforcement ..
        _create_basic_auth(page, base_url, definition_name, username, password)
        _create_echo_gateway(page, base_url, gateway_name, url_path, definition_name)
        _wait_until_authenticated(mcp_url, auth)

        # .. one whole agent conversation produces the audit trail ..
        result = _run_agent_conversation(mcp_url, auth)

        # .. the audit page narrowed to this conversation lists its events ..
        _open_conversation_page(page, base_url, gateway_name, result.session_id)

        rows = page.query_selector_all(_Row_Selector)
        assert rows, 'Expected audit log rows for the conversation'

        # .. and every event's detail pane renders its facts without errors.
        row_count = len(rows)

        for row_index in range(row_count):

            # The rows are re-read on each pass - opening a pane re-renders the list
            rows = page.query_selector_all(_Row_Selector)
            row = rows[row_index]

            # What kind of event this row is - the text is read through text_content
            # because a narrow list hides the label with CSS while the pane is open
            event_element = row.query_selector(_Row_Event_Selector)
            event_label = event_element.text_content().strip()

            row.click()

            _ = page.wait_for_selector(_Details_Tab_Selector, state='visible', timeout=_UI_Timeout)
            page.click(_Details_Tab_Selector)
            _ = page.wait_for_selector(_Details_Panel_Selector, state='visible', timeout=_UI_Timeout)

            # The fact labels are uppercased with CSS, so the whole text is compared lowercase
            details_text = page.inner_text(_Details_Panel_Selector)
            details_text = details_text.lower()

            assert details_text.strip() != '', f'Expected details for row {row_index}'
            assert 'size\n' in details_text, f'Expected a Size line for row {row_index}, got: "{details_text}"'

            # A tool call is the one event kind whose pane carries a duration
            if event_label == _Event_Tools_Call_Label:
                assert 'duration' in details_text, f'Expected a Duration line for row {row_index}, got: "{details_text}"'

            cid_text = page.inner_text(f'{_Details_Panel_Selector} .audit-log-cid-link')
            assert cid_text.strip() != '', f'Expected a CID for row {row_index}'

        # .. pluralization is clean throughout.
        page_text = page.inner_text('body')
        assert _Plural_Suffix not in page_text, f'Expected no "{_Plural_Suffix}" on the page, got one'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_filtering_finds_exactly_the_conversation(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition_name = _Test_Name_Prefix + 'filter-basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        gateway_name = _Test_Name_Prefix + 'filter-gateway'
        url_path = '/mcp/test/agent/filter/' + CryptoManager.generate_hex_string()

        mcp_url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (username, password)

        # Create the credentials and the gateway, then wait for live enforcement ..
        _create_basic_auth(page, base_url, definition_name, username, password)
        _create_echo_gateway(page, base_url, gateway_name, url_path, definition_name)
        _wait_until_authenticated(mcp_url, auth)

        # .. one agent conversation, plus a second conversation whose events
        # must never show under the first one's filter ..
        result = _run_agent_conversation(mcp_url, auth)

        other_client = MCPClient(mcp_url, auth=auth)
        other_session_id = other_client.initialize().session_id

        params = {'name': _Echo_Service, 'arguments': {'note': 'Other conversation traffic'}}
        response = other_client.jsonrpc('tools/call', params=params, session_id=other_session_id)
        assert response.status_code == OK, response.text

        # .. the page filtered by the conversation's session shows exactly its events -
        # the initialize, the tool listing and one row per tool call of the transcript.
        _open_conversation_page(page, base_url, gateway_name, result.session_id)

        rows = page.query_selector_all(_Row_Selector)
        row_count = len(rows)

        call_count = len(result.tool_calls)
        expected_count = call_count + 2

        assert row_count == expected_count, f'Expected {expected_count} rows, got {row_count}'

        # .. and the other conversation's session appears nowhere on the page.
        page_text = page.inner_text('body')
        assert other_session_id not in page_text, f'Expected no "{other_session_id}" on the page'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_stored_markup_renders_as_text(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        definition_name = _Test_Name_Prefix + 'markup-basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        group_name = _Test_Name_Prefix + 'markup-group'
        gateway_name = _Test_Name_Prefix + 'markup-gateway'
        url_path = '/mcp/test/agent/markup/' + CryptoManager.generate_hex_string()

        # The gateway comes from enmasse because the filter expression needs client filters allowed ..
        yaml_content = f"""
security:
  - name: {definition_name}
    type: basic_auth
    username: {username}
    password: "{password}"

groups:
  - name: {group_name}
    members:
      - {definition_name}

mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {_Echo_Service}
    security_groups:
      - {group_name}
    is_audit_log_active: true
    allow_client_filters: true
"""

        input_path = os.path.join(tempfile.gettempdir(), f'zato-mcp-agent-markup-{os.getpid()}.yaml')

        with open(input_path, 'w') as input_file:
            _ = input_file.write(yaml_content)

        try:
            _run_enmasse(server_dir, ['--import', '--input', input_path])
        finally:
            os.remove(input_path)

        mcp_url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (username, password)

        _wait_until_authenticated(mcp_url, auth)

        # .. one real conversation stores the markup-laden values - an unknown method,
        # an unknown tool and a successful call whose filter expression carries the markup ..
        client = MCPClient(mcp_url, auth=auth)
        session_id = client.initialize().session_id

        response = client.jsonrpc(_Markup_Method, session_id=session_id)
        body = response.json()
        assert 'error' in body, body

        params:'anydict' = {'name': _Markup_Tool, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        body = response.json()
        assert 'error' in body, body

        params = {'name': _Echo_Service, 'arguments': {
            'note': 'Quarterly note', 'response_filter': _Markup_Filter}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        assert response.status_code == OK, response.text

        # .. any dialog firing anywhere on the page is recorded as a failure ..
        dialog_messages = []

        def _on_dialog(dialog:'any_') -> 'None':
            dialog_messages.append(dialog.message)
            dialog.dismiss()

        page.on('dialog', _on_dialog)

        # .. the audit page narrowed to this gateway renders every event and its pane ..
        gateway_quoted = quote(gateway_name)
        url = f'{base_url}{_Audit_Log_URL_Prefix}?source=mcp&object_name={gateway_quoted}'

        _ = page.goto(url)
        _wait_for_table(page)

        rows = page.query_selector_all(_Row_Selector)
        assert rows, 'Expected audit log rows for the gateway'

        row_count = len(rows)
        seen_texts = []

        for row_index in range(row_count):

            # The rows are re-read on each pass - opening a pane re-renders the list
            rows = page.query_selector_all(_Row_Selector)
            row = rows[row_index]

            row.click()

            _ = page.wait_for_selector(_Details_Tab_Selector, state='visible', timeout=_UI_Timeout)
            page.click(_Details_Tab_Selector)
            _ = page.wait_for_selector(_Details_Panel_Selector, state='visible', timeout=_UI_Timeout)

            seen_texts.append(page.inner_text('body'))

        # .. no dialog fired while anything rendered ..
        assert dialog_messages == [], dialog_messages

        # .. the probe flag stays unset ..
        probe_value = page.evaluate(f'window.{_Probe_Var}')
        assert probe_value is None, probe_value

        # .. the markup became no DOM node - neither the image
        # nor a script element carrying the probe ..
        image_node = page.query_selector(f'#{_Probe_Img_Id}')
        assert image_node is None, 'Expected no image node'

        script_node_count = page.evaluate(
            f'''() => {{
                let out = 0;
                for (let node of document.querySelectorAll('script')) {{
                    if (node.textContent.includes('{_Probe_Var}')) {{
                        out += 1;
                    }}
                }}
                return out;
            }}''')
        assert script_node_count == 0, script_node_count

        # .. and the markup strings display as the text they are.
        all_text = '\n'.join(seen_texts)

        assert _Probe_Img_Id in all_text, 'Expected the tool name to display as text'
        assert _Probe_Var in all_text, 'Expected the filter expression to display as text'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Edit_Log_Patterns)
    def test_both_creation_paths_make_the_same_gateway(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        # The wizard-side gateway and its credentials ..
        wizard_definition_name = _Test_Name_Prefix + 'wizard-basic-auth'
        wizard_username = 'user.' + wizard_definition_name
        wizard_password = 'password.' + CryptoManager.generate_hex_string()

        wizard_gateway_name = _Test_Name_Prefix + 'wizard-gateway'
        wizard_url_path = '/mcp/test/agent/wizard/' + CryptoManager.generate_hex_string()

        _create_basic_auth(page, base_url, wizard_definition_name, wizard_username, wizard_password)
        _create_echo_gateway(page, base_url, wizard_gateway_name, wizard_url_path, wizard_definition_name)

        # .. the enmasse-side gateway from the same values, with credentials of its own ..
        enmasse_definition_name = _Test_Name_Prefix + 'enmasse-basic-auth'
        enmasse_username = 'user.' + enmasse_definition_name
        enmasse_password = 'password.' + CryptoManager.generate_hex_string()

        enmasse_group_name = _Test_Name_Prefix + 'enmasse-group'
        enmasse_gateway_name = _Test_Name_Prefix + 'enmasse-gateway'
        enmasse_url_path = '/mcp/test/agent/enmasse/' + CryptoManager.generate_hex_string()

        yaml_content = f"""
security:
  - name: {enmasse_definition_name}
    type: basic_auth
    username: {enmasse_username}
    password: "{enmasse_password}"

groups:
  - name: {enmasse_group_name}
    members:
      - {enmasse_definition_name}

mcp_gateway:
  - name: {enmasse_gateway_name}
    url_path: {enmasse_url_path}
    services:
      - {_Echo_Service}
    security_groups:
      - {enmasse_group_name}
    is_audit_log_active: true
    validate_input: true
"""

        input_path = os.path.join(tempfile.gettempdir(), f'zato-mcp-agent-audit-{os.getpid()}.yaml')

        with open(input_path, 'w') as input_file:
            _ = input_file.write(yaml_content)

        try:
            _run_enmasse(server_dir, ['--import', '--input', input_path])
        finally:
            os.remove(input_path)

        # .. both gateways behave identically on one probe call each ..
        wizard_mcp_url = f'http://127.0.0.1:{server_port}{wizard_url_path}'
        enmasse_mcp_url = f'http://127.0.0.1:{server_port}{enmasse_url_path}'

        _wait_until_authenticated(wizard_mcp_url, (wizard_username, wizard_password))
        _wait_until_authenticated(enmasse_mcp_url, (enmasse_username, enmasse_password))

        # .. and they export as equal documents, apart from the fields that identify them.
        output_path = os.path.join(tempfile.gettempdir(), f'zato-mcp-agent-audit-export-{os.getpid()}.yaml')

        try:
            _run_enmasse(server_dir, ['--export', '--output', output_path, '--include-type', 'mcp_gateway'])

            with open(output_path) as output_file:
                exported = safe_load(output_file.read())

        finally:
            if os.path.isfile(output_path):
                os.remove(output_path)

        gateways_by_name = {}

        for item in exported['mcp_gateway']:
            gateways_by_name[item['name']] = item

        wizard_document = dict(gateways_by_name[wizard_gateway_name])
        enmasse_document = dict(gateways_by_name[enmasse_gateway_name])

        for field in _Gateway_Identifying_Fields:
            _ = wizard_document.pop(field, None)
            _ = enmasse_document.pop(field, None)

        assert wizard_document == enmasse_document, (wizard_document, enmasse_document)

# ################################################################################################################################
# ################################################################################################################################
