# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test.playwright_pubsub import set_select_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

FHIR_Page_Url = '/zato/outgoing/hl7/fhir/?cluster=1'

# How long to wait for a dialog to appear or a row to show up, in milliseconds
_Dialog_Timeout = 5000

# How long to wait for a submitted form to close its dialog, in milliseconds
_Submit_Timeout = 10000

# How long to let the dashboard settle after a form was submitted, in seconds
_Settle_Sleep_Time = 0.3

# How long to let the dashboard settle after a connection was deleted, in seconds
_Delete_Sleep_Time = 0.5

# ################################################################################################################################
# ################################################################################################################################

def row_selector(name:'str') -> 'str':
    """ Returns the selector matching the table row of a connection of the given name.
    """
    out = f'#data-table tbody tr:has(td:text-is("{name}"))'
    return out

# ################################################################################################################################

def open_fhir_page(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing FHIR page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{FHIR_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def open_create_dialog(page:'Page') -> 'None':
    """ Opens the create dialog of the page.
    """
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def create_fhir_connection(page:'Page', name:'str', address:'str', *, is_audit_log_active:'bool'=True) -> 'None':
    """ Creates an outgoing FHIR connection via the UI, with no security definition.
    """

    # Open the create dialog ..
    open_create_dialog(page)

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    set_select_value(page, '#id_security_id', ZATO_NONE)
    page.set_checked('#id_is_audit_log_active', is_audit_log_active)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Submit_Timeout)

    # .. and wait for the row to appear.
    row = row_selector(name)
    _ = page.wait_for_selector(row, state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def get_fhir_conn_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    selector = row_selector(name)
    row = page.query_selector(selector)
    assert row is not None, f'No row for connection "{name}"'

    id_cell = row.query_selector('td[class*="item_id_"]')
    assert id_cell is not None, f'No ID cell in the row of connection "{name}"'

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def get_audit_log_cell_text(page:'Page', name:'str') -> 'str':
    """ The visible text of the row's Audit log cell - the link alone when the log is on, with `(off)` after it otherwise.
    """
    selector = row_selector(name)
    row = page.query_selector(selector)
    assert row is not None, f'No row for connection "{name}"'

    cell = row.query_selector('td:has(a[href*="/zato/audit-log/"])')
    assert cell is not None, f'No Audit log cell in the row of connection "{name}"'

    out = cell.inner_text().strip()
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    """ Opens the edit dialog of a connection of the given ID.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.hl7.fhir.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def submit_edit_form(page:'Page') -> 'None':
    """ Submits the edit dialog and waits for it to close.
    """
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Submit_Timeout)
    time.sleep(_Settle_Sleep_Time)

# ################################################################################################################################

def set_audit_log_active(page:'Page', item_id:'str', is_active:'bool') -> 'None':
    """ Opens the edit dialog of a connection, sets its audit log checkbox and submits.
    """
    open_edit_dialog(page, item_id)
    page.set_checked('#id_edit-is_audit_log_active', is_active)
    submit_edit_form(page)

# ################################################################################################################################

def delete_fhir_connection(page:'Page', item_id:'str') -> 'None':
    """ Deletes a connection of the given ID through the UI confirmation dialog.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.hl7.fhir.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Dialog_Timeout)
    page.click('#popup_ok')
    time.sleep(_Delete_Sleep_Time)

# ################################################################################################################################
# ################################################################################################################################
