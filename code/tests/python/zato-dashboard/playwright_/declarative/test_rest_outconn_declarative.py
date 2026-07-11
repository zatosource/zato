# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import activate_rest_tab, Callback_Store_Service, fill_rest_invocation_tabs, \
    invoke_rest_declarative_from_service, job_row_exists, wait_for_callback_entry, wait_for_rest_declarative_invoker
from http_test_server import HTTPTestServer
from rest_outconn import delete_outconn, fill_outconn_form, get_outconn_id, open_edit_dialog, open_outconn_page, \
    ping_outconn_until_success, wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.declarative.' + rand_string() + '.'

# The default user profile displays dates as day-first
_Past_Start_Date = '01-01-2020 00:00:00'
_Future_Start_Date = '01-01-2099 00:00:00'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server for the duration of a single test.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def declarative_invoker(zato_dashboard:'anydict', api_client:'ZatoClient') -> 'any_':
    """ Waits for the boot-deployed declarative invoker service, shared by this module's tests.
    """
    wait_for_rest_declarative_invoker(api_client)
    yield

# ################################################################################################################################
# ################################################################################################################################

def create_declarative_outconn(
    page:'Page',
    base_url:'str',
    name:'str',
    host:'str',
    base_options:'anydict',
    invocation_options:'anydict',
    ) -> 'str':
    """ Creates an outgoing REST connection with its invocation tabs filled in and returns its ID.
    """

    # Navigate to the outgoing REST connections page and open the create dialog ..
    open_outconn_page(page, base_url)
    open_create_dialog(page)

    # .. fill the Config tab ..
    form_data = {
        'name': name,
        'host': host,
    } # type: anydict
    form_data.update(base_options)

    if 'security' not in form_data:
        if 'security_value' not in form_data:
            form_data['security_value'] = ZATO_NONE

    fill_outconn_form(page, form_data)

    # .. fill the invocation tabs ..
    fill_rest_invocation_tabs(page, invocation_options, 'create')

    # .. submit and wait for the row.
    submit_create_form(page)
    _ = wait_for_outconn_row(page, name)

    out = get_outconn_id(page, name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnDeclarative:
    """ Tests for the declarative invocation profile of outgoing REST connections - the tabbed UI,
    no-argument invocations from services, JSONata evaluation, response mapping, callbacks,
    scheduled invocations and health checks.
    """

# ################################################################################################################################

    def test_tabs_round_trip(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ Values entered across all the tabs at create time come back in the edit dialog,
        the linked jobs appear on the scheduler page and deleting the connection removes them.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'round-trip'
        url_path = '/test/declarative/round-trip/' + rand_string()

        # Create the connection with every tab filled in ..
        outconn_id = create_declarative_outconn(
            page, base_url, name, http_test_server.address,
            {'url_path': url_path},
            {
                'scheduler_run_every': '30',
                'scheduler_run_unit': 'minutes',
                'scheduler_start_date': _Future_Start_Date,
                'request_method': 'PUT',
                'request_query_string': [{'key': 'region', 'value': 'emea'}],
                'request_headers': [{'key': 'X-Test-Round-Trip', 'value': 'yes'}],
                'request_data': '{"phrase": "declarative round trip"}',
                'response_map': 'payload',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
                'health_check_run_every': '45',
                'health_check_run_unit': 'minutes',
                'health_check_notify_on': 'all',
                'health_check_callback_type': 'service',
                'health_check_callback_name': Callback_Store_Service,
            })

        # .. both linked jobs exist on the scheduler page ..
        assert job_row_exists(page, base_url, 'rest.' + name), f'Job "rest.{name}" should exist after create'
        assert job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should exist after create'

        # .. reopen the edit dialog - every value entered must come back ..
        open_outconn_page(page, base_url)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-scheduler_run_every') == '30'
        assert page.input_value('#id_edit-scheduler_run_unit') == 'minutes'
        assert '2099' in page.input_value('#id_edit-scheduler_start_date')

        assert page.input_value('#id_edit-request_method') == 'PUT'
        assert page.input_value('#id_edit-request_data') == '{"phrase": "declarative round trip"}'

        query_rows = json.loads(page.input_value('#id_edit-request_query_string'))
        assert query_rows == [{'key': 'region', 'value': 'emea', 'mode': 'text'}], \
            f'Expected the query row back, got: {query_rows}'

        header_rows = json.loads(page.input_value('#id_edit-request_headers'))
        assert header_rows == [{'key': 'X-Test-Round-Trip', 'value': 'yes', 'mode': 'text'}], \
            f'Expected the header row back, got: {header_rows}'

        # .. the row widgets themselves are rendered too ..
        row_key_value = page.input_value('#request-query_string-rows-edit .request-param-key')
        assert row_key_value == 'region', f'Expected the query row widget, got: "{row_key_value}"'

        assert page.input_value('#id_edit-response_map') == 'payload'
        assert page.input_value('#id_edit-response_map_mode') == 'jsonata'

        assert page.input_value('#id_edit-callback_type') == 'service'
        assert page.input_value('#id_edit-callback_service') == Callback_Store_Service

        assert page.input_value('#id_edit-health_check_run_every') == '45'
        assert page.input_value('#id_edit-health_check_notify_on') == 'all'
        assert page.input_value('#id_edit-health_check_callback_type') == 'service'
        assert page.input_value('#id_edit-health_check_callback_service') == Callback_Store_Service

        # .. change one value through the edit form and save - the field lives
        # on the Request tab, which must be active for the fill to see it ..
        activate_rest_tab(page, 'edit', 'request')
        page.fill('#id_edit-request_method', 'PATCH')
        submit_edit_form(page)

        # .. reopen to confirm the change stuck and nothing else was lost ..
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-request_method') == 'PATCH'
        assert page.input_value('#id_edit-scheduler_run_every') == '30'

        query_rows = json.loads(page.input_value('#id_edit-request_query_string'))
        assert query_rows == [{'key': 'region', 'value': 'emea', 'mode': 'text'}], \
            f'Expected the query row to survive the edit, got: {query_rows}'

        page.click('#edit-div button:has-text("Cancel")')
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

        # .. delete the connection ..
        delete_outconn(page, outconn_id)

        # .. and both linked jobs are gone with it.
        assert not job_row_exists(page, base_url, 'rest.' + name), f'Job "rest.{name}" should be gone after delete'
        assert not job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should be gone after delete'

# ################################################################################################################################

    def test_declarative_invoke_with_callback(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A no-argument self.rest[name].invoke() fills in the method, query string - including
        a JSONata value evaluated at call time - headers and body from the connection's profile,
        and the response-mapped result lands in the configured callback service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'invoke'
        marker = rand_string()
        url_path = '/test/declarative/invoke/' + rand_string()

        # The response carries a nested payload that the response map extracts
        server_response = {'payload': {'marker': marker, 'user_id': 42}, 'noise': 'dropped by the map'}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the connection - the profile carries everything an invocation needs ..
        _ = create_declarative_outconn(
            page, base_url, name, http_test_server.address,
            {'url_path': url_path, 'data_format': 'json'},
            {
                'request_method': 'PUT',
                'request_query_string': [
                    {'key': 'region', 'value': 'emea'},
                    {'key': 'batch', 'value': '"batch" & "-" & "7"', 'mode': 'jsonata'},
                ],
                'request_headers': [{'key': 'X-Test-Declarative', 'value': 'yes'}],
                'request_data': '{"phrase": "from the declarative profile"}',
                'response_map': 'payload',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        _ = ping_outconn_until_success(page, name)
        http_test_server.clear_requests()

        # .. run the connection from inside a service with no arguments at all ..
        result = invoke_rest_declarative_from_service(api_client, name)

        logger.info('[test_declarative_invoke_with_callback] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'

        # .. the test server received exactly what the profile describes ..
        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert request['method'] == 'PUT', f'Expected the declarative method, got: {request}'
        assert request['query'] == {'region': 'emea', 'batch': 'batch-7'}, \
            f'Expected the declarative query string with the JSONata value evaluated, got: {request}'
        assert request['headers']['X-Test-Declarative'] == 'yes', f'Expected the declarative header, got: {request}'
        assert json.loads(request['body']) == {'phrase': 'from the declarative profile'}, \
            f'Expected the declarative body, got: {request}'

        # .. and the callback received the response-mapped result in the background.
        entry = wait_for_callback_entry(marker)
        assert entry == {'marker': marker, 'user_id': 42}, f'Expected the mapped payload, got: {entry}'

# ################################################################################################################################

    def test_path_params_fill_url_placeholders(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ Declarative path parameters fill in the {placeholders} of the connection's URL path.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'path-params'
        token = rand_string()

        # The URL path carries a placeholder that the profile's path params fill in
        url_path = '/test/declarative/path/{region}/' + token
        resolved_path = '/test/declarative/path/emea/' + token

        http_test_server.set_response(resolved_path, body='{"resolved": true}')

        _ = create_declarative_outconn(
            page, base_url, name, http_test_server.address,
            {'url_path': url_path},
            {
                'request_method': 'GET',
                'request_path_params': [{'key': 'region', 'value': 'emea'}],
            })

        http_test_server.clear_requests()

        # Run the connection - the placeholder resolves from the profile
        result = invoke_rest_declarative_from_service(api_client, name)

        logger.info('[test_path_params_fill_url_placeholders] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'

        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert request['method'] == 'GET', f'Expected a GET request, got: {request}'
        assert request['path'] == resolved_path, f'Expected the resolved path "{resolved_path}", got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('test.rest.outconn.declarative')
    def test_scheduler_fires_the_connection(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A connection with a scheduler configured is invoked by the actual scheduler process,
        with no service call involved at all - the test server receives the declarative request
        and the callback receives the mapped response.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'scheduled'
        marker = rand_string()
        url_path = '/test/declarative/scheduled/' + rand_string()

        server_response = {'payload': {'marker': marker, 'source': 'scheduler'}}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the connection with a one-second schedule that started in the past,
        # so the scheduler begins firing it right away ..
        outconn_id = create_declarative_outconn(
            page, base_url, name, http_test_server.address,
            {'url_path': url_path, 'data_format': 'json'},
            {
                'scheduler_run_every': '1',
                'scheduler_run_unit': 'seconds',
                'scheduler_start_date': _Past_Start_Date,
                'request_method': 'POST',
                'request_data': '{"origin": "scheduled"}',
                'response_map': 'payload',
                'response_map_mode': 'jsonata',
                'callback_type': 'service',
                'callback_name': Callback_Store_Service,
            })

        # .. the scheduler fires the job, which sends the declarative request to the test server ..
        requests = http_test_server.wait_for_request_count(2, timeout=60)
        request = requests[-1]

        assert request['method'] == 'POST', f'Expected the declarative method from the scheduler, got: {request}'
        assert request['path'] == url_path, f'Expected the connection path, got: {request}'
        assert json.loads(request['body']) == {'origin': 'scheduled'}, \
            f'Expected the declarative body from the scheduler, got: {request}'

        # .. and each scheduled invocation delivered the mapped response to the callback.
        entry = wait_for_callback_entry(marker)
        assert entry == {'marker': marker, 'source': 'scheduler'}, f'Expected the mapped payload, got: {entry}'

        # Clean up - the connection would otherwise keep firing every second
        delete_outconn(page, outconn_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors('test.rest.outconn.declarative')
    def test_health_check_pings_and_notifies(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A connection with a health check configured is pinged by the scheduler and each outcome
        is delivered to the callback service, including the response time and the health flag.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'health.' + rand_string()
        url_path = '/test/declarative/health/' + rand_string()

        http_test_server.set_response(url_path, body='{"pong": true}')

        # Create the connection with a one-second health check notifying on every outcome ..
        outconn_id = create_declarative_outconn(
            page, base_url, name, http_test_server.address,
            {'url_path': url_path},
            {
                'health_check_run_every': '1',
                'health_check_run_unit': 'seconds',
                'health_check_notify_on': 'all',
                'health_check_callback_type': 'service',
                'health_check_callback_name': Callback_Store_Service,
            })

        # .. the scheduler pings the connection ..
        _ = http_test_server.wait_for_request_count(1, timeout=60)

        # .. and the callback receives a healthy outcome - the connection's own name
        # is the marker since every outcome carries it.
        entry = wait_for_callback_entry(name)

        assert entry['conn_name'] == name, f'Expected the connection name in the outcome, got: {entry}'
        assert entry['is_ok'] is True, f'Expected a healthy outcome, got: {entry}'
        assert entry['error'] == '', f'Expected no error in a healthy outcome, got: {entry}'
        assert entry['response_time_ms'] >= 0, f'Expected a response time, got: {entry}'

        # Clean up - the health check would otherwise keep pinging every second
        delete_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
