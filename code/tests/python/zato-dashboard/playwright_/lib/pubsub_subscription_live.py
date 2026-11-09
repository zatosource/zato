# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import confirm_delete, get_item_id, navigate_to_page, open_edit_dialog, \
    open_publish_overlay, publish_via_overlay, select_option_by_label, set_select_value, trigger_delete
from zato.common.typing_ import cast_

# Zato - test helpers
from mcp_gateway_live import import_enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

Subscription_Page_Url = '/zato/pubsub/subscription/'

_Topic_Page_Url = '/zato/pubsub/topic/?query={}'

_Edit_Topics_Selector    = '#id_edit-multi-select-div'
_Edit_Delivery_Selector  = '#id_edit-delivery_type'
_Edit_Push_Type_Selector = '#id_edit-push_type'
_Edit_Endpoint_Selector  = '#id_edit-rest_push_endpoint_id'
_Edit_Is_Active_Selector = '#id_edit-is_delivery_active'

_Push_Type_REST = 'rest'

_Indeterminate_Class = 'indeterminate'

# A topic checkbox of the edit form goes through three states, so reaching any of them takes at most this many clicks
_Max_Topic_Clicks = 3

# How long the Dashboard and the server may take to act, in milliseconds
Timeout = 15000

# How long a published message may take to reach its subscriber, in seconds
Delivery_Timeout = 20

# How long a test waits to make sure a message does not reach a subscriber, in seconds
No_Delivery_Wait = 5

# How often a page or a log is read again while waiting, in seconds
_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def new_marker() -> 'str':
    """ Returns a value unique to one message, which identifies the message wherever it is delivered.
    """
    out = 'marker' + CryptoManager.generate_hex_string(16)
    return out

# ################################################################################################################################

def import_client_objects(
    zato_dashboard:'anydict',
    sec_name:'str',
    topic_names:'strlist',
    endpoints:'anydict',
    ) -> 'None':
    """ Creates through enmasse an API client allowed to subscribe to the topics, the topics,
    and an outgoing REST connection for each name and address in endpoints.
    """
    password = 'password.' + CryptoManager.generate_hex_string()

    lines = [
        'security:',
        f'  - name: {sec_name}',
        '    type: basic_auth',
        f'    username: {sec_name}',
        f'    password: {password}',
        '',
    ]

    if endpoints:
        lines.append('outgoing_rest:')

        for endpoint_name, address in endpoints.items():
            lines.append(f'  - name: {endpoint_name}')
            lines.append(f'    host: {address}')
            lines.append(f'    url_path: /push/{endpoint_name}')
            lines.append('    data_format: json')
            lines.append('    timeout: 30')

        lines.append('')

    lines.append('pubsub_topic:')

    for topic_name in topic_names:
        lines.append(f'  - name: {topic_name}')

    lines.append('')
    lines.append('pubsub_permission:')
    lines.append(f'  - security: {sec_name}')
    lines.append('    sub:')

    for topic_name in topic_names:
        lines.append(f'      - {topic_name}')

    lines.append('')

    yaml_content = '\n'.join(lines)
    import_enmasse(zato_dashboard, yaml_content)

# ################################################################################################################################

def import_topics(zato_dashboard:'anydict', topic_names:'strlist') -> 'None':
    """ Creates the topics through enmasse.
    """
    lines = ['pubsub_topic:']

    for topic_name in topic_names:
        lines.append(f'  - name: {topic_name}')

    lines.append('')

    yaml_content = '\n'.join(lines)
    import_enmasse(zato_dashboard, yaml_content)

# ################################################################################################################################
# ################################################################################################################################

def row_selector(subscriber_name:'str') -> 'str':
    """ Returns the selector of the row whose subscriber column names the API client or the service.
    """
    out = f'#data-table tbody tr:has(td:nth-child(3) a:text-is("{subscriber_name}"))'
    return out

# ################################################################################################################################

def open_subscription_page(page:'Page', base_url:'str') -> 'None':
    navigate_to_page(page, base_url, Subscription_Page_Url)

# ################################################################################################################################

def wait_for_row(page:'Page', subscriber_name:'str') -> 'any_':
    out = page.wait_for_selector(row_selector(subscriber_name), state='visible', timeout=Timeout)
    return out

# ################################################################################################################################

def get_row_text(page:'Page', base_url:'str', subscriber_name:'str') -> 'str':
    """ Reloads the subscriptions page and returns the text of the subscriber's row.
    """
    open_subscription_page(page, base_url)

    row = wait_for_row(page, subscriber_name)

    out = row.inner_text()
    return out

# ################################################################################################################################

