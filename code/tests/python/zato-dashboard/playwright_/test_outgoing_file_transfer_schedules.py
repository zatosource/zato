# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import ConsoleMessage, Page, Response
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.file.transfer.' + CryptoManager.generate_hex_string(32) + '.'

# The service every schedule in these tests invokes - it exists in each test environment
_Test_Service = 'demo.ping'

# The name of the schedule the server will not accept
_Refused_Schedule_Name = 'runs.never'

# An interval the wizard lets through and the server does not, since it is not a positive number of minutes
_Refused_Run_Every = '0'

# What the server says about that interval, which is what must reach the screen
_Refused_Reason = 'Run-every'

# ################################################################################################################################
# ################################################################################################################################

class ConnKind(NamedTuple):
    """ One kind of connection that carries file transfer schedules, as the dashboard presents it.
    """
    # What the test calls this kind of connection
    label: str

    # The list page of connections of this kind
    page_url: str

    # The JavaScript namespace whose delete_ removes one of them
    namespace: str

    # The directory of a schedule of this kind, in the shape its remote paths take
    directory: str

    # The directory an edit changes the schedule to
    edited_directory: str

# ################################################################################################################################

_sftp_kind = ConnKind(
    label='sftp',
    page_url='/zato/outgoing/sftp/?cluster=1&type_=outconn-sftp',
    namespace='$.fn.zato.outgoing.sftp',
    directory='/incoming/invoices',
    edited_directory='/incoming/invoices-v2',
)

_smb_kind = ConnKind(
    label='smb',
    page_url='/zato/outgoing/smb/?cluster=1&type_=outconn-smb',
    namespace='$.fn.zato.outgoing.smb',
    directory='my-share/incoming/invoices',
    edited_directory='my-share/incoming/invoices-v2',
)

_conn_kinds = [_sftp_kind, _smb_kind]

# ################################################################################################################################
# ################################################################################################################################

