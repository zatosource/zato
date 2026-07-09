# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import urlparse

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The type_ parameter is required for the page to list its connections,
# the same way the dashboard's own menu links carry it.
IBM_MQ_Outconn_Page_Url = '/zato/outgoing/ibm-mq/?cluster=1&type_=outconn-ibm-mq'

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'address', 'queue_manager', 'mq_channel_name', 'queue',
    'username', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file')

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'ssl')

# The forms are tabbed and a text field is only fillable while its tab is active
_Field_To_Tab = {
    'name': 'basic',
    'address': 'basic',
    'queue_manager': 'basic',
    'mq_channel_name': 'basic',
    'queue': 'basic',
    'username': 'security',
    'cipher_spec': 'security',
    'ssl_ca_file': 'security',
    'ssl_cert_file': 'security',
    'ssl_key_file': 'security',
}

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_ibm_mq_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing IBM MQ connections page, optionally filtering by a query.
    """

    url_path = IBM_MQ_Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_ibm_mq_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an outgoing IBM MQ connection of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_ibm_mq_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing IBM MQ connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_ibm_mq_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing IBM MQ connection row identified by name.
    """

    row = find_ibm_mq_outconn_row(page, name)
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

def fill_ibm_mq_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing IBM MQ connection create or edit form. An empty prefix means
    the create form, the 'edit-' prefix means the edit form. Only the fields present
    in options are touched.
    """

    # Plain text inputs, switching to the tab each field lives on; the first field
    # always clicks its tab so the form's current tab does not matter ..
    current_tab = None

    for field_name in _Text_Fields:
        if field_name in options:

            field_tab = _Field_To_Tab[field_name]
            if field_tab != current_tab:
                _activate_tab(page, prefix, field_tab)
                current_tab = field_tab

            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. checkboxes, checked via JS because toggle-switch styling covers the inputs ..
    for field_name in _Checkbox_Fields:
        if field_name in options:
            checked = 'true' if options[field_name] else 'false'
            page.evaluate(f'$("#id_{prefix}{field_name}").prop("checked", {checked})')

    # .. and the form goes back to its first tab so the submit flow always starts from the same place.
    if current_tab not in (None, 'basic'):
        _activate_tab(page, prefix, 'basic')

# ################################################################################################################################
# ################################################################################################################################
#
# Outgoing connection CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_ibm_mq_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing IBM MQ connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing IBM MQ connections page ..
    open_ibm_mq_outconn_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_ibm_mq_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_ibm_mq_outconn_row(page, name)

    out = get_ibm_mq_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing IBM MQ connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.outgoing.ibm_mq.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_ibm_mq_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing IBM MQ connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_ibm_mq_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def change_ibm_mq_outconn_password(page:'Page', outconn_id:'str', password:'str') -> 'None':
    """ Sets the password of an outgoing IBM MQ connection through the change password dialog.
    """

    # Open the dialog ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{outconn_id}")')
    _ = page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    # .. fill in the password and submit ..
    page.fill('#change_password-div #id_password', password)
    page.click('#change_password-div input[type="submit"]')

    # .. and wait for the dialog to close.
    _ = page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

# ################################################################################################################################

def delete_ibm_mq_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing IBM MQ connection via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the connections page first.
    if '/zato/outgoing/ibm-mq/' not in page.url:
        parsed_url = urlparse(page.url)
        open_ibm_mq_outconn_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.outgoing.ibm_mq.delete_("{outconn_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
