# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from http.client import INTERNAL_SERVER_ERROR, OK
from urllib.parse import quote

# The live IMAP test server lives in the zato-server IMAP scheduler suite so both suites share one implementation.
_imap_server_lib_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'zato-server', 'email_imap_scheduler'))
if _imap_server_lib_dir not in sys.path:
    sys.path.insert(0, _imap_server_lib_dir)

# pytest
import pytest

# Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

from _imap_test_server import IMAPTestServer
from rest_channel import create_channel, deploy_service_file, invoke_until_status, wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.imap.audit.' + rand_string() + '.'

_IMAP_Page_Url = '/zato/email/imap/?cluster=1'

_Audit_Log_Url_Prefix = '/zato/audit-log/'
_Poll_Url_Path        = '/zato/audit-log/poll/'

_Event_Message_Received    = 'message-received'
_Event_Message_Marked_Seen = 'message-marked-seen'
_Event_Message_Deleted     = 'message-deleted'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

_No_Events_Text = 'No events found'

# The section title for the IMAP source, compared lowercase because the heading is styled with CSS
_IMAP_Title = 'imap audit log'

# The folder that the helper service reads messages from
_Folder = 'INBOX'

# Column indexes: Time, CID, Event, Folder, Message id, Outcome, Size, Data preview
_Column_Time    = 0
_Column_CID     = 1
_Column_Event   = 2
_Column_Folder  = 3
_Column_Msg_ID  = 4
_Column_Outcome = 5
_Column_Size    = 6
_Column_Data    = 7

# A TCP port that nothing listens on, for connections that must fail
_Closed_Port = 1

# Who the test messages are exchanged between
_Sender    = 'sender@example.com'
_Recipient = 'recipient@example.com'

# ################################################################################################################################
# ################################################################################################################################

# The helper service runs IMAP operations on behalf of the tests, invoked through a REST channel
_Helper_Service_Name = 'test.imap.audit.helper'

_Helper_Service_Source = '''
# -*- coding: utf-8 -*-

# stdlib
from json import dumps
from time import sleep

# Zato
from zato.server.service import Service

class IMAPAuditHelper(Service):
    """ Runs IMAP operations on behalf of the IMAP audit log tests.
    """

    name = 'test.imap.audit.helper'

    def handle(self):

        request = self.request.payload
        conn_name = request['conn_name']
        action = request['action']

        # The connection may still be propagating from the dashboard to the server,
        # which is why the store is polled directly - unlike the public API,
        # it does not log warnings about names it does not know yet.
        for _ in range(50):
            item = self.email.imap._conn_store.get(conn_name)
            if item:
                break
            sleep(0.2)
        else:
            raise Exception('IMAP connection not ready: ' + conn_name)

        conn = item.conn

        uids = []

        # Read all matching messages, marking each one as seen ..
        if action == 'get':
            for uid, message in conn.get():
                uids.append(uid.decode('utf-8'))
                message.mark_seen()

        # .. or read them all first and delete them through the connection-level call.
        elif action == 'connection-delete':
            for uid, message in conn.get():
                uids.append(uid.decode('utf-8'))
            conn.delete(*uids)

        self.response.payload = dumps({'uids': uids})
        self.response.content_type = 'application/json'
'''.lstrip()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def imap_test_server() -> 'any_':
    """ A live in-process IMAP server for the duration of this module.
    """
    server = IMAPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def helper_service(zato_dashboard:'anydict') -> 'any_':
    """ Hot-deploys the IMAP helper service for the duration of this module.
    """

    server_dir = zato_dashboard['server_dir']
    file_path = deploy_service_file(server_dir, 'test_imap_audit_helper.py', _Helper_Service_Source)

    yield _Helper_Service_Name

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _create_imap_connection(page:'Page', base_url:'str', name:'str', host:'str', port:'int') -> 'None':
    """ Creates a plaintext generic IMAP connection via the UI, pointing it at the given host and port.
    """

    # Open the IMAP connections page ..
    _ = page.goto(f'{base_url}{_IMAP_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the basic fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', 'imap-user@example.com')

    # .. expand the generic IMAP options ..
    page.click('#create-div a[href*="generic-imap-options-block"]')

    # .. point the connection at the test server, over a plaintext connection
    # .. because the default mode is SSL which the test server does not speak ..
    page.fill('#id_host', host)
    page.fill('#id_port', str(port))
    _ = page.select_option('#id_mode', 'plain')

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _create_helper_channel(page:'Page', base_url:'str', name_suffix:'str') -> 'str':
    """ Creates a JSON REST channel pointing at the helper service and returns its URL path.
    """

    channel_name = _Test_Name_Prefix + name_suffix
    url_path = f'/test/imap/audit/{name_suffix}/' + rand_string()

    _ = create_channel(page, base_url, channel_name, _Helper_Service_Name, url_path, {
        'data_format': 'json',
    })

    out = url_path
    return out

