# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.soap.common import FaultCode
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import Callback_Store_Service, fill_soap_invocation_tabs, job_row_exists, wait_for_callback_entry
from soap_outconn import delete_soap_outconn, fill_soap_outconn_form, get_soap_outconn_id, invoke_service_in_ide, \
    open_edit_dialog, open_soap_invoker_in_ide, open_soap_outconn_page, wait_for_soap_invoker_service, \
    wait_for_soap_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.soap.outconn.declarative.' + rand_string() + '.'

# The default user profile displays dates as day-first
_Past_Start_Date = '01-01-2020 00:00:00'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def create_declarative_soap_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    host:'str',
    base_options:'anydict',
    invocation_options:'anydict',
    ) -> 'str':
    """ Creates an outgoing SOAP connection with its invocation tabs filled in and returns its ID.
    """

    # Navigate to the outgoing SOAP connections page and open the create dialog ..
    open_soap_outconn_page(page, base_url)
    open_create_dialog(page)

    # .. fill the base tabs ..
    form_data = {
        'name': name,
        'host': host,
    } # type: anydict
    form_data.update(base_options)

    if 'security' not in form_data:
        if 'security_value' not in form_data:
            form_data['security_value'] = ZATO_NONE

    fill_soap_outconn_form(page, form_data)

    # .. fill the invocation tabs ..
    fill_soap_invocation_tabs(page, invocation_options, 'create')

    # .. submit and wait for the row.
    submit_create_form(page)
    _ = wait_for_soap_outconn_row(page, name)

    out = get_soap_outconn_id(page, name)
    return out

# ################################################################################################################################

def invoke_declarative_with_retry(page:'Page', base_url:'str', outconn_name:'str', operation:'str') -> 'anydict':
    """ Runs an outgoing SOAP connection through its declarative profile - self.soap[name].invoke()
    with no arguments - from the pre-deployed service driven in the IDE, retrying while
    the connection configured a moment ago in the browser propagates to the server.
    """

    request = {
        'mode': 'invoke_declarative',
        'outconn_name': outconn_name,
        'operation': operation,
        'response_fields': ['status'],
    }

    open_soap_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_service_in_ide(page, request)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            if error := (out.get('error') or out.get('fault_code')):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return out

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################

def invoke_declarative_expecting_fault(page:'Page', base_url:'str', outconn_name:'str') -> 'anydict':
    """ Runs a declarative invocation that is expected to end in a SOAP fault - retries only
    while the connection configured a moment ago in the browser propagates to the server,
    a fault code in the reply is the final answer, not a reason to retry.
    """

    request = {
        'mode': 'invoke_declarative',
        'outconn_name': outconn_name,
    }

    open_soap_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_service_in_ide(page, request)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
            continue

        # A fault code means the connection is up and the endpoint answered with the fault
        if out.get('fault_code'):
            return out

        last_error = out.get('error')
        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'No fault arrived from `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnDeclarative:
    """ Tests for the declarative invocation profile of outgoing SOAP connections - the operation
    and message rows, JSONata values, SOAP headers, response mapping with the JSONata/XPath toggle,
    callbacks and scheduled invocations.
    """

