# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time
from urllib.parse import urlparse

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, select_option_by_label, \
    set_select_value, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

SOAP_Outconn_Page_Url = '/zato/outgoing/soap/?cluster=1'

# How long to wait for a pre-deployed service to respond to its first invocation
_Service_Deploy_Timeout = 60

# How long to wait between the polling attempts above
_Service_Poll_Interval = 1.0

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'host', 'url_path', 'soap_action', 'timeout', 'tls_client_cert', 'tls_client_key',
    'ping_method', 'content_type')

# Select fields set by raw value via JS since Chosen.js hides the underlying elements
_Select_Fields = ('soap_version', 'validate_tls')

# Checkbox fields toggled by boolean options
_Checkbox_Fields = ('is_active', 'is_audit_log_active', 'use_ws_addressing', 'use_mtom')

# The forms are tabbed and a text field is only fillable while its tab is active
_Field_To_Tab = {
    'name': 'main',
    'host': 'main',
    'url_path': 'main',
    'soap_action': 'main',
    'timeout': 'main',
    'tls_client_cert': 'security',
    'tls_client_key': 'security',
    'ping_method': 'more',
    'content_type': 'more',
}

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_soap_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing SOAP connections page, optionally filtering by a query.
    """

    url_path = SOAP_Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_soap_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of an outgoing SOAP connection of the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_soap_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing SOAP connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_soap_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing SOAP connection row identified by name.
    """

    row = find_soap_outconn_row(page, name)
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

def fill_soap_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing SOAP connection create or edit form. An empty prefix means
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

    # .. the security select, selected by its visible label, e.g. "WS-Security/My def" ..
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

    # .. the body-credential mapping rows, each a name with an optional position ..
    if 'body_credentials' in options:
        action = 'edit' if prefix else 'create'
        page.evaluate(f'$("#body-credentials-{action}").empty()')

        for row in options['body_credentials']:
            name = row['name']
            position = row.get('position') or ''
            page.evaluate(f'$.fn.zato.outgoing.soap.add_body_credential_row("{action}", "{name}", "{position}")')

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

def create_soap_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    host:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing SOAP connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing SOAP connections page ..
    open_soap_outconn_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'host': host,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. default to no security definition unless the caller chose one ..
    if 'security' not in form_data:
        if 'security_value' not in form_data:
            form_data['security_value'] = ZATO_NONE

    # .. fill the form ..
    fill_soap_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_soap_outconn_row(page, name)

    out = get_soap_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing SOAP connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.outgoing.soap.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_soap_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing SOAP connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_soap_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_soap_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing SOAP connection via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the connections page first.
    if '/zato/outgoing/soap/' not in page.url:
        parsed_url = urlparse(page.url)
        open_soap_outconn_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.outgoing.soap.delete_("{outconn_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
#
# Ping
#
# ################################################################################################################################
# ################################################################################################################################

def ping_soap_outconn(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Ping link of an outgoing SOAP connection's row and returns the parsed ping response.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    # Click the link and wait for the ping response to arrive ..
    def is_ping_response(response:'any_') -> 'bool':
        found = '/zato/outgoing/soap/ping/' in response.url
        return found

    with page.expect_response(is_ping_response, timeout=30000) as response_info:
        page.click(f'{row_selector} a.ping-link')

    # .. dismiss the tooltip the action runner shows so it does not obstruct later interactions ..
    response = response_info.value
    page.evaluate('$.fn.zato.action_runner.close_all()')

    # .. and hand the parsed body to the caller.
    out = response.json()
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The pre-deployed invoker service, driven through the IDE invoker in the browser
#
# ################################################################################################################################
# ################################################################################################################################

# The invoker service calls an outgoing SOAP connection from inside the server,
# which is the same code path production services use. It deploys during server
# boot from fixtures/services, so no hot-deployment wait is needed. Tests invoke
# it the way a person would - by opening it in the IDE and clicking Invoke.
SOAP_Invoker_Service_Name = 'test.soap.outconn.invoke'

# ################################################################################################################################

def open_soap_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed invoker service in the IDE and waits until the Invoke button is usable.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{SOAP_Invoker_Service_Name}/?cluster=1')
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

def wait_for_soap_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness
    probe until the service responds, confirming it deployed during server boot.
    """

    open_soap_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Service_Deploy_Timeout

    while time.monotonic() < deadline:

        # The invocation errors out until the service is deployed, at which point
        # the probe comes back with its readiness flag.
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            logger.info('[wait_for_soap_invoker_service] not ready yet: %s', probe_error)
        else:
            if response.get('is_ready'):
                logger.info('[wait_for_soap_invoker_service] ready: %s', response)
                return
            logger.info('[wait_for_soap_invoker_service] unexpected probe response: %s', response)

        time.sleep(_Service_Poll_Interval)

    raise Exception(f'Service `{SOAP_Invoker_Service_Name}` did not deploy within {_Service_Deploy_Timeout}s')

# ################################################################################################################################

def invoke_soap_outconn_from_ide(
    page:'Page',
    base_url:'str',
    outconn_name:'str',
    operation:'str',
    *,
    namespace:'str'='',
    fields:'anydict | None'=None,
    bytes_fields:'anydict | None'=None,
    response_fields:'list | None'=None,
    ) -> 'anydict':
    """ Calls an outgoing SOAP connection through the pre-deployed invoker service,
    driven from the IDE in the browser, and returns a dict with the response fields,
    addressing headers and attachments.
    """

    request = {
        'mode': 'invoke',
        'outconn_name': outconn_name,
        'operation': operation,
        'namespace': namespace,
        'fields': fields or {},
        'bytes_fields': bytes_fields or {},
        'response_fields': response_fields or [],
    }

    open_soap_invoker_in_ide(page, base_url)

    out = invoke_service_in_ide(page, request)
    return out

# ################################################################################################################################
# ################################################################################################################################
