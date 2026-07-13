# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, select_option_by_label, \
    set_select_value, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

Outconn_Page_Url = '/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http'

# How long to wait for a hot-deployed service to respond to its first invocation
_Service_Deploy_Timeout = 60

# How long to wait between the polling attempts above
_Service_Poll_Interval = 1.0

# How long to wait for the invoke overlay to report a result
_Invoke_Overlay_Timeout = 30000

# How long to keep pinging while a UI change propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the pings above
_Propagation_Poll_Interval = 0.5

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'host', 'url_path', 'ping_method', 'pool_size', 'timeout', 'content_type')

# Select fields set by raw value via JS since Chosen.js hides the underlying elements
_Select_Fields = ('data_format', 'validate_tls')

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_outconn_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the outgoing REST connections page, optionally filtering by a query.
    """

    url_path = Outconn_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row for an outgoing connection of the given name or None if there is no such row.
    """

    # The name cell wraps the actual name in a span so other cell content does not interfere with matching.
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_outconn_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of an outgoing connection with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_outconn_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of an outgoing connection row identified by name.
    """

    row = find_outconn_row(page, name)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def get_row_cell_texts(row:'any_') -> 'list':
    """ Returns the stripped text of every cell in a row.
    """

    out = [] # type: list

    cells = row.query_selector_all('td')
    for cell in cells:
        text = cell.inner_text().strip()
        out.append(text)

    return out

# ################################################################################################################################

def get_row_hidden_cell_texts(row:'any_') -> 'list':
    """ Returns the stripped text content of every cell in a row, including the hidden ones.
    """

    out = [] # type: list

    cells = row.query_selector_all('td')
    for cell in cells:
        text = cell.text_content().strip()
        out.append(text)

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Form filling
#
# ################################################################################################################################
# ################################################################################################################################

def fill_outconn_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the outgoing REST connection create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
    """

    # Plain text inputs ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. selects set by raw value ..
    for field_name in _Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. the security select, selected by its visible label, e.g. "Basic Auth/My def" ..
    if 'security' in options:
        select_option_by_label(page, f'#id_{prefix}security', options['security'])

    # .. the security select, selected by its raw value, e.g. ZATO_NONE ..
    if 'security_value' in options:
        set_select_value(page, f'#id_{prefix}security', options['security_value'])

    # .. the active checkbox ..
    if 'is_active' in options:
        page.set_checked(f'#id_{prefix}is_active', options['is_active'])

    # .. and the audit log checkbox.
    if 'is_audit_log_active' in options:
        page.set_checked(f'#id_{prefix}is_audit_log_active', options['is_audit_log_active'])

