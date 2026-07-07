# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

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
from rest_outconn import find_outconn_row, get_row_cell_texts, open_outconn_page, ping_outconn_until_success, \
    wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.openapi.' + rand_string() + '.'

# Row cell indexes for outgoing REST connection rows
_Cell_Host = 4
_Cell_Url_Path = 5

# How long to wait for the enmasse-backed import call to complete, in milliseconds
_Import_Timeout = 120000

# The OpenAPI document pasted into the overlay - the operation summaries become
# the names of the imported connections and the server URL becomes their host.
_OpenAPI_Document_Template = '''
openapi: 3.0.0
info:
  title: Test API for outgoing REST connection imports
  version: 1.0.0
servers:
  - url: {server_address}
paths:
  {orders_path}:
    get:
      summary: {orders_name}
      responses:
        '200':
          description: A list of orders
  {billing_path}:
    post:
      summary: {billing_name}
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: An invoice confirmation
'''.lstrip()

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

class TestRESTOutconnOpenAPI:
    """ Tests for the OpenAPI import overlay of the outgoing REST connections page.
    """

# ################################################################################################################################

    def test_openapi_import(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Imports two connections from a pasted OpenAPI document, verifies their rows appear
        with the expected names, hosts and URL paths, then pings one of them against the live server.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        orders_name = _Test_Name_Prefix + 'orders'
        billing_name = _Test_Name_Prefix + 'billing'

        orders_path = '/test/outconn/openapi/orders/' + rand_string()
        billing_path = '/test/outconn/openapi/billing/' + rand_string()

        openapi_document = _OpenAPI_Document_Template.format(
            server_address=http_test_server.address,
            orders_path=orders_path,
            orders_name=orders_name,
            billing_path=billing_path,
            billing_name=billing_name,
        )

        # Navigate to the outgoing REST connections page ..
        open_outconn_page(page, base_url)

        # .. open the import popover and choose the copy/paste flow ..
        page.click('#openapi-import-link')
        page.wait_for_selector('#openapi-from-copy-paste', state='visible', timeout=5000)
        page.click('#openapi-from-copy-paste')

        page.wait_for_selector('#openapi-copy-paste-overlay:not(.hidden)', state='visible', timeout=5000)

        # .. paste the document ..
        page.fill('#openapi-copy-paste-textarea', openapi_document)

        # .. parse it ..
        def is_parse_response(response:'any_') -> 'bool':
            found = '/zato/http-soap/openapi/parse/' in response.url
            return found

        with page.expect_response(is_parse_response, timeout=30000) as parse_response_info:
            page.click('#openapi-copy-paste-ok')

        parse_response = parse_response_info.value.json()
        assert parse_response['success'], f'Expected the document to parse, got: {parse_response}'

        # .. the overlay now shows the table with both operations ..
        page.wait_for_selector('#openapi-data-table-container-table tbody tr', state='visible', timeout=10000)

        table_text = page.inner_text('#openapi-data-table-container-table')

        assert orders_name in table_text, f'Expected "{orders_name}" in the import table, got: {table_text}'
        assert billing_name in table_text, f'Expected "{billing_name}" in the import table, got: {table_text}'
        assert orders_path in table_text, f'Expected "{orders_path}" in the import table, got: {table_text}'
        assert billing_path in table_text, f'Expected "{billing_path}" in the import table, got: {table_text}'

        # .. select both rows ..
        page.check('#openapi-data-table-container-select-all')

        # .. run the import, which invokes enmasse against the test environment's server ..
        def is_import_response(response:'any_') -> 'bool':
            found = '/zato/http-soap/openapi/import/' in response.url
            return found

        with page.expect_response(is_import_response, timeout=_Import_Timeout) as import_response_info:
            page.click('#openapi-table-import')

        # The response body cannot be read here because a successful import reloads
        # the page on its own, discarding the resource, hence only the status is checked
        # while the actual import outcome is verified through the connection list below.
        import_status = import_response_info.value.status
        assert import_status == 200, f'Expected a successful import, got status {import_status}'

        # .. a successful import reloads the page on its own ..
        page.wait_for_load_state()

        # .. reload the list and verify both rows with their hosts and paths ..
        open_outconn_page(page, base_url)

        _ = wait_for_outconn_row(page, orders_name)
        _ = wait_for_outconn_row(page, billing_name)

        expected_rows = {
            orders_name: orders_path,
            billing_name: billing_path,
        }

        for outconn_name, url_path in expected_rows.items():
            row = find_outconn_row(page, outconn_name)
            cells = get_row_cell_texts(row)

            logger.info('[test_openapi_import] name=%s cells=%s', outconn_name, cells)

            assert cells[_Cell_Host] == http_test_server.address, \
                f'Expected host "{http_test_server.address}", got: "{cells[_Cell_Host]}"'
            assert cells[_Cell_Url_Path] == url_path, f'Expected url_path "{url_path}", got: "{cells[_Cell_Url_Path]}"'

        # .. and one of the imported connections answers a live ping.
        ping_result = ping_outconn_until_success(page, orders_name)

        logger.info('[test_openapi_import] ping_result=%s', ping_result)

        assert ping_result['is_success'], f'Expected a successful ping of the imported connection, got: {ping_result}'

        requests = http_test_server.wait_for_request_count(1)
        request = requests[-1]
        assert request['path'] == orders_path, f'Expected path "{orders_path}", got: {request}'

# ################################################################################################################################
# ################################################################################################################################
