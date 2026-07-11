# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Callbacks configured by the declarative tests deliver to the callback-store fixture service,
# which appends every delivery to this file - the same path the service itself uses.
Callback_Store_Path = '/tmp/zato-test-declarative-callback.jsonl'

# Name of the boot-deployed fixture service that callbacks are delivered to
Callback_Store_Service = 'test.declarative.callback-store'

# Name of the boot-deployed fixture service that runs self.rest[name].invoke()
REST_Declarative_Invoker_Service = 'test.rest.outconn.declarative-invoke'

# How long to wait for a callback delivery or a scheduled invocation to arrive
Delivery_Timeout = 60.0

# How long to sleep between the polling attempts above
_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################
#
# The callback store
#
# ################################################################################################################################
# ################################################################################################################################

def read_callback_entries(marker:'str') -> 'anylist':
    """ Returns every callback-store entry whose serialized form contains the given marker.
    """
    out = [] # type: anylist

    if not os.path.exists(Callback_Store_Path):
        return out

    with open(Callback_Store_Path, 'r') as callback_file:
        for line in callback_file:
            line = line.strip()
            if line and marker in line:
                out.append(json.loads(line))

    return out

# ################################################################################################################################

def wait_for_callback_entry(marker:'str', timeout:'float'=Delivery_Timeout) -> 'anydict':
    """ Waits until the callback store receives an entry containing the given marker and returns it.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        entries = read_callback_entries(marker)
        if entries:
            logger.info('[wait_for_callback_entry] found: %s', entries[0])
            return entries[0]
        time.sleep(_Poll_Interval)

    raise Exception(f'No callback entry with marker `{marker}` arrived within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
#
# Filling the invocation tabs of the REST page
#
# ################################################################################################################################
# ################################################################################################################################

def activate_rest_tab(page:'Page', action:'str', tab_name:'str') -> 'None':
    """ Clicks a tab header in the REST create or edit dialog so the tab's fields become visible.
    """
    container = '#edit-div' if action == 'edit' else '#create-div'
    page.click(f'{container} .dashboard-tab[data-tab="{tab_name}"]')

# ################################################################################################################################

def add_rest_param_row(page:'Page', action:'str', kind:'str', key:'str', value:'str', mode:'str'='text') -> 'None':
    """ Adds one parameter row - a key, a value and its Text/JSONata mode - to the Request tab.
    """
    _ = page.evaluate(
        '([action, kind, key, value, mode]) => $.fn.zato.http_soap.add_param_row(action, kind, key, value, mode)',
        [action, kind, key, value, mode])

# ################################################################################################################################

def _set_chosen_select(page:'Page', selector:'str', value:'str') -> 'None':
    """ Sets a select that has a Chosen widget attached, which hides the underlying element.
    """
    _ = page.evaluate(
        '([selector, value]) => $(selector).val(value).trigger("chosen:updated").trigger("change")',
        [selector, value])

# ################################################################################################################################

def fill_rest_invocation_tabs(page:'Page', options:'anydict', action:'str'='create') -> 'None':
    """ Fills the Scheduler, Request, Response, Callback and Health check tabs of the REST
    create or edit dialog. Only the fields present in options are touched.
    """
    prefix = 'edit-' if action == 'edit' else ''

    # Scheduler tab - the start date field has a datetimepicker attached which rewrites
    # the field on focus, hence it is set through jQuery, the same way the widget does it ..
    if 'scheduler_run_every' in options:
        activate_rest_tab(page, action, 'scheduler')
        page.fill(f'#id_{prefix}scheduler_run_every', options['scheduler_run_every'])

        if 'scheduler_run_unit' in options:
            _ = page.select_option(f'#id_{prefix}scheduler_run_unit', options['scheduler_run_unit'])

        if 'scheduler_start_date' in options:
            start_date = options['scheduler_start_date']
            _ = page.evaluate(f'$("#id_{prefix}scheduler_start_date").val("{start_date}")')

    # .. Request tab - the method, the parameter rows and the body ..
    request_row_kinds = ('query_string', 'path_params', 'headers')
    has_request_fields = 'request_method' in options or 'request_data' in options
    has_request_rows = any(f'request_{kind}' in options for kind in request_row_kinds)

    if has_request_fields or has_request_rows:
        activate_rest_tab(page, action, 'request')

        if 'request_method' in options:
            page.fill(f'#id_{prefix}request_method', options['request_method'])

        for kind in request_row_kinds:
            if rows := options.get(f'request_{kind}'):
                for row in rows:
                    add_rest_param_row(page, action, kind, row['key'], row['value'], row.get('mode', 'text'))

        if 'request_data' in options:
            page.fill(f'#id_{prefix}request_data', options['request_data'])

        if 'request_data_mode' in options:
            _ = page.select_option(f'#id_{prefix}request_data_mode', options['request_data_mode'])

    # .. Response tab ..
    if 'response_map' in options:
        activate_rest_tab(page, action, 'response')

        if 'response_map_mode' in options:
            _ = page.select_option(f'#id_{prefix}response_map_mode', options['response_map_mode'])

        page.fill(f'#id_{prefix}response_map', options['response_map'])

    # .. Callback tab - the name goes into the widget matching the callback type ..
    if callback_type := options.get('callback_type'):
        activate_rest_tab(page, action, 'callback')
        _ = page.select_option(f'#id_{prefix}callback_type', callback_type)

        if callback_type == 'service':
            _set_chosen_select(page, f'#id_{prefix}callback_service', options['callback_name'])
        elif callback_type == 'topic':
            page.fill(f'#id_{prefix}callback_topic', options['callback_name'])
        else:
            _set_chosen_select(page, f'#id_{prefix}callback_rest', options['callback_name'])

    # .. and the Health check tab, whose callback widgets work the same way.
    if 'health_check_run_every' in options:
        activate_rest_tab(page, action, 'health_check')
        page.fill(f'#id_{prefix}health_check_run_every', options['health_check_run_every'])

        if 'health_check_run_unit' in options:
            _ = page.select_option(f'#id_{prefix}health_check_run_unit', options['health_check_run_unit'])

        if 'health_check_notify_on' in options:
            _ = page.select_option(f'#id_{prefix}health_check_notify_on', options['health_check_notify_on'])

        if health_check_callback_type := options.get('health_check_callback_type'):
            _ = page.select_option(f'#id_{prefix}health_check_callback_type', health_check_callback_type)

            if health_check_callback_type == 'service':
                _set_chosen_select(
                    page, f'#id_{prefix}health_check_callback_service', options['health_check_callback_name'])
            elif health_check_callback_type == 'topic':
                page.fill(f'#id_{prefix}health_check_callback_topic', options['health_check_callback_name'])
            else:
                _set_chosen_select(
                    page, f'#id_{prefix}health_check_callback_rest', options['health_check_callback_name'])

    # The form goes back to its first tab so the submit flow always starts from the same place
    activate_rest_tab(page, action, 'config')

# ################################################################################################################################
# ################################################################################################################################
#
# Filling the invocation tabs of the SOAP page
#
# ################################################################################################################################
# ################################################################################################################################

def activate_soap_tab(page:'Page', action:'str', tab_name:'str') -> 'None':
    """ Clicks a tab header in the SOAP create or edit dialog so the tab's fields become visible.
    """
    container = '#edit-div' if action == 'edit' else '#create-div'
    page.click(f'{container} .dashboard-tab[data-tab="{tab_name}"]')

# ################################################################################################################################

def add_soap_param_row(page:'Page', action:'str', kind:'str', key:'str', value:'str', mode:'str'='text') -> 'None':
    """ Adds one message or SOAP header row to the Request tab of the SOAP dialog.
    """
    _ = page.evaluate(
        '([action, kind, key, value, mode]) => $.fn.zato.outgoing.soap.add_param_row(action, kind, key, value, mode)',
        [action, kind, key, value, mode])

# ################################################################################################################################

def fill_soap_invocation_tabs(page:'Page', options:'anydict', action:'str'='create') -> 'None':
    """ Fills the Scheduler, Request, Response, Callback and Health check tabs of the SOAP
    create or edit dialog. Only the fields present in options are touched.
    """
    prefix = 'edit-' if action == 'edit' else ''

    # Scheduler tab ..
    if 'scheduler_run_every' in options:
        activate_soap_tab(page, action, 'scheduler')
        page.fill(f'#id_{prefix}scheduler_run_every', options['scheduler_run_every'])

        if 'scheduler_run_unit' in options:
            _ = page.select_option(f'#id_{prefix}scheduler_run_unit', options['scheduler_run_unit'])

        if 'scheduler_start_date' in options:
            start_date = options['scheduler_start_date']
            _ = page.evaluate(f'$("#id_{prefix}scheduler_start_date").val("{start_date}")')

    # .. Request tab - the operation, message rows, message map, SOAP header rows and WS-Addressing ..
    request_fields = ('request_operation', 'request_message_map', 'wsa_action', 'wsa_to', 'wsa_reply_to')
    request_row_kinds = ('message', 'soap_headers')

    has_request_fields = any(name in options for name in request_fields)
    has_request_rows = any(f'request_{kind}' in options for kind in request_row_kinds)

    if has_request_fields or has_request_rows:
        activate_soap_tab(page, action, 'request')

        if 'request_operation' in options:
            page.fill(f'#id_{prefix}request_operation', options['request_operation'])

        for kind in request_row_kinds:
            if rows := options.get(f'request_{kind}'):
                for row in rows:
                    add_soap_param_row(page, action, kind, row['key'], row['value'], row.get('mode', 'text'))

        if 'request_message_map' in options:
            page.fill(f'#id_{prefix}request_message_map', options['request_message_map'])

        for name in ('wsa_action', 'wsa_to', 'wsa_reply_to'):
            if name in options:
                page.fill(f'#id_{prefix}{name}', options[name])

    # .. Response tab ..
    if 'response_map' in options:
        activate_soap_tab(page, action, 'response')

        if 'response_map_mode' in options:
            _ = page.select_option(f'#id_{prefix}response_map_mode', options['response_map_mode'])

        page.fill(f'#id_{prefix}response_map', options['response_map'])

    # .. Callback tab ..
    if callback_type := options.get('callback_type'):
        activate_soap_tab(page, action, 'callback')
        _ = page.select_option(f'#id_{prefix}callback_type', callback_type)

        if callback_type == 'service':
            _set_chosen_select(page, f'#id_{prefix}callback_service', options['callback_name'])
        elif callback_type == 'topic':
            page.fill(f'#id_{prefix}callback_topic', options['callback_name'])
        else:
            _set_chosen_select(page, f'#id_{prefix}callback_rest', options['callback_name'])

    # .. and the Health check tab.
    if 'health_check_run_every' in options:
        activate_soap_tab(page, action, 'health_check')
        page.fill(f'#id_{prefix}health_check_run_every', options['health_check_run_every'])

        if 'health_check_run_unit' in options:
            _ = page.select_option(f'#id_{prefix}health_check_run_unit', options['health_check_run_unit'])

        if 'health_check_notify_on' in options:
            _ = page.select_option(f'#id_{prefix}health_check_notify_on', options['health_check_notify_on'])

        if health_check_callback_type := options.get('health_check_callback_type'):
            _ = page.select_option(f'#id_{prefix}health_check_callback_type', health_check_callback_type)

            if health_check_callback_type == 'service':
                _set_chosen_select(
                    page, f'#id_{prefix}health_check_callback_service', options['health_check_callback_name'])
            elif health_check_callback_type == 'topic':
                page.fill(f'#id_{prefix}health_check_callback_topic', options['health_check_callback_name'])
            else:
                _set_chosen_select(
                    page, f'#id_{prefix}health_check_callback_rest', options['health_check_callback_name'])

    # The form goes back to its first tab so the submit flow always starts from the same place
    activate_soap_tab(page, action, 'main')

# ################################################################################################################################
# ################################################################################################################################
#
# The scheduler page
#
# ################################################################################################################################
# ################################################################################################################################

def job_row_exists(page:'Page', base_url:'str', job_name:'str') -> 'bool':
    """ Returns True if the scheduler page shows a job of the given name.
    """
    _ = page.goto(f'{base_url}/zato/scheduler/?cluster=1')
    page.wait_for_selector('#data-table', state='visible')

    row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{job_name}"))')
    out = row is not None

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Invoking the declarative REST invoker service
#
# ################################################################################################################################
# ################################################################################################################################

def invoke_rest_declarative_from_service(api_client:'any_', outconn_name:'str') -> 'anydict':
    """ Runs an outgoing REST connection through its declarative profile from inside
    the boot-deployed invoker service and returns what the connection received back.
    """
    request = {
        'mode': 'invoke',
        'outconn_name': outconn_name,
    }

    response = api_client.invoke(REST_Declarative_Invoker_Service, request)

    if isinstance(response, str):
        response = json.loads(response)

    out = response
    return out

# ################################################################################################################################

def wait_for_rest_declarative_invoker(api_client:'any_', timeout:'float'=Delivery_Timeout) -> 'None':
    """ Polls the boot-deployed declarative invoker service until it responds to a readiness probe.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            response = api_client.invoke(REST_Declarative_Invoker_Service, {'mode': 'ping'})
        except Exception as probe_error:
            logger.info('[wait_for_rest_declarative_invoker] not ready yet: %s', probe_error)
        else:
            logger.info('[wait_for_rest_declarative_invoker] ready: %s', response)
            return

        time.sleep(_Poll_Interval)

    raise Exception(f'Service `{REST_Declarative_Invoker_Service}` did not deploy within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
