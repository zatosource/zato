# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from urllib.parse import urlparse

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, set_select_value, \
    submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

WSS_Page_Url = '/zato/security/wss/?cluster=1'

# Plain text and textarea fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'username', 'issuer', 'subject', 'audience', 'signing_key', 'signing_certificate_chain',
    'decryption_key', 'peer_certificate', 'trust_anchors')

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'use_digest', 'sign', 'encrypt')

# The forms are tabbed and a field is only fillable while its tab is active
_Field_To_Tab = {
    'name': 'main',
    'username': 'main',
    'issuer': 'saml',
    'subject': 'saml',
    'audience': 'saml',
    'signing_key': 'crypto',
    'signing_certificate_chain': 'crypto',
    'decryption_key': 'crypto',
    'peer_certificate': 'crypto',
    'trust_anchors': 'crypto',
}

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_wss_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the WS-Security definitions page, optionally filtering by a query.
    """

    url_path = WSS_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_wss_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of a WS-Security definition of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_wss_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of a WS-Security definition with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_wss_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of a WS-Security definition row identified by name.
    """

    row = find_wss_row(page, name)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.text_content().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Form filling
#
# ################################################################################################################################
# ################################################################################################################################

def _activate_tab(page:'Page', prefix:'str', tab_name:'str') -> 'None':
    """ Clicks a tab header in the create or edit dialog so the tab's fields become visible.
    """
    container = '#edit-div' if prefix else '#create-div'
    page.click(f'{container} .dashboard-tab[data-tab="{tab_name}"]')

# ################################################################################################################################

def fill_wss_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the WS-Security create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
    """

    # The mode select drives which tabs are visible, so it goes first ..
    if 'mode' in options:
        set_select_value(page, f'#id_{prefix}mode', options['mode'])

    # .. plain text inputs and textareas, switching to the tab each field lives on;
    # the first field always clicks its tab so the form's current tab does not matter ..
    current_tab = None

    for field_name in _Text_Fields:
        if field_name in options:

            field_tab = _Field_To_Tab[field_name]
            if field_tab != current_tab:
                _activate_tab(page, prefix, field_tab)
                current_tab = field_tab

            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. checkboxes are checked via JS because toggle-switch styling covers the inputs ..
    for field_name in _Checkbox_Fields:
        if field_name in options:
            checked = 'true' if options[field_name] else 'false'
            page.evaluate(f'$("#id_{prefix}{field_name}").prop("checked", {checked})')

    # .. and the form goes back to its first tab so the submit flow always starts from the same place.
    if current_tab not in (None, 'main'):
        _activate_tab(page, prefix, 'main')

# ################################################################################################################################
# ################################################################################################################################
#
# WS-Security definition CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_wss_definition(
    page:'Page',
    base_url:'str',
    name:'str',
    username:'str',
    mode:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates a WS-Security definition via the UI and returns its server-side ID.
    """

    # Navigate to the WS-Security page ..
    open_wss_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'username': username,
        'mode': mode,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_wss_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the definition's ID.
    _ = wait_for_wss_row(page, name)

    out = get_wss_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', wss_id:'str') -> 'None':
    """ Opens the edit dialog for a WS-Security definition of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.security.wss.edit("{wss_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_wss_definition(page:'Page', wss_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for a WS-Security definition, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, wss_id)

    # .. apply the changes ..
    fill_wss_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_wss_definition(page:'Page', wss_id:'str') -> 'None':
    """ Deletes a WS-Security definition via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the definitions page first.
    if '/zato/security/wss/' not in page.url:
        parsed_url = urlparse(page.url)
        open_wss_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.security.wss.delete_("{wss_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{wss_id}', state='detached', timeout=5000)

# ################################################################################################################################

def change_wss_password(page:'Page', wss_id:'str', password:'str') -> 'None':
    """ Changes the password of a WS-Security definition via the change-password dialog.
    """

    # Open the dialog ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{wss_id}")')
    _ = page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    # .. type the password in ..
    page.fill('#change_password-div #id_password', password)

    # .. submit and wait for the dialog to close.
    page.click('#change_password-div input[type="submit"]')
    _ = page.wait_for_selector('#change_password-div', state='hidden', timeout=10000)

# ################################################################################################################################
# ################################################################################################################################
