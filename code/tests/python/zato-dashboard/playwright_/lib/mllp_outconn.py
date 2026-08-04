# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

# The list page these helpers start from
Outgoing_Page_Url = '/zato/outgoing/hl7/mllp/?cluster=1&type_=outconn-hl7-mllp'

# The wizard creating and editing a connection - every element on the page derives its id
# from this one, so the selectors below are built out of it rather than spelled out
Wizard_Id = 'mllp-outconn-wizard'

# What the wizard calls the inputs of its popover micro-forms, the field name completing it
Popover_Input_Prefix = f'{Wizard_Id}-tippy-'

# The popover itself, and the button that writes its answers back and closes it
Popover_Selector = f'#{Wizard_Id}-popup'
Popover_Ok_Selector = f'#{Wizard_Id}-popup .wizard-tippy-buttons .action-button'

# What a save that went through says beside the button it was asked for through
Saved_Tippy_Selector = '.tippy-box:has-text("OK, saved")'

# How long the wizard is given to open, to save and to land back on the list
_Wizard_Timeout = 10000

# How long a row is given to appear on the list page after a save
_Row_Timeout = 5000

# How long the confirmation dialog of a delete is given to appear
_Confirm_Timeout = 5000

# How long a popover is given to settle once it has been asked to open or close - tippy
# fades them in and out rather than swapping them in place
_Popover_Settle_Seconds = 0.3

# How long a delete is given to reach the server before the page is read again
_Delete_Settle_Seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

def navigate_to_outgoing(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing HL7 MLLP connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{Outgoing_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    assert row is not None, f'No row for "{name}" on the list page'

    id_cell = row.query_selector('td[class*="item_id_"]')
    assert id_cell is not None, f'No id cell in the row of "{name}"'

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

def open_create_wizard(page:'Page', base_url:'str') -> 'None':
    """ Opens the wizard on a new connection, the way a person does - from the list page.
    """
    navigate_to_outgoing(page, base_url)

    page.click('#markup .page_prompt a:has-text("Create a new connection")')
    _ = page.wait_for_selector(f'#{Wizard_Id}', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def open_edit_wizard(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Opens the wizard on the connection of that name, from its row's Edit link.
    """
    navigate_to_outgoing(page, base_url)

    page.click(f'#data-table tbody tr:has(td:text-is("{name}")) a:text-is("Edit")')
    _ = page.wait_for_selector(f'#{Wizard_Id}', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def open_popover(page:'Page', link_name:'str') -> 'None':
    """ Opens one of the wizard's popover micro-forms through the summary link that
    stands for it, e.g. framing, timing or retries.
    """
    page.click(f'#{Wizard_Id}-edit-{link_name}')
    _ = page.wait_for_selector(Popover_Selector, state='visible', timeout=_Wizard_Timeout)

    # The popover fades in, and typing into an input still on its way is typing into nothing
    time.sleep(_Popover_Settle_Seconds)

# ################################################################################################################################

def close_popover(page:'Page') -> 'None':
    """ Presses OK, which is what writes a popover's answers back into the form.
    """
    page.click(Popover_Ok_Selector)
    _ = page.wait_for_selector(Popover_Selector, state='detached', timeout=_Wizard_Timeout)

    time.sleep(_Popover_Settle_Seconds)

# ################################################################################################################################

def set_in_popover(page:'Page', link_name:'str', field_name:'str', value:'str') -> 'None':
    """ Opens the popover behind one summary link, replaces one of its answers and presses OK.
    """
    open_popover(page, link_name)
    page.fill(f'#{Popover_Input_Prefix}{field_name}', value)
    close_popover(page)

# ################################################################################################################################

def go_to_step(page:'Page', step_index:'int') -> 'None':
    """ Jumps to one step of the wizard through its tab in the step strip.
    """
    page.click(f'#{Wizard_Id}-steps .wizard-step[data-step="{step_index}"]')
    _ = page.wait_for_selector(f'#{Wizard_Id}-step-body-{step_index}', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def finish_wizard(page:'Page', name:'str') -> 'None':
    """ Saves through the button the action ends in, waits for the tooltip saying the save
    went through and then closes the form, a save leaving open the page it was made on. The
    list page it goes back to carries the connection's own row.
    """
    # An edit is saved from the step it stands on, a create from the end of its walk
    if page.is_visible(f'#{Wizard_Id}-save'):
        page.click(f'#{Wizard_Id}-save')

    else:
        go_to_step(page, 2)
        page.click(f'#{Wizard_Id}-next')

    _ = page.wait_for_selector(Saved_Tippy_Selector, timeout=_Wizard_Timeout)

    page.click(f'#{Wizard_Id}-cancel')
    page.wait_for_url('**/zato/outgoing/hl7/mllp/**', timeout=_Wizard_Timeout)

    _ = page.wait_for_selector('#data-table', state='visible')
    _ = page.wait_for_selector(f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=_Row_Timeout)

# ################################################################################################################################
# ################################################################################################################################

def create_outgoing_connection(page:'Page', base_url:'str', name:'str', address:'str', recv_timeout_ms:'int'=0) -> 'None':
    """ Creates an outgoing MLLP connection through the wizard, the way a person does.
    A receive timeout in milliseconds replaces the form's default when the receiver
    the connection points at is a slow one.
    """
    open_create_wizard(page, base_url)

    page.fill('#id_name', name)
    page.fill('#id_address', address)

    # The timeout lives behind the timing popover, which is where it is changed
    if recv_timeout_ms:
        set_in_popover(page, 'timing', 'recv_timeout', str(recv_timeout_ms))

    finish_wizard(page, name)

# ################################################################################################################################

def delete_outgoing_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes an outgoing MLLP connection through its own page.
    """
    navigate_to_outgoing(page, base_url)

    item_id = get_item_id(page, name)

    page.evaluate(f'$.fn.zato.outgoing.hl7.mllp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Confirm_Timeout)
    page.click('#popup_ok')
    time.sleep(_Delete_Settle_Seconds)

# ################################################################################################################################
# ################################################################################################################################
