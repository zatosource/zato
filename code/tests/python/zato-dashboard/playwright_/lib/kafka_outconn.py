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
Kafka_Outconn_Page_Url = '/zato/outgoing/kafka/?cluster=1&type_=outconn-kafka'

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'address', 'topic', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file')

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'ssl')

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_kafka_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing Kafka connections page, optionally filtering by a query.
    """

    url_path = Kafka_Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_kafka_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an outgoing Kafka connection of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_kafka_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing Kafka connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_kafka_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing Kafka connection row identified by name.
    """

    row = find_kafka_outconn_row(page, name)
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

def fill_kafka_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing Kafka connection create or edit form. An empty prefix means
    the create form, the 'edit-' prefix means the edit form. Only the fields present
    in options are touched.
    """

    # Plain text inputs ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. and checkboxes, checked via JS so the state is set directly regardless of the slider styling.
    for field_name in _Checkbox_Fields:
        if field_name in options:
            checked = 'true' if options[field_name] else 'false'
            page.evaluate(f'$("#id_{prefix}{field_name}").prop("checked", {checked})')

# ################################################################################################################################
# ################################################################################################################################
#
# Outgoing connection CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_kafka_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing Kafka connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing Kafka connections page ..
    open_kafka_outconn_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_kafka_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_kafka_outconn_row(page, name)

    out = get_kafka_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing Kafka connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.outgoing.kafka.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_kafka_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing Kafka connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_kafka_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_kafka_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing Kafka connection via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the connections page first.
    if '/zato/outgoing/kafka/' not in page.url:
        parsed_url = urlparse(page.url)
        open_kafka_outconn_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.outgoing.kafka.delete_("{outconn_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
