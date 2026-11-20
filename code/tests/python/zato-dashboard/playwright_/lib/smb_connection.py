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

# The list of outgoing SMB connections, relative to the address of the Dashboard
Page_Url = '/zato/outgoing/smb/?type_=outconn-smb'

# How long to wait for a dialog to open or for a row to appear, in milliseconds
_Dialog_Timeout = 5000

# How long to wait for a form to be submitted, in milliseconds
_Submit_Timeout = 10000

# How long to let the list refresh after an edit and after a delete, in seconds
_Edit_Sleep_Time = 0.3
_Delete_Sleep_Time = 0.5

# ################################################################################################################################
# ################################################################################################################################

def row_selector(name:'str') -> 'str':
    out = f'#data-table tbody tr:has(td:text-is("{name}"))'
    return out

# ################################################################################################################################

def navigate_to_list(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the outgoing SMB page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{Page_Url}{url_suffix}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def create_connection(page:'Page', name:'str', host:'str', port:'int', username:'str', password:'str') -> 'None':
    """ Creates an outgoing SMB connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_host', host)
    page.fill('#id_port', str(port))
    page.fill('#id_username', username)
    page.fill('#id_secret', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Submit_Timeout)

    # .. and wait for the row to appear.
    selector = row_selector(name)
    _ = page.wait_for_selector(selector, state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    selector = row_selector(name)
    id_cell = page.locator(f'{selector} td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    _ = page.evaluate(f'$.fn.zato.outgoing.smb.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Submit_Timeout)
    time.sleep(_Edit_Sleep_Time)

# ################################################################################################################################

def edit_connection(page:'Page', item_id:'str', host:'str', port:'int', username:'str', password:'str') -> 'None':
    """ Changes the address and the credentials of an outgoing SMB connection via the UI.
    An empty password keeps the one that the connection has.
    """
    open_edit_dialog(page, item_id)

    page.fill('#id_edit-host', host)
    page.fill('#id_edit-port', str(port))
    page.fill('#id_edit-username', username)
    page.fill('#id_edit-secret', password)

    submit_edit_form(page)

# ################################################################################################################################

def delete_connection(page:'Page', item_id:'str') -> 'None':
    _ = page.evaluate(f'$.fn.zato.outgoing.smb.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Dialog_Timeout)
    page.click('#popup_ok')
    time.sleep(_Delete_Sleep_Time)

# ################################################################################################################################
# ################################################################################################################################
