# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.common.api import FileTransfer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strdict

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

# The tab of the step of the wizard that is shown, whose data-step attribute is the index of the step
_Active_Step_Selector = '#file-transfer-wizard-steps .wizard-step-active'

# The prefix of the identifier of each input of a micro-form, followed by the name of its field
_Micro_Form_Input_Prefix = '#file-transfer-wizard-tippy-'

# The button that closes a micro-form and keeps what was entered in it
_Micro_Form_OK = '.micro-form-buttons button:has-text("OK")'

# The labels of the segments that the readiness check and the post-processing are picked with, by their modes
_Ready_Labels = {
    FileTransfer.Scheduler.ReadyHow.Stability: 'Stable size',
    FileTransfer.Scheduler.ReadyHow.Marker:    'Marker file',
}

_Success_Labels = {
    FileTransfer.Scheduler.OnSuccess.Move:   'Move',
    FileTransfer.Scheduler.OnSuccess.Delete: 'Delete',
}

# The field of a schedule that the micro-form of each readiness check and of each kind of post-processing asks for,
# empty if there is no such micro-form
_Ready_Fields = {
    FileTransfer.Scheduler.ReadyHow.Stability: 'stability_delay',
    FileTransfer.Scheduler.ReadyHow.Marker:    'marker_suffix',
}

_Success_Fields = {
    FileTransfer.Scheduler.OnSuccess.Move:   'move_directory',
    FileTransfer.Scheduler.OnSuccess.Delete: '',
}

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
    """ Moves the wizard to its next step and waits until that step is shown.
    """
    current_step = cast_('str', page.get_attribute(_Active_Step_Selector, 'data-step'))
    next_step = int(current_step) + 1

    page.click('#file-transfer-wizard-next')
    _ = page.wait_for_selector(f'{_Active_Step_Selector}[data-step="{next_step}"]', state='visible', timeout=_Dialog_Timeout)

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

def _pick_segment(page:'Page', slot_id:'str', label:'str') -> 'None':
    page.click(f'#{slot_id} .decision-segment:text-is("{label}")')

# ################################################################################################################################

def _fill_micro_form(page:'Page', link_id:'str', values:'strdict') -> 'None':
    """ Opens the micro-form of an edit link, enters each value in the input of its field and closes the micro-form.
    """
    page.click(f'#{link_id}')

    # Each input is waited for, so the micro-form is open before the first value is entered ..
    for field, value in values.items():
        selector = _Micro_Form_Input_Prefix + field
        _ = page.wait_for_selector(selector, state='visible', timeout=_Dialog_Timeout)
        page.fill(selector, value)

    # .. and the micro-form is gone once OK keeps what was entered in it.
    page.click(_Micro_Form_OK)
    for field in values:
        selector = _Micro_Form_Input_Prefix + field
        _ = page.wait_for_selector(selector, state='detached', timeout=_Dialog_Timeout)

# ################################################################################################################################

def fill_schedule_wizard(page:'Page', schedule:'anydict', start_date:'str') -> 'None':
    """ Enters a schedule, in the form an enmasse file defines one in, in each step of the open wizard and saves it.
    The start date is in the format of the date fields of the Dashboard.
    """

    # The first step names the files and how they are recognized as complete ..
    page.fill('#id_name', schedule['name'])
    page.fill('#id_directory', schedule['directory'])
    page.fill('#id_pattern', schedule['pattern'])

    ready_how = schedule['ready_how']
    ready_label = _Ready_Labels[ready_how]
    ready_field = _Ready_Fields[ready_how]
    ready_value = str(schedule[ready_field])

    _pick_segment(page, 'file-transfer-wizard-slot-ready', ready_label)
    _fill_micro_form(page, 'file-transfer-wizard-edit-ready', {ready_field: ready_value})

    page.set_checked('#id_should_claim', schedule['should_claim'])

    wizard_next(page)

    # .. the second one names the service and what becomes of each file ..
    fill_service(page, schedule['service'])

    on_success = schedule['on_success']
    success_label = _Success_Labels[on_success]
    success_field = _Success_Fields[on_success]

    _pick_segment(page, 'file-transfer-wizard-slot-success', success_label)

    if success_field:
        success_value = schedule[success_field]
        _fill_micro_form(page, 'file-transfer-wizard-edit-success', {success_field: success_value})

    max_attempts = str(schedule['max_attempts'])
    retry_backoff = str(schedule['retry_backoff'])
    retries = {
        'max_attempts': max_attempts,
        'retry_backoff': retry_backoff,
        'quarantine_directory': schedule['quarantine_directory'],
    }
    _fill_micro_form(page, 'file-transfer-wizard-edit-retries', retries)

    # .. and when it polls.
    run_every = str(schedule['run_every'])
    fill_run_every(page, run_every, schedule['run_unit'])

    _ = page.evaluate(f'$("#id_start_date").val("{start_date}")')

    # A create is saved from the review step, an edit from the step it is on.
    if not page.is_visible('#file-transfer-wizard-save'):
        wizard_next(page)

    wizard_save(page)

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
