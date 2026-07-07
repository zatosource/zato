# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from base64 import b64encode

# pytest
import pytest

# Zato
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import create_basic_auth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from http_test_server import HTTPTestServer
from rest_channel import create_apikey_definition, create_bearer_token_definition, create_ntlm_definition
from rest_outconn import create_outconn, edit_outconn, find_outconn_row, get_row_cell_texts, invoke_outconn_via_overlay, \
    open_edit_dialog, open_outconn_page, ping_outconn_until_success

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.sec.' + rand_string() + '.'

# The header API key definitions use by default
_API_Key_Header = 'X-API-Key'

# Row cell index with the connection's security definition
_Cell_Security = 6

# How long to keep invoking while a security change propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the invocations above
_Propagation_Poll_Interval = 0.5

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

def _build_basic_auth_header(username:'str', password:'str') -> 'str':
    """ Returns the value of the Authorization header for the given Basic Auth credentials.
    """

    credentials = f'{username}:{password}'
    credentials_bytes = credentials.encode('utf-8')
    encoded = b64encode(credentials_bytes)

    out = 'Basic ' + encoded.decode('utf-8')
    return out

# ################################################################################################################################

def _invoke_and_get_request(page:'Page', http_test_server:'HTTPTestServer', outconn_id:'str') -> 'anydict':
    """ Invokes a connection once through the overlay and returns the single request
    the test server recorded for it.
    """

    http_test_server.clear_requests()

    _ = invoke_outconn_via_overlay(page, outconn_id, request_body='{"check": "security"}')

    requests = http_test_server.wait_for_request_count(1)

    out = requests[0]
    return out

# ################################################################################################################################

