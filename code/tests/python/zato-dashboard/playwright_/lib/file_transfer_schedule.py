# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time

# Zato
from zato.common.api import FileTransfer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The invoice totals fixture service appends every invoice it processes to this file - the same path the service itself uses.
Invoice_Totals_Path = '/tmp/zato-test-file-transfer-invoice-totals.jsonl'

# Name of the boot-deployed fixture service that adds up the amounts of each invoice
Invoice_Totals_Service = 'test.file-transfer.invoice-totals'

# The unit a schedule's interval is counted in, unless a test picks another one
Default_Run_Unit = FileTransfer.Scheduler.Unit.Minutes

# Where a save that went through lands - the schedules list, pointed at the saved row
_Saved_Redirect_Pattern = '**/zato/outgoing/file-transfer/schedules/**highlight=*'

# The row the list marks as the one just saved
_Highlighted_Row_Selector = '#data-table tbody tr.updated'

# How long to wait for a dialog, a popup or a wizard element, in milliseconds
_Dialog_Timeout = 5000

# How long to wait for a save to complete, in milliseconds
_Submit_Timeout = 10000

# How long to let the wizard move between steps, in seconds
_Step_Sleep_Time = 0.2

# ################################################################################################################################
# ################################################################################################################################
#
# The schedule wizard
#
# ################################################################################################################################
# ################################################################################################################################

def open_schedules(page:'Page', conn_name:'str') -> 'None':
    """ Clicks the Scheduler link of a connection's row and waits for the schedules list page.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{conn_name}"))'
    page.click(f'{row_selector} a[href*="/file-transfer/schedules/"]')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def open_create_wizard(page:'Page') -> 'None':
    page.click('#markup .page_prompt a:has-text("Create a new schedule")')
    _ = page.wait_for_selector('#file-transfer-wizard', state='visible')

# ################################################################################################################################

def wizard_next(page:'Page') -> 'None':
    page.click('#file-transfer-wizard-next')
    time.sleep(_Step_Sleep_Time)

# ################################################################################################################################

def wizard_save(page:'Page') -> 'None':
    """ Saves from the button the current action ends in - Save on an edit, the last Next
    on a create - and waits for the redirect a save that went through makes, to the schedules
    list with the saved row highlighted.
    """
    if page.is_visible('#file-transfer-wizard-save'):
        page.click('#file-transfer-wizard-save')
    else:
        page.click('#file-transfer-wizard-next')

    _ = page.wait_for_url(_Saved_Redirect_Pattern, timeout=_Submit_Timeout)
    _ = page.wait_for_selector('#data-table', state='visible')
    _ = page.wait_for_selector(_Highlighted_Row_Selector, state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def fill_service(page:'Page', service_name:'str') -> 'None':
    """ Picks the schedule's target service.
    """
    _ = page.evaluate(f'$("#id_scheduler_service").val("{service_name}").trigger("chosen:updated")')

# ################################################################################################################################

def fill_run_every(page:'Page', run_every:'str', run_unit:'str'=Default_Run_Unit) -> 'None':
    """ Sets the schedule's interval and the unit it is counted in.
    """
    page.click('#file-transfer-wizard-edit-run-every')
    _ = page.wait_for_selector('#file-transfer-wizard-tippy-run_every', state='visible', timeout=_Dialog_Timeout)

    page.fill('#file-transfer-wizard-tippy-run_every', run_every)
    _ = page.select_option('#file-transfer-wizard-tippy-run_unit', run_unit)

    page.click('.micro-form-buttons button:has-text("OK")')
    _ = page.wait_for_selector('#file-transfer-wizard-tippy-run_every', state='detached', timeout=_Dialog_Timeout)

# ################################################################################################################################
# ################################################################################################################################
#
# The invoice totals
#
# ################################################################################################################################
# ################################################################################################################################

def read_invoice_totals() -> 'anydict':
    """ Returns every result of the invoice totals service, by the name of the file it was computed for.
    """
    out:'anydict' = {}

    # Nothing was processed yet ..
    if not os.path.exists(Invoice_Totals_Path):
        return out

    # .. otherwise, each line is one processed invoice.
    with open(Invoice_Totals_Path) as totals_file:
        for line in totals_file:
            result = json.loads(line)
            file_name = result['file_name']
            out[file_name] = result

    return out

# ################################################################################################################################
# ################################################################################################################################
