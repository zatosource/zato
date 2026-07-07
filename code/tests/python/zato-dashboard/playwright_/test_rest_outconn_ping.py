# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
from rest_outconn import create_outconn, edit_outconn, ping_outconn, ping_outconn_until_success

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.ping.' + rand_string() + '.'

# A port from the ephemeral range that nothing listens on in the test environment -
# connections to it are refused, which is what the failure tests need.
_Dead_Port = 1

# Log patterns produced when a ping cannot reach its target
_Ping_Failure_Log_Patterns = ('Connection refused', 'NewConnectionError', 'Max retries exceeded')

# How long to keep pinging while a UI change propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the pings above
_Propagation_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _ping_until_method(
    page:'Page',
    http_test_server:'HTTPTestServer',
    outconn_name:'str',
    expected_method:'str',
    ) -> 'anydict':
    """ Keeps pinging a connection until the test server records the expected HTTP method,
    which covers the propagation delay of a freshly edited ping method. Returns the last
    recorded request, letting the caller assert on it themselves.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:

        # Each attempt looks only at its own traffic ..
        http_test_server.clear_requests()

        ping_result = ping_outconn(page, outconn_name)
        logger.info('[_ping_until_method] ping_result=%s', ping_result)

        requests = http_test_server.wait_for_request_count(1)
        out = requests[0]

        # .. stop as soon as the expected method arrives ..
        if out['method'] == expected_method:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

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
# ################################################################################################################################

class TestRESTOutconnPing:
    """ Tests for pinging outgoing REST connections against a live HTTP server.
    """

# ################################################################################################################################

    def test_ping_default_method(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Pings a connection pointing at the live test server and verifies the server
        received exactly one request with the default ping method and the connection's URL path.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'default-method'
        url_path = '/test/outconn/ping-default/' + rand_string()

        # Create the connection pointing at the live server ..
        _ = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        # .. ping until the freshly created connection propagates to the server ..
        ping_result = ping_outconn_until_success(page, outconn_name)

        logger.info('[test_ping_default_method] ping_result=%s', ping_result)

        assert ping_result['is_success'], f'Expected a successful ping, got: {ping_result}'

        # .. now that the connection is live, a single ping produces exactly one request ..
        http_test_server.clear_requests()

        ping_result = ping_outconn(page, outconn_name)
        assert ping_result['is_success'], f'Expected a successful ping, got: {ping_result}'

        # .. which the server saw as HEAD for the connection's path.
        requests = http_test_server.wait_for_request_count(1)
        request_count = len(requests)

        assert request_count == 1, f'Expected exactly one request, got {request_count}: {requests}'

        request = requests[0]
        assert request['method'] == 'HEAD', f'Expected a HEAD request, got: {request}'
        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'

# ################################################################################################################################

    def test_ping_custom_method(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates a connection with ping_method=GET, verifies the server records GET,
        then edits the method to POST and verifies the server records POST.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'custom-method'
        url_path = '/test/outconn/ping-custom/' + rand_string()

        # Create the connection with a custom ping method ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'ping_method': 'GET',
        })

        # .. ping until the connection propagates, confirming the server saw a GET request ..
        _ = ping_outconn_until_success(page, outconn_name)

        request = _ping_until_method(page, http_test_server, outconn_name, 'GET')
        assert request['method'] == 'GET', f'Expected a GET request, got: {request}'

        # .. switch the ping method to POST ..
        edit_outconn(page, outconn_id, {
            'ping_method': 'POST',
        })

        # .. and the next ping arrives as POST.
        request = _ping_until_method(page, http_test_server, outconn_name, 'POST')
        assert request['method'] == 'POST', f'Expected a POST request after the edit, got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Ping_Failure_Log_Patterns)
    def test_ping_failure(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Pings a connection pointing at a closed port and verifies the failure
        is reported with its details.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'failure'
        url_path = '/test/outconn/ping-failure/' + rand_string()

        # Create the connection pointing at a port nothing listens on ..
        _ = create_outconn(page, base_url, outconn_name, f'http://127.0.0.1:{_Dead_Port}', {
            'url_path': url_path,
        })

        # .. and the ping reports the failure.
        ping_result = ping_outconn(page, outconn_name)

        logger.info('[test_ping_failure] ping_result=%s', ping_result)

        assert not ping_result['is_success'], f'Expected a failed ping, got: {ping_result}'
        assert ping_result['info'], f'Expected failure details in the ping response, got: {ping_result}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Ping_Failure_Log_Patterns)
    def test_ping_recovers_after_edit(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates a connection pointing at a closed port, confirms the ping fails,
        then edits the host to the live server and confirms the ping succeeds.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'recovery'
        url_path = '/test/outconn/ping-recovery/' + rand_string()

        # Create the connection pointing at a port nothing listens on ..
        outconn_id = create_outconn(page, base_url, outconn_name, f'http://127.0.0.1:{_Dead_Port}', {
            'url_path': url_path,
        })

        # .. the ping fails ..
        ping_result = ping_outconn(page, outconn_name)
        assert not ping_result['is_success'], f'Expected a failed ping before the edit, got: {ping_result}'

        # .. point the connection at the live server ..
        edit_outconn(page, outconn_id, {
            'host': http_test_server.address,
        })

        # .. and now the ping succeeds against the live server.
        ping_result = ping_outconn_until_success(page, outconn_name)
        assert ping_result['is_success'], f'Expected a successful ping after the edit, got: {ping_result}'

        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]
        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'

# ################################################################################################################################
# ################################################################################################################################
