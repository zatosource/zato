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

# The list of outgoing FTP connections
FTP_Page_Url = '/zato/outgoing/ftp/?cluster=1&type_=outconn-ftp'

# How long to wait for a dialog to open, in milliseconds
_Dialog_Timeout = 5000

# How long to wait for a dialog to close once its form was submitted, in milliseconds
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

def open_ftp_page(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing FTP page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{FTP_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def create_ftp_connection(
    page:'Page',
    name:'str',
    host:'str',
    port:'int',
    username:'str',
    password:'str',
    use_ssl:'bool' = False,
    ) -> 'None':
    """ Creates an outgoing FTP connection via the UI.
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

    # .. turn on TLS if requested ..
    if use_ssl:
        page.click('#id_use_ssl')

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Submit_Timeout)

    # .. and wait for the row to appear.
    row = row_selector(name)
    _ = page.wait_for_selector(row, state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def get_ftp_conn_id(page:'Page', name:'str') -> 'str':
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

def open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    """ Opens the edit dialog of a connection of the given ID.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.ftp.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def submit_edit_form(page:'Page') -> 'None':
    """ Submits the edit dialog and waits for it to close.
    """
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Submit_Timeout)
    time.sleep(_Settle_Sleep_Time)

# ################################################################################################################################

def delete_ftp_connection(page:'Page', item_id:'str') -> 'None':
    """ Deletes a connection of the given ID through the UI confirmation dialog.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.ftp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Dialog_Timeout)
    page.click('#popup_ok')
    time.sleep(_Delete_Sleep_Time)

# ################################################################################################################################
# ################################################################################################################################
