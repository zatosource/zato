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
from zato.common.test.playwright_pubsub import create_topic, open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import fill_rest_invocation_tabs, invoke_rest_declarative_from_service, wait_for_rest_declarative_invoker, \
    wait_for_topic_message
from http_test_server import HTTPTestServer
from rest_outconn import create_outconn, fill_outconn_form, get_outconn_id, open_outconn_page, ping_outconn_until_success, \
    wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.callback.' + rand_string() + '.'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server the primary connection points at.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture()
def callback_test_server() -> 'any_':
    """ A second live recording HTTP server that REST callbacks are delivered to.
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

class TestRESTOutconnCallbackTypes:
    """ Tests for the rest and topic callback types of the declarative invocation profile -
    the service type is covered by test_rest_outconn_declarative.py.
    """

# ################################################################################################################################

    def test_rest_callback_delivers_to_second_connection(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        callback_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A rest-type callback delivers the response-mapped result to another outgoing REST
        connection pointing at a second recording server, while the caller receives the raw,
        unmapped response body.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'rest'
        callback_name = _Test_Name_Prefix + 'rest-sink'
        marker = rand_string()

        url_path = '/test/declarative/callback-rest/' + rand_string()
        callback_url_path = '/test/declarative/callback-sink/' + rand_string()

        # The raw response carries a nested payload that the response map extracts for the callback
        server_response = {'payload': {'marker': marker}, 'noise': 'not for the callback'}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the callback connection first so the primary one can select it by name ..
        _ = create_outconn(page, base_url, callback_name, callback_test_server.address, {
            'url_path': callback_url_path,
            'data_format': 'json',
        })

        # .. then the primary connection whose callback is that second connection ..
        _ = _create_outconn_with_profile(
            page, base_url, name, http_test_server.address, url_path,
            {
                'request_method': 'POST',
                'response_map': 'payload',
                'response_map_mode': 'jsonata',
                'callback_type': 'rest',
                'callback_name': callback_name,
            })

        _ = ping_outconn_until_success(page, callback_name)
        _ = ping_outconn_until_success(page, name)

        http_test_server.clear_requests()
        callback_test_server.clear_requests()

        # .. run the primary connection from inside a service ..
        result = invoke_rest_declarative_from_service(api_client, name)

        logger.info('[test_rest_callback_delivers_to_second_connection] result=%s', result)

        # .. the caller received the raw, unmapped response body ..
        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'
        assert json.loads(result['text']) == server_response, \
            f'Expected the caller to receive the raw response body, got: {result}'

        # .. and the second recording server received the mapped payload from the callback.
        callback_requests = callback_test_server.wait_for_request_count(1, timeout=30)
        callback_request = callback_requests[-1]

        assert callback_request['path'] == callback_url_path, \
            f'Expected the callback connection path, got: {callback_request}'
        assert json.loads(callback_request['body']) == {'marker': marker}, \
            f'Expected the mapped payload in the callback delivery, got: {callback_request}'

# ################################################################################################################################

    def test_topic_callback_publishes_to_pubsub(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        declarative_invoker:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A topic-type callback publishes the response-mapped result to a pub/sub topic,
        which the test observes in the SQL pub/sub store.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'topic'
        marker = rand_string()
        url_path = '/test/declarative/callback-topic/' + rand_string()

        server_response = {'payload': {'marker': marker}, 'noise': 'not for the topic'}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the topic the callback publishes to ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'callback-topic')

        # .. and the connection whose callback is that topic ..
        _ = _create_outconn_with_profile(
            page, base_url, name, http_test_server.address, url_path,
            {
                'request_method': 'POST',
                'response_map': 'payload',
                'response_map_mode': 'jsonata',
                'callback_type': 'topic',
                'callback_name': topic['name'],
            })

        _ = ping_outconn_until_success(page, name)
        http_test_server.clear_requests()

        # .. run the connection from inside a service ..
        result = invoke_rest_declarative_from_service(api_client, name)

        logger.info('[test_topic_callback_publishes_to_pubsub] result=%s', result)

        assert result.get('status_code') == OK, f'Expected OK from the declarative invocation, got: {result}'

        # .. and the mapped payload arrived on the topic.
        entry = wait_for_topic_message(topic['name'], marker)

        assert entry['topic_name'] == topic['name'].lower(), f'Expected the topic name in the message, got: {entry}'
        assert marker in entry['data_preview'], f'Expected the marker in the published data, got: {entry}'

# ################################################################################################################################
# ################################################################################################################################