def _invoke_until_header(
    page:'Page',
    http_test_server:'HTTPTestServer',
    outconn_id:'str',
    header_name:'str',
    expected_value:'str',
    ) -> 'anydict':
    """ Keeps invoking a connection until the test server records a request whose header
    carries the expected value, an empty value meaning the header must be absent. This covers
    the propagation delay of security changes. Returns the last recorded request, letting
    the caller assert on it themselves.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = _invoke_and_get_request(page, http_test_server, outconn_id)

        # An empty expected value means waiting for the header to disappear ..
        if expected_value:
            has_expected = out['headers'].get(header_name) == expected_value
        else:
            has_expected = header_name not in out['headers']

        # .. stop as soon as the expectation is met ..
        if has_expected:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnSecurity:
    """ Tests for security definitions assigned to outgoing REST connections.
    """

# ################################################################################################################################

    def test_basic_auth_live_header(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates a Basic Auth definition, assigns it to a connection and verifies the test
        server received the matching Authorization header.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'basic-auth'
        url_path = '/test/outconn/sec-basic/' + rand_string()

        # Create the security definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'live-header')

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'security': f'Basic Auth/{definition["name"]}',
        })

        _ = ping_outconn_until_success(page, outconn_name)

        # .. invoke it ..
        request = _invoke_and_get_request(page, http_test_server, outconn_id)

        logger.info('[test_basic_auth_live_header] request=%s', request)

        # .. and the server received the credentials of that definition.
        expected_header = _build_basic_auth_header(definition['username'], definition['password'])
        assert request['headers']['Authorization'] == expected_header, \
            f'Expected Authorization "{expected_header}", got: {request}'

# ################################################################################################################################

    def test_apikey_live_header(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates an API key definition, assigns it to a connection and verifies the test
        server received the key header.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'apikey'
        url_path = '/test/outconn/sec-apikey/' + rand_string()

        # Create the security definition ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'apikey-def')

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'security': f'API key/{definition["name"]}',
        })

        _ = ping_outconn_until_success(page, outconn_name)

        # .. invoke it ..
        request = _invoke_and_get_request(page, http_test_server, outconn_id)

        logger.info('[test_apikey_live_header] request=%s', request)

        # .. and the server received the key header.
        assert request['headers'][_API_Key_Header] == definition['key'], \
            f'Expected the {_API_Key_Header} header with the key, got: {request}'

# ################################################################################################################################

    def test_ntlm_assignment(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an NTLM definition, assigns it to a connection and verifies the assignment
        persists across the row and the edit dialog. NTLM requires a Windows domain so there
        is no live invocation here.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'ntlm'
        url_path = '/test/outconn/sec-ntlm/' + rand_string()

        # Create the security definition ..
        definition = create_ntlm_definition(page, base_url, _Test_Name_Prefix + 'ntlm-def')

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, 'http://rest-sec.example.com:8080', {
            'url_path': url_path,
            'security': f'NTLM/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_outconn_page(page, base_url)
        row = find_outconn_row(page, outconn_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. and the edit dialog has it selected.
        open_edit_dialog(page, outconn_id)

        selected_label = page.evaluate('$("#id_edit-security option:selected").text()')
        expected_label = f'NTLM/{definition["name"]}'
        assert selected_label == expected_label, f'Expected "{expected_label}" selected, got: "{selected_label}"'

# ################################################################################################################################

    def test_bearer_token_assignment(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a Bearer token definition, assigns it to a connection and verifies
        the assignment persists across the row and the edit dialog. Bearer tokens require
        an external identity provider so there is no live invocation here.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'bearer'
        url_path = '/test/outconn/sec-bearer/' + rand_string()

        # Create the security definition ..
        definition = create_bearer_token_definition(page, base_url, _Test_Name_Prefix + 'bearer-def')

        # .. create the connection with that definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, 'http://rest-sec.example.com:8080', {
            'url_path': url_path,
            'security': f'Bearer token/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_outconn_page(page, base_url)
        row = find_outconn_row(page, outconn_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. and the edit dialog has it selected.
        open_edit_dialog(page, outconn_id)

        selected_label = page.evaluate('$("#id_edit-security option:selected").text()')
        expected_label = f'Bearer token/{definition["name"]}'
        assert selected_label == expected_label, f'Expected "{expected_label}" selected, got: "{selected_label}"'

# ################################################################################################################################

    def test_transition_none_to_basic_auth(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates an open connection, confirms its requests carry no Authorization header,
        then assigns Basic Auth via edit and verifies the header appears at the test server.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'none-to-basic'
        url_path = '/test/outconn/sec-add/' + rand_string()

        # Create the security definition first ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'transition-add')

        # .. create the connection without security ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
        })

        _ = ping_outconn_until_success(page, outconn_name)

        # .. requests carry no Authorization header ..
        request = _invoke_and_get_request(page, http_test_server, outconn_id)
        assert 'Authorization' not in request['headers'], f'Expected no Authorization header, got: {request}'

        # .. assign the definition via edit ..
        edit_outconn(page, outconn_id, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. and the header appears once the change propagates.
        expected_header = _build_basic_auth_header(definition['username'], definition['password'])
        request = _invoke_until_header(page, http_test_server, outconn_id, 'Authorization', expected_header)

        assert request['headers']['Authorization'] == expected_header, \
            f'Expected Authorization "{expected_header}", got: {request}'

# ################################################################################################################################

    def test_transition_basic_auth_to_none(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates a Basic Auth connection, confirms its requests carry the Authorization header,
        then removes the definition via edit and verifies the header disappears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'basic-to-none'
        url_path = '/test/outconn/sec-remove/' + rand_string()

        # Create the security definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'transition-remove')

        # .. create the connection with the definition assigned ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'security': f'Basic Auth/{definition["name"]}',
        })

        _ = ping_outconn_until_success(page, outconn_name)

        # .. requests carry the Authorization header ..
        expected_header = _build_basic_auth_header(definition['username'], definition['password'])
        request = _invoke_and_get_request(page, http_test_server, outconn_id)

        assert request['headers']['Authorization'] == expected_header, \
            f'Expected Authorization "{expected_header}", got: {request}'

        # .. remove the security definition via edit ..
        edit_outconn(page, outconn_id, {
            'security': 'No security definition',
        })

        # .. and the header disappears once the change propagates.
        request = _invoke_until_header(page, http_test_server, outconn_id, 'Authorization', '')
        assert 'Authorization' not in request['headers'], f'Expected no Authorization header, got: {request}'

# ################################################################################################################################

    def test_transition_between_definitions(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Creates two Basic Auth definitions and a connection using the first one, then switches
        to the second one via edit and verifies the Authorization header value changes.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'switch-defs'
        url_path = '/test/outconn/sec-switch/' + rand_string()

        # Create both definitions ..
        definition_first = create_basic_auth(page, base_url, _Test_Name_Prefix, 'switch-first')
        definition_second = create_basic_auth(page, base_url, _Test_Name_Prefix, 'switch-second')

        # .. create the connection with the first one ..
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path,
            'security': f'Basic Auth/{definition_first["name"]}',
        })

        _ = ping_outconn_until_success(page, outconn_name)

        header_first = _build_basic_auth_header(definition_first['username'], definition_first['password'])
        header_second = _build_basic_auth_header(definition_second['username'], definition_second['password'])

        # .. requests carry the first credentials ..
        request = _invoke_and_get_request(page, http_test_server, outconn_id)
        assert request['headers']['Authorization'] == header_first, \
            f'Expected Authorization "{header_first}", got: {request}'

        # .. switch the connection to the second definition ..
        edit_outconn(page, outconn_id, {
            'security': f'Basic Auth/{definition_second["name"]}',
        })

        # .. and requests carry the second credentials once the change propagates.
        request = _invoke_until_header(page, http_test_server, outconn_id, 'Authorization', header_second)
        assert request['headers']['Authorization'] == header_second, \
            f'Expected Authorization "{header_second}", got: {request}'

# ################################################################################################################################
# ################################################################################################################################