def _navigate_to_list(page:'Page', base_url:'str', kind:'ConnKind') -> 'None':
    """ Opens the list page of one kind of connection and waits for the data table.
    """
    _ = page.goto(f'{base_url}{kind.page_url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _fill_connection_fields(page:'Page', kind:'ConnKind') -> 'None':
    """ Fills in the fields that only this kind of connection has.
    """
    if kind is _sftp_kind:
        page.fill('#id_address', 'sftp.example.com:22')
        page.fill('#id_username', 'sftp-user')
        page.fill('#id_secret', 'sftp-password-' + CryptoManager.generate_hex_string())

    else:
        page.fill('#id_host', 'smb.example.com')
        page.fill('#id_port', '445')
        page.fill('#id_username', 'smb-user')
        page.fill('#id_secret', 'smb-password-' + CryptoManager.generate_hex_string())

# ################################################################################################################################

def _create_connection(page:'Page', kind:'ConnKind', name:'str') -> 'None':
    """ Creates one outgoing connection via the UI - the schedules under test belong to it.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    _fill_connection_fields(page, kind)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}")) td[class*="item_id_"]'
    out = page.inner_text(row_selector).strip()

    return out

# ################################################################################################################################

def _delete_connection(page:'Page', kind:'ConnKind', item_id:'str') -> 'None':
    page.evaluate(f'{kind.namespace}.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _open_schedules(page:'Page', conn_name:'str') -> 'None':
    """ Clicks the Schedules link of a connection's row and waits for the schedules list page.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{conn_name}"))'
    page.click(f'{row_selector} a:has-text("Schedules")')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _open_schedules_directly(page:'Page') -> 'None':
    """ Goes back to the schedules list the wizard was opened from.
    """
    _ = page.go_back()
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _open_create_wizard(page:'Page') -> 'None':
    page.click('#markup .page_prompt a:has-text("Create a new schedule")')
    _ = page.wait_for_selector('#file-transfer-wizard', state='visible')

# ################################################################################################################################

def _wizard_next(page:'Page') -> 'None':
    page.click('#file-transfer-wizard-next')
    time.sleep(0.2)

# ################################################################################################################################

def _wizard_finish(page:'Page') -> 'None':
    """ Clicks Finish on the review step and waits for the redirect back to the schedules list.
    """
    page.click('#file-transfer-wizard-next')
    page.wait_for_url('**/zato/outgoing/file-transfer/schedules/**', timeout=10000)
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _fill_wizard_service(page:'Page') -> 'None':
    """ Picks the schedule's target service - the select is a searchable chosen widget,
    so the value goes into the underlying select directly.
    """
    page.evaluate(f'$("#id_scheduler_service").val("{_Test_Service}").trigger("chosen:updated")')

# ################################################################################################################################

def _submit_a_schedule_the_server_refuses(page:'Page', kind:'ConnKind') -> 'None':
    """ Walks the wizard to the end with a schedule the server will not accept and clicks Finish.
    """
    _open_create_wizard(page)

    page.fill('#id_name', _Refused_Schedule_Name)
    page.fill('#id_directory', kind.directory)

    _wizard_next(page)

    _fill_wizard_service(page)
    page.fill('#id_run_every', _Refused_Run_Every)

    _wizard_next(page)

    page.click('#file-transfer-wizard-next')
    _ = page.wait_for_selector('#file-transfer-wizard-status.wizard-status-error', timeout=10000)

# ################################################################################################################################

def _watch_for_errors(page:'Page') -> 'tuple':
    """ Starts collecting console errors and server errors, returning the two lists they go into.
    """
    console_errors:'strlist' = []
    server_errors:'strlist' = []

    def _on_console(msg:'ConsoleMessage') -> 'None':
        if msg.type == 'error':
            console_errors.append(msg.text)

    def _on_response(response:'Response') -> 'None':
        if response.status >= 500:
            server_errors.append(f'{response.status} {response.url}')

    page.on('console', _on_console)
    page.on('response', _on_response)

    out = console_errors, server_errors
    return out

# ################################################################################################################################

def _assert_no_errors(console_errors:'strlist', server_errors:'strlist') -> 'None':

    real_errors:'strlist' = []

    for error_text in console_errors:
        if 'favicon.ico' in error_text:
            continue
        if 'Content-Security-Policy' in error_text:
            continue
        real_errors.append(error_text)

    assert not real_errors, 'Console errors during the schedule cycle:\n' + '\n'.join(real_errors)
    assert not server_errors, 'HTTP 500+ responses during the schedule cycle:\n' + '\n'.join(server_errors)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('kind', _conn_kinds, ids=['sftp', 'smb'])
class TestOutgoingFileTransferSchedules:
    """ Walks the file transfer schedule screens end to end - the list page, the three-step
    create wizard, the edit wizard and the delete action, all through a connection's Schedules link,
    for each kind of connection that carries schedules.
    """

    def test_schedule_wizard_full_cycle(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        kind:'ConnKind',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        console_errors, server_errors = _watch_for_errors(page)

        # Create the connection the schedules will belong to
        _navigate_to_list(page, base_url, kind)

        conn_name = _Test_Name_Prefix + kind.label + '.wizard'
        _create_connection(page, kind, conn_name)
        conn_id = _get_item_id(page, conn_name)

        try:

            # The connection's Schedules link leads to an empty list
            _open_schedules(page, conn_name)

            no_schedules = page.query_selector('#data-table tbody tr td[colspan]')
            assert no_schedules is not None, 'A new connection should have no schedules'

            _open_create_wizard(page)

            # The context badge names the connection the schedule belongs to
            badge_text = page.inner_text('#file-transfer-wizard-context-badge')
            assert conn_name in badge_text, f'Expected "{conn_name}" in the context badge, got: "{badge_text}"'

            # Step 1 - name and directory, everything else keeps its defaults
            schedule_name = 'invoices.hourly'

            page.fill('#id_name', schedule_name)
            page.fill('#id_directory', kind.directory)

            _wizard_next(page)

            # Step 2 - the target service, the rest keeps its defaults
            _fill_wizard_service(page)

            _wizard_next(page)

            # Step 3 - the review shows what was filled in
            review_text = page.inner_text('#file-transfer-wizard-review')

            assert schedule_name in review_text, f'Expected "{schedule_name}" in the review, got: "{review_text}"'
            assert kind.directory in review_text, f'Expected the directory in the review, got: "{review_text}"'
            assert _Test_Service in review_text, f'Expected "{_Test_Service}" in the review, got: "{review_text}"'

            # Finish - back on the list with the new schedule
            _wizard_finish(page)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is not None, f'Schedule "{schedule_name}" should be on the list after create'

            row_text = row.inner_text()
            assert kind.directory in row_text, f'Expected the directory in the row, got: "{row_text}"'
            assert _Test_Service in row_text, f'Expected the service in the row, got: "{row_text}"'

            # Edit - the wizard opens prefilled, the directory changes
            page.click(f'#data-table tbody tr:has(td:text-is("{schedule_name}")) a:has-text("Edit")')
            _ = page.wait_for_selector('#file-transfer-wizard', state='visible')

            prefilled_name = page.input_value('#id_name')
            assert prefilled_name == schedule_name, f'Expected the name prefilled, got: "{prefilled_name}"'

            prefilled_directory = page.input_value('#id_directory')
            assert prefilled_directory == kind.directory, \
                f'Expected the directory prefilled, got: "{prefilled_directory}"'

            page.fill('#id_directory', kind.edited_directory)

            _wizard_next(page)
            _wizard_next(page)
            _wizard_finish(page)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is not None, f'Schedule "{schedule_name}" should still be on the list after edit'

            row_text = row.inner_text()
            assert kind.edited_directory in row_text, f'Expected the edited directory in the row, got: "{row_text}"'

            # Delete - the row goes away
            page.click(f'#data-table tbody tr:has(td:text-is("{schedule_name}")) a:has-text("Delete")')
            _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
            page.click('#popup_ok')
            time.sleep(0.5)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is None, f'Schedule "{schedule_name}" should be gone after delete'

        finally:

            # The connection goes away together with anything the test left behind
            _navigate_to_list(page, base_url, kind)
            _delete_connection(page, kind, conn_id)

        _assert_no_errors(console_errors, server_errors)

# ################################################################################################################################

    def test_a_schedule_the_server_refuses_keeps_the_wizard_open(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        kind:'ConnKind',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _navigate_to_list(page, base_url, kind)

        conn_name = _Test_Name_Prefix + kind.label + '.refused'
        _create_connection(page, kind, conn_name)
        conn_id = _get_item_id(page, conn_name)

        try:

            _open_schedules(page, conn_name)
            _submit_a_schedule_the_server_refuses(page, kind)

            # The wizard stays open with the reason on the screen rather than sending the user
            # to a page of its own, so nothing already filled in is lost.
            assert page.is_visible('#file-transfer-wizard'), \
                'The wizard must stay open when the server refuses the schedule'

            message = page.inner_text('#user-message-div')
            assert _Refused_Reason in message, f'Expected the reason on the screen, got: "{message}"'

            # Nothing was created
            _open_schedules_directly(page)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{_Refused_Schedule_Name}"))')
            assert row is None, f'Schedule "{_Refused_Schedule_Name}" must not have been created'

        finally:

            _navigate_to_list(page, base_url, kind)
            _delete_connection(page, kind, conn_id)

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='A schedule the server refuses comes back as a server error')
    def test_a_schedule_the_server_refuses_is_not_a_server_error(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        kind:'ConnKind',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        console_errors, server_errors = _watch_for_errors(page)

        _navigate_to_list(page, base_url, kind)

        conn_name = _Test_Name_Prefix + kind.label + '.refused.status'
        _create_connection(page, kind, conn_name)
        conn_id = _get_item_id(page, conn_name)

        try:
            _open_schedules(page, conn_name)
            _submit_a_schedule_the_server_refuses(page, kind)

        finally:
            _navigate_to_list(page, base_url, kind)
            _delete_connection(page, kind, conn_id)

        # A schedule the server will not accept is a request that was understood, never a server error
        _assert_no_errors(console_errors, server_errors)

# ################################################################################################################################
# ################################################################################################################################
