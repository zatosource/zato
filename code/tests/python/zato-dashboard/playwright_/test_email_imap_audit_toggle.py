# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time
from http.client import OK

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
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

from _imap_test_server import IMAPTestServer
from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from rest_channel import create_channel, deploy_service_file, invoke_until_status, wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.imap.audit.toggle.' + rand_string() + '.'

_IMAP_Page_Url = '/zato/email/imap/?cluster=1'

_Audit_Source = 'email-imap'

# Who the test messages are exchanged between
_Sender    = 'sender@example.com'
_Recipient = 'recipient@example.com'

# How long to keep polling while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the polls above
_Propagation_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

# The helper service runs IMAP operations on behalf of the tests, invoked through a REST channel
_Helper_Service_Name = 'test.imap.audit.toggle.helper'

_Helper_Service_Source = '''
# -*- coding: utf-8 -*-

# stdlib
from json import dumps
from time import sleep

# Zato
from zato.server.service import Service

class IMAPAuditToggleHelper(Service):
    """ Runs IMAP operations on behalf of the IMAP audit log toggle tests.
    """

    name = 'test.imap.audit.toggle.helper'

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

        # Report whether the connection writes audit events, which is how the tests
        # detect that an edit made in the dashboard has propagated to the server ..
        if action == 'get-audit-flag':
            self.response.payload = dumps({'needs_audit': conn.needs_audit})

        # .. or read all matching messages, marking each one as seen.
        elif action == 'get':
            uids = []
            for uid, message in conn.get():
                uids.append(uid.decode('utf-8'))
                message.mark_seen()
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
    file_path = deploy_service_file(server_dir, 'test_imap_audit_toggle_helper.py', _Helper_Service_Source)

    yield _Helper_Service_Name

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _open_imap_page(page:'Page', base_url:'str') -> 'None':
    """ Opens the IMAP connections page and waits for the data table to be ready.
    """
    _ = page.goto(f'{base_url}{_IMAP_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_imap_connection(page:'Page', base_url:'str', name:'str', host:'str', port:'int') -> 'None':
    """ Creates a plaintext generic IMAP connection via the UI, pointing it at the given host and port.
    """

    # Open the IMAP connections page ..
    _open_imap_page(page, base_url)

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

def _open_edit_dialog(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Opens the edit dialog of one IMAP connection through its row's edit link.
    """

    _open_imap_page(page, base_url)

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.click(f'{row_selector} a:text-is("Edit")')
    _ = page.wait_for_selector('#edit-div', state='visible')

# ################################################################################################################################

def _edit_audit_flag(page:'Page', base_url:'str', name:'str', is_audit_log_active:'bool') -> 'None':
    """ Sets the audit log checkbox of one IMAP connection through the edit dialog.
    """

    # Open the edit dialog ..
    _open_edit_dialog(page, base_url, name)

    # .. flip the checkbox ..
    page.set_checked('#id_edit-is_audit_log_active', is_audit_log_active)

    # .. and submit, waiting for the dialog to close.
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

# ################################################################################################################################

def _create_helper_channel(page:'Page', base_url:'str', name_suffix:'str') -> 'str':
    """ Creates a JSON REST channel pointing at the helper service and returns its URL path.
    """

    channel_name = _Test_Name_Prefix + name_suffix
    url_path = f'/test/imap/audit/toggle/{name_suffix}/' + rand_string()

    _ = create_channel(page, base_url, channel_name, _Helper_Service_Name, url_path, {
        'data_format': 'json',
    })

    out = url_path
    return out

# ################################################################################################################################

def _invoke_helper(server_port:'int', url_path:'str', conn_name:'str', action:'str') -> 'anydict':
    """ Invokes the helper service through its REST channel and returns its response.
    """

    payload = {'conn_name': conn_name, 'action': action}

    response = invoke_until_status(server_port, url_path, OK, json_data=payload)
    assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

    out = response.json()
    return out

# ################################################################################################################################

def _read_mailbox(server_port:'int', url_path:'str', conn_name:'str', expected_uids:'anylist') -> 'None':
    """ Reads the whole mailbox through the helper service and checks which uids came back.
    """

    response_data = _invoke_helper(server_port, url_path, conn_name, 'get')
    uids = response_data['uids']
    assert uids == expected_uids, f'Expected uids {expected_uids}, got: {uids}'

# ################################################################################################################################

def _wait_for_audit_flag(server_port:'int', url_path:'str', conn_name:'str', expected:'bool') -> 'None':
    """ Polls the helper service until the connection's audit flag matches the expected value,
    which proves an edit made a moment ago in the browser has propagated to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_value = None

    while time.monotonic() < deadline:

        response_data = _invoke_helper(server_port, url_path, conn_name, 'get-audit-flag')
        last_value = response_data['needs_audit']

        if last_value is expected:
            return

        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'The audit flag of `{conn_name}` did not become {expected} ' \
        f'within {_Propagation_Timeout}s, last value: {last_value}')

# ################################################################################################################################
# ################################################################################################################################

class TestEmailIMAPAuditToggle:
    """ The per-connection audit log toggle of IMAP connections - the checkbox is on by default
    and turning it off stops audit events while the connection keeps reading messages.
    """

    def test_checkbox_defaults(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        _open_imap_page(page, base_url)

        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        page.evaluate('$("#create-div").dialog("close")')

        # .. and a connection created with the default carries it into the edit dialog.
        conn_name = _Test_Name_Prefix + 'defaults'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        _open_edit_dialog(page, base_url, conn_name)

        assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
        assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on in the edit dialog of a default connection'

        page.evaluate('$("#edit-div").dialog("close")')

# ################################################################################################################################

    def test_toggle_gates_events(
        self, logged_in_page:'Page', zato_dashboard:'anydict', imap_test_server:'any_', helper_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a connection with the toggle on ..
        conn_name = _Test_Name_Prefix + 'gates'
        _create_imap_connection(page, base_url, conn_name, imap_test_server.host, imap_test_server.port)

        # .. make sure the helper service is selectable and create a channel for it ..
        wait_for_service_in_dialog(page, base_url, helper_service)
        url_path = _create_helper_channel(page, base_url, 'gates')

        # .. read one message with the toggle on ..
        imap_test_server.clear()
        first_uid = imap_test_server.add_message(_Sender, _Recipient, 'Toggle on', 'Read with the toggle on')

        _read_mailbox(server_port, url_path, conn_name, [first_uid])

        # .. the read produced its two events - received and marked-seen ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, conn_name)
        assert row_count == 2, f'Expected 2 audit log rows with the toggle on, got {row_count}'

        # .. turn the toggle off and wait for the change to reach the server ..
        _edit_audit_flag(page, base_url, conn_name, False)
        _wait_for_audit_flag(server_port, url_path, conn_name, False)

        # .. read another message - the traffic goes through but no new events are recorded ..
        imap_test_server.clear()
        second_uid = imap_test_server.add_message(_Sender, _Recipient, 'Toggle off', 'Read with the toggle off')

        _read_mailbox(server_port, url_path, conn_name, [second_uid])

        row_count = get_audit_row_count(page, base_url, _Audit_Source, conn_name)
        assert row_count == 2, f'Expected still 2 audit log rows with the toggle off, got {row_count}'

        # .. turn the toggle back on the same way ..
        _edit_audit_flag(page, base_url, conn_name, True)
        _wait_for_audit_flag(server_port, url_path, conn_name, True)

        # .. and the events resumed.
        imap_test_server.clear()
        third_uid = imap_test_server.add_message(_Sender, _Recipient, 'Toggle back on', 'Read with the toggle back on')

        _read_mailbox(server_port, url_path, conn_name, [third_uid])

        row_count = get_audit_row_count(page, base_url, _Audit_Source, conn_name)
        assert row_count == 4, f'Expected 4 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
