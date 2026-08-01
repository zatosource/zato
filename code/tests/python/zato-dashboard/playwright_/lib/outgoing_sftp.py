# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import subprocess
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The list of outgoing SFTP connections
Sftp_Page_Url = '/zato/outgoing/sftp/?cluster=1&type_=outconn-sftp'

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

def open_sftp_page(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the outgoing SFTP page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{Sftp_Page_Url}{url_suffix}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def create_sftp_connection(
    page:'Page',
    name:'str',
    address:'str',
    username:'str',
    password:'str',
    private_key:'str'='',
    strict_host_key_checking:'bool'=True,
    ignore_host_key_changes:'bool'=False,
    ) -> 'None':
    """ Creates an outgoing SFTP connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    page.fill('#id_username', username)
    page.fill('#id_secret', password)
    page.fill('#id_private_key', private_key)

    # .. the slider is on by default, which means it only ever needs to be clicked to turn it off ..
    if not strict_host_key_checking:
        page.click('#id_strict_host_key_checking')

    # .. this one is off by default, so it is the other way round ..
    if ignore_host_key_changes:
        page.click('#id_ignore_host_key_changes')

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Submit_Timeout)

    # .. and wait for the row to appear.
    _ = page.wait_for_selector(row_selector(name), state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def get_sftp_conn_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row = page.query_selector(row_selector(name))
    assert row is not None, f'No row for connection "{name}"'

    id_cell = row.query_selector('td[class*="item_id_"]')
    assert id_cell is not None, f'No ID cell in the row of connection "{name}"'

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    """ Opens the edit dialog of a connection of the given ID.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.sftp.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def submit_edit_form(page:'Page') -> 'None':
    """ Submits the edit dialog and waits for it to close.
    """
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Submit_Timeout)
    time.sleep(_Settle_Sleep_Time)

# ################################################################################################################################

def delete_sftp_connection(page:'Page', item_id:'str') -> 'None':
    """ Deletes a connection of the given ID through the UI confirmation dialog.
    """
    _ = page.evaluate(f'$.fn.zato.outgoing.sftp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Dialog_Timeout)
    page.click('#popup_ok')
    time.sleep(_Delete_Sleep_Time)

# ################################################################################################################################

def forget_host_key(host:'str', port:'int') -> 'None':
    """ Removes the given host and port from the user's known_hosts file. The zato server reaches
    the test SSH server through the real sftp binary, and because the test server's port may have
    been used by an earlier test run with a different key, any recorded entry must go away first.
    """
    _ = subprocess.run(['ssh-keygen', '-R', f'[{host}]:{port}'], capture_output=True)

# ################################################################################################################################
# ################################################################################################################################
