# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from datetime import datetime, timedelta, timezone
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import fill_rest_invocation_tabs, invoke_rest_declarative_from_service, wait_for_rest_declarative_invoker
from http_test_server import HTTPTestServer
from rest_outconn import fill_outconn_form, find_outconn_row, get_outconn_id, open_outconn_page, \
    ping_outconn_until_success, wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.jsonata.' + rand_string() + '.'

# The JSONata expression computing yesterday's date at call time
_Milliseconds_Per_Day = 86400000
_Yesterday_Expression = "$fromMillis($toMillis($now()) - " + str(_Milliseconds_Per_Day) + ", '[Y0001]-[M01]-[D01]')"

# ################################################################################################################################
# ################################################################################################################################

def _yesterday_utc() -> 'str':
    """ Returns yesterday's date in UTC, the same way the JSONata expression computes it.
    """
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    out = yesterday.strftime('%Y-%m-%d')
    return out

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

def _create_outconn_with_profile(
    page:'Page',
    base_url:'str',
    name:'str',
    host:'str',
    url_path:'str',
    invocation_options:'anydict',
    ) -> 'str':
    """ Creates a JSON outgoing REST connection with its invocation tabs filled in and returns its ID.
    """

    open_outconn_page(page, base_url)
    open_create_dialog(page)

    fill_outconn_form(page, {
        'name': name,
        'host': host,
        'url_path': url_path,
        'data_format': 'json',
        'security_value': ZATO_NONE,
    })

    fill_rest_invocation_tabs(page, invocation_options, 'create')

    submit_create_form(page)
    _ = wait_for_outconn_row(page, name)

    out = get_outconn_id(page, name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnJSONata:
    """ Tests for JSONata evaluation in the declarative invocation profile - query values computed
    at call time, a body reshaping the caller's request data and server-side expression validation.
    """

# ################################################################################################################################

    def test_query_value_computes_yesterdays_date(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A JSONata-mode query-string row computing yesterday's date is evaluated at call time,
        asserted against a date the test computes independently.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'date'
        url_path = '/test/declarative/jsonata-date/' + rand_string()

        _ = _create_outconn_with_profile(
            page, base_url, name, http_test_server.address, url_path,
            {
                'request_method': 'GET',
                'request_query_string': [{'key': 'since', 'value': _Yesterday_Expression, 'mode': 'jsonata'}],
            })

        _ = ping_outconn_until_success(page, name)
        http_test_server.clear_requests()

        # Compute the expected date both before and after the call - if the call straddles
        # midnight UTC, either value is correct.
        date_before = _yesterday_utc()
        result = invoke_rest_declarative_from_service(api_client, name)
        date_after = _yesterday_utc()

        logger.info('[test_query_value_computes_yesterdays_date] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'

        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert request['query']['since'] in (date_before, date_after), \
            f'Expected yesterday\'s date ({date_before} or {date_after}) in the query string, got: {request}'

# ################################################################################################################################

    def test_body_reshapes_caller_data(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A JSONata-mode body is evaluated against the request data the calling service
        passed in, so the profile reshapes the caller's data into the request that goes out.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'body'
        url_path = '/test/declarative/jsonata-body/' + rand_string()

        _ = _create_outconn_with_profile(
            page, base_url, name, http_test_server.address, url_path,
            {
                'request_method': 'POST',
                'request_data': '{"order_id": order_id, "is_priority": quantity > 100}',
                'request_data_mode': 'jsonata',
            })

        _ = ping_outconn_until_success(page, name)
        http_test_server.clear_requests()

        # The caller passes its own request data, which the profile's body expression reshapes
        caller_data = {'order_id': 'order-1', 'quantity': 150}
        result = invoke_rest_declarative_from_service(api_client, name, data=caller_data)

        logger.info('[test_body_reshapes_caller_data] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'

        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert json.loads(request['body']) == {'order_id': 'order-1', 'is_priority': True}, \
            f'Expected the body reshaped from the caller\'s data, got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Invalid jsonata expression', 'Object could not be created')
    def test_invalid_expression_rejected_at_create_time(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ An invalid JSONata expression is rejected by server-side validation at create time,
        the form error message becomes visible and no connection is created.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'invalid'
        url_path = '/test/declarative/jsonata-invalid/' + rand_string()

        # Fill the create form with a query row whose JSONata expression does not compile ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_outconn_form(page, {
            'name': name,
            'host': http_test_server.address,
            'url_path': url_path,
            'security_value': ZATO_NONE,
        })

        fill_rest_invocation_tabs(page, {
            'request_query_string': [{'key': 'since', 'value': '$fromMillis(', 'mode': 'jsonata'}],
        }, 'create')

        # .. submit and wait for the error message to become visible ..
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#user-message-div', state='visible', timeout=10000)

        # .. the message names the invalid expression ..
        message_text = page.inner_text('#user-message')
        assert 'Invalid jsonata expression' in message_text, \
            f'Expected the validation error to be shown, got: "{message_text}"'

        # .. and no connection was created.
        open_outconn_page(page, base_url)
        row = find_outconn_row(page, name)
        assert row is None, f'Expected no connection row after the rejected submission, got one for "{name}"'

# ################################################################################################################################
# ################################################################################################################################
