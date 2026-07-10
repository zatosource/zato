# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

AS2_Outconn_Page_Url = '/zato/outgoing/as2/?cluster=1&type_=outconn-as2'

# Plain text and textarea fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'endpoint_url', 'as2_from', 'as2_to', 'subject',
    'isa_qualifier', 'isa_id', 'gs_id', 'unb_id', 'inbound_topic', 'inbound_service',
    'async_mdn_url',
    'as2_partner_cert', 'as2_partner_next_cert', 'as2_partner_next_cert_from',
    'as2_peer_signing_cert', 'as2_peer_encryption_cert', 'as2_trust_anchors',
    'as2_signing_key', 'as2_signing_cert_chain', 'as2_decryption_key',
    'as2_next_decryption_key', 'as2_next_decryption_cert',
    'username', 'http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries',
    'pool_size')

# Select fields set by raw value via JS
_Select_Fields = ('content_type', 'sign_algorithm', 'encryption_algorithm', 'mdn_mode',
    'http_transfer_mode', 'as2_version', 'content_transfer_encoding')

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'sign', 'encrypt', 'compress', 'compress_before_signing', 'mdn_signed',
    'preserve_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', 'warn_on_duplicate_filename')

# The forms are tabbed and a text field is only fillable while its tab is active
_Field_To_Tab = {
    'name': 'main',
    'endpoint_url': 'main',
    'as2_from': 'main',
    'as2_to': 'main',
    'subject': 'main',
    'isa_qualifier': 'edi',
    'isa_id': 'edi',
    'gs_id': 'edi',
    'unb_id': 'edi',
    'inbound_topic': 'edi',
    'inbound_service': 'edi',
    'async_mdn_url': 'security',
    'as2_partner_cert': 'partner',
    'as2_partner_next_cert': 'partner',
    'as2_partner_next_cert_from': 'partner',
    'as2_peer_signing_cert': 'partner',
    'as2_peer_encryption_cert': 'partner',
    'as2_trust_anchors': 'partner',
    'as2_signing_key': 'keys',
    'as2_signing_cert_chain': 'keys',
    'as2_decryption_key': 'keys',
    'as2_next_decryption_key': 'keys',
    'as2_next_decryption_cert': 'keys',
    'username': 'delivery',
    'http_timeout_seconds': 'delivery',
    'chunked_threshold_bytes': 'delivery',
    'ack_overdue_after': 'delivery',
    'resend_max_retries': 'delivery',
    'pool_size': 'more',
}

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_as2_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing AS2 connections page, optionally filtering by a query.
    """

    url_path = AS2_Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_as2_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an outgoing AS2 connection of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_as2_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing AS2 connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_as2_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing AS2 connection row identified by name.
    """

    row = find_as2_outconn_row(page, name)
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

def fill_as2_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing AS2 connection create or edit form. An empty prefix means
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

    # .. selects set by raw value ..
    for field_name in _Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. checkboxes, checked via JS because toggle-switch styling covers the inputs ..
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
# Outgoing connection CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_as2_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    endpoint_url:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing AS2 connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing AS2 connections page ..
    open_as2_outconn_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'endpoint_url': endpoint_url,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_as2_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_as2_outconn_row(page, name)

    out = get_as2_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing AS2 connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.outgoing.as2.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_as2_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing AS2 connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_as2_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_as2_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing AS2 connection via the UI confirmation dialog.
    """

    # The page may be somewhere else, so go back to the connections page first.
    if '/zato/outgoing/as2/' not in page.url:
        parsed_url = urlparse(page.url)
        open_as2_outconn_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.outgoing.as2.delete_("{outconn_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
