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
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from http_test_server import HTTPSTestServer, HTTPTestServer
from rest_channel import deploy_service_file
from rest_outconn import Outconn_Invoker_Service_Source, create_outconn, edit_outconn, invoke_outconn_from_service, \
    ping_outconn_until_success, wait_for_invoker_service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.live.' + rand_string() + '.'

# How long to keep invoking while a UI change propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the invocations above
_Propagation_Poll_Interval = 0.5

# Log patterns produced when TLS validation rejects the self-signed certificate
_TLS_Failure_Log_Patterns = ('certificate verify failed', 'SSLError', 'Max retries exceeded', 'CERTIFICATE_VERIFY_FAILED')

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

@pytest.fixture()
def https_test_server() -> 'any_':
    """ A live recording HTTPS server with a self-signed certificate for the duration of a single test.
    """

    server = HTTPSTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def invoker_service(zato_dashboard:'anydict', api_client:'ZatoClient') -> 'any_':
    """ Hot-deploys the outgoing connection invoker service for the duration of this module.
    """

    server_dir = zato_dashboard['server_dir']
    file_path = deploy_service_file(server_dir, 'test_rest_outconn_invoker.py', Outconn_Invoker_Service_Source)

    wait_for_invoker_service(api_client)

    yield

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnLive:
    """ Tests for calling outgoing REST connections from inside a hot-deployed service,
    which is the same code path production services use.
    """

# ################################################################################################################################

    def test_service_post_and_get(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        invoker_service:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ Calls the connection from inside a service with POST and a body, then with GET
        and query parameters, verifying both the recorded traffic and what the service received back.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'post-get'
        url_path = '/test/outconn/live-post-get/' + rand_string()

        server_response = {'received': 'by the live test server'}
        http_test_server.set_response(url_path, body=json.dumps(server_response))

        # Create the connection and wait for it to propagate ..
        _ = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        _ = ping_outconn_until_success(page, outconn_name)
        http_test_server.clear_requests()

        # .. POST a body through the service ..
        request_body = '{"phrase": "From inside a service"}'
        result = invoke_outconn_from_service(api_client, outconn_name, method='POST', data=request_body)

        logger.info('[test_service_post_and_get] post result=%s', result)

        # .. the service saw the test server's response ..
        assert result['status_code'] == OK, f'Expected OK from the connection, got: {result}'
        assert json.loads(result['text']) == server_response, f'Expected the server response, got: {result}'

        # .. and the server recorded the POST with its body ..
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        assert request['method'] == 'POST', f'Expected a POST request, got: {request}'
        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'
        assert json.loads(request['body']) == {'phrase': 'From inside a service'}, \
            f'Expected the body the service sent, got: {request}'

        # .. now GET with query parameters ..
        http_test_server.clear_requests()

        result = invoke_outconn_from_service(api_client, outconn_name, method='GET', params={'region': 'emea'})

        logger.info('[test_service_post_and_get] get result=%s', result)

        assert result['status_code'] == OK, f'Expected OK from the connection, got: {result}'

        # .. and the server recorded the GET with the query string.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        assert request['method'] == 'GET', f'Expected a GET request, got: {request}'
        assert request['query'] == {'region': 'emea'}, f'Expected the query parameters, got: {request}'

# ################################################################################################################################

    def test_data_format_json_serializes_dict(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        invoker_service:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A connection with data_format=json serializes the dict a service passes,
        which the test server receives as a JSON document with the JSON content type.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'data-format-json'
        url_path = '/test/outconn/live-json/' + rand_string()

        # Create the connection with data_format=json ..
        _ = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'data_format': 'json',
        })

        _ = ping_outconn_until_success(page, outconn_name)
        http_test_server.clear_requests()

        # .. the service passes a dict, not a string ..
        request_data = {'phrase': 'A dict, not a string', 'count': 3}
        result = invoke_outconn_from_service(api_client, outconn_name, method='POST', data=request_data)

        logger.info('[test_data_format_json_serializes_dict] result=%s', result)

        assert result['status_code'] == OK, f'Expected OK from the connection, got: {result}'

        # .. and the server received it serialized to JSON with the matching content type.
        requests = http_test_server.wait_for_request_count(1)
        request = requests[0]

        assert json.loads(request['body']) == request_data, f'Expected the dict serialized to JSON, got: {request}'
        assert request['headers']['Content-Type'] == 'application/json', \
            f'Expected the JSON content type, got: {request}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_TLS_Failure_Log_Patterns)
    def test_validate_tls(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        invoker_service:'any_',
        https_test_server:'HTTPSTestServer',
        ) -> 'None':
        """ A connection with validate_tls=No accepts the test server's self-signed certificate,
        while flipping validate_tls to Yes makes the same call fail with a TLS verification error.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'validate-tls'
        url_path = '/test/outconn/live-tls/' + rand_string()

        # Create the connection over HTTPS with TLS validation off ..
        outconn_id = create_outconn(page, base_url, outconn_name, https_test_server.address, {
            'url_path': url_path,
            'validate_tls': 'False',
        })

        _ = ping_outconn_until_success(page, outconn_name)
        https_test_server.clear_requests()

        # .. the call goes through despite the self-signed certificate ..
        result = invoke_outconn_from_service(api_client, outconn_name, method='POST', data='{"check": "tls"}')

        logger.info('[test_validate_tls] result=%s', result)

        assert result['status_code'] == OK, f'Expected OK with validate_tls off, got: {result}'

        requests = https_test_server.wait_for_request_count(1)
        request = requests[0]
        assert request['path'] == url_path, f'Expected path "{url_path}", got: {request}'

        # .. turn TLS validation on ..
        edit_outconn(page, outconn_id, {
            'validate_tls': 'True',
        })

        # .. and once the change propagates, the same call fails with a verification error.
        deadline = time.monotonic() + _Propagation_Timeout

        while True:
            try:
                result = invoke_outconn_from_service(
                    api_client, outconn_name, method='POST', data='{"check": "tls"}')
            except Exception as tls_error:
                error_text = str(tls_error)
                break
            else:
                logger.info('[test_validate_tls] still passing, waiting for propagation: %s', result)
                error_text = ''

            # The edit has not propagated yet, so give it a moment unless the deadline passed.
            if time.monotonic() >= deadline:
                break

            time.sleep(_Propagation_Poll_Interval)

        assert 'certificate verify failed' in error_text, \
            f'Expected a TLS verification error, got: "{error_text}"'

# ################################################################################################################################
# ################################################################################################################################