# ################################################################################################################################

def _invoke_helper(server_port:'int', url_path:'str', conn_name:'str', action:'str') -> 'anylist':
    """ Invokes the helper service through its REST channel and returns the uids it reports.
    """

    payload = {'conn_name': conn_name, 'action': action}

    response = invoke_until_status(server_port, url_path, OK, json_data=payload)
    assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

    response_data = response.json()

    out = response_data['uids']
    return out

# ################################################################################################################################

def _goto_audit_log(page:'Page', base_url:'str', conn_name:'str') -> 'None':
    """ Navigates to the audit log page of one IMAP connection and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(conn_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=email-imap&object_name={encoded_name}&cluster=1'

    # .. go there ..
    _ = page.goto(url)

    # .. and wait for the initial poll to replace the loading row.
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events,
    i.e. until the table body exists, has rows and none of them is the loading placeholder.
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

def _get_rows(page:'Page') -> 'anylist':
    """ Returns all rows currently shown in the audit log table.
    """
    out = page.query_selector_all('#audit-log-table-body tr')
    return out

# ################################################################################################################################

def _get_row_cells(row:'any_') -> 'anylist':
    """ Returns the text of each cell in one audit log row.
    """
    out = [] # type: anylist

    for cell in row.query_selector_all('td'):
        out.append(cell.inner_text().strip())

    return out

# ################################################################################################################################

def _attach_diagnostics(page:'Page') -> 'anydict':
    """ Captures everything the browser and Django report while a test runs - console messages,
    uncaught page errors, failed requests and the full body of each poll response.
    """

    # All the captured facts go here ..
    out = {
        'console': [],
        'page_errors': [],
        'failed_requests': [],
        'poll_responses': [],
    } # type: anydict

    # .. every console message is recorded with its severity ..
    def _on_console(message:'any_') -> 'None':
        out['console'].append(f'[console.{message.type}] {message.text}')

    # .. uncaught JavaScript exceptions are recorded in full ..
    def _on_page_error(error:'any_') -> 'None':
        out['page_errors'].append(f'[pageerror] {error}')

    # .. requests that never completed are recorded with their failure reason, except for
    # .. requests aborted by navigation, e.g. the session keepalive ping, which are not errors ..
    def _on_request_failed(request:'any_') -> 'None':
        if request.failure != 'net::ERR_ABORTED':
            out['failed_requests'].append(f'[requestfailed] {request.method} {request.url} -> {request.failure}')

    # .. and each poll response is recorded with its status and body, which is what Django returned.
    def _on_response(response:'any_') -> 'None':
        if _Poll_Url_Path in response.url:
            body = response.text()
            out['poll_responses'].append(f'[poll] {response.status} {response.url} -> {body}')

    page.on('console', _on_console)
    page.on('pageerror', _on_page_error)
    page.on('requestfailed', _on_request_failed)
    page.on('response', _on_response)

    return out

# ################################################################################################################################

def _format_diagnostics(diagnostics:'anydict') -> 'str':
    """ Turns the captured diagnostics into one readable block for assertion messages.
    """

    lines = [] # type: anylist

    for key in ('page_errors', 'failed_requests', 'console', 'poll_responses'):
        for entry in diagnostics[key]:
            lines.append(entry)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _search(page:'Page', query:'str') -> 'None':
    """ Types a query into the audit log search form and submits it with the search button.
    """

    # Fill in the query ..
    page.fill('#audit-log-search-input', query)

    # .. and submit the form.
    page.click('#audit-log-search-form button[type="submit"]')

# ################################################################################################################################

def _wait_for_body_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table body contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'document.querySelector("#audit-log-table-body").innerText.includes(\'{text}\')', timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for "{text}" in the table, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def _wait_for_body_without_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table body no longer contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'!document.querySelector("#audit-log-table-body").innerText.includes(\'{text}\')', timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(
            f'Timed out waiting for "{text}" to disappear, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################
# ################################################################################################################################

class TestEmailIMAPAuditLog:
    """ Live tests for the IMAP audit log page, driven by real IMAP operations against a live test server.
    """

    def test_get_creates_events(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Start with an empty mailbox and add two messages ..
        imap_test_server.clear()
        first_uid = imap_test_server.add_message(_Sender, _Recipient, 'Invoice created', 'The first invoice was created')
        second_uid = imap_test_server.add_message(_Sender, _Recipient, 'Invoice updated', 'The first invoice was updated')

        # .. create an IMAP connection pointing at the test server ..
        conn_name = _Test_Name_Prefix + 'events'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        # .. make sure the helper service is selectable and create a channel for it ..
        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'events')

        # .. read the mailbox live, marking each message as seen ..
        uids = _invoke_helper(server_port, url_path, conn_name, 'get')
        assert uids == [first_uid, second_uid], f'Expected uids {first_uid} and {second_uid}, got: {uids}'

        # .. open the audit log page for that connection ..
        _goto_audit_log(page, base_url, conn_name)

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_IMAP_Title), \
            f'Expected the title to start with "{_IMAP_Title}", got: "{title_text}"'

        # .. the section title pill shows the connection name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == conn_name, f'Expected connection name "{conn_name}" in the pill, got: "{pill_text}"'

        # .. the table shows the IMAP columns, compared case-insensitively
        # .. because the headers are uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'folder' in header_text, f'Expected a Folder column, got: "{header_text}"'
        assert 'message id' in header_text, f'Expected a Message id column, got: "{header_text}"'
        assert 'outcome' in header_text, f'Expected an Outcome column, got: "{header_text}"'

        # .. reading two messages and marking each as seen produces four events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the events come newest first - each message's marked-seen event precedes its received event ..
        expected_rows = (
            (_Event_Message_Marked_Seen, second_uid, ''),
            (_Event_Message_Received, second_uid, 'The first invoice was updated'),
            (_Event_Message_Marked_Seen, first_uid, ''),
            (_Event_Message_Received, first_uid, 'The first invoice was created'),
        )

        for row_index, (expected_event, expected_uid, expected_body) in enumerate(expected_rows):

            cells = _get_row_cells(rows[row_index])

            assert cells[_Column_Event] == expected_event, \
                f'Row {row_index}: expected event "{expected_event}", got: "{cells[_Column_Event]}"'
            assert cells[_Column_Msg_ID] == expected_uid, \
                f'Row {row_index}: expected message id "{expected_uid}", got: "{cells[_Column_Msg_ID]}"'
            assert cells[_Column_Folder] == _Folder, \
                f'Row {row_index}: expected folder "{_Folder}", got: "{cells[_Column_Folder]}"'
            assert cells[_Column_Outcome] == _Outcome_OK, \
                f'Row {row_index}: expected outcome "{_Outcome_OK}", got: "{cells[_Column_Outcome]}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            assert cells[_Column_Time] != '', f'Row {row_index}: expected a non-empty event time'
            assert '+00:00' not in cells[_Column_Time], \
                f'Row {row_index}: expected a locale-formatted time, got a raw ISO string: "{cells[_Column_Time]}"'

            # .. received events carry the message summary while marked-seen events carry no data.
            if expected_body:
                assert expected_body in cells[_Column_Data], \
                    f'Row {row_index}: expected "{expected_body}" in the data preview, got: "{cells[_Column_Data]}"'

                size = int(cells[_Column_Size])
                assert size > 0, f'Row {row_index}: expected a positive size, got {size}'

# ################################################################################################################################

    def test_link_from_connection_list(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Start with an empty mailbox and add one message ..
        imap_test_server.clear()
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Order confirmed', 'The order from the list was confirmed')

        # .. create an IMAP connection and read the mailbox once ..
        conn_name = _Test_Name_Prefix + 'from-list'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'from-list')

        _ = _invoke_helper(server_port, url_path, conn_name, 'get')

        # .. go back to the IMAP connections page ..
        _ = page.goto(f'{base_url}{_IMAP_Page_Url}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. click the audit log link in this connection's row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{conn_name}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the audit log page for this connection ..
        assert _Audit_Log_Url_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=email-imap' in page.url, f'Expected source=email-imap in the URL, got: "{page.url}"'
        assert quote(conn_name) in page.url, f'Expected the connection name in the URL, got: "{page.url}"'

        # .. and the events of the earlier read are shown.
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        cells = _get_row_cells(rows[1])
        assert 'The order from the list was confirmed' in cells[_Column_Data], \
            f'Expected the message body in the data preview, got: "{cells[_Column_Data]}"'

# ################################################################################################################################

    def test_events_share_cid(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Start with an empty mailbox and add one message ..
        imap_test_server.clear()
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Shipment sent', 'The first shipment was sent')

        # .. create an IMAP connection and read the mailbox once ..
        conn_name = _Test_Name_Prefix + 'cid'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'cid')

        _ = _invoke_helper(server_port, url_path, conn_name, 'get')

        # .. add another message and read the mailbox again, in a separate call ..
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Shipment delivered', 'The first shipment was delivered')
        _ = _invoke_helper(server_port, url_path, conn_name, 'get')

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, conn_name)

        # .. both reads are shown, two events each ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        first_read_seen_cells      = _get_row_cells(rows[2])
        first_read_received_cells  = _get_row_cells(rows[3])
        second_read_seen_cells     = _get_row_cells(rows[0])
        second_read_received_cells = _get_row_cells(rows[1])

        # .. a message's received and marked-seen events share the same CID ..
        assert first_read_received_cells[_Column_CID] == first_read_seen_cells[_Column_CID], \
            'Expected one shared CID within a read, got: ' + \
            f'"{first_read_received_cells[_Column_CID]}" and "{first_read_seen_cells[_Column_CID]}"'

        assert second_read_received_cells[_Column_CID] == second_read_seen_cells[_Column_CID], \
            'Expected one shared CID within a read, got: ' + \
            f'"{second_read_received_cells[_Column_CID]}" and "{second_read_seen_cells[_Column_CID]}"'

        # .. and separate reads carry separate CIDs.
        assert first_read_received_cells[_Column_CID] != second_read_received_cells[_Column_CID], \
            f'Expected distinct CIDs across reads, got: "{first_read_received_cells[_Column_CID]}" twice'

# ################################################################################################################################

    def test_search_filters_rows(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. start with an empty mailbox and add three messages with distinct bodies ..
        imap_test_server.clear()
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Invoice events', 'invoice-created')
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Invoice events', 'invoice-paid')
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Invoice events', 'invoice-cancelled')

        # .. create an IMAP connection and read the mailbox once ..
        conn_name = _Test_Name_Prefix + 'search'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'search')

        _ = _invoke_helper(server_port, url_path, conn_name, 'get')

        # .. open the audit log page and confirm all six events are there ..
        _goto_audit_log(page, base_url, conn_name)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. search for one body and wait for the others to disappear ..
        _search(page, 'invoice-paid')
        _wait_for_body_without_text(page, 'invoice-created', diagnostics)

        # .. only the matching received event remains - marked-seen events carry no data to match ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 filtered row, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'invoice-paid' in cells[_Column_Data], \
            f'Expected the matching body, got: "{cells[_Column_Data]}"'

        # .. a query matching nothing shows the empty placeholder ..
        _search(page, 'no-such-message-anywhere')
        _wait_for_body_text(page, _No_Events_Text, diagnostics)

        # .. clearing the query brings all six events back ..
        _search(page, '')
        _wait_for_body_text(page, 'invoice-created', diagnostics)
        _wait_for_body_text(page, 'invoice-cancelled', diagnostics)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 rows after clearing the search, got {row_count}'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. build a body much longer than the 200-character preview shown in the table,
        # .. made of space-separated tokens so e-mail line wrapping cannot split any of them ..
        tokens:'strlist' = []

        for token_index in range(40):
            tokens.append(f'test-product-{token_index}')

        long_body = ' '.join(tokens)

        # .. start with an empty mailbox and add the long message ..
        imap_test_server.clear()
        _ = imap_test_server.add_message(_Sender, _Recipient, 'Product catalog', long_body)

        # .. create an IMAP connection and read the mailbox once ..
        conn_name = _Test_Name_Prefix + 'complete'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'complete')

        _ = _invoke_helper(server_port, url_path, conn_name, 'get')

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, conn_name)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the table shows only a truncated preview of the message summary ..
        received_row = rows[1]
        cells = _get_row_cells(received_row)
        preview = cells[_Column_Data]
        size = int(cells[_Column_Size])
        assert len(preview) < size, \
            f'Expected a truncated preview, got {len(preview)} characters for a {size}-character summary'

        # .. clicking the received event's CID opens the overlay with the complete message ..
        cid_link = received_row.query_selector('a.audit-log-cid-link')
        cid_link.click()
        _ = page.wait_for_selector('#zato-highlight-pane-overlay:not(.hidden)', state='visible', timeout=10000)

        # .. the overlay editor holds the summary in full, read through the Ace API
        # .. because Ace renders only the visible part of the text into the DOM ..
        editor_value = page.evaluate(
            '''() => {
                let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
                return ace.edit(element).getValue();
            }''')

        assert len(editor_value) > len(preview), \
            f'Expected the complete summary in the overlay, got {len(editor_value)} characters'

        for token in tokens:
            assert token in editor_value, f'Expected "{token}" in the overlay, got: "{editor_value}"'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Connection refused', 'ConnectionRefusedError')
    def test_error_outcome(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create an IMAP connection pointing at a port that nothing listens on ..
        conn_name = _Test_Name_Prefix + 'error'
        _create_imap_connection(page, base_url, conn_name, '127.0.0.1', _Closed_Port)

        # .. make sure the helper service is selectable and create a channel for it ..
        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'error')

        # .. reading the mailbox fails and the channel reports an error ..
        payload = {'conn_name': conn_name, 'action': 'get'}
        response = invoke_until_status(server_port, url_path, INTERNAL_SERVER_ERROR, json_data=payload)
        assert response.status_code == INTERNAL_SERVER_ERROR, \
            f'Expected INTERNAL_SERVER_ERROR, got {response.status_code}: {response.text}'

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, conn_name)

        # .. the failed read produced exactly one event ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        cells = _get_row_cells(rows[0])

        # .. and it carries the error outcome together with the traceback.
        assert cells[_Column_Event] == _Event_Message_Received, \
            f'Expected event type "{_Event_Message_Received}", got: "{cells[_Column_Event]}"'
        assert cells[_Column_Outcome] == _Outcome_Error, \
            f'Expected outcome "{_Outcome_Error}", got: "{cells[_Column_Outcome]}"'
        assert 'Traceback' in cells[_Column_Data], \
            f'Expected a traceback in the data preview, got: "{cells[_Column_Data]}"'

# ################################################################################################################################

    def test_connection_delete(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Start with an empty mailbox and add two messages ..
        imap_test_server.clear()
        first_uid = imap_test_server.add_message(_Sender, _Recipient, 'Old report', 'The first report to delete')
        second_uid = imap_test_server.add_message(_Sender, _Recipient, 'Old summary', 'The first summary to delete')

        # .. create an IMAP connection pointing at the test server ..
        conn_name = _Test_Name_Prefix + 'delete'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'delete')

        # .. read the mailbox and delete everything through the connection-level call ..
        uids = _invoke_helper(server_port, url_path, conn_name, 'connection-delete')
        assert uids == [first_uid, second_uid], f'Expected uids {first_uid} and {second_uid}, got: {uids}'

        # .. the deletion commands really reached the IMAP server ..
        assert imap_test_server.has_received('DELETED'), 'Expected the IMAP server to receive a deletion command'
        assert imap_test_server.has_received('EXPUNGE'), 'Expected the IMAP server to receive an expunge command'

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, conn_name)

        # .. two received events and two deleted events are shown ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        second_deleted_cells  = _get_row_cells(rows[0])
        first_deleted_cells   = _get_row_cells(rows[1])
        second_received_cells = _get_row_cells(rows[2])
        first_received_cells  = _get_row_cells(rows[3])

        # .. the newest events are the deletions, in the reverse order of their uids ..
        for cells, expected_uid in ((second_deleted_cells, second_uid), (first_deleted_cells, first_uid)):

            assert cells[_Column_Event] == _Event_Message_Deleted, \
                f'Expected event type "{_Event_Message_Deleted}", got: "{cells[_Column_Event]}"'
            assert cells[_Column_Msg_ID] == expected_uid, \
                f'Expected message id "{expected_uid}", got: "{cells[_Column_Msg_ID]}"'
            assert cells[_Column_Outcome] == _Outcome_OK, \
                f'Expected outcome "{_Outcome_OK}", got: "{cells[_Column_Outcome]}"'

        # .. both deletions ran in one call so they share one CID ..
        assert first_deleted_cells[_Column_CID] == second_deleted_cells[_Column_CID], \
            'Expected one shared CID for both deletions, got: ' + \
            f'"{first_deleted_cells[_Column_CID]}" and "{second_deleted_cells[_Column_CID]}"'

        # .. while the earlier read carries its own, separate CID.
        assert first_received_cells[_Column_CID] == second_received_cells[_Column_CID], \
            'Expected one shared CID for the read, got: ' + \
            f'"{first_received_cells[_Column_CID]}" and "{second_received_cells[_Column_CID]}"'

        assert first_received_cells[_Column_CID] != first_deleted_cells[_Column_CID], \
            f'Expected distinct CIDs for the read and the deletions, got: "{first_deleted_cells[_Column_CID]}" twice'

# ################################################################################################################################
# ################################################################################################################################
