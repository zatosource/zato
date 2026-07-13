# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import urlparse

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, select_option_by_label, \
    set_select_value, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

AS4_Channel_Page_Url = '/zato/channel/as4/?cluster=1'

# Plain text and textarea fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'url_path', 'as4_from_party', 'as4_to_party', 'as4_service', 'as4_action',
    'as4_agreement', 'as4_mpc', 'as4_extra_pmodes',
    'as4_signing_key', 'as4_signing_cert_chain', 'as4_decryption_key', 'as4_peer_signing_cert',
    'as4_peer_encryption_cert', 'as4_trust_anchors',
    'as4_serviced_participants', 'as4_original_sender', 'as4_final_recipient',
    'service', 'as4_inbound_topic')

# Select fields set by raw value via JS
_Select_Fields = ('as4_profile',)

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active',)

# The forms are tabbed and a text field is only fillable while its tab is active
_Field_To_Tab = {
    'name': 'main',
    'url_path': 'main',
    'as4_from_party': 'main',
    'as4_to_party': 'main',
    'as4_service': 'main',
    'as4_action': 'main',
    'as4_agreement': 'main',
    'as4_mpc': 'main',
    'as4_extra_pmodes': 'main',
    'as4_signing_key': 'security',
    'as4_signing_cert_chain': 'security',
    'as4_decryption_key': 'security',
    'as4_peer_signing_cert': 'security',
    'as4_peer_encryption_cert': 'security',
    'as4_trust_anchors': 'security',
    'as4_serviced_participants': 'participants',
    'as4_original_sender': 'participants',
    'as4_final_recipient': 'participants',
    'service': 'routing',
    'as4_inbound_topic': 'routing',
}

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_as4_channel_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the AS4 channels page, optionally filtering by a query.
    """

    url_path = AS4_Channel_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_as4_channel_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an AS4 channel of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_as4_channel_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an AS4 channel with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_as4_channel_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an AS4 channel row identified by name.
    """

    row = find_as4_channel_row(page, name)
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

def fill_as4_channel_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the AS4 channel create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
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

    # .. the security select, selected by its visible label, e.g. "Basic Auth/My def" ..
    if 'security' in options:
        select_option_by_label(page, f'#id_{prefix}security_id', options['security'])

    # .. the security select, selected by its raw value, e.g. ZATO_NONE ..
    if 'security_value' in options:
        set_select_value(page, f'#id_{prefix}security_id', options['security_value'])

    # .. checkboxes, checked via JS so the state is set directly regardless of the slider styling ..
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
# Channel CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_as4_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    url_path:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an AS4 channel via the UI and returns its server-side ID.
    """

    # Navigate to the AS4 channels page ..
    open_as4_channel_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'url_path': url_path,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_as4_channel_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the channel's ID.
    _ = wait_for_as4_channel_row(page, name)

    out = get_as4_channel_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', channel_id:'str') -> 'None':
    """ Opens the edit dialog for an AS4 channel of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.channel.as4.edit("{channel_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_as4_channel(page:'Page', channel_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an AS4 channel, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, channel_id)

    # .. apply the changes ..
    fill_as4_channel_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_as4_channel(page:'Page', channel_id:'str') -> 'None':
    """ Deletes an AS4 channel via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the channels page first.
    if '/zato/channel/as4/' not in page.url:
        parsed_url = urlparse(page.url)
        open_as4_channel_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.channel.as4.delete_("{channel_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{channel_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
