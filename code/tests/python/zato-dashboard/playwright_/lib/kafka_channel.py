# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import urlparse

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, set_select_value, submit_create_form, \
    submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The type_ parameter is required for the page to list its connections,
# the same way the dashboard's own menu links carry it.
Kafka_Channel_Page_Url = '/zato/channel/kafka/?cluster=1&type_=channel-kafka'

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'address', 'topic', 'group_id', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file')

# Select fields set by raw value via JS since Chosen.js hides the underlying elements
_Select_Fields = ('service',)

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'ssl')

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_kafka_channel_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the Kafka channels page, optionally filtering by a query.
    """

    url_path = Kafka_Channel_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_kafka_channel_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of a Kafka channel of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_kafka_channel_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of a Kafka channel with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_kafka_channel_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of a Kafka channel row identified by name.
    """

    row = find_kafka_channel_row(page, name)
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

def fill_kafka_channel_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the Kafka channel create or edit form. An empty prefix means
    the create form, the 'edit-' prefix means the edit form. Only the fields present
    in options are touched.
    """

    # Plain text inputs ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. selects, set via JS because Chosen.js hides the underlying select elements ..
    for field_name in _Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. and checkboxes, checked via JS so the state is set directly regardless of the slider styling.
    for field_name in _Checkbox_Fields:
        if field_name in options:
            checked = 'true' if options[field_name] else 'false'
            page.evaluate(f'$("#id_{prefix}{field_name}").prop("checked", {checked})')

# ################################################################################################################################
# ################################################################################################################################
#
# Channel CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_kafka_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates a Kafka channel via the UI and returns its server-side ID.
    """

    # Navigate to the Kafka channels page ..
    open_kafka_channel_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_kafka_channel_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the channel's ID.
    _ = wait_for_kafka_channel_row(page, name)

    out = get_kafka_channel_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', channel_id:'str') -> 'None':
    """ Opens the edit dialog for a Kafka channel of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.channel.kafka.edit("{channel_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_kafka_channel(page:'Page', channel_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for a Kafka channel, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, channel_id)

    # .. apply the changes ..
    fill_kafka_channel_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_kafka_channel(page:'Page', channel_id:'str') -> 'None':
    """ Deletes a Kafka channel via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the channels page first.
    if '/zato/channel/kafka/' not in page.url:
        parsed_url = urlparse(page.url)
        open_kafka_channel_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.channel.kafka.delete_("{channel_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{channel_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
