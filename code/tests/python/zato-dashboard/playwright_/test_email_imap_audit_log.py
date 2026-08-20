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

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

from _imap_test_server import IMAPTestServer
from audit_log_ui import attach_diagnostics, format_diagnostics, get_details_value, get_row_cid, get_row_event, \
    get_row_main_text, get_row_outcome, get_row_time_text, get_rows, goto_audit_log, open_cid_overlay, open_data, \
    open_details, close_cid_overlay, search, wait_for_empty, wait_for_payload_text, wait_for_row_count, wait_for_table

from rest_channel import create_channel, deploy_service_file, invoke_until_status, wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.imap.audit.' + rand_string() + '.'

_IMAP_Page_URL = '/zato/email/imap/?cluster=1'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'email-imap'

# How the events of a mailbox read run through the log
_Event_Message_Received_Label    = 'Message received'
_Event_Message_Marked_Seen_Label = 'Message marked seen'
_Event_Message_Deleted_Label     = 'Message deleted'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

# The section title for the IMAP source, compared lowercase because the heading is styled with CSS
_IMAP_Title = 'imap audit log'

# The folder that the helper service reads messages from
_Folder = 'INBOX'

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
    _ = page.goto(f'{base_url}{_IMAP_Page_URL}')
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

def _get_row_msg_id(page:'Page', row:'any_') -> 'str':
    """ The message id of one row's event, read off the Message id fact in the pane's Details tab.
    """

    open_details(page, row)

    out = get_details_value(page, 'Message id')
    return out

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
        goto_audit_log(page, base_url, _Source, conn_name)

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

        # .. reading two messages and marking each as seen produces four events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the events come newest first - each message's marked-seen event precedes its received event ..
        expected_rows = (
            (_Event_Message_Marked_Seen_Label, second_uid, ''),
            (_Event_Message_Received_Label, second_uid, 'The first invoice was updated'),
            (_Event_Message_Marked_Seen_Label, first_uid, ''),
            (_Event_Message_Received_Label, first_uid, 'The first invoice was created'),
        )

        for row_index, (expected_event, expected_uid, expected_body) in enumerate(expected_rows):

            row = rows[row_index]

            event_label = get_row_event(row)
            assert event_label == expected_event, \
                f'Row {row_index}: expected event "{expected_event}", got: "{event_label}"'

            # .. the folder is worn as a chip on the row ..
            main_text = get_row_main_text(row)
            assert _Folder in main_text, f'Row {row_index}: expected folder "{_Folder}" on the row, got: "{main_text}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            time_text = get_row_time_text(row)
            assert time_text != '', f'Row {row_index}: expected a non-empty event time'
            assert '+00:00' not in time_text, \
                f'Row {row_index}: expected a locale-formatted time, got a raw ISO string: "{time_text}"'

            # .. the message id is read off the pane's Details tab ..
            msg_id = _get_row_msg_id(page, row)
            assert msg_id == expected_uid, \
                f'Row {row_index}: expected message id "{expected_uid}", got: "{msg_id}"'

            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Row {row_index}: expected outcome "{_Outcome_OK}", got: "{outcome}"'

            # .. and received events carry the message summary while marked-seen events carry no data.
            if expected_body:
                open_data(page, row)
                wait_for_payload_text(page, expected_body)

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
        _ = page.goto(f'{base_url}{_IMAP_Page_URL}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. click the audit log link in this connection's row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{conn_name}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_table(page)

        # .. the URL points to the audit log page for this connection ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=email-imap' in page.url, f'Expected source=email-imap in the URL, got: "{page.url}"'
        assert quote(conn_name) in page.url, f'Expected the connection name in the URL, got: "{page.url}"'

        # .. and the events of the earlier read are shown, with the message body in the Data tab.
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        open_data(page, rows[1])
        wait_for_payload_text(page, 'The order from the list was confirmed')

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
        goto_audit_log(page, base_url, _Source, conn_name)

        # .. both reads are shown, two events each ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        second_read_seen_cid     = get_row_cid(page, rows[0])
        second_read_received_cid = get_row_cid(page, rows[1])
        first_read_seen_cid      = get_row_cid(page, rows[2])
        first_read_received_cid  = get_row_cid(page, rows[3])

        # .. a message's received and marked-seen events share the same CID ..
        assert first_read_received_cid == first_read_seen_cid, \
            f'Expected one shared CID within a read, got: "{first_read_received_cid}" and "{first_read_seen_cid}"'

        assert second_read_received_cid == second_read_seen_cid, \
            f'Expected one shared CID within a read, got: "{second_read_received_cid}" and "{second_read_seen_cid}"'

        # .. and separate reads carry separate CIDs.
        assert first_read_received_cid != second_read_received_cid, \
            f'Expected distinct CIDs across reads, got: "{first_read_received_cid}" twice'

# ################################################################################################################################

    def test_search_filters_rows(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

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
        goto_audit_log(page, base_url, _Source, conn_name)

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the stored message summaries, so one body keeps only
        # .. the matching received event - marked-seen events carry no data to match ..
        search(page, 'invoice-paid')
        wait_for_row_count(page, 1, diagnostics)

        rows = get_rows(page)

        open_data(page, rows[0])
        wait_for_payload_text(page, 'invoice-paid', diagnostics)

        # .. a query matching nothing shows the empty placeholder ..
        search(page, 'no-such-message-anywhere')
        wait_for_empty(page, diagnostics)

        # .. clearing the query brings all six events back ..
        search(page, '')
        wait_for_row_count(page, 6, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a body long enough that no row could ever show it whole,
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
        goto_audit_log(page, base_url, _Source, conn_name)

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the row itself carries no message body - the summary is read in the pane ..
        received_row = rows[1]
        main_text = get_row_main_text(received_row)
        assert 'test-product-0' not in main_text, f'Expected no message body on the row, got: "{main_text}"'

        # .. while the overlay behind the received event's CID holds the summary in full.
        editor_value = open_cid_overlay(page, received_row)

        for token in tokens:
            assert token in editor_value, f'Expected "{token}" in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

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
        goto_audit_log(page, base_url, _Source, conn_name)

        # .. the failed read produced exactly one event ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        # .. and it carries the error outcome together with the traceback.
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Message_Received_Label, \
            f'Expected event "{_Event_Message_Received_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

        open_data(page, rows[0])
        wait_for_payload_text(page, 'Traceback')

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
        goto_audit_log(page, base_url, _Source, conn_name)

        # .. two received events and two deleted events are shown ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest events are the deletions, in the reverse order of their uids ..
        for row, expected_uid in ((rows[0], second_uid), (rows[1], first_uid)):

            event_label = get_row_event(row)
            assert event_label == _Event_Message_Deleted_Label, \
                f'Expected event "{_Event_Message_Deleted_Label}", got: "{event_label}"'

            msg_id = _get_row_msg_id(page, row)
            assert msg_id == expected_uid, f'Expected message id "{expected_uid}", got: "{msg_id}"'

            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. both deletions ran in one call so they share one CID ..
        second_deleted_cid = get_row_cid(page, rows[0])
        first_deleted_cid = get_row_cid(page, rows[1])
        assert first_deleted_cid == second_deleted_cid, \
            f'Expected one shared CID for both deletions, got: "{first_deleted_cid}" and "{second_deleted_cid}"'

        # .. while the earlier read carries its own, separate CID.
        second_received_cid = get_row_cid(page, rows[2])
        first_received_cid = get_row_cid(page, rows[3])
        assert first_received_cid == second_received_cid, \
            f'Expected one shared CID for the read, got: "{first_received_cid}" and "{second_received_cid}"'

        assert first_received_cid != first_deleted_cid, \
            f'Expected distinct CIDs for the read and the deletions, got: "{first_deleted_cid}" twice'

# ################################################################################################################################
# ################################################################################################################################
