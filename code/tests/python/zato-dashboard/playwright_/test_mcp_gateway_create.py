# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys
import time
from http.client import FORBIDDEN, NOT_FOUND, OK

# pytest
import pytest

# requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test import rand_string
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import create_basic_auth, navigate_to_page, open_create_dialog, submit_create_form
from zato.common.typing_ import cast_

# Zato - test helpers - the wizard driver lives next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, anynone

    # Referenced only inside cast_ strings, which linters do not read as annotations
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Page_URL_Pattern = '/zato/gateway/mcp/?cluster=1'

_Test_Name_Prefix = 'test.mcp.playwright.' + rand_string() + '.'

# What the server logs when a gateway with no security at all is probed - the default deny
# these tests confirm, not a fault
_No_Members_Log = 'is protected by security groups that have no members'

# Column indexes on the gateway list - numbering, selection, name, active,
# URL path, agent filters, size caps, services, security
_Column_Name       = 2
_Column_Is_Active  = 3
_Column_URL_Path   = 4
_Column_Services   = 7
_Column_Security   = 8

# ################################################################################################################################
# ################################################################################################################################

def _delete_gateway_row(page:'Page', item_id:'str', gateway_name:'str') -> 'None':
    """ Deletes a gateway through its list row's confirmation popup and waits for the row to go.
    """
    row_selector = wizard_page.row_selector(gateway_name)

    page.evaluate(f'$.fn.zato.gateway.mcp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    _ = page.wait_for_selector(row_selector, state='hidden', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

def _post_mcp(server_port:'int', url_path:'str', auth:'anynone' = None) -> 'requests.Response':
    """ Posts a JSON-RPC initialize request to the given MCP URL path.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'
    data = make_jsonrpc_initialize()
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)

    logger.info('[_post_mcp] POST %s auth=%s -> status=%d', url_path, auth[0] if auth else None, response.status_code)

    return response

# ################################################################################################################################
# ################################################################################################################################

class TestMCPGatewayCreate:
    """ Tests for MCP gateway creation via the web admin UI.
    """

# ################################################################################################################################

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the MCP gateways page and verifies its structure.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the MCP gateways page ..
        navigate_to_page(page, base_url, _Page_URL_Pattern)

        # .. verify the page heading ..
        heading = cast_('any_', page.query_selector('h2.zato'))
        heading_text = heading.inner_text()
        assert 'MCP gateways' in heading_text, f'Expected "MCP gateways" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = cast_('any_', page.query_selector('#markup .page_prompt a'))
        create_link_text = create_link.inner_text()
        assert 'Create a new MCP gateway' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts:'anylist' = []

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'active' in header_texts, f'Expected "active" in headers, got: {header_texts}'
        assert 'url path' in header_texts, f'Expected "url path" in headers, got: {header_texts}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_create_minimal(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with only name and url_path via the UI, verifies the row
        appears correctly, then confirms the gateway is live on the server (returns 403 because
        no security groups are configured - default deny).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'minimal'
        url_path = '/mcp/test/' + rand_string()

        # Create the gateway through the wizard - name and URL path only ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path)

        # .. the create flow ends back on the list with the new row on it ..
        row = wizard_page.go_to_list(page, base_url, gateway_name)

        # .. extract cell texts from the row ..
        cells = row.query_selector_all('td')

        name_cell_text = cells[_Column_Name].inner_text().strip()
        is_active_text = cells[_Column_Is_Active].inner_text().strip()
        url_path_text = cells[_Column_URL_Path].inner_text().strip()

        logger.info('[test_create_minimal] name=%s is_active=%s url_path=%s', name_cell_text, is_active_text, url_path_text)

        # .. verify each cell has the correct value ..
        assert name_cell_text == gateway_name, \
            f'Expected name "{gateway_name}", got: "{name_cell_text}"'

        assert is_active_text == 'Yes', \
            f'Expected is_active "Yes", got: "{is_active_text}"'

        assert url_path_text == url_path, \
            f'Expected url_path "{url_path}", got: "{url_path_text}"'

        # .. POST an MCP request - should get 403 (no security groups = default deny) ..
        response = _post_mcp(server_port, url_path)

        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for no-security gateway, got {response.status_code}: {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_create_with_services(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with two services assigned via the badge picker.
        Verifies the row shows service count = 2, reopens edit to confirm both are pre-selected,
        then confirms the gateway is live on the server.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'with-services'
        url_path = '/mcp/test-service/' + rand_string()

        # Open the create wizard and answer step 1 ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # .. open the services card and wait for at least two badges to pick from ..
        wizard_page.open_picker_card(page, 'services')
        wizard_page.wait_for_available_badges(page, 'services', 2)

        # .. pick the first two available service badges ..
        available_names = wizard_page.get_available_badge_names(page, 'services')

        service_name_1 = available_names[0]
        service_name_2 = available_names[1]

        logger.info('[test_create_with_services] selecting services: %s, %s', service_name_1, service_name_2)

        # .. assign both by name through the card ..
        wizard_page.assign_badge(page, 'services', service_name_1)
        wizard_page.assign_badge(page, 'services', service_name_2)

        # .. verify the assigned zone counts 2 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-wizard .badge-zone-count')
        assert assigned_count_text == '2', f'Expected assigned count "2", got: "{assigned_count_text}"'

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. verify the new row appears with service count = 2 ..
        row = wizard_page.go_to_list(page, base_url, gateway_name)
        cells = row.query_selector_all('td')

        service_count_text = cells[_Column_Services].inner_text().strip()
        logger.info('[test_create_with_services] service_count_text=%s', service_count_text)

        assert service_count_text == '2', \
            f'Expected service count "2", got: "{service_count_text}"'

        # .. reopen the edit wizard to confirm the services are pre-selected ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        # .. verify the two services are in the assigned zone ..
        assigned_names = set(wizard_page.get_assigned_badge_names(page, 'services'))

        logger.info('[test_create_with_services] assigned_names in edit=%s', assigned_names)

        assert service_name_1 in assigned_names, \
            f'Expected "{service_name_1}" in assigned, got: {assigned_names}'

        assert service_name_2 in assigned_names, \
            f'Expected "{service_name_2}" in assigned, got: {assigned_names}'

        # .. POST an MCP request - should get 403 (no security groups = default deny) ..
        response = _post_mcp(server_port, url_path)

        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for no-security gateway, got {response.status_code}: {response.text}'

        # .. verify the ODB has the correct services stored ..
        api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
        api_auth = ('admin.invoke', zato_dashboard['password'])
        api_headers = {'Content-Type': 'application/json'}
        api_payload = json.dumps({'cluster_id': 1, 'type_': 'gateway-mcp'})

        odb_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert odb_response.status_code == OK, f'API call failed: {odb_response.status_code} {odb_response.text}'

        items = odb_response.json()
        gateway_data:'anynone' = None

        for item in items:
            if item['name'] == gateway_name:
                gateway_data = item
                break

        assert gateway_data is not None, f'Gateway "{gateway_name}" not found in ODB'

        stored_services = set(gateway_data['services'])
        logger.info('[test_create_with_services] stored_services=%s', stored_services)

        assert service_name_1 in stored_services, \
            f'Expected "{service_name_1}" in stored services, got: {stored_services}'

        assert service_name_2 in stored_services, \
            f'Expected "{service_name_2}" in stored services, got: {stored_services}'

# ################################################################################################################################

    def test_create_with_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth definition via the UI, then creates an MCP gateway
        with that sec def assigned via the security badge picker.
        Verifies the row shows security count = 1, then POSTs with valid and invalid creds.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'with-security'
        url_path = '/mcp/test-security/' + rand_string()

        # Create a basic auth definition via the UI so we know the credentials ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'mcp-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        logger.info('[test_create_with_security] created sec def: name=%s username=%s', security_name, security_username)

        # .. open the create wizard and answer step 1 ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # .. assign the badge matching our newly created sec def ..
        wizard_page.assign_badge(page, 'security', security_name)

        # .. verify the assigned zone counts 1 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-sec-wizard .badge-zone-count')
        assert assigned_count_text == '1', f'Expected assigned count "1", got: "{assigned_count_text}"'

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. verify the new row appears with security count = 1 ..
        row = wizard_page.go_to_list(page, base_url, gateway_name)
        cells = row.query_selector_all('td')

        security_count_text = cells[_Column_Security].inner_text().strip()
        logger.info('[test_create_with_security] security_count_text=%s', security_count_text)

        assert security_count_text == '1', f'Expected security count "1", got: "{security_count_text}"'

        # .. POST with valid creds - should get OK (MCP initialize response) ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK with valid creds, got {response.status_code}: {response.text}'

        # .. POST with invalid creds - should get FORBIDDEN ..
        response = _post_mcp(server_port, url_path, auth=('invalid_user', 'invalid_password'))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN with invalid creds, got {response.status_code}: {response.text}'

# ################################################################################################################################

    def test_export(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with both a Basic Auth and an API key definition assigned,
        clicks the row's Export link and verifies the downloaded server.json-format document,
        including both authentication headers.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'export'
        url_path = '/mcp/test-export/' + rand_string()

        # Create a Basic Auth definition via the UI ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'mcp-export')
        basic_auth_name = security_info['name']

        # .. create an API key definition via the UI, the header field is pre-filled with X-API-Key ..
        apikey_name = _Test_Name_Prefix + 'apikey.mcp-export'
        apikey_value = 'key.' + CryptoManager.generate_hex_string()

        navigate_to_page(page, base_url, '/zato/security/apikey/?cluster=1')
        open_create_dialog(page)

        page.fill('#id_name', apikey_name)
        page.fill('#id_password', apikey_value)

        submit_create_form(page)

        apikey_row_selector = f'#data-table tbody tr:has(td:text-is("{apikey_name}"))'
        _ = page.wait_for_selector(apikey_row_selector, state='visible', timeout=5000)

        logger.info('[test_export] created sec defs: basic_auth=%s apikey=%s', basic_auth_name, apikey_name)

        # .. open the create wizard and answer step 1 ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # .. assign both definitions to the gateway ..
        wizard_page.assign_badge(page, 'security', basic_auth_name)
        wizard_page.assign_badge(page, 'security', apikey_name)

        # .. verify the assigned zone counts 2 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-sec-wizard .badge-zone-count')
        assert assigned_count_text == '2', f'Expected assigned count "2", got: "{assigned_count_text}"'

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. wait for the new row to appear ..
        row = wizard_page.go_to_list(page, base_url, gateway_name)

        # .. click the Export link and capture the download ..
        export_link = row.query_selector('a:text-is("Export")')
        assert export_link is not None, 'Could not find the Export link in the row'

        with page.expect_download() as download_info:
            export_link.click()

        download = download_info.value

        # .. the gateway name contains only characters allowed in a slug, so the file name uses it as is ..
        expected_file_name = f'mcp-{gateway_name}.json'
        assert download.suggested_filename == expected_file_name, \
            f'Expected file name "{expected_file_name}", got: "{download.suggested_filename}"'

        # .. load the downloaded document ..
        download_path = download.path()

        with open(download_path) as json_file:
            document = json.load(json_file)

        logger.info('[test_export] document=%s', document)

        # .. the dashboard under test runs with Zato_Server_Address=http://127.0.0.1:<server_port>,
        # and IP addresses are used as namespaces as they are, without reversing their labels ..
        expected_name = f'127.0.0.1/{gateway_name}'
        assert document['name'] == expected_name, f'Expected name "{expected_name}", got: "{document["name"]}"'

        # .. the description comes from the export view ..
        assert document['description'] == f'MCP gateway {gateway_name}', \
            f'Unexpected description: "{document["description"]}"'

        # .. verify the remote endpoint ..
        remotes = document['remotes']
        remote_count = len(remotes)
        assert remote_count == 1, f'Expected 1 remote, got: {remote_count}'

        remote = remotes[0]
        assert remote['type'] == 'streamable-http', f'Expected type "streamable-http", got: "{remote["type"]}"'

        expected_url = f'http://127.0.0.1:{server_port}{url_path}'
        assert remote['url'] == expected_url, f'Expected URL "{expected_url}", got: "{remote["url"]}"'

        # .. verify both authentication headers are present ..
        header_names = set()

        for header in remote['headers']:
            header_names.add(header['name'])
            assert header['isRequired'] is True, f'Expected isRequired for header: {header}'
            assert header['isSecret'] is True, f'Expected isSecret for header: {header}'

        assert 'Authorization' in header_names, f'Expected "Authorization" in headers, got: {header_names}'
        assert 'X-API-Key' in header_names, f'Expected "X-API-Key" in headers, got: {header_names}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_edit_rename(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, then edits it to change both name and url_path.
        Asserts the old URL returns 404 and the new URL is routable (403 = no security, but routable).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        old_name = _Test_Name_Prefix + 'rename-old'
        old_url_path = '/mcp/rename-old/' + rand_string()
        new_name = _Test_Name_Prefix + 'rename-new'
        new_url_path = '/mcp/rename-new/' + rand_string()

        # Create the initial gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, old_name, old_url_path)

        # .. confirm old URL is routable (403 = no security but gateway exists) ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN on old URL, got {response.status_code}'

        # .. open the edit wizard ..
        wizard_page.open_wizard_edit(page, base_url, old_name)

        # .. change name and url_path ..
        page.fill('#id_edit-name', new_name)
        page.fill('#id_edit-url_path', new_url_path)

        # .. save the edit ..
        wizard_page.save_edit(page)

        # .. verify the list now shows the new name ..
        _ = wizard_page.go_to_list(page, base_url, new_name)

        logger.info('[test_edit_rename] renamed %s -> %s, %s -> %s', old_name, new_name, old_url_path, new_url_path)

        # .. old URL should now return 404 ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND on old URL after rename, got {response.status_code}'

        # .. new URL should be routable (403 = no security) ..
        response = _post_mcp(server_port, new_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN on new URL, got {response.status_code}'

# ################################################################################################################################

    def test_edit_rename_preserves_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with a security member, renames it (changes url_path),
        and asserts that security group enforcement still works at the new URL.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'rename-sec'
        old_url_path = '/mcp/rename-security-old/' + rand_string()
        new_url_path = '/mcp/rename-security-new/' + rand_string()

        # Create a basic auth definition via the UI ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rename-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create the gateway through the wizard with the sec def assigned ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, old_url_path, security=[security_name])

        # .. verify the gateway works with valid creds at old URL ..
        response = _post_mcp(server_port, old_url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK at old URL with valid creds, got {response.status_code}'

        # .. open the edit wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        # .. change only the url_path ..
        page.fill('#id_edit-url_path', new_url_path)

        # .. save the edit ..
        wizard_page.save_edit(page)

        logger.info('[test_edit_rename_preserves_security] renamed url_path %s -> %s', old_url_path, new_url_path)

        # .. old URL should be gone ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND on old URL, got {response.status_code}'

        # .. new URL with valid creds should still work ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK at new URL with valid creds, got {response.status_code}'

        # .. new URL with invalid creds should be forbidden ..
        response = _post_mcp(server_port, new_url_path, auth=('invalid_user', 'invalid_password'))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at new URL with bad creds, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_edit_deactivate(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, then edits it to uncheck is_active.
        Asserts the URL returns 404 after deactivation.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'deactivate'
        url_path = '/mcp/deactivate/' + rand_string()

        # Create the gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path)

        # .. confirm URL is routable while active ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN (active, no sec), got {response.status_code}'

        # .. open the edit wizard and uncheck is_active ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.uncheck('#id_edit-is_active')

        # .. save the edit ..
        wizard_page.save_edit(page)

        logger.info('[test_edit_deactivate] deactivated gateway %s', gateway_name)

        # .. URL should now return 404 ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after deactivation, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_edit_reactivate(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, deactivates it, then reactivates it.
        Asserts the URL returns 404 when inactive and is routable again after reactivation.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'reactivate'
        url_path = '/mcp/reactivate/' + rand_string()

        # Create the gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path)

        # .. open the edit wizard and deactivate ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.uncheck('#id_edit-is_active')
        wizard_page.save_edit(page)

        # .. confirm URL is now 404 ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND when inactive, got {response.status_code}'

        # .. reopen the edit wizard and reactivate ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.check('#id_edit-is_active')
        wizard_page.save_edit(page)

        logger.info('[test_edit_reactivate] reactivated gateway %s', gateway_name)

        # .. URL should be routable again (403 = no security, but exists) ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN after reactivation, got {response.status_code}'

# ################################################################################################################################

    def test_edit_add_service(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with 1 service and security, edits it to add a second service.
        Asserts tools/list returns both services.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'add-service'
        url_path = '/mcp/add-service/' + rand_string()

        # Create a sec def so we can authenticate ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-service')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. open the create wizard and answer step 1 ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # .. pick only the first available service ..
        wizard_page.open_picker_card(page, 'services')
        wizard_page.wait_for_available_badges(page, 'services', 2)

        available_names = wizard_page.get_available_badge_names(page, 'services')
        service_name_1 = available_names[0]

        wizard_page.assign_badge(page, 'services', service_name_1)

        # .. assign security ..
        wizard_page.assign_badge(page, 'security', security_name)

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. initialize to confirm gateway is live ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. open the edit wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        # .. pick a second service out of what is still available ..
        wizard_page.open_picker_card(page, 'services')
        wizard_page.wait_for_available_badges(page, 'services', 1)

        available_names_edit = wizard_page.get_available_badge_names(page, 'services')
        service_name_2 = available_names_edit[0]

        wizard_page.assign_badge(page, 'services', service_name_2)

        logger.info('[test_edit_add_service] adding service: %s (already has: %s)', service_name_2, service_name_1)

        # .. save the edit ..
        wizard_page.save_edit(page)

        # .. initialize a session, then send tools/list with the session ID ..
        url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (security_username, security_password)
        headers = {'Content-Type': 'application/json'}

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'initialize failed: {initialize_response.status_code}'

        session_id = initialize_response.headers['Mcp-Session-Id']

        headers['Mcp-Session-Id'] = session_id
        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_list_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert tools_list_response.status_code == OK, f'tools/list failed: {tools_list_response.status_code}'

        json_body = tools_list_response.json()
        result = json_body['result']
        tools = result['tools']

        tool_names = set()

        for tool in tools:
            tool_names.add(tool['name'])

        logger.info('[test_edit_add_service] tool_names=%s', tool_names)

        assert service_name_1 in tool_names, f'Expected "{service_name_1}" in tools, got: {tool_names}'
        assert service_name_2 in tool_names, f'Expected "{service_name_2}" in tools, got: {tool_names}'

# ################################################################################################################################

    def test_edit_remove_service(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway with 2 services and security, edits it to remove one.
        Asserts tools/list returns only the remaining service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'rm-service'
        url_path = '/mcp/remove-service/' + rand_string()

        # Create a sec def ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-service')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. open the create wizard and answer step 1 ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # .. pick two services ..
        wizard_page.open_picker_card(page, 'services')
        wizard_page.wait_for_available_badges(page, 'services', 2)

        available_names = wizard_page.get_available_badge_names(page, 'services')
        service_name_1 = available_names[0]
        service_name_2 = available_names[1]

        wizard_page.assign_badge(page, 'services', service_name_1)
        wizard_page.assign_badge(page, 'services', service_name_2)

        # .. assign security ..
        wizard_page.assign_badge(page, 'security', security_name)

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. open the edit wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        # .. remove the first service through the assigned zone ..
        wizard_page.remove_assigned_badge(page, 'services', service_name_1)

        logger.info('[test_edit_remove_service] removing service: %s (keeping: %s)', service_name_1, service_name_2)

        # .. save the edit ..
        wizard_page.save_edit(page)

        # .. initialize a session, then send tools/list with the session ID ..
        url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (security_username, security_password)
        headers = {'Content-Type': 'application/json'}

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'initialize failed: {initialize_response.status_code}'

        session_id = initialize_response.headers['Mcp-Session-Id']

        headers['Mcp-Session-Id'] = session_id
        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_list_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert tools_list_response.status_code == OK, f'tools/list failed: {tools_list_response.status_code}'

        json_body = tools_list_response.json()
        result = json_body['result']
        tools = result['tools']

        tool_names = set()

        for tool in tools:
            tool_names.add(tool['name'])

        logger.info('[test_edit_remove_service] tool_names=%s', tool_names)

        assert service_name_2 in tool_names, f'Expected "{service_name_2}" in tools, got: {tool_names}'
        assert service_name_1 not in tool_names, f'Expected "{service_name_1}" NOT in tools, got: {tool_names}'

# ################################################################################################################################

    def test_edit_add_security_member(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway with 1 sec def, edits to add a second sec def.
        Asserts both can authenticate.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'add-sec'
        url_path = '/mcp/add-security/' + rand_string()

        # Create two basic auth definitions ..
        security_info_1 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-sec-1')
        security_name_1 = security_info_1['name']
        security_username_1 = security_info_1['username']
        security_password_1 = security_info_1['password']

        security_info_2 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-sec-2')
        security_name_2 = security_info_2['name']
        security_username_2 = security_info_2['username']
        security_password_2 = security_info_2['password']

        # .. create the gateway through the wizard with only the first sec def ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name_1])

        # .. confirm first creds work, second does not ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for sec_2 before edit, got {response.status_code}'

        # .. open the edit wizard and add the second sec def ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.assign_badge(page, 'security', security_name_2)

        # .. save the edit ..
        wizard_page.save_edit(page)

        logger.info('[test_edit_add_security_member] added sec def %s to gateway %s', security_name_2, gateway_name)

        # .. both should now authenticate ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 after edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for sec_2 after edit, got {response.status_code}'

# ################################################################################################################################

    def test_edit_remove_security_member(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway with 2 sec defs, edits to remove one.
        Removed member -> 403, remaining member -> 200.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'rm-sec'
        url_path = '/mcp/remove-security/' + rand_string()

        # Create two basic auth definitions ..
        security_info_1 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-sec-1')
        security_name_1 = security_info_1['name']
        security_username_1 = security_info_1['username']
        security_password_1 = security_info_1['password']

        security_info_2 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-sec-2')
        security_name_2 = security_info_2['name']
        security_username_2 = security_info_2['username']
        security_password_2 = security_info_2['password']

        # .. create the gateway through the wizard with both sec defs ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name_1, security_name_2])

        # .. confirm both work ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 before edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for sec_2 before edit, got {response.status_code}'

        # .. open the edit wizard and remove the first sec def through the assigned zone ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.remove_assigned_badge(page, 'security', security_name_1)

        # .. save the edit ..
        wizard_page.save_edit(page)

        logger.info('[test_edit_remove_security_member] removed sec def %s from gateway %s', security_name_1, gateway_name)

        # .. removed member should get 403, remaining should get 200 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for removed sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for remaining sec_2, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_edit_remove_all_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway with sec defs, edits to remove all.
        Asserts all requests return 403 (default deny).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'rm-all-sec'
        url_path = '/mcp/remove-all-security/' + rand_string()

        # Create a basic auth definition ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-all-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create the gateway through the wizard with security ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name])

        # .. confirm creds work ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK before edit, got {response.status_code}'

        # .. open the edit wizard and remove the one assigned sec def ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.remove_assigned_badge(page, 'security', security_name)

        # .. save the edit ..
        wizard_page.save_edit(page)

        logger.info('[test_edit_remove_all_security] removed all security from gateway %s', gateway_name)

        # .. wait for security change to propagate ..
        page.wait_for_timeout(2000)

        # .. with valid creds should get 403 (no group = default deny) ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN with creds after removing all security, got {response.status_code}'

        # .. without creds should also get 403 ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN without creds after removing all security, got {response.status_code}'

# ################################################################################################################################

    def test_create_duplicate_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway, then tries to create another with the same name.
        Asserts the wizard blocks the save - the taken indicator shows and the page stays.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _Test_Name_Prefix + 'dup-name'
        url_path_1 = '/mcp/duplicate-1/' + rand_string()
        url_path_2 = '/mcp/duplicate-2/' + rand_string()

        # Create the first gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path_1)

        # .. try to create a second gateway with the same name ..
        wizard_page.open_wizard_create(page, base_url)
        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path_2)

        # .. the live check marks the name as taken ..
        _ = page.wait_for_selector('.zato-unique-taken', state='visible', timeout=5000)

        # .. a save from the review step is refused ..
        wizard_page.go_to_step(page, wizard_page.Review_Step)
        page.click('#mcp-wizard-next')

        # .. no save confirmation shows and the wizard stays on its page ..
        page.wait_for_timeout(2000)

        saved_visible = page.is_visible(f'text="{wizard_page.Saved_Label}"')
        assert not saved_visible, 'Expected no save confirmation for duplicate name'

        wizard_visible = page.is_visible('#mcp-wizard')
        assert wizard_visible, 'Expected the wizard to remain open for duplicate name'

        logger.info('[test_create_duplicate_name] duplicate name correctly blocked')

# ################################################################################################################################

    def test_create_duplicate_url_path(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway with a URL path, then tries to create another with the same path.
        Asserts the wizard blocks the save - the taken indicator shows and the page stays.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name_1 = _Test_Name_Prefix + 'dup-path-1'
        gateway_name_2 = _Test_Name_Prefix + 'dup-path-2'
        url_path = '/mcp/duplicate-path/' + rand_string()

        # Create the first gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name_1, url_path)

        # .. try to create a second gateway with the same url_path ..
        wizard_page.open_wizard_create(page, base_url)
        page.fill('#id_name', gateway_name_2)
        page.fill('#id_url_path', url_path)

        # .. the live check marks the path as taken ..
        _ = page.wait_for_selector('.zato-unique-taken', state='visible', timeout=5000)

        # .. a save from the review step is refused ..
        wizard_page.go_to_step(page, wizard_page.Review_Step)
        page.click('#mcp-wizard-next')

        # .. no save confirmation shows and the wizard stays on its page ..
        page.wait_for_timeout(2000)

        saved_visible = page.is_visible(f'text="{wizard_page.Saved_Label}"')
        assert not saved_visible, 'Expected no save confirmation for duplicate url_path'

        wizard_visible = page.is_visible('#mcp-wizard')
        assert wizard_visible, 'Expected the wizard to remain open for duplicate url_path'

        logger.info('[test_create_duplicate_url_path] duplicate url_path correctly blocked')

# ################################################################################################################################

    def test_service_hot_deploy_updates_tools_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Hot-deploys a new service, edits an MCP gateway via UI to include it,
        then verifies tools/list returns the new service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        gateway_name = _Test_Name_Prefix + 'hotdep'
        url_path = '/mcp/hot-deploy/' + rand_string()
        hot_deploy_service_name = 'mcp-test.hot-deploy-tools.' + rand_string()

        # Create a sec def so we can authenticate ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'hotdep')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create a gateway through the wizard with demo.echo and security ..
        _ = wizard_page.create_gateway(
            page, base_url, gateway_name, url_path, services=['demo.echo'], security=[security_name])

        # .. hot-deploy a new service ..
        pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')
        service_file_name = '_mcp_test_hot_deploy_tools.py'
        service_file_path = os.path.join(pickup_directory, service_file_name)

        service_code = f'''\
from zato.server.service import Service

class MCPTestHotDeployTools(Service):
    name = '{hot_deploy_service_name}'

    def handle(self):
        self.response.payload = '{{"status": "ok"}}'
'''

        with open(service_file_path, 'w') as service_file:
            _ = service_file.write(service_code)

        logger.info('[test_service_hot_deploy_updates_tools_list] deployed %s', hot_deploy_service_name)

        # .. wait for the service to be picked up ..
        time.sleep(5)

        # .. open the edit wizard to add the hot-deployed service ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.open_picker_card(page, 'services')

        # .. wait for the hot-deployed service to appear in the available services badge picker ..
        badge_selector_edit = wizard_page.available_badge_selector('services', hot_deploy_service_name)

        deadline = time.monotonic() + 15

        while time.monotonic() < deadline:
            badge = page.query_selector(badge_selector_edit)
            if badge:
                break
            # .. reopen the wizard to refresh the badge list ..
            time.sleep(1)
            wizard_page.open_wizard_edit(page, base_url, gateway_name)
            wizard_page.open_picker_card(page, 'services')
        else:
            os.remove(service_file_path)
            raise AssertionError(
                f'Hot-deployed service "{hot_deploy_service_name}" did not appear in edit badge picker within 15s')

        wizard_page.assign_badge(page, 'services', hot_deploy_service_name)

        wizard_page.save_edit(page)

        # .. verify tools/list now includes the hot-deployed service ..
        url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (security_username, security_password)
        headers = {'Content-Type': 'application/json'}

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'initialize failed: {initialize_response.status_code}'

        session_id = initialize_response.headers['Mcp-Session-Id']
        headers['Mcp-Session-Id'] = session_id

        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_list_response = requests.post(url, data=request_body, headers=headers, auth=auth, timeout=10)
        assert tools_list_response.status_code == OK, f'tools/list failed: {tools_list_response.status_code}'

        json_body = tools_list_response.json()
        result = json_body['result']
        tools = result['tools']

        tool_names = set()

        for tool in tools:
            tool_names.add(tool['name'])

        logger.info('[test_service_hot_deploy_updates_tools_list] tool_names=%s', tool_names)

        # .. the gateway must not outlive the hot-deployed service its allow list references,
        # otherwise a fresh server start would fail rebuilding the MCP tool registries,
        # so delete the gateway first ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name)
        item_id = wizard_page.get_gateway_id(page, gateway_name)

        _delete_gateway_row(page, item_id, gateway_name)

        # .. delete the basic auth definition ..
        basic_auth_page_url = f'/zato/security/basic-auth/?cluster=1&query={security_name}'
        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_security = f'#data-table tbody tr:has(td:text-is("{security_name}"))'
        row_security = cast_('any_', page.wait_for_selector(row_selector_security, state='visible', timeout=5000))
        item_id_cell_security = row_security.query_selector('td[class*="item_id_"]')
        item_id_security = item_id_cell_security.inner_text().strip()

        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id_security}")')
        _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        _ = page.wait_for_selector(row_selector_security, state='hidden', timeout=5000)

        # .. and only now remove the deployed service file.
        os.remove(service_file_path)

        assert hot_deploy_service_name in tool_names, \
            f'Expected "{hot_deploy_service_name}" in tools after hot-deploy, got: {tool_names}'

# ################################################################################################################################

    def test_sec_def_password_change(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth, assigns it to an MCP gateway's security group,
        verifies the original password works, changes the password via the basic auth UI,
        then verifies old password -> 403 and new password -> 200.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'pwd-chg'
        url_path = '/mcp/password-change/' + rand_string()

        # Create a basic auth definition ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pwd-chg')
        security_name = security_info['name']
        security_username = security_info['username']
        old_password = security_info['password']

        # .. create a gateway through the wizard with this sec def ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name])

        # .. verify the original password works ..
        response = _post_mcp(server_port, url_path, auth=(security_username, old_password))
        assert response.status_code == OK, f'Expected OK with original password, got {response.status_code}'

        # .. navigate to the basic auth page and change the password ..
        new_password = 'changed.' + rand_string()
        # The query parameter makes sure the definition is on the first page of results,
        # otherwise it could land on a later page among definitions from earlier tests.
        basic_auth_page_url = f'/zato/security/basic-auth/?cluster=1&query={security_name}'

        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_basic_auth = f'#data-table tbody tr:has(td:text-is("{security_name}"))'
        row = cast_('any_', page.wait_for_selector(row_selector_basic_auth, state='visible', timeout=5000))

        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        _ = page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', new_password)
        page.click('#change_password-div input[type="submit"]')
        _ = page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        logger.info('[test_sec_def_password_change] password changed for %s', security_name)

        # .. wait for the password change to propagate to the security cache ..
        page.wait_for_timeout(2000)

        # .. old password should be rejected ..
        response = _post_mcp(server_port, url_path, auth=(security_username, old_password))
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN with old password after change, got {response.status_code}'

        # .. new password should work ..
        response = _post_mcp(server_port, url_path, auth=(security_username, new_password))
        assert response.status_code == OK, f'Expected OK with new password, got {response.status_code}'

# ################################################################################################################################

    def test_two_gateways_different_groups(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two MCP gateways, each with a different security group member.
        Verifies cross-group access is denied: A with Y-creds -> 403, B with X-creds -> 403.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name_a = _Test_Name_Prefix + 'iso-a'
        gateway_name_b = _Test_Name_Prefix + 'iso-b'
        url_path_a = '/mcp/isolation-a/' + rand_string()
        url_path_b = '/mcp/isolation-b/' + rand_string()

        # Create two separate basic auth definitions ..
        security_info_a = create_basic_auth(page, base_url, _Test_Name_Prefix, 'iso-a')
        security_name_a = security_info_a['name']
        security_username_a = security_info_a['username']
        security_password_a = security_info_a['password']

        security_info_b = create_basic_auth(page, base_url, _Test_Name_Prefix, 'iso-b')
        security_name_b = security_info_b['name']
        security_username_b = security_info_b['username']
        security_password_b = security_info_b['password']

        # .. create gateway A with security A and gateway B with security B, both through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name_a, url_path_a, security=[security_name_a])
        _ = wizard_page.create_gateway(page, base_url, gateway_name_b, url_path_b, security=[security_name_b])

        # .. verify own creds work on own gateway ..
        response = _post_mcp(server_port, url_path_a, auth=(security_username_a, security_password_a))
        assert response.status_code == OK, f'Expected OK for A with A-creds, got {response.status_code}'

        response = _post_mcp(server_port, url_path_b, auth=(security_username_b, security_password_b))
        assert response.status_code == OK, f'Expected OK for B with B-creds, got {response.status_code}'

        # .. verify cross-group access is denied ..
        response = _post_mcp(server_port, url_path_a, auth=(security_username_b, security_password_b))
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for A with B-creds, got {response.status_code}'

        response = _post_mcp(server_port, url_path_b, auth=(security_username_a, security_password_a))
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for B with A-creds, got {response.status_code}'

# ################################################################################################################################

    def test_two_gateways_different_allow_lists(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two MCP gateways with different service allow lists.
        Gateway A allows svc-a only, gateway B allows svc-b only.
        Verifies each gateway's tools/list only exposes its own allowed service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        suffix_a = rand_string()
        suffix_b = rand_string()

        gateway_name_a = _Test_Name_Prefix + 'allow-a'
        gateway_name_b = _Test_Name_Prefix + 'allow-b'
        url_path_a = '/mcp/allow-list-a/' + suffix_a
        url_path_b = '/mcp/allow-list-b/' + suffix_b

        service_name_a = 'mcp-test.allow-list-a.' + suffix_a
        service_name_b = 'mcp-test.allow-list-b.' + suffix_b

        # Hot-deploy two distinct services ..
        pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')

        service_file_name_a = '_mcp_test_allow_list_a.py'
        service_file_path_a = os.path.join(pickup_directory, service_file_name_a)

        service_code_a = f'''\
from zato.server.service import Service

class MCPTestAllowListA(Service):
    name = '{service_name_a}'

    def handle(self):
        self.response.payload = '{{"status": "a"}}'
'''

        with open(service_file_path_a, 'w') as service_file:
            _ = service_file.write(service_code_a)

        service_file_name_b = '_mcp_test_allow_list_b.py'
        service_file_path_b = os.path.join(pickup_directory, service_file_name_b)

        service_code_b = f'''\
from zato.server.service import Service

class MCPTestAllowListB(Service):
    name = '{service_name_b}'

    def handle(self):
        self.response.payload = '{{"status": "b"}}'
'''

        with open(service_file_path_b, 'w') as service_file:
            _ = service_file.write(service_code_b)

        logger.info('[test_two_gateways_different_allow_lists] deployed %s and %s', service_name_a, service_name_b)

        # .. wait for both services to be picked up ..
        time.sleep(5)

        # .. create a basic auth for both gateways to share ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'allow-list')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create gateway A restricted to service A and gateway B restricted to service B,
        # both through the wizard and sharing the one sec def ..
        _ = wizard_page.create_gateway(
            page, base_url, gateway_name_a, url_path_a, services=[service_name_a], security=[security_name])
        _ = wizard_page.create_gateway(
            page, base_url, gateway_name_b, url_path_b, services=[service_name_b], security=[security_name])

        # .. verify gateway A only exposes service A ..
        url_a = f'http://127.0.0.1:{server_port}{url_path_a}'
        auth = (security_username, security_password)
        headers = {'Content-Type': 'application/json'}

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url_a, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'Gateway A initialize failed: {initialize_response.status_code}'

        session_id_a = initialize_response.headers['Mcp-Session-Id']
        headers_a = {'Content-Type': 'application/json', 'Mcp-Session-Id': session_id_a}

        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_response_a = requests.post(url_a, data=request_body, headers=headers_a, auth=auth, timeout=10)
        assert tools_response_a.status_code == OK, f'Gateway A tools/list failed: {tools_response_a.status_code}'

        json_body_a = tools_response_a.json()
        result_a = json_body_a['result']
        tools_a = result_a['tools']

        tool_names_a = set()
        for tool in tools_a:
            tool_names_a.add(tool['name'])

        logger.info('[test_two_gateways_different_allow_lists] gateway A tools: %s', tool_names_a)

        assert service_name_a in tool_names_a, \
            f'Expected "{service_name_a}" in gateway A tools, got: {tool_names_a}'
        assert service_name_b not in tool_names_a, \
            f'Gateway A should NOT expose "{service_name_b}", got: {tool_names_a}'

        # .. verify gateway B only exposes service B ..
        url_b = f'http://127.0.0.1:{server_port}{url_path_b}'

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url_b, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'Gateway B initialize failed: {initialize_response.status_code}'

        session_id_b = initialize_response.headers['Mcp-Session-Id']
        headers_b = {'Content-Type': 'application/json', 'Mcp-Session-Id': session_id_b}

        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_response_b = requests.post(url_b, data=request_body, headers=headers_b, auth=auth, timeout=10)
        assert tools_response_b.status_code == OK, f'Gateway B tools/list failed: {tools_response_b.status_code}'

        json_body_b = tools_response_b.json()
        result_b = json_body_b['result']
        tools_b = result_b['tools']

        tool_names_b = set()
        for tool in tools_b:
            tool_names_b.add(tool['name'])

        logger.info('[test_two_gateways_different_allow_lists] gateway B tools: %s', tool_names_b)

        assert service_name_b in tool_names_b, \
            f'Expected "{service_name_b}" in gateway B tools, got: {tool_names_b}'
        assert service_name_a not in tool_names_b, \
            f'Gateway B should NOT expose "{service_name_a}", got: {tool_names_b}'

        # .. the gateways must not outlive the hot-deployed services their allow lists reference,
        # otherwise a fresh server start would fail rebuilding the MCP tool registries,
        # so delete gateway A first ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name_a)
        item_id_a = wizard_page.get_gateway_id(page, gateway_name_a)

        _delete_gateway_row(page, item_id_a, gateway_name_a)

        # .. then delete gateway B ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name_b)
        item_id_b = wizard_page.get_gateway_id(page, gateway_name_b)

        _delete_gateway_row(page, item_id_b, gateway_name_b)

        # .. delete the shared basic auth definition ..
        basic_auth_page_url = f'/zato/security/basic-auth/?cluster=1&query={security_name}'
        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_security = f'#data-table tbody tr:has(td:text-is("{security_name}"))'
        row_security = cast_('any_', page.wait_for_selector(row_selector_security, state='visible', timeout=5000))
        item_id_cell_security = row_security.query_selector('td[class*="item_id_"]')
        item_id_security = item_id_cell_security.inner_text().strip()

        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id_security}")')
        _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        _ = page.wait_for_selector(row_selector_security, state='hidden', timeout=5000)

        # .. and only now remove the deployed service files.
        os.remove(service_file_path_a)
        os.remove(service_file_path_b)

# ################################################################################################################################

    def test_mcp_delete_gateway(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, deletes it via the UI confirm dialog,
        then verifies the row is gone from the table and the URL returns 404.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'del'
        url_path = '/mcp/delete-test/' + rand_string()

        # Create a basic auth so we can verify the gateway works before deletion ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'del')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create the gateway through the wizard ..
        item_id = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name])

        # .. verify the gateway is live ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK before delete, got {response.status_code}'

        # .. delete the gateway via UI ..
        _delete_gateway_row(page, item_id, gateway_name)

        # .. verify the row is gone ..
        row_after_delete = page.query_selector(wizard_page.row_selector(gateway_name))
        assert row_after_delete is None, f'Row "{gateway_name}" should be gone after delete'

        # .. verify the URL returns 404 ..
        page.wait_for_timeout(1000)
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == NOT_FOUND, \
            f'Expected NOT_FOUND after delete, got {response.status_code}'

# ################################################################################################################################

    def test_mcp_delete_gateway_cleans_channel_rest(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, deletes it via the UI,
        then verifies no REST channel with the gateway's name remains in the ODB.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'delete-cleanup'
        url_path = '/mcp/delete-cleanup/' + rand_string()

        # Create a basic auth ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'delete-cleanup')
        security_name = security_info['name']

        # .. create the gateway through the wizard ..
        item_id = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name])

        # .. verify the REST channel exists before deletion ..
        api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.http-soap.get-list'
        api_auth = ('admin.invoke', zato_dashboard['password'])
        api_headers = {'Content-Type': 'application/json'}
        api_payload = json.dumps({'cluster_id': 1, 'connection': 'channel', 'transport': 'plain_http'})

        rest_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert rest_response.status_code == OK, f'API get-list failed: {rest_response.status_code}'

        rest_channels = rest_response.json()
        found_before = False

        for item in rest_channels:
            if item['name'] == gateway_name:
                found_before = True
                break

        assert found_before, f'REST channel "{gateway_name}" should exist before deletion'

        # .. delete the MCP gateway ..
        _delete_gateway_row(page, item_id, gateway_name)

        # .. wait for cleanup to propagate ..
        page.wait_for_timeout(1000)

        # .. verify no REST channel with the gateway's name remains ..
        rest_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert rest_response.status_code == OK, f'API get-list failed after delete: {rest_response.status_code}'

        rest_channels = rest_response.json()
        found_after = False

        for item in rest_channels:
            if item['name'] == gateway_name:
                found_after = True
                break

        assert not found_after, f'REST channel "{gateway_name}" still exists after MCP gateway deletion'

# ################################################################################################################################

    def test_mcp_delete_cancel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP gateway, clicks delete but cancels the confirmation dialog.
        Verifies the row remains in the table and the URL still works.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'del-cancel'
        url_path = '/mcp/delete-cancel/' + rand_string()

        # Create a basic auth ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'del-cancel')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. create the gateway through the wizard ..
        item_id = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name])

        # .. click delete but cancel ..
        page.evaluate(f'$.fn.zato.gateway.mcp.delete_("{item_id}")')
        _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_cancel')

        # .. wait for the popup to close ..
        _ = page.wait_for_selector('#popup_container', state='hidden', timeout=5000)

        # .. verify the row is still there ..
        row_after_cancel = page.query_selector(wizard_page.row_selector(gateway_name))
        assert row_after_cancel is not None, f'Row "{gateway_name}" should still exist after cancel'

        # .. verify the URL still works ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK after cancel, got {response.status_code}'

# ################################################################################################################################

    def test_mcp_list_pagination(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates 45 MCP gateways via UI to span 3 pages (page size = 20).
        Navigates forward through all pages using Next, then backward using Previous,
        verifying each page displays rows and correct pagination info.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _gateway_count = 45
        _page_size = 20

        # .. create 45 gateways, each through the wizard ..
        for idx in range(_gateway_count):
            gateway_name = _Test_Name_Prefix + f'pag-{idx:02d}'
            url_path = f'/mcp/pagination-{idx:02d}/' + rand_string()

            wizard_page.open_wizard_create(page, base_url)
            page.fill('#id_name', gateway_name)
            page.fill('#id_url_path', url_path)
            wizard_page.save_create(page)

        logger.info('[test_mcp_list_pagination] created %d gateways', _gateway_count)

        # .. reload to get a fresh paginated view, filtered to this test's gateways only,
        # otherwise gateways left over from other tests in this file would add extra pages ..
        pagination_list_url = f'{_Page_URL_Pattern}&query={_Test_Name_Prefix}pag-'
        navigate_to_page(page, base_url, pagination_list_url)
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        # .. verify page 1 ..
        action_panel = page.query_selector('.action-panel')
        assert action_panel is not None, 'Pagination action-panel should be visible on page 1'

        panel_text = action_panel.inner_text()
        assert 'Page 1' in panel_text, f'Should be on page 1, got: {panel_text}'

        rows_page_1 = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows_page_1) == _page_size, f'Page 1 should have {_page_size} rows, got {len(rows_page_1)}'

        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is not None, 'Next link should be present on page 1'

        # .. navigate to page 2 ..
        next_link.click()
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = cast_('any_', action_panel).inner_text()
        assert 'Page 2' in panel_text, f'Should be on page 2, got: {panel_text}'

        rows_page_2 = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows_page_2) == _page_size, f'Page 2 should have {_page_size} rows, got {len(rows_page_2)}'

        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is not None, 'Next link should be present on page 2'

        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Previous link should be present on page 2'

        # .. navigate to page 3 ..
        next_link.click()
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = cast_('any_', action_panel).inner_text()
        assert 'Page 3' in panel_text, f'Should be on page 3, got: {panel_text}'

        rows_page_3 = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows_page_3) >= 1, f'Page 3 should have at least 1 row, got {len(rows_page_3)}'

        # .. no Next link on the last page ..
        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is None, 'Next link should NOT be present on the last page'

        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Previous link should be present on page 3'

        # .. navigate back to page 2 ..
        prev_link.click()
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = cast_('any_', action_panel).inner_text()
        assert 'Page 2' in panel_text, f'Should be back on page 2, got: {panel_text}'

        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Previous link should be present on page 2'

        # .. navigate back to page 1 ..
        prev_link.click()
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = cast_('any_', action_panel).inner_text()
        assert 'Page 1' in panel_text, f'Should be back on page 1, got: {panel_text}'

        # .. no Previous link on page 1 ..
        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is None, 'Previous link should NOT be present on page 1'

# ################################################################################################################################

    def test_mcp_list_search(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates gateways with distinct name suffixes, uses the search box to filter,
        and verifies only matching rows appear in the table.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        unique_token = rand_string()
        gateway_name_match = _Test_Name_Prefix + 'srch-' + unique_token
        gateway_name_other = _Test_Name_Prefix + 'srch-other'

        # .. create a gateway with the unique token in its name and another one without it,
        # both through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name_match, '/mcp/search-match/' + rand_string())
        _ = wizard_page.create_gateway(page, base_url, gateway_name_other, '/mcp/search-other/' + rand_string())

        row_selector_match = wizard_page.row_selector(gateway_name_match)
        row_selector_other = wizard_page.row_selector(gateway_name_other)

        # .. go back to the unfiltered list ..
        navigate_to_page(page, base_url, _Page_URL_Pattern)

        # .. search for the unique token ..
        search_input = page.query_selector('input[name="query"]')
        assert search_input is not None, 'Search input should exist'

        search_input.fill(unique_token)
        page.click('input[type="submit"][value="Show gateways"]')
        _ = page.wait_for_selector('#data-table', state='visible', timeout=5000)

        # .. the matching gateway should appear ..
        row_match = page.query_selector(row_selector_match)
        assert row_match is not None, f'Gateway "{gateway_name_match}" should appear in search results'

        # .. the other gateway should not ..
        row_other = page.query_selector(row_selector_other)
        assert row_other is None, f'Gateway "{gateway_name_other}" should NOT appear when searching for "{unique_token}"'

# ################################################################################################################################

    def test_mcp_full_lifecycle_via_ui(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ End-to-end lifecycle: create with security, verify live, rename, verify new URL live
        and old URL dead, verify non-member rejected, deactivate, verify dead, reactivate,
        verify live again, delete, verify dead. All state transitions driven via UI.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'lifecycle'
        url_path = '/mcp/lifecycle/' + rand_string()
        new_name = _Test_Name_Prefix + 'lifecycle-renamed'
        new_url_path = '/mcp/lifecycle-renamed/' + rand_string()

        # Create two basic auth definitions - one member, one non-member ..
        security_info_member = create_basic_auth(page, base_url, _Test_Name_Prefix, 'life-member')
        security_name_member = security_info_member['name']
        security_username_member = security_info_member['username']
        security_password_member = security_info_member['password']

        security_info_nonmember = create_basic_auth(page, base_url, _Test_Name_Prefix, 'life-nonmember')
        security_username_nonmember = security_info_nonmember['username']
        security_password_nonmember = security_info_nonmember['password']

        # 1. CREATE through the wizard with security ..
        item_id = wizard_page.create_gateway(page, base_url, gateway_name, url_path, security=[security_name_member])

        # 2. POST with member creds -> 200 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK with member creds, got {response.status_code}'

        # 3. EDIT RENAME through the wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.fill('#id_edit-name', new_name)
        page.fill('#id_edit-url_path', new_url_path)
        wizard_page.save_edit(page)

        _ = wizard_page.go_to_list(page, base_url, new_name)

        # 4. POST new URL with member creds -> 200 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK at new URL, got {response.status_code}'

        # 5. Old URL -> 404 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at old URL, got {response.status_code}'

        # 6. Non-member -> 403 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_nonmember, security_password_nonmember))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for non-member, got {response.status_code}'

        # 7. EDIT DEACTIVATE through the wizard ..
        wizard_page.open_wizard_edit(page, base_url, new_name)
        page.uncheck('#id_edit-is_active')
        wizard_page.save_edit(page)

        # 8. URL -> 404 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after deactivation, got {response.status_code}'

        # 9. EDIT REACTIVATE through the wizard ..
        wizard_page.open_wizard_edit(page, base_url, new_name)
        page.check('#id_edit-is_active')
        wizard_page.save_edit(page)

        # 10. URL -> 200 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK after reactivation, got {response.status_code}'

        # 11. DELETE via the list page ..
        _ = wizard_page.go_to_list(page, base_url, new_name)
        _delete_gateway_row(page, item_id, new_name)

        # 12. URL -> 404 ..
        page.wait_for_timeout(1000)
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after delete, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(_No_Members_Log)
    def test_mcp_concurrent_edit_via_ui_and_api(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a gateway via UI, edits its url_path via the API, refreshes the UI page,
        asserts the new url_path is displayed in the table, then edits via UI again
        to confirm the edit form carries the values the API saved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _Test_Name_Prefix + 'conc-edit'
        original_url_path = '/mcp/concurrent-original/' + rand_string()
        api_url_path = '/mcp/concurrent-api/' + rand_string()
        ui_url_path = '/mcp/concurrent-ui/' + rand_string()

        # .. create the gateway through the wizard ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, original_url_path)

        # .. get the gateway's ID from the API ..
        api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
        api_auth = ('admin.invoke', zato_dashboard['password'])
        api_headers = {'Content-Type': 'application/json'}
        api_payload = json.dumps({'cluster_id': 1, 'type_': 'gateway-mcp'})

        list_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert list_response.status_code == OK, f'get-list failed: {list_response.status_code}'

        gateway_data = None
        for item in list_response.json():
            if item['name'] == gateway_name:
                gateway_data = item
                break

        assert gateway_data is not None, f'Gateway "{gateway_name}" not found via API'
        gateway_id = gateway_data['id']

        # .. edit url_path via API ..
        edit_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.edit'
        edit_payload = json.dumps({
            'id': gateway_id,
            'name': gateway_name,
            'type_': 'gateway-mcp',
            'is_active': True,
            'is_internal': False,
            'is_channel': True,
            'is_outconn': False,
            'url_path': api_url_path,
        })

        edit_response = requests.post(edit_url, data=edit_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert edit_response.status_code == OK, f'API edit failed: {edit_response.status_code} {edit_response.text}'

        # .. refresh the UI page ..
        row = wizard_page.go_to_list(page, base_url, gateway_name)

        # .. the table should show the API-set url_path ..
        row_text = row.inner_text()
        assert api_url_path in row_text, \
            f'Expected API url_path "{api_url_path}" in row, got: {row_text}'

        # .. verify the API-set URL is live (403 = no security but routable) ..
        response = _post_mcp(server_port, api_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at API url, got {response.status_code}'

        # .. original URL should be gone ..
        response = _post_mcp(server_port, original_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at original url, got {response.status_code}'

        # .. now edit through the wizard to change url_path again ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.fill('#id_edit-url_path', ui_url_path)
        wizard_page.save_edit(page)

        # .. verify UI-set URL is live ..
        response = _post_mcp(server_port, ui_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at UI url, got {response.status_code}'

        # .. API-set URL should now be gone ..
        response = _post_mcp(server_port, api_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at API url after UI edit, got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
