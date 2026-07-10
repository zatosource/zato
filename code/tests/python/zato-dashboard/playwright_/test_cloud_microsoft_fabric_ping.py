# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import socket
import sys
import time

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The simulated Fabric server is shared with the live server-side test suite.
_fabric_live_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-server', 'fabric_live'))
if _fabric_live_dir not in sys.path:
    sys.path.insert(0, _fabric_live_dir)

from _fabric_server import start_fabric_server

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Page_Url_Pattern = '/zato/cloud/microsoft-fabric/?cluster=1&type_=cloud-microsoft-fabric'

_Test_Name_Prefix = 'test.microsoft.fabric.ping.' + CryptoManager.generate_hex_string(32) + '.'

_Connection_Type = 'cloud-microsoft-fabric'

_Cluster_ID = 1

# A ping that fails on the server side is logged as a warning whose first line is the traceback header,
# the token error message itself appears in later lines of the same record, and the dashboard
# additionally logs the resulting HTTP 500 response.
_Ping_Failure_Log_Patterns = (
    'Traceback (most recent call last)',
    'Fabric token error',
    'Max retries exceeded',
    'Internal Server Error',
)

# How long to keep pinging while a UI or API change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the pings above
_Propagation_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def fabric_test_server() -> 'any_':
    """ A live simulated Fabric tenant for the duration of a single test.
    """

    port = _find_free_port()

    tenant_id = 'tenant-' + CryptoManager.generate_hex_string()
    client_id = 'client-' + CryptoManager.generate_hex_string()
    client_secret = 'secret-' + CryptoManager.generate_hex_string()

    server, _thread = start_fabric_server(port, tenant_id, client_id, client_secret)

    yield {
        'port': port,
        'address': f'http://127.0.0.1:{port}',
        'token_url': f'http://127.0.0.1:{port}/{tenant_id}/oauth2/v2.0/token',
        'tenant_id': tenant_id,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    server.shutdown()

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str') -> 'None':
    """ Opens the Microsoft Fabric connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', address:'str', tenant_id:'str', client_id:'str',
    client_secret:'str') -> 'None':
    """ Creates a Microsoft Fabric connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields, pointing the connection at the simulated server ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    page.fill('#id_tenant_id', tenant_id)
    page.fill('#id_client_id', client_id)
    page.fill('#id_client_secret', client_secret)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    out = id_cell.inner_text().strip()

    return out

# ################################################################################################################################

def _set_token_url(
    api_client:'any_',
    item_id:'str',
    name:'str',
    fabric_server:'anydict',
    client_secret:'str',
    ) -> 'None':
    """ The create form has no token_url field, which in production is always derived from the tenant ID,
    so pointing the token endpoint at the simulated server requires an API-level edit of the connection.
    """

    _ = api_client.edit('zato.generic.connection.edit',
        id=int(item_id),
        cluster_id=_Cluster_ID,
        name=name,
        type_=_Connection_Type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=False,
        pool_size=1,
        address=fabric_server['address'],
        tenant_id=fabric_server['tenant_id'],
        client_id=fabric_server['client_id'],
        client_secret=client_secret,
        token_url=fabric_server['token_url'],
    )

# ################################################################################################################################

def _ping_connection(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Ping link of a connection's row and returns the HTTP status and text of the ping response.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    # Click the link and wait for the ping response to arrive ..
    def is_ping_response(response:'any_') -> 'bool':
        found = '/zato/cloud/microsoft-fabric/ping/' in response.url
        return found

    with page.expect_response(is_ping_response, timeout=30000) as response_info:
        page.click(f'{row_selector} a:has-text("Ping")')

    # .. dismiss the tooltip the action runner shows so it does not obstruct later interactions ..
    response = response_info.value
    page.evaluate('$.fn.zato.action_runner.close_all()')

    # .. and hand the status and body to the caller.
    out = {
        'status': response.status,
        'text': response.text(),
    }
    return out

# ################################################################################################################################

def _ping_until_success(page:'Page', name:'str') -> 'anydict':
    """ Keeps pinging a connection until the ping succeeds, which covers the short window
    between a UI or API change and its propagation to the server. Returns the last ping result,
    letting the caller assert on it themselves.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = _ping_connection(page, name)

        # Stop as soon as the ping goes through ..
        if out['status'] == 200:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCloudMicrosoftFabricPing:
    """ Tests for pinging Microsoft Fabric connections against a live simulated Fabric server.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Ping_Failure_Log_Patterns)
    def test_ping_success(
        self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'any_', fabric_test_server:'anydict') -> 'None':
        """ Creates a connection pointing at the simulated server and verifies the ping succeeds.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        fabric_server = fabric_test_server

        name = _Test_Name_Prefix + 'success'
        client_secret = fabric_server['client_secret']

        # Navigate ..
        _navigate(page, base_url)

        # .. create the connection through the UI, pointing it at the simulated server ..
        _create_connection(page, name, fabric_server['address'], fabric_server['tenant_id'],
            fabric_server['client_id'], client_secret)

        # .. point the token endpoint at the simulated server too ..
        item_id = _get_item_id(page, name)
        _set_token_url(api_client, item_id, name, fabric_server, client_secret)

        # .. ping until the connection propagates to the server ..
        ping_result = _ping_until_success(page, name)

        logger.info('[test_ping_success] ping_result=%s', ping_result)

        # .. and the ping reports success with its response time.
        assert ping_result['status'] == 200, f'Expected a successful ping, got: {ping_result}'
        assert 'Connection pinged' in ping_result['text'], f'Expected ping details in the response, got: {ping_result}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Ping_Failure_Log_Patterns)
    def test_ping_wrong_secret(
        self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'any_', fabric_test_server:'anydict') -> 'None':
        """ Creates a connection with a wrong client secret and verifies the ping failure is surfaced.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        fabric_server = fabric_test_server

        name = _Test_Name_Prefix + 'wrong-secret'
        wrong_secret = 'wrong-secret-' + CryptoManager.generate_hex_string()

        # Navigate ..
        _navigate(page, base_url)

        # .. create the connection through the UI, with a secret the simulated server rejects ..
        _create_connection(page, name, fabric_server['address'], fabric_server['tenant_id'],
            fabric_server['client_id'], wrong_secret)

        # .. point the token endpoint at the simulated server too ..
        item_id = _get_item_id(page, name)
        _set_token_url(api_client, item_id, name, fabric_server, wrong_secret)

        # .. wait until the connection with the simulated token endpoint propagates to the server,
        # .. which is when pings start reaching the simulated server and its token error is surfaced ..
        deadline = time.monotonic() + _Propagation_Timeout

        while True:
            ping_result = _ping_connection(page, name)

            # Stop as soon as the simulated server rejects the credentials - the invalid_client
            # marker is what distinguishes its response from errors of the default, real token endpoint ..
            if 'invalid_client' in ping_result['text']:
                break

            # .. or when the deadline passes, in which case the assertions below fail with details.
            if time.monotonic() >= deadline:
                break

            time.sleep(_Propagation_Poll_Interval)

        logger.info('[test_ping_wrong_secret] ping_result=%s', ping_result)

        # .. the ping reports a failure with the token error from the simulated server.
        assert ping_result['status'] == 500, f'Expected a failed ping, got: {ping_result}'
        assert 'Fabric token error' in ping_result['text'], f'Expected a token error in the response, got: {ping_result}'
        assert 'invalid_client' in ping_result['text'], f'Expected the token error details in the response, got: {ping_result}'

# ################################################################################################################################
# ################################################################################################################################