# ################################################################################################################################
# ################################################################################################################################
#
# Outgoing connection CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    host:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates an outgoing REST connection via the UI and returns its server-side ID.
    """

    # Navigate to the outgoing REST connections page ..
    open_outconn_page(page, base_url)

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
    fill_outconn_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the connection's ID.
    _ = wait_for_outconn_row(page, name)

    out = get_outconn_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', outconn_id:'str') -> 'None':
    """ Opens the edit dialog for an outgoing connection of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.http_soap.edit("{outconn_id}")')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_outconn(page:'Page', outconn_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for an outgoing connection, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, outconn_id)

    # .. apply the changes ..
    fill_outconn_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_outconn(page:'Page', outconn_id:'str') -> 'None':
    """ Deletes an outgoing connection via the UI confirmation dialog.
    """

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.http_soap.delete_("{outconn_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    page.wait_for_selector(f'#tr_{outconn_id}', state='detached', timeout=5000)

# ################################################################################################################################

def submit_create_form_expect_blocked(page:'Page') -> 'None':
    """ Clicks submit on the create form and asserts the dialog stays open,
    which is what happens when client-side validation blocks the submission.
    """

    # Click submit ..
    page.click('#create-div input[type="submit"]')

    # .. give the synchronous uniqueness check a moment to complete ..
    page.wait_for_timeout(1000)

    # .. and confirm the dialog is still there.
    dialog = page.query_selector('#create-div')
    assert dialog.is_visible(), 'Expected the create dialog to remain open after a blocked submission'

# ################################################################################################################################
# ################################################################################################################################
#
# Ping and the invoke overlay
#
# ################################################################################################################################
# ################################################################################################################################

def ping_outconn(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Ping link of an outgoing connection's row and returns the parsed ping response.
    """

    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'

    # Click the link and wait for the ping response to arrive ..
    def is_ping_response(response:'any_') -> 'bool':
        found = '/zato/http-soap/ping/' in response.url
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

def ping_outconn_until_success(page:'Page', name:'str', timeout:'float'=_Propagation_Timeout) -> 'anydict':
    """ Keeps pinging a connection until the ping succeeds, which covers the short window
    between a UI change and its propagation to the server. Returns the last ping result,
    letting the caller assert on it themselves.
    """

    deadline = time.monotonic() + timeout

    while True:
        out = ping_outconn(page, name)

        # Stop as soon as the ping goes through ..
        if out['is_success']:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################

def invoke_outconn_via_overlay(
    page:'Page',
    outconn_id:'str',
    *,
    request_body:'str'='',
    method:'str'='',
    query_params:'str'='',
    path_params:'str'='',
    ) -> 'anydict':
    """ Invokes an outgoing connection through the per-row Invoke overlay and returns a dict
    with the raw response text the overlay displays and the overlay's status line.
    """

    # Open the overlay ..
    page.evaluate(f'$.fn.zato.http_soap.invoke("{outconn_id}")')
    page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=5000)

    # .. type in the request ..
    escaped = request_body.replace('\\', '\\\\').replace("'", "\\'")
    page.evaluate(f"$.fn.zato.invoker._request_pane.setValue('{escaped}')")

    # .. the method and parameter fields live in the "More options" block, which may be
    # .. collapsed, so they are set via JS rather than filled directly ..
    if method:
        page.evaluate(f'$("#invoker-modal-method").val("{method}")')

    if query_params:
        page.evaluate(f'$("#invoker-modal-query-params").val("{query_params}")')

    if path_params:
        page.evaluate(f'$("#invoker-modal-path-params").val("{path_params}")')

    # .. click Invoke ..
    page.click('#invoker-modal-invoke-button')

    # .. wait for the status line to show a result ..
    page.wait_for_function(
        '''() => {
            let status = document.querySelector("#invoker-modal-status");
            if (!status) return false;
            let text = status.textContent;
            return text && text.indexOf("Invoking") === -1 && text.trim().length > 0;
        }''',
        timeout=_Invoke_Overlay_Timeout
    )

    # .. read what the overlay displays ..
    response_text = page.evaluate('$("#invoker-modal-response-pane").data("raw-response")')
    status_text = page.evaluate('$("#invoker-modal-status").text()')

    # .. close the overlay so it does not obstruct later interactions ..
    page.evaluate('$.fn.zato.invoker.close_overlay()')

    logger.info('[invoke_outconn_via_overlay] status=%s response=%s', status_text, response_text)

    # .. and hand both to the caller.
    out = {
        'response': response_text,
        'status': status_text,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Hot deployment
#
# ################################################################################################################################
# ################################################################################################################################

# The invoker service calls an outgoing REST connection from inside the server,
# which is the same code path production services use.
Outconn_Invoker_Service_Name = 'test.rest.outconn.invoke'

Outconn_Invoker_Service_Source = '''
# -*- coding: utf-8 -*-

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

class InvokeOutconnForTests(Service):
    """ Invokes an outgoing REST connection on behalf of outgoing REST connection tests.
    """

    name = 'test.rest.outconn.invoke'

    def handle(self):

        request = self.request.payload
        mode = request['mode']

        # A readiness probe sent while the test waits for this service to deploy ..
        if mode == 'ping':
            out = {'is_ready': True}

        # .. otherwise, call the outgoing connection and report what came back.
        else:
            outconn_name = request['outconn_name']
            method = request['method']
            data = request['data']
            params = request['params']

            connection = self.out.rest[outconn_name].conn
            response = connection.http_request(method, self.cid, data=data, params=params)

            out = {
                'status_code': response.status_code,
                'text': response.text,
            }

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'
'''.lstrip()

# ################################################################################################################################

def wait_for_invoker_service(api_client:'ZatoClient') -> 'None':
    """ Polls the hot-deployed invoker service until it responds to a readiness probe.
    """

    deadline = time.monotonic() + _Service_Deploy_Timeout

    while time.monotonic() < deadline:

        # The service raises until it is deployed, at which point the probe returns cleanly.
        try:
            response = api_client.invoke(Outconn_Invoker_Service_Name, {'mode': 'ping'})
        except Exception as probe_error:
            logger.info('[wait_for_invoker_service] not ready yet: %s', probe_error)
        else:
            logger.info('[wait_for_invoker_service] ready: %s', response)
            return

        time.sleep(_Service_Poll_Interval)

    raise Exception(f'Service `{Outconn_Invoker_Service_Name}` did not deploy within {_Service_Deploy_Timeout}s')

# ################################################################################################################################

def invoke_outconn_from_service(
    api_client:'ZatoClient',
    outconn_name:'str',
    *,
    method:'str'='POST',
    data:'any_'='',
    params:'anydict | None'=None,
    ) -> 'anydict':
    """ Calls an outgoing REST connection from inside the hot-deployed invoker service
    and returns a dict with the status code and body of what the connection received back.
    """

    request = {
        'mode': 'invoke',
        'outconn_name': outconn_name,
        'method': method,
        'data': data,
        'params': params or {},
    }

    response = api_client.invoke(Outconn_Invoker_Service_Name, request)

    # The service serializes its response to JSON on its own, yet the admin invoke channel
    # may hand it back either as a string or as an already parsed document.
    if isinstance(response, str):
        response = json.loads(response)

    out = response
    return out

# ################################################################################################################################
# ################################################################################################################################
