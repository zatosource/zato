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
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from http_test_server import HTTPTestServer
from rest_outconn import create_outconn, edit_outconn, invoke_outconn_via_overlay, ping_outconn_until_success

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.invoke.' + rand_string() + '.'

# How long the server delays its response in the timeout test, in seconds
_Server_Delay = 3

# How long to keep invoking while an edited timeout propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the invocations above
_Propagation_Poll_Interval = 0.5

# Log patterns produced when an invocation times out
_Timeout_Log_Patterns = ('Read timed out', 'ReadTimeoutError')

# Log patterns produced when an invocation runs before the connection propagates to the server
_Propagation_Log_Patterns = (
    'Outgoing REST connection wrapper',
    'invoke_outconn error',
    'Internal Server Error: /zato/http-soap/invoke-outconn',
)

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
# ################################################################################################################################

def _invoke_until_response(page:'Page', outconn_id:'str', expected_fragment:'str', **invoke_kwargs:'any_') -> 'anydict':
    """ Keeps invoking a connection through the overlay until the expected fragment appears
    in the displayed response, which covers the propagation delay of freshly edited options.
    Returns the last result, letting the caller assert on it themselves.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = invoke_outconn_via_overlay(page, outconn_id, **invoke_kwargs)

        # Stop as soon as the expected response arrives ..
        if expected_fragment in out['response']:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnInvoke:
    """ Tests for the per-row Invoke overlay of outgoing REST connections against a live HTTP server.
    """

# ################################################################################################################################

    def test_invoke_post_with_payload(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Invokes a connection with a JSON payload and verifies both the overlay's response
        and what the test server recorded.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'post-payload'
        url_path = '/test/outconn/invoke-post/' + rand_string()

        request_payload = {'phrase': 'Invoked through the overlay'}
        request_body = json.dumps(request_payload)

        server_response = {'received': 'by the test server'}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the connection and wait for it to propagate ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        _ = ping_outconn_until_success(page, outconn_name)
        http_test_server.clear_requests()

        # .. invoke it through the overlay ..
        result = invoke_outconn_via_overlay(page, outconn_id, request_body=request_body)

        # .. the overlay shows what the test server returned ..
        overlay_parsed = json.loads(result['response'])
        assert overlay_parsed == server_response, f'Expected the server response in the overlay, got: {result}'

        # .. and the server recorded the method, path and body.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        logger.info('[test_invoke_post_with_payload] request=%s', request)

        assert request['method'] == 'POST', f'Expected a POST request, got: {request}'
        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'
        assert json.loads(request['body']) == request_payload, f'Expected the payload in the body, got: {request}'

# ################################################################################################################################

    def test_invoke_with_query_params(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Invokes a connection with query parameters and verifies the server saw them
        in the query string.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'query-params'
        url_path = '/test/outconn/invoke-query/' + rand_string()

        # Create the connection and wait for it to propagate ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        _ = ping_outconn_until_success(page, outconn_name)
        http_test_server.clear_requests()

        # .. invoke it with query parameters ..
        _ = invoke_outconn_via_overlay(page, outconn_id, query_params='region=emea&tenant=main')

        # .. and the server saw them in the query string.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        logger.info('[test_invoke_with_query_params] request=%s', request)

        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'
        assert request['query'] == {'region': 'emea', 'tenant': 'main'}, \
            f'Expected the query parameters, got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Propagation_Log_Patterns)
    def test_invoke_get_with_path_params(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Invokes a connection whose URL path is a template, using GET, and verifies
        the path parameter was substituted into the path the server received.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'path-params'
        path_prefix = '/test/outconn/invoke-path/' + rand_string()
        url_path = path_prefix + '/{phrase}'

        # Create the connection with a templated URL path ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        # .. a templated path cannot be pinged without parameters, so propagation is covered
        # .. by retrying the invocation until the substituted path arrives at the server ..
        result = _invoke_until_response(
            page,
            outconn_id,
            'result',
            method='GET',
            path_params='phrase=hello-from-tests',
            query_params='tenant=main',
        )

        logger.info('[test_invoke_get_with_path_params] result=%s', result)

        # .. and the server saw the substituted path, the method and the query string.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]

        assert request['method'] == 'GET', f'Expected a GET request, got: {request}'
        assert request['path'] == path_prefix + '/hello-from-tests', \
            f'Expected the substituted path, got: {request}'
        assert request['query'] == {'tenant': 'main'}, f'Expected the query parameters, got: {request}'

# ################################################################################################################################

    def test_invoke_content_type(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Sets a custom content type on the connection and verifies the recorded request
        carries it in its Content-Type header.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'content-type'
        url_path = '/test/outconn/invoke-content-type/' + rand_string()

        content_type = 'application/vnd.zato.test+json'

        # Create the connection with a custom content type ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'content_type': content_type,
        })

        _ = ping_outconn_until_success(page, outconn_name)
        http_test_server.clear_requests()

        # .. invoke it ..
        _ = invoke_outconn_via_overlay(page, outconn_id, request_body='{"check": "content type"}')

        # .. and the server saw the configured Content-Type header.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        logger.info('[test_invoke_content_type] request=%s', request)

        assert request['headers']['Content-Type'] == content_type, \
            f'Expected Content-Type "{content_type}", got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Timeout_Log_Patterns)
    def test_invoke_timeout(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Invokes a connection with timeout=1 against a server that delays its response,
        verifies the timeout error is reported, then raises the timeout via edit and verifies
        the same call succeeds.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'timeout'
        url_path = '/test/outconn/invoke-timeout/' + rand_string()

        # Create the connection with a one-second timeout ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'timeout': '1',
        })

        # .. wait for it to propagate while the server still responds instantly ..
        _ = ping_outconn_until_success(page, outconn_name)

        # .. now tell the server to delay its responses past the timeout ..
        http_test_server.set_response(url_path, delay=_Server_Delay)
        http_test_server.clear_requests()

        # .. the invocation reports the timeout ..
        result = invoke_outconn_via_overlay(page, outconn_id, request_body='{"check": "timeout"}')

        logger.info('[test_invoke_timeout] result=%s', result)

        assert 'timed out' in result['response'], f'Expected a timeout error, got: {result}'

        # .. raise the timeout above the server's delay ..
        edit_outconn(page, outconn_id, {
            'timeout': '10',
        })

        # .. and the same call now succeeds once the new timeout propagates.
        result = _invoke_until_response(page, outconn_id, 'result', request_body='{"check": "timeout"}')

        overlay_parsed = json.loads(result['response'])
        assert overlay_parsed == {'result': 'ok'}, f'Expected the server response after the edit, got: {result}'

# ################################################################################################################################
# ################################################################################################################################