# ################################################################################################################################

    def test_tabs_round_trip(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ Values entered across the SOAP invocation tabs at create time come back
        in the edit dialog and the linked job appears on the scheduler page.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'round-trip'
        path = '/declarative-round-trip'

        # Create the connection with the invocation tabs filled in ..
        outconn_id = create_declarative_soap_outconn(
            page, base_url, name, soap_test_server.address,
            {'url_path': path, 'soap_version': '1.2'},
            {
                'scheduler_run_every': '30',
                'scheduler_run_unit': 'minutes',
                'scheduler_start_date': '01-01-2099 00:00:00',
                'request_operation': 'getItemDetails',
                'request_message': [{'key': 'order.item_id', 'value': 'ITEM-01'}],
                'request_soap_headers': [{'key': 'ClientContext', 'value': 'test-suite'}],
                'response_map': 'getItemDetailsResponse',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        # .. the linked job exists on the scheduler page ..
        assert job_row_exists(page, base_url, 'soap.' + name), f'Job "soap.{name}" should exist after create'

        # .. reopen the edit dialog - every value entered must come back ..
        open_soap_outconn_page(page, base_url)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-scheduler_run_every') == '30'
        assert page.input_value('#id_edit-request_operation') == 'getItemDetails'

        message_rows = json.loads(page.input_value('#id_edit-request_message'))
        assert message_rows == [{'key': 'order.item_id', 'value': 'ITEM-01', 'mode': 'text'}], \
            f'Expected the message row back, got: {message_rows}'

        header_rows = json.loads(page.input_value('#id_edit-request_soap_headers'))
        assert header_rows == [{'key': 'ClientContext', 'value': 'test-suite', 'mode': 'text'}], \
            f'Expected the SOAP header row back, got: {header_rows}'

        assert page.input_value('#id_edit-response_map') == 'getItemDetailsResponse'
        assert page.input_value('#id_edit-response_map_mode') == 'jsonata'

        assert page.input_value('#id_edit-callback_type') == 'service'
        assert page.input_value('#id_edit-callback_service') == Callback_Store_Service

        page.click('#edit-div button:has-text("Cancel")')
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

        # .. delete the connection ..
        delete_soap_outconn(page, outconn_id)

        # .. and the linked job is gone with it.
        assert not job_row_exists(page, base_url, 'soap.' + name), f'Job "soap.{name}" should be gone after delete'

# ################################################################################################################################

    def test_declarative_invoke_builds_message_and_headers(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ A no-argument self.soap[name].invoke() builds the operation and message from the rows -
        including a JSONata value evaluated at call time - injects the declarative SOAP headers
        into the envelope and the callback receives the mapped response.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'invoke'
        marker = rand_string()
        path = '/declarative-invoke'

        soap_test_server.configure(path)

        # Create the connection - the profile carries the operation, the message rows
        # and a custom SOAP header ..
        _ = create_declarative_soap_outconn(
            page, base_url, name, soap_test_server.address,
            {'url_path': path, 'soap_version': '1.2'},
            {
                'request_operation': 'submitReading',
                'request_message': [
                    {'key': 'meter.serial', 'value': 'MTR-1001'},
                    {'key': 'meter.batch', 'value': f'"{marker}" & "-" & "1"', 'mode': 'jsonata'},
                ],
                'request_soap_headers': [{'key': 'ClientContext', 'value': 'declarative-suite'}],
                'response_map': '{"status": submitReadingResponse.status, "marker": "' + marker + '"}',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        soap_test_server.clear_requests()

        # .. run the connection with no arguments at all ..
        result = invoke_declarative_with_retry(page, base_url, name, 'submitReading')

        logger.info('[test_declarative_invoke_builds_message_and_headers] result=%s', result)

        # .. the endpoint answered the declarative operation ..
        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # .. the message was built from the rows, with the JSONata value evaluated ..
        operation = soap_test_server.last_request['body'].submitReading
        assert str(operation.meter.serial) == 'MTR-1001', f'Expected the text row value, got: {operation.meter.serial}'
        assert str(operation.meter.batch) == f'{marker}-1', f'Expected the JSONata value, got: {operation.meter.batch}'

        # .. the declarative SOAP header travelled in the envelope ..
        envelope = soap_test_server.last_request['envelope']

        header_element = None
        for element in envelope.iter():
            if element.tag.rpartition('}')[2] == 'ClientContext':
                header_element = element
                break

        assert header_element is not None, 'Expected the declarative SOAP header in the envelope'
        assert header_element.text == 'declarative-suite', f'Expected the header value, got: {header_element.text}'

        # .. and the callback received the mapped response.
        entry = wait_for_callback_entry(marker)
        assert entry == {'status': 'ok', 'marker': marker}, f'Expected the mapped response, got: {entry}'

# ################################################################################################################################

    def test_response_map_xpath(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ With the XPath mode selected, the response map runs against the raw response XML
        and the callback receives what the expression selected.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'xpath'
        marker = rand_string()
        path = '/declarative-xpath'

        # The endpoint answers with a prepared envelope that carries a unique reference
        # element - the XPath map selects its text and that is what the callback receives.
        raw_envelope = (
            '<?xml version="1.0"?>'
            '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
            '<soap:Body>'
            '<checkStatusResponse>'
            '<status>ok</status>'
            f'<reference>{marker}-ref</reference>'
            '</checkStatusResponse>'
            '</soap:Body>'
            '</soap:Envelope>'
        )
        soap_test_server.configure(path, respond_raw=(200, raw_envelope.encode(), 'application/soap+xml; charset=utf-8'))

        _ = create_declarative_soap_outconn(
            page, base_url, name, soap_test_server.address,
            {'url_path': path, 'soap_version': '1.2'},
            {
                'request_operation': 'checkStatus',
                'request_message': [{'key': 'request_id', 'value': name}],
                'response_map': '//reference/text()',
                'response_map_mode': 'xpath',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        soap_test_server.clear_requests()

        # Run the connection - the endpoint answers with the prepared envelope
        result = invoke_declarative_with_retry(page, base_url, name, 'checkStatus')

        logger.info('[test_response_map_xpath] result=%s', result)

        assert result['fields']['status'] == 'ok', f'Expected an ok response, got: {result}'

        # The message row carried the request id to the endpoint ..
        operation = soap_test_server.last_request['body'].checkStatus
        assert str(operation.request_id) == name, f'Expected the request id, got: {operation.request_id}'

        # .. and the callback received exactly what the XPath selected.
        entry = wait_for_callback_entry(marker)
        assert entry == f'{marker}-ref', f'Expected the XPath-selected value, got: {entry}'

# ################################################################################################################################

    def test_fault_routed_to_callback_and_reraised(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ When the endpoint answers with a soap:Fault, the callback receives the fault payload
        with is_fault set while the calling service sees the SOAPFault re-raised unchanged.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'fault'
        marker = rand_string()
        path = '/declarative-fault'

        # The endpoint always faults on this path - the reason carries the marker
        # so the test can find its own callback delivery.
        fault_reason = f'Backend unavailable {marker}'
        soap_test_server.configure(path, respond_fault=(FaultCode.Receiver, fault_reason))

        _ = create_declarative_soap_outconn(
            page, base_url, name, soap_test_server.address,
            {'url_path': path, 'soap_version': '1.2'},
            {
                'request_operation': 'checkStatus',
                'request_message': [{'key': 'request_id', 'value': name}],
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        soap_test_server.clear_requests()

        # Run the connection - the calling service must see the re-raised fault ..
        result = invoke_declarative_expecting_fault(page, base_url, name)

        logger.info('[test_fault_routed_to_callback_and_reraised] result=%s', result)

        assert result['fault_code'] == 'Receiver', f'Expected the fault code, got: {result}'
        assert result['fault_reason'] == fault_reason, f'Expected the fault reason, got: {result}'

        # .. and the callback received the fault payload with the is_fault flag.
        entry = wait_for_callback_entry(marker)
        assert entry == {'is_fault': True, 'code': 'Receiver', 'reason': fault_reason, 'detail': {}}, \
            f'Expected the fault payload, got: {entry}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('test.soap.outconn.declarative')
    def test_scheduler_fires_the_connection(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ A SOAP connection with a scheduler configured is invoked by the actual scheduler process,
        with no service call involved - the endpoint receives the declarative operation and message
        and the callback receives the mapped response.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'scheduled'
        marker = rand_string()
        path = '/declarative-scheduled'

        soap_test_server.configure(path)
        soap_test_server.clear_requests()

        # Create the connection with a one-second schedule that started in the past,
        # so the scheduler begins firing it right away ..
        outconn_id = create_declarative_soap_outconn(
            page, base_url, name, soap_test_server.address,
            {'url_path': path, 'soap_version': '1.2'},
            {
                'scheduler_run_every': '1',
                'scheduler_run_unit': 'seconds',
                'scheduler_start_date': _Past_Start_Date,
                'request_operation': 'pollUpdates',
                'request_message': [{'key': 'source', 'value': 'scheduler'}],
                'response_map': '{"status": pollUpdatesResponse.status, "marker": "' + marker + '"}',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        # .. the scheduler fires the job, which sends the declarative operation to the endpoint ..
        _ = soap_test_server.wait_for_request_count(2, timeout=60)

        operation = soap_test_server.last_request['body'].pollUpdates
        assert str(operation.source) == 'scheduler', f'Expected the declarative message, got: {operation.source}'

        # .. and each scheduled invocation delivered the mapped response to the callback.
        entry = wait_for_callback_entry(marker)
        assert entry == {'status': 'ok', 'marker': marker}, f'Expected the mapped response, got: {entry}'

        # Clean up - the connection would otherwise keep firing every second
        delete_soap_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
