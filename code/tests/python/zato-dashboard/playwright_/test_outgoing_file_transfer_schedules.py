# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/outgoing/sftp/?cluster=1&type_=outconn-sftp'

_Test_Name_Prefix = 'test.file.transfer.' + CryptoManager.generate_hex_string(32) + '.'

# The service every schedule in these tests invokes - it exists in each test environment
_Test_Service = 'demo.ping'

# ################################################################################################################################
# ################################################################################################################################

def _navigate_to_sftp(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing SFTP page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str') -> 'None':
    """ Creates an outgoing SFTP connection via the UI - the schedules under test belong to it.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', 'sftp.example.com:22')
    page.fill('#id_username', 'sftp-user')
    page.fill('#id_secret', 'sftp-password-' + CryptoManager.generate_hex_string())

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    out = id_cell.inner_text().strip()

    return out

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.outgoing.sftp.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _open_schedules(page:'Page', conn_name:'str') -> 'None':
    """ Clicks the Schedules link of a connection's row and waits for the schedules list page.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{conn_name}"))'
    page.click(f'{row_selector} a:has-text("Schedules")')
    page.wait_for_selector('#data-table', state='visible')

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
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _fill_wizard_service(page:'Page') -> 'None':
    """ Picks the schedule's target service - the select is a searchable chosen widget,
    so the value goes into the underlying select directly.
    """
    page.evaluate(f'$("#id_scheduler_service").val("{_Test_Service}").trigger("chosen:updated")')

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFileTransferSchedules:
    """ Walks the file transfer schedule screens end to end - the list page, the three-step
    create wizard, the edit wizard and the delete action, all through a connection's Schedules link.
    """

    def test_schedule_wizard_full_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors along the way ..
        console_errors = [] # type: list

        def _on_console(msg:'object') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. and server errors too.
        server_errors = [] # type: list

        def _on_response(response:'object') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # Create the connection the schedules will belong to
        _navigate_to_sftp(page, base_url)

        conn_name = _Test_Name_Prefix + 'wizard'
        _create_connection(page, conn_name)
        conn_id = _get_item_id(page, conn_name)

        try:

            # The connection's Schedules link leads to an empty list
            _open_schedules(page, conn_name)

            no_schedules = page.query_selector('#data-table tbody tr td[colspan]')
            assert no_schedules is not None, 'A new connection should have no schedules'

            # Open the create wizard
            page.click('#markup .page_prompt a:has-text("Create a new schedule")')
            page.wait_for_selector('#file-transfer-wizard', state='visible')

            # The context badge names the connection the schedule belongs to
            badge_text = page.inner_text('#file-transfer-wizard-context-badge')
            assert conn_name in badge_text, f'Expected "{conn_name}" in the context badge, got: "{badge_text}"'

            # Step 1 - name and directory, everything else keeps its defaults
            schedule_name = 'invoices.hourly'

            page.fill('#id_name', schedule_name)
            page.fill('#id_directory', '/incoming/invoices')

            _wizard_next(page)

            # Step 2 - the target service, the rest keeps its defaults
            _fill_wizard_service(page)

            _wizard_next(page)

            # Step 3 - the review shows what was filled in
            review_text = page.inner_text('#file-transfer-wizard-review')

            assert schedule_name in review_text, f'Expected "{schedule_name}" in the review, got: "{review_text}"'
            assert '/incoming/invoices' in review_text, f'Expected the directory in the review, got: "{review_text}"'
            assert _Test_Service in review_text, f'Expected "{_Test_Service}" in the review, got: "{review_text}"'

            # Finish - back on the list with the new schedule
            _wizard_finish(page)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is not None, f'Schedule "{schedule_name}" should be on the list after create'

            row_text = row.inner_text()
            assert '/incoming/invoices' in row_text, f'Expected the directory in the row, got: "{row_text}"'
            assert _Test_Service in row_text, f'Expected the service in the row, got: "{row_text}"'

            # Edit - the wizard opens prefilled, the directory changes
            page.click(f'#data-table tbody tr:has(td:text-is("{schedule_name}")) a:has-text("Edit")')
            page.wait_for_selector('#file-transfer-wizard', state='visible')

            prefilled_name = page.input_value('#id_name')
            assert prefilled_name == schedule_name, f'Expected the name prefilled, got: "{prefilled_name}"'

            prefilled_directory = page.input_value('#id_directory')
            assert prefilled_directory == '/incoming/invoices', f'Expected the directory prefilled, got: "{prefilled_directory}"'

            page.fill('#id_directory', '/incoming/invoices-v2')

            _wizard_next(page)
            _wizard_next(page)
            _wizard_finish(page)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is not None, f'Schedule "{schedule_name}" should still be on the list after edit'

            row_text = row.inner_text()
            assert '/incoming/invoices-v2' in row_text, f'Expected the edited directory in the row, got: "{row_text}"'

            # Delete - the row goes away
            page.click(f'#data-table tbody tr:has(td:text-is("{schedule_name}")) a:has-text("Delete")')
            page.wait_for_selector('#popup_container', state='visible', timeout=5000)
            page.click('#popup_ok')
            time.sleep(0.5)

            row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{schedule_name}"))')
            assert row is None, f'Schedule "{schedule_name}" should be gone after delete'

        finally:

            # The connection goes away together with anything the test left behind
            _navigate_to_sftp(page, base_url)
            _delete_connection(page, conn_id)

        # No console or server errors along the way
        real_errors = [] # type: list

        for error_text in console_errors:
            if 'favicon.ico' in error_text or 'Content-Security-Policy' in error_text:
                continue
            real_errors.append(error_text)

        assert not real_errors, 'Console errors during the schedule cycle:\n' + '\n'.join(real_errors)
        assert not server_errors, 'HTTP 500+ responses during the schedule cycle:\n' + '\n'.join(server_errors)

# ################################################################################################################################
# ################################################################################################################################
