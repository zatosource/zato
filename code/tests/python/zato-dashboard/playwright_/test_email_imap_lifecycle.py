# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.api import EMAIL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = EMAIL.IMAP.Scheduler

_Page_Url_Pattern = '/zato/email/imap/?cluster=1'
_Scheduler_Page_Url_Pattern = '/zato/scheduler/?cluster=1'

_Test_Name_Prefix = 'test.imap.' + CryptoManager.generate_hex_string(32) + '.'

_Invoked_Service = 'demo.ping'

# The default user profile displays dates as day-first
_Start_Date = '01-01-2099 00:00:00'

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str') -> 'None':
    """ Opens the IMAP connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', invoke_with:'str') -> 'None':
    """ Creates an IMAP connection with scheduler fields via the UI, using the given invoke-with mode.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the basic fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', 'imap-user@example.com')

    # .. expand the generic IMAP options and fill the host in ..
    page.click('#create-div a[href*="generic-imap-options-block"]')
    page.fill('#id_host', 'imap.example.com')

    # .. expand the scheduler options and fill them all in, including the invoke-with mode -
    # .. the service select is a chosen widget which hides the underlying select element
    # .. and the start date field has a datetimepicker attached which rewrites the field on focus,
    # .. hence both are set through jQuery, the same way the widgets themselves do it ..
    page.click('#create-div a[href*="scheduler-options-block"]')
    page.fill('#id_scheduler_run_every', '5')
    _ = page.select_option('#id_scheduler_run_unit', _scheduler.Unit.Minutes)
    _ = page.evaluate(f'$("#id_scheduler_start_date").val("{_Start_Date}")')
    _ = page.evaluate(f'$("#id_scheduler_service").val("{_Invoked_Service}").trigger("chosen:updated").trigger("change")')
    _ = page.select_option('#id_scheduler_invoke_with', invoke_with)

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

def _get_row_hidden_text(page:'Page', name:'str') -> 'str':
    """ Returns the full text of a row, including its hidden cells.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    out = row.text_content()

    return out

# ################################################################################################################################

def _open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.email.imap.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.email.imap.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _job_row_exists(page:'Page', base_url:'str', job_name:'str') -> 'bool':
    """ Returns True if the scheduler page shows a job of the given name.
    """
    _ = page.goto(f'{base_url}{_Scheduler_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    row = page.query_selector(f'#data-table tbody tr:has(td a:text-is("{job_name}"))')
    out = row is not None

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEmailIMAPLifecycle:
    """ Tests the IMAP connection lifecycle with scheduler fields, focusing on the invoke-with select.
    """

    def test_invoke_with_lifecycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Create with each-attachment, verify, switch to the message mode via edit, verify, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _navigate(page, base_url)

        # .. create a connection whose scheduler invokes the service once per attachment ..
        name = _Test_Name_Prefix + 'invoke-with'
        job_name = _scheduler.Job_Prefix + name

        _create_connection(page, name, _scheduler.InvokeWith.EachAttachment)

        # .. the row's hidden cells carry the each-attachment mode ..
        row_text = _get_row_hidden_text(page, name)
        assert _scheduler.InvokeWith.EachAttachment in row_text, f'Expected each-attachment mode in row, got: "{row_text}"'

        # .. a scheduler job was auto-created for the connection ..
        assert _job_row_exists(page, base_url, job_name), f'Job "{job_name}" should exist after create'

        # .. go back and open the edit dialog - the select must be pre-populated with the stored mode ..
        _navigate(page, base_url)
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        invoke_with_value = page.input_value('#id_edit-scheduler_invoke_with')
        assert invoke_with_value == _scheduler.InvokeWith.EachAttachment, \
            f'Expected the edit select to show each-attachment, got: "{invoke_with_value}"'

        # .. switch the mode to message and save - the scheduler options block is collapsed
        # .. by default so it needs to be expanded first for the select to be visible ..
        page.click('#edit-div a[href*="scheduler-options-block"]')
        _ = page.select_option('#id_edit-scheduler_invoke_with', _scheduler.InvokeWith.Message)
        _submit_edit_form(page)

        # .. the row now carries the message mode ..
        row_text = _get_row_hidden_text(page, name)
        assert _scheduler.InvokeWith.Message in row_text, f'Expected the message mode in row, got: "{row_text}"'

        # .. reopen the edit dialog to confirm the new mode was stored ..
        _open_edit_dialog(page, item_id)

        invoke_with_value = page.input_value('#id_edit-scheduler_invoke_with')
        assert invoke_with_value == _scheduler.InvokeWith.Message, \
            f'Expected the edit select to show the message mode, got: "{invoke_with_value}"'

        page.click('#edit-div button:has-text("Cancel")')
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

        # .. delete the connection ..
        _delete_connection(page, item_id)

        # .. verify the row is gone ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is None, f'Row "{name}" should be gone after delete'

        # .. and the linked job is gone too.
        assert not _job_row_exists(page, base_url, job_name), f'Job "{job_name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