def get_row_id(page:'Page', subscriber_name:'str') -> 'str':
    row = wait_for_row(page, subscriber_name)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def count_rows(page:'Page', subscriber_name:'str') -> 'int':
    rows = page.query_selector_all(row_selector(subscriber_name))

    out = len(rows)
    return out

# ################################################################################################################################

def get_pending_count(page:'Page', subscriber_name:'str') -> 'int':
    """ Returns the number of pending messages that the subscriber's row shows.
    """
    row = wait_for_row(page, subscriber_name)
    pending_link = row.query_selector('td a[href*="pubsub/subscription/queue"]')
    pending_text = pending_link.inner_text().strip()

    out = int(pending_text)
    return out

# ################################################################################################################################

def wait_for_pending_count(page:'Page', base_url:'str', subscriber_name:'str', expected:'int') -> 'None':
    """ Reloads the subscriptions page until the subscriber's row shows the expected number of pending messages.
    """
    deadline = time.monotonic() + Delivery_Timeout

    while True:

        open_subscription_page(page, base_url)
        pending_count = get_pending_count(page, subscriber_name)

        # Stop as soon as the count is the expected one ..
        if pending_count == expected:
            break

        # .. or fail once the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Expected {expected} pending messages for {subscriber_name}, the row shows {pending_count}')

        time.sleep(_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def publish_to_topic(page:'Page', base_url:'str', topic_name:'str', marker:'str') -> 'None':
    """ Publishes a message with the marker to the topic through the topics page.
    """
    topic_url = _Topic_Page_Url.format(topic_name)
    navigate_to_page(page, base_url, topic_url)

    topic_id = get_item_id(page, topic_name)
    open_publish_overlay(page, topic_id)

    payload = f'{{"marker": "{marker}"}}'
    publish_via_overlay(page, payload)

    status_text = page.inner_text('#invoker-modal-status')
    status_lower = status_text.lower()
    assert 'error' not in status_lower, f'Publication to {topic_name} failed: "{status_text}"'

# ################################################################################################################################

def delete_topic(page:'Page', base_url:'str', topic_name:'str') -> 'None':
    """ Deletes the topic through the topics page.
    """
    topic_url = _Topic_Page_Url.format(topic_name)
    navigate_to_page(page, base_url, topic_url)

    topic_id = get_item_id(page, topic_name)
    trigger_delete(page, 'topic', topic_id)
    confirm_delete(page)

    deleted_row_selector = f'#data-table tbody tr:has(td:text-is("{topic_name}"))'
    _ = page.wait_for_selector(deleted_row_selector, state='detached', timeout=Timeout)

# ################################################################################################################################
# ################################################################################################################################

def open_subscription_edit(page:'Page', base_url:'str', subscriber_name:'str') -> 'None':
    """ Opens the edit dialog of the subscriber's subscription on a freshly loaded page, once its topics are listed.
    """
    open_subscription_page(page, base_url)
    row_id = get_row_id(page, subscriber_name)

    open_edit_dialog(page, 'subscription', row_id)

    first_checkbox = f'{_Edit_Topics_Selector} input[name="topic_name"]'
    _ = page.wait_for_selector(first_checkbox, state='attached', timeout=Timeout)

# ################################################################################################################################

def _edit_topic_checkbox(topic_name:'str') -> 'str':
    out = f'{_Edit_Topics_Selector} input[name="topic_name"][value="{topic_name}"]'
    return out

# ################################################################################################################################

def is_edit_topic_on(page:'Page', topic_name:'str') -> 'bool':
    """ Tells whether the topic is checked in the edit form, with both publication and delivery enabled.
    """
    checkbox_selector = _edit_topic_checkbox(topic_name)
    _ = page.wait_for_selector(checkbox_selector, state='attached', timeout=Timeout)

    is_checked = page.is_checked(checkbox_selector)
    class_names = cast_('str', page.get_attribute(checkbox_selector, 'class'))
    is_indeterminate = _Indeterminate_Class in class_names.split()

    out = is_checked
    if is_indeterminate:
        out = False

    return out

# ################################################################################################################################

def set_edit_topic(page:'Page', topic_name:'str', is_on:'bool') -> 'None':
    """ Clicks the topic's checkbox in the edit form until it is checked or entirely unchecked.
    """
    checkbox_selector = _edit_topic_checkbox(topic_name)

    for _ in range(_Max_Topic_Clicks):

        is_checked = page.is_checked(checkbox_selector)
        class_names = cast_('str', page.get_attribute(checkbox_selector, 'class'))
        is_indeterminate = _Indeterminate_Class in class_names.split()

        if not is_indeterminate:
            if is_checked == is_on:
                break

        page.click(checkbox_selector)

    else:
        raise Exception(f'Topic {topic_name} could not be set to is_on={is_on}')

# ################################################################################################################################

def set_edit_pull(page:'Page') -> 'None':
    set_select_value(page, _Edit_Delivery_Selector, 'pull')

# ################################################################################################################################

def set_edit_push_rest(page:'Page', endpoint_name:'str') -> 'None':
    """ Switches the edit form to push delivery to the REST endpoint.
    """

    # Choose push delivery to a REST endpoint ..
    set_select_value(page, _Edit_Delivery_Selector, 'push')
    set_select_value(page, _Edit_Push_Type_Selector, _Push_Type_REST)

    # .. wait for the endpoints to load ..
    _ = page.wait_for_function(
        '(name) => Array.from(document.querySelectorAll("' + _Edit_Endpoint_Selector + ' option"))' +
        '.some(option => option.textContent === name)',
        arg=endpoint_name,
        timeout=Timeout,
    )

    # .. and pick the one by its name.
    select_option_by_label(page, _Edit_Endpoint_Selector, endpoint_name)

# ################################################################################################################################

def set_edit_delivery_active(page:'Page', is_active:'bool') -> 'None':
    page.set_checked(_Edit_Is_Active_Selector, is_active)

# ################################################################################################################################

def submit_subscription_edit(page:'Page') -> 'None':
    """ Submits the edit form, failing with the alert or the message the page shows if the dialog stays open.
    """
    alert_messages = [] # type: list

    def handle_dialog(dialog:'any_') -> 'None':
        alert_messages.append(dialog.message)
        dialog.accept()

    page.on('dialog', handle_dialog)

    try:
        page.click('#edit-div input[type="submit"]')

        try:
            _ = page.wait_for_selector('#edit-div', state='hidden', timeout=Timeout)
        except Exception as e:
            user_message = page.inner_text('#user-message')
            raise Exception(f'Edit dialog did not close, alerts: {alert_messages}, message: "{user_message}"') from e

    finally:
        page.remove_listener('dialog', handle_dialog)

# ################################################################################################################################

def delete_subscription(page:'Page', base_url:'str', subscriber_name:'str') -> 'str':
    """ Deletes the subscriber's subscription through the subscriptions page and returns the text of the confirmation.
    """
    open_subscription_page(page, base_url)
    row_id = get_row_id(page, subscriber_name)

    trigger_delete(page, 'subscription', row_id)
    out = page.inner_text('#popup_container')

    confirm_delete(page)
    _ = page.wait_for_selector(row_selector(subscriber_name), state='detached', timeout=Timeout)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _service_received_prefix(service_name:'str') -> 'str':
    out = f'Service {service_name} received -> '
    return out

# ################################################################################################################################

def _read_server_log(zato_dashboard:'anydict') -> 'str':
    log_path = os.path.join(zato_dashboard['server_dir'], 'logs', 'server.log')

    with open(log_path, 'r', encoding='utf-8', errors='replace') as log_file:
        out = log_file.read()

    return out

# ################################################################################################################################

def has_service_received(zato_dashboard:'anydict', service_name:'str', marker:'str') -> 'bool':
    """ Tells whether the server log shows that the service received the message with the marker.
    """
    prefix = _service_received_prefix(service_name)
    log_content = _read_server_log(zato_dashboard)

    out = False

    for line in log_content.splitlines():
        if prefix in line:
            if marker in line:
                out = True
                break

    return out

# ################################################################################################################################

def wait_for_service_delivery(zato_dashboard:'anydict', service_name:'str', marker:'str') -> 'None':
    deadline = time.monotonic() + Delivery_Timeout

    while not has_service_received(zato_dashboard, service_name, marker):
        if time.monotonic() >= deadline:
            raise Exception(f'Service {service_name} did not receive the message with {marker}')
        time.sleep(_Poll_Interval)

# ################################################################################################################################

def has_request_with_marker(requests:'any_', marker:'str') -> 'bool':
    """ Tells whether any of the requests a REST receiver recorded has the marker in its body.
    """
    out = False

    for request in requests:
        if marker in request['body']:
            out = True
            break

    return out

# ################################################################################################################################

def wait_for_rest_delivery(receiver:'any_', marker:'str') -> 'None':
    deadline = time.monotonic() + Delivery_Timeout

    while not has_request_with_marker(receiver.recorded_requests, marker):
        if time.monotonic() >= deadline:
            raise Exception(f'The receiver at {receiver.address} did not receive the message with {marker}')
        time.sleep(_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
