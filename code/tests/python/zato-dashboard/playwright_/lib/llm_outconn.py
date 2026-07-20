# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time
from http.client import OK
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

LLM_Outconn_Page_Url = '/zato/outgoing/llm/?cluster=1&type_=outconn-llm'

# How long to wait for a pre-deployed service to respond to its first invocation
_Service_Deploy_Timeout = 60

# How long to wait between the polling attempts above
_Service_Poll_Interval = 1.0

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'address', 'model', 'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry')

# Select fields set by raw value via JS since Chosen.js hides the underlying elements
_Select_Fields = ('provider',)

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active',)

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_llm_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing LLM connections page, optionally filtering by a query.
    """

    url_path = LLM_Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_llm_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an outgoing LLM connection of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_llm_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing LLM connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_llm_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing LLM connection row identified by name.
    """

    row = find_llm_outconn_row(page, name)
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

def fill_llm_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing LLM connection create or edit form. An empty prefix means
    the create form, the 'edit-' prefix means the edit form. Only the fields present
    in options are touched.
    """

    # Plain text inputs ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. selects set by raw value ..
    for field_name in _Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. and checkboxes, checked via JS so the state is set directly regardless of the styling.
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

def create_llm_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    address:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing LLM connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing LLM connections page ..
    open_llm_outconn_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'address': address,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. fill the form ..
    fill_llm_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_llm_outconn_row(page, name)

    out = get_llm_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing LLM connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.outgoing.llm.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_llm_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing LLM connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_llm_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_llm_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing LLM connection via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the connections page first.
    if '/zato/outgoing/llm/' not in page.url:
        parsed_url = urlparse(page.url)
        open_llm_outconn_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.outgoing.llm.delete_("{outconn_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
#
# API key and ping
#
# ################################################################################################################################
# ################################################################################################################################

def _is_change_password_response(response:'any_') -> 'bool':
    found = '/zato/outgoing/llm/change-password/' in response.url
    return found

# ################################################################################################################################

def change_llm_api_key(page:'Page', outconn_id:'str', api_key:'str') -> 'None':
    """ Sets the API key of an outgoing LLM connection via the change-password dialog.
    """

    # Open the dialog ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{outconn_id}")')
    _ = page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    # .. type the key in ..
    page.fill('#change_password-div #id_password', api_key)

    # .. submit, waiting for the server to confirm the change - the dialog closes before
    # the request completes, so the dialog state alone is not enough to synchronize on ..
    with page.expect_response(_is_change_password_response, timeout=10000) as response_info:
        page.click('#change_password-div input[type="submit"]')

    assert response_info.value.status == OK

    # .. and wait for the dialog to close too.
    _ = page.wait_for_selector('#change_password-div', state='hidden', timeout=10000)

# ################################################################################################################################

def ping_llm_outconn(page:'Page', name:'str') -> 'any_':
    """ Clicks the Ping link of an outgoing LLM connection's row and returns the response.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    # Click the link and wait for the ping response to arrive ..
    def is_ping_response(response:'any_') -> 'bool':
        found = '/zato/outgoing/llm/ping/' in response.url
        return found

    with page.expect_response(is_ping_response, timeout=30000) as response_info:
        page.click(f'{row_selector} td a:text-is("Ping")')

    out = response_info.value
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The pre-deployed invoker service, driven through the IDE invoker in the browser
#
# ################################################################################################################################
# ################################################################################################################################

# The invoker service calls an outgoing LLM connection from inside the server,
# which is the same code path production services use. It deploys during server
# boot from fixtures/services, so no hot-deployment wait is needed. Tests invoke
# it the way a person would - by opening it in the IDE and clicking Invoke.
LLM_Invoker_Service_Name = 'test.llm.outconn.invoke'

# ################################################################################################################################

def open_llm_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed invoker service in the IDE and waits until the Invoke button is usable.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{LLM_Invoker_Service_Name}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

# ################################################################################################################################

def invoke_service_in_ide(page:'Page', request:'anydict') -> 'anydict':
    """ Types a request into the IDE's request area, clicks Invoke and returns the parsed
    response read back from the IDE's response area. The IDE must already be open.
    """

    # Clear whatever a previous invocation may have left in the response area ..
    page.evaluate('$("#data-response").text("")')

    # .. type the request in ..
    page.fill('#data-request', json.dumps(request))

    # .. click Invoke and wait for the browser to receive the reply ..
    def is_invoke_response(response:'any_') -> 'bool':
        found = '/zato/service/invoke/' in response.url
        return found

    with page.expect_response(is_invoke_response, timeout=30000):
        page.click('#invoke-service')

    # .. wait for the response to be rendered in the response area ..
    _ = page.wait_for_function('document.querySelector("#data-response").value.length > 0', timeout=15000)
    response_text = page.input_value('#data-response')

    # .. and parse it - the service replies with JSON, which the IDE may show
    # either directly or wrapped in one more layer of string encoding.
    out = json.loads(response_text)
    if isinstance(out, str):
        out = json.loads(out)

    return out

# ################################################################################################################################

def wait_for_llm_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness
    probe until the service responds, confirming it deployed during server boot.
    """

    open_llm_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Service_Deploy_Timeout

    while time.monotonic() < deadline:

        # The invocation errors out until the service is deployed, at which point
        # the probe comes back with its readiness flag.
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            logger.info('[wait_for_llm_invoker_service] not ready yet: %s', probe_error)
        else:
            if response.get('is_ready'):
                logger.info('[wait_for_llm_invoker_service] ready: %s', response)
                return
            logger.info('[wait_for_llm_invoker_service] unexpected probe response: %s', response)

        time.sleep(_Service_Poll_Interval)

    raise Exception(f'Service `{LLM_Invoker_Service_Name}` did not deploy within {_Service_Deploy_Timeout}s')

# ################################################################################################################################

def invoke_llm_outconn_from_ide(
    page:'Page',
    base_url:'str',
    outconn_name:'str',
    text:'str',
    *,
    chat_id:'str'='',
    ) -> 'anydict':
    """ Calls an outgoing LLM connection through the pre-deployed invoker service,
    driven from the IDE in the browser, and returns a dict with the reply's text and usage.
    A chat_id makes it a multi-turn chat call, otherwise it is a one-shot invoke.
    """

    request = {
        'mode': 'chat' if chat_id else 'invoke',
        'outconn_name': outconn_name,
        'text': text,
        'chat_id': chat_id,
    }

    open_llm_invoker_in_ide(page, base_url)

    out = invoke_service_in_ide(page, request)
    return out

# ################################################################################################################################
# ################################################################################################################################
