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
from rest_outconn import fill_outconn_form, get_outconn_id, open_outconn_page, ping_outconn_until_success, \
    wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.explicit.' + rand_string() + '.'

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

class TestRESTOutconnExplicitArgs:
    """ Tests for the merge of explicit call arguments with a connection's declarative profile -
    what the caller passes always wins while the profile fills in everything else.
    """

# ################################################################################################################################

    def test_explicit_post_wins_over_declarative_method_and_body(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ An explicit self.rest[name].post(data) call uses the explicit method and body
        while the declarative query string and headers are still merged in.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'post-wins'
        url_path = '/test/declarative/explicit/' + rand_string()

        # Create the connection - the profile declares a PUT with its own body,
        # which the explicit call must override ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_outconn_form(page, {
            'name': name,
            'host': http_test_server.address,
            'url_path': url_path,
            'data_format': 'json',
            'security_value': ZATO_NONE,
        })

        fill_rest_invocation_tabs(page, {
            'request_method': 'PUT',
            'request_query_string': [{'key': 'region', 'value': 'emea'}],
            'request_headers': [{'key': 'X-Test-Declarative', 'value': 'yes'}],
            'request_data': '{"phrase": "from the declarative profile"}',
        }, 'create')

        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)
        _ = get_outconn_id(page, name)

        _ = ping_outconn_until_success(page, name)
        http_test_server.clear_requests()

        # .. make an explicit .post() call with its own body from inside a service ..
        explicit_body = {'phrase': 'explicit body'}
        result = invoke_rest_declarative_from_service(api_client, name, mode='post', data=explicit_body)

        logger.info('[test_explicit_post_wins_over_declarative_method_and_body] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the explicit invocation, got: {result}'

        # .. the test server received the explicit method and body ..
        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert request['method'] == 'POST', f'Expected the explicit method to win over the declarative PUT, got: {request}'
        assert json.loads(request['body']) == explicit_body, f'Expected the explicit body to win, got: {request}'

        # .. while the declarative query string and headers were still merged in.
        assert request['query'] == {'region': 'emea'}, f'Expected the declarative query string, got: {request}'
        assert request['headers']['X-Test-Declarative'] == 'yes', f'Expected the declarative header, got: {request}'

# ################################################################################################################################
# ################################################################################################################################
