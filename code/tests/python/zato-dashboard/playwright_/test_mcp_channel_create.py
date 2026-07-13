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
from http.client import FORBIDDEN, NOT_FOUND, OK

# requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test import rand_string
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import create_basic_auth, navigate_to_page, open_create_dialog, \
    submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist, anynone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Page_Url_Pattern = '/zato/channel/mcp/?cluster=1'

_Test_Name_Prefix = 'test.mcp.playwright.' + rand_string() + '.'

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

class TestMCPChannelCreate:
    """ Tests for MCP channel creation via the web admin UI.
    """

# ################################################################################################################################

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the MCP channels page and verifies its structure.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'MCP channels' in heading_text, f'Expected "MCP channels" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a new MCP channel' in create_link_text, \
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

    def test_create_minimal(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel with only name and url_path via the UI, verifies the row
        appears correctly, then confirms the channel is live on the server (returns 403 because
        no security groups are configured - default deny).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'minimal'
        url_path = '/mcp/test/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in the fields ..
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. submit and wait for dialog to close ..
        submit_create_form(page)

        # .. verify the new row appears in the table ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. extract cell texts from the row ..
        cells = row.query_selector_all('td')

        name_cell_text = cells[2].inner_text().strip()
        is_active_text = cells[3].inner_text().strip()
        url_path_text = cells[4].inner_text().strip()

        logger.info('[test_create_minimal] name=%s is_active=%s url_path=%s', name_cell_text, is_active_text, url_path_text)

        # .. verify each cell has the correct value ..
        assert name_cell_text == channel_name, \
            f'Expected name "{channel_name}", got: "{name_cell_text}"'

        assert is_active_text == 'Yes', \
            f'Expected is_active "Yes", got: "{is_active_text}"'

        assert url_path_text == url_path, \
            f'Expected url_path "{url_path}", got: "{url_path_text}"'

        # .. POST an MCP request - should get 403 (no security groups = default deny) ..
        response = _post_mcp(server_port, url_path)

        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for no-security channel, got {response.status_code}: {response.text}'

# ################################################################################################################################

    def test_create_with_services(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel with two services assigned via the badge picker.
        Verifies the row shows service count = 2, reopens edit to confirm both are pre-selected,
        then confirms the channel is live on the server.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'with-services'
        url_path = '/mcp/test-service/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in the fields ..
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. wait for the service badge picker to load ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        # .. pick the first two available service badges ..
        available_badges = page.query_selector_all('#badge-zone-available-create .badge-zone-body .security-badge')

        service_name_1 = available_badges[0].get_attribute('data-name')
        service_name_2 = available_badges[1].get_attribute('data-name')

        logger.info('[test_create_with_services] selecting services: %s, %s', service_name_1, service_name_2)

        # .. click badges to move them to assigned zone ..
        available_badges[0].click()
        available_badges[1].click()

        # .. verify assigned count shows 2 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-create .badge-zone-count')
        assert assigned_count_text == '2', f'Expected assigned count "2", got: "{assigned_count_text}"'

        # .. submit and wait for dialog to close ..
        submit_create_form(page)

        # .. verify the new row appears with service count = 2 ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        cells = row.query_selector_all('td')

        service_count_text = cells[5].inner_text().strip()
        logger.info('[test_create_with_services] service_count_text=%s', service_count_text)

        assert service_count_text == '2', \
            f'Expected service count "2", got: "{service_count_text}"'

        # .. reopen the edit dialog to confirm services are pre-selected ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for the badge picker to load in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-assigned-edit .badge-zone-body .security-badge").length === 2',
            timeout=10000
        )

        # .. verify the two services are in the assigned zone ..
        assigned_badges = page.query_selector_all('#badge-zone-assigned-edit .badge-zone-body .security-badge')
        assigned_names = set()

        for badge in assigned_badges:
            assigned_names.add(badge.get_attribute('data-name'))

        logger.info('[test_create_with_services] assigned_names in edit=%s', assigned_names)

        assert service_name_1 in assigned_names, \
            f'Expected "{service_name_1}" in assigned, got: {assigned_names}'

        assert service_name_2 in assigned_names, \
            f'Expected "{service_name_2}" in assigned, got: {assigned_names}'

        # .. POST an MCP request - should get 403 (no security groups = default deny) ..
        response = _post_mcp(server_port, url_path)

        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for no-security channel, got {response.status_code}: {response.text}'

        # .. verify the ODB has the correct services stored ..
        api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
        api_auth = ('admin.invoke', zato_dashboard['password'])
        api_headers = {'Content-Type': 'application/json'}
        api_payload = json.dumps({'cluster_id': 1, 'type_': 'channel-mcp'})

        odb_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert odb_response.status_code == OK, f'API call failed: {odb_response.status_code} {odb_response.text}'

        items = odb_response.json()
        channel_data:'anynone' = None

        for item in items:
            if item['name'] == channel_name:
                channel_data = item
                break

        assert channel_data is not None, f'Channel "{channel_name}" not found in ODB'

        services = channel_data.get('services')
        if services is None:
            services = []

        stored_services = set(services)
        logger.info('[test_create_with_services] stored_services=%s', stored_services)

        assert service_name_1 in stored_services, \
            f'Expected "{service_name_1}" in stored services, got: {stored_services}'

        assert service_name_2 in stored_services, \
            f'Expected "{service_name_2}" in stored services, got: {stored_services}'

# ################################################################################################################################

    def test_create_with_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth definition via the UI, then creates an MCP channel
        with that sec def assigned via the security badge picker.
        Verifies the row shows security count = 1, then POSTs with valid and invalid creds.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'with-security'
        url_path = '/mcp/test-security/' + rand_string()

        # Create a basic auth definition via the UI so we know the credentials ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'mcp-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        logger.info('[test_create_with_security] created sec def: name=%s username=%s', security_name, security_username)

        # .. navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in the fields ..
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. wait for the security badge picker to load ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. pick the badge matching our newly created sec def ..
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for sec def "{security_name}"'

        security_badge.click()

        # .. verify assigned count shows 1 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-sec-create .badge-zone-count')
        assert assigned_count_text == '1', f'Expected assigned count "1", got: "{assigned_count_text}"'

        # .. submit and wait for dialog to close ..
        submit_create_form(page)

        # .. verify the new row appears with security count = 1 ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        cells = row.query_selector_all('td')

        # Column index 6 is the security members count
        security_count_text = cells[6].inner_text().strip()
        logger.info('[test_create_with_security] security_count_text=%s', security_count_text)

        assert security_count_text == '1', f'Expected security count "1", got: "{security_count_text}"'

        # .. POST with valid creds - should get OK (MCP initialize response) ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK with valid creds, got {response.status_code}: {response.text}'

        # .. POST with invalid creds - should get FORBIDDEN ..
        response = _post_mcp(server_port, url_path, auth=('bogus_user', 'bogus_pass'))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN with invalid creds, got {response.status_code}: {response.text}'

# ################################################################################################################################

    def test_export(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel with both a Basic Auth and an API key definition assigned,
        clicks the row's Export link and verifies the downloaded server.json-format document,
        including both authentication headers.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'export'
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

        # .. navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in the fields ..
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. wait for both of our security badges to be available ..
        basic_auth_badge_selector = \
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{basic_auth_name}"]'
        apikey_badge_selector = \
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{apikey_name}"]'

        basic_auth_badge = page.wait_for_selector(basic_auth_badge_selector, state='visible', timeout=10000)
        apikey_badge = page.wait_for_selector(apikey_badge_selector, state='visible', timeout=10000)

        assert basic_auth_badge is not None, f'Could not find badge for sec def "{basic_auth_name}"'
        assert apikey_badge is not None, f'Could not find badge for sec def "{apikey_name}"'

        # .. assign both definitions to the channel ..
        basic_auth_badge.click()
        apikey_badge.click()

        # .. verify the assigned count shows 2 ..
        assigned_count_text = page.inner_text('#badge-zone-assigned-sec-create .badge-zone-count')
        assert assigned_count_text == '2', f'Expected assigned count "2", got: "{assigned_count_text}"'

        # .. submit and wait for the dialog to close ..
        submit_create_form(page)

        # .. wait for the new row to appear ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        assert row is not None, f'Could not find the row for channel "{channel_name}"'

        # .. click the Export link and capture the download ..
        export_link = row.query_selector('a:text-is("Export")')
        assert export_link is not None, 'Could not find the Export link in the row'

        with page.expect_download() as download_info:
            export_link.click()

        download = download_info.value

        # .. the channel name contains only characters allowed in a slug, so the file name uses it as is ..
        expected_file_name = f'mcp-{channel_name}.json'
        assert download.suggested_filename == expected_file_name, \
            f'Expected file name "{expected_file_name}", got: "{download.suggested_filename}"'

        # .. load the downloaded document ..
        download_path = download.path()

        with open(download_path) as json_file:
            document = json.load(json_file)

        logger.info('[test_export] document=%s', document)

        # .. the dashboard under test runs with Zato_Server_Address=http://127.0.0.1:<server_port>,
        # and IP addresses are used as namespaces as they are, without reversing their labels ..
        expected_name = f'127.0.0.1/{channel_name}'
        assert document['name'] == expected_name, f'Expected name "{expected_name}", got: "{document["name"]}"'

        assert document['description'] == f'MCP channel {channel_name}', \
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

    def test_edit_rename(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, then edits it to change both name and url_path.
        Asserts the old URL returns 404 and the new URL is routable (403 = no security, but routable).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        old_name = _Test_Name_Prefix + 'rename-old'
        old_url_path = '/mcp/rename-old/' + rand_string()
        new_name = _Test_Name_Prefix + 'rename-new'
        new_url_path = '/mcp/rename-new/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the initial channel ..
        open_create_dialog(page)
        page.fill('#id_name', old_name)
        page.fill('#id_url_path', old_url_path)
        submit_create_form(page)

        # .. verify it appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{old_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm old URL is routable (403 = no security but channel exists) ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN on old URL, got {response.status_code}'

        # .. open the edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. change name and url_path ..
        page.fill('#edit-div #id_edit-name', new_name)
        page.fill('#edit-div #id_edit-url_path', new_url_path)

        # .. submit the edit form ..
        submit_edit_form(page)

        # .. verify the row now shows the new name ..
        new_row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
        page.wait_for_selector(new_row_selector, state='visible', timeout=5000)

        logger.info('[test_edit_rename] renamed %s -> %s, %s -> %s', old_name, new_name, old_url_path, new_url_path)

        # .. old URL should now return 404 ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND on old URL after rename, got {response.status_code}'

        # .. new URL should be routable (403 = no security) ..
        response = _post_mcp(server_port, new_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN on new URL, got {response.status_code}'

# ################################################################################################################################

    def test_edit_rename_preserves_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel with a security member, renames it (changes url_path),
        and asserts that security group enforcement still works at the new URL.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'rename-sec'
        old_url_path = '/mcp/rename-security-old/' + rand_string()
        new_url_path = '/mcp/rename-security-new/' + rand_string()

        # Create a basic auth definition via the UI ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rename-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', old_url_path)

        # .. wait for the security badge picker ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. select our sec def ..
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for sec def "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        # .. verify the channel works with valid creds at old URL ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        response = _post_mcp(server_port, old_url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK at old URL with valid creds, got {response.status_code}'

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. change only the url_path ..
        page.fill('#edit-div #id_edit-url_path', new_url_path)

        # .. submit ..
        submit_edit_form(page)

        # .. wait for the table to refresh ..
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        logger.info('[test_edit_rename_preserves_security] renamed url_path %s -> %s', old_url_path, new_url_path)

        # .. old URL should be gone ..
        response = _post_mcp(server_port, old_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND on old URL, got {response.status_code}'

        # .. new URL with valid creds should still work ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK at new URL with valid creds, got {response.status_code}'

        # .. new URL with invalid creds should be forbidden ..
        response = _post_mcp(server_port, new_url_path, auth=('bogus_user', 'bogus_pass'))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at new URL with bad creds, got {response.status_code}'

# ################################################################################################################################

    def test_edit_deactivate(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, then edits it to uncheck is_active.
        Asserts the URL returns 404 after deactivation.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'deactivate'
        url_path = '/mcp/deactivate/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)
        submit_create_form(page)

        # .. verify it appears and is active ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm URL is routable while active ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN (active, no sec), got {response.status_code}'

        # .. open the edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. uncheck is_active ..
        page.uncheck('#edit-div #id_edit-is_active')

        # .. submit ..
        submit_edit_form(page)

        logger.info('[test_edit_deactivate] deactivated channel %s', channel_name)

        # .. URL should now return 404 ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after deactivation, got {response.status_code}'

# ################################################################################################################################

    def test_edit_reactivate(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, deactivates it, then reactivates it.
        Asserts the URL returns 404 when inactive and is routable again after reactivation.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'reactivate'
        url_path = '/mcp/reactivate/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)
        submit_create_form(page)

        # .. verify it appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. open edit and deactivate ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        page.uncheck('#edit-div #id_edit-is_active')
        submit_edit_form(page)

        # .. confirm URL is now 404 ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND when inactive, got {response.status_code}'

        # .. reopen edit and reactivate ..
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        page.check('#edit-div #id_edit-is_active')
        submit_edit_form(page)

        logger.info('[test_edit_reactivate] reactivated channel %s', channel_name)

        # .. URL should be routable again (403 = no security, but exists) ..
        response = _post_mcp(server_port, url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN after reactivation, got {response.status_code}'

# ################################################################################################################################

    def test_edit_add_service(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel with 1 service and security, edits it to add a second service.
        Asserts tools/list returns both services.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'add-service'
        url_path = '/mcp/add-service/' + rand_string()

        # Create a sec def so we can authenticate ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-service')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with 1 service and security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. wait for service badges ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        # .. pick only the first service ..
        available_services = page.query_selector_all('#badge-zone-available-create .badge-zone-body .security-badge')
        service_name_1 = available_services[0].get_attribute('data-name')
        available_services[0].click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        security_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. initialize to confirm channel is live ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for service badges in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-edit .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. pick a second service ..
        available_services_edit = page.query_selector_all('#badge-zone-available-edit .badge-zone-body .security-badge')
        service_name_2 = available_services_edit[0].get_attribute('data-name')
        available_services_edit[0].click()

        logger.info('[test_edit_add_service] adding service: %s (already has: %s)', service_name_2, service_name_1)

        # .. submit edit ..
        submit_edit_form(page)

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
        """ Creates an MCP channel with 2 services and security, edits it to remove one.
        Asserts tools/list returns only the remaining service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'rm-service'
        url_path = '/mcp/remove-service/' + rand_string()

        # Create a sec def ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-service')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with 2 services and security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        # .. wait for service badges ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        # .. pick two services ..
        available_services = page.query_selector_all('#badge-zone-available-create .badge-zone-body .security-badge')
        service_name_1 = available_services[0].get_attribute('data-name')
        service_name_2 = available_services[1].get_attribute('data-name')
        available_services[0].click()
        available_services[1].click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        security_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for assigned badges in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-assigned-edit .badge-zone-body .security-badge").length === 2',
            timeout=10000
        )

        # .. remove the first service by clicking it in the assigned zone ..
        remove_selector = f'#badge-zone-assigned-edit .badge-zone-body .security-badge[data-name="{service_name_1}"]'
        badge_to_remove = page.query_selector(remove_selector)
        assert badge_to_remove is not None, f'Could not find badge "{service_name_1}" in assigned zone'
        badge_to_remove.click()

        logger.info('[test_edit_remove_service] removing service: %s (keeping: %s)', service_name_1, service_name_2)

        # .. submit edit ..
        submit_edit_form(page)

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
        """ Creates a channel with 1 sec def, edits to add a second sec def.
        Asserts both can authenticate.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'add-sec'
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

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with only the first sec def ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_1}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name_1}"'
        security_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm first creds work, second does not ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for sec_2 before edit, got {response.status_code}'

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for the security badge picker in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-edit .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. add the second sec def ..
        badge_selector = f'#badge-zone-available-sec-edit .badge-zone-body .security-badge[data-name="{security_name_2}"]'
        security_badge_2 = page.query_selector(badge_selector)
        assert security_badge_2 is not None, f'Could not find badge for "{security_name_2}" in edit available zone'
        security_badge_2.click()

        submit_edit_form(page)

        logger.info('[test_edit_add_security_member] added sec def %s to channel %s', security_name_2, channel_name)

        # .. both should now authenticate ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 after edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for sec_2 after edit, got {response.status_code}'

# ################################################################################################################################

    def test_edit_remove_security_member(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with 2 sec defs, edits to remove one.
        Removed member -> 403, remaining member -> 200.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'rm-sec'
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

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with both sec defs ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        badge_1 = page.query_selector(
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_1}"]')
        badge_2 = page.query_selector(
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_2}"]')
        assert badge_1 is not None, f'Could not find badge for "{security_name_1}"'
        assert badge_2 is not None, f'Could not find badge for "{security_name_2}"'
        badge_1.click()
        badge_2.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm both work ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 before edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for sec_2 before edit, got {response.status_code}'

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for assigned sec badges in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-assigned-sec-edit .badge-zone-body .security-badge").length === 2',
            timeout=10000
        )

        # .. remove the first sec def by clicking it in the assigned zone ..
        remove_selector = f'#badge-zone-assigned-sec-edit .badge-zone-body .security-badge[data-name="{security_name_1}"]'
        badge_to_remove = page.query_selector(remove_selector)
        assert badge_to_remove is not None, f'Could not find badge "{security_name_1}" in assigned sec zone'
        badge_to_remove.click()

        submit_edit_form(page)

        logger.info('[test_edit_remove_security_member] removed sec def %s from channel %s', security_name_1, channel_name)

        # .. removed member should get 403, remaining should get 200 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_1, security_password_1))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for removed sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(security_username_2, security_password_2))
        assert response.status_code == OK, f'Expected OK for remaining sec_2, got {response.status_code}'

# ################################################################################################################################

    def test_edit_remove_all_security(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with sec defs, edits to remove all.
        Asserts all requests return 403 (default deny).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'rm-all-sec'
        url_path = '/mcp/remove-all-security/' + rand_string()

        # Create a basic auth definition ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-all-sec')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel with security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm creds work ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK before edit, got {response.status_code}'

        # .. open edit dialog ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for assigned sec badges in edit mode ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-assigned-sec-edit .badge-zone-body .security-badge").length === 1',
            timeout=10000
        )

        # .. remove all sec defs by clicking the one assigned badge ..
        remove_selector = f'#badge-zone-assigned-sec-edit .badge-zone-body .security-badge[data-name="{security_name}"]'
        badge_to_remove = page.query_selector(remove_selector)
        assert badge_to_remove is not None, f'Could not find badge "{security_name}" in assigned sec zone'
        badge_to_remove.click()

        submit_edit_form(page)

        logger.info('[test_edit_remove_all_security] removed all security from channel %s', channel_name)

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
        """ Creates a channel, then tries to create another with the same name.
        Asserts the UI blocks submission (dialog stays open, field gets attention indicator).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'dup-name'
        url_path_1 = '/mcp/duplicate-1/' + rand_string()
        url_path_2 = '/mcp/duplicate-2/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the first channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path_1)
        submit_create_form(page)

        # .. verify it appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. try to create a second channel with the same name ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path_2)

        # .. click submit ..
        page.click('#create-div input[type="submit"]')

        # .. the dialog should stay open because the name is taken ..
        page.wait_for_selector('.zato-unique-taken', state='visible', timeout=5000)

        # .. verify the dialog is still visible ..
        dialog_visible = page.is_visible('#create-div')
        assert dialog_visible, 'Expected create dialog to remain open for duplicate name'

        logger.info('[test_create_duplicate_name] duplicate name correctly blocked')

# ################################################################################################################################

    def test_create_duplicate_url_path(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with a URL path, then tries to create another with the same path.
        Asserts the UI blocks submission (dialog stays open, field gets attention indicator).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name_1 = _Test_Name_Prefix + 'dup-path-1'
        channel_name_2 = _Test_Name_Prefix + 'dup-path-2'
        url_path = '/mcp/duplicate-path/' + rand_string()

        # Navigate to the MCP channels page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the first channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_1)
        page.fill('#id_url_path', url_path)
        submit_create_form(page)

        # .. verify it appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name_1}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. try to create a second channel with the same url_path ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_2)
        page.fill('#id_url_path', url_path)

        # .. click submit ..
        page.click('#create-div input[type="submit"]')

        # .. the dialog should stay open because the url_path is taken ..
        page.wait_for_selector('.zato-unique-taken', state='visible', timeout=5000)

        # .. verify the dialog is still visible ..
        dialog_visible = page.is_visible('#create-div')
        assert dialog_visible, 'Expected create dialog to remain open for duplicate url_path'

        logger.info('[test_create_duplicate_url_path] duplicate url_path correctly blocked')

# ################################################################################################################################

    def test_service_hot_deploy_updates_tools_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Hot-deploys a new service, edits an MCP channel via UI to include it,
        then verifies tools/list returns the new service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        channel_name = _Test_Name_Prefix + 'hotdep'
        url_path = '/mcp/hot-deploy/' + rand_string()
        hot_deploy_service_name = 'mcp-test.hot-deploy-tools.' + rand_string()

        # Create a sec def so we can authenticate ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'hotdep')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a channel with demo.echo and security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. pick demo.echo ..
        service_badge_selector = '#badge-zone-available-create .badge-zone-body .security-badge[data-name="demo.echo"]'
        service_badge = page.query_selector(service_badge_selector)
        assert service_badge is not None, 'Could not find badge for "demo.echo"'
        service_badge.click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

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

        # .. open the edit dialog to add the hot-deployed service ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. wait for the hot-deployed service to appear in the available services badge picker ..
        badge_selector_edit = f'#badge-zone-available-edit .badge-zone-body .security-badge[data-name="{hot_deploy_service_name}"]'

        deadline = time.monotonic() + 15

        while time.monotonic() < deadline:
            badge = page.query_selector(badge_selector_edit)
            if badge:
                break
            # .. close and reopen edit to refresh the badge list ..
            page.keyboard.press('Escape')
            page.wait_for_selector('#edit-div', state='hidden', timeout=3000)
            time.sleep(1)
            page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
            page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        else:
            os.remove(service_file_path)
            raise AssertionError(
                f'Hot-deployed service "{hot_deploy_service_name}" did not appear in edit badge picker within 15s')

        badge.click()

        submit_edit_form(page)

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

        # .. the channel must not outlive the hot-deployed service its allow list references,
        # otherwise a fresh server start would fail rebuilding the MCP tool registries,
        # so delete the channel first ..
        mcp_list_url = f'{_Page_Url_Pattern}&query={channel_name}'
        navigate_to_page(page, base_url, mcp_list_url)

        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector, state='hidden', timeout=5000)

        # .. delete the basic auth definition ..
        basic_auth_page_url = f'/zato/security/basic-auth/?cluster=1&query={security_name}'
        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_security = f'#data-table tbody tr:has(td:text-is("{security_name}"))'
        row_security = page.wait_for_selector(row_selector_security, state='visible', timeout=5000)
        item_id_cell_security = row_security.query_selector('td[class*="item_id_"]')
        item_id_security = item_id_cell_security.inner_text().strip()

        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id_security}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector_security, state='hidden', timeout=5000)

        # .. and only now remove the deployed service file.
        os.remove(service_file_path)

        assert hot_deploy_service_name in tool_names, \
            f'Expected "{hot_deploy_service_name}" in tools after hot-deploy, got: {tool_names}'

# ################################################################################################################################

    def test_sec_def_password_change(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth, assigns it to an MCP channel's security group,
        verifies the original password works, changes the password via the basic auth UI,
        then verifies old password -> 403 and new password -> 200.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'pwd-chg'
        url_path = '/mcp/password-change/' + rand_string()

        # Create a basic auth definition ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pwd-chg')
        security_name = security_info['name']
        security_username = security_info['username']
        old_password = security_info['password']

        # .. navigate to MCP channels and create a channel with this sec def ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

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
        row = page.wait_for_selector(row_selector_basic_auth, state='visible', timeout=5000)

        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', new_password)
        page.click('#change_password-div input[type="submit"]')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

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

    def test_two_channels_different_groups(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two MCP channels, each with a different security group member.
        Verifies cross-group access is denied: A with Y-creds -> 403, B with X-creds -> 403.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name_a = _Test_Name_Prefix + 'iso-a'
        channel_name_b = _Test_Name_Prefix + 'iso-b'
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

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create channel A with security A ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_a)
        page.fill('#id_url_path', url_path_a)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 2',
            timeout=10000
        )

        badge_selector_a = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_a}"]'
        security_badge_a = page.query_selector(badge_selector_a)
        assert security_badge_a is not None, f'Could not find badge for "{security_name_a}"'
        security_badge_a.click()

        submit_create_form(page)

        row_selector_a = f'#data-table tbody tr:has(td:text-is("{channel_name_a}"))'
        page.wait_for_selector(row_selector_a, state='visible', timeout=5000)

        # .. create channel B with security B ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_b)
        page.fill('#id_url_path', url_path_b)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector_b = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_b}"]'
        security_badge_b = page.query_selector(badge_selector_b)
        assert security_badge_b is not None, f'Could not find badge for "{security_name_b}"'
        security_badge_b.click()

        submit_create_form(page)

        row_selector_b = f'#data-table tbody tr:has(td:text-is("{channel_name_b}"))'
        page.wait_for_selector(row_selector_b, state='visible', timeout=5000)

        # .. verify own creds work on own channel ..
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

    def test_two_channels_different_allow_lists(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two MCP channels with different service allow lists.
        Channel A allows svc-a only, channel B allows svc-b only.
        Verifies each channel's tools/list only exposes its own allowed service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        suffix_a = rand_string()
        suffix_b = rand_string()

        channel_name_a = _Test_Name_Prefix + 'allow-a'
        channel_name_b = _Test_Name_Prefix + 'allow-b'
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

        logger.info('[test_two_channels_different_allow_lists] deployed %s and %s', service_name_a, service_name_b)

        # .. wait for both services to be picked up ..
        time.sleep(5)

        # .. create a basic auth for both channels to share ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'allow-list')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create channel A restricted to service A ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_a)
        page.fill('#id_url_path', url_path_a)

        # .. wait for service badges to load ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. select service A ..
        service_badge_selector_a = f'#badge-zone-available-create .badge-zone-body .security-badge[data-name="{service_name_a}"]'
        service_badge_a = page.query_selector(service_badge_selector_a)
        assert service_badge_a is not None, f'Could not find service badge for "{service_name_a}"'
        service_badge_a.click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find security badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        row_selector_a = f'#data-table tbody tr:has(td:text-is("{channel_name_a}"))'
        page.wait_for_selector(row_selector_a, state='visible', timeout=5000)

        # .. create channel B restricted to service B ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_b)
        page.fill('#id_url_path', url_path_b)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. select service B ..
        service_badge_selector_b = f'#badge-zone-available-create .badge-zone-body .security-badge[data-name="{service_name_b}"]'
        service_badge_b = page.query_selector(service_badge_selector_b)
        assert service_badge_b is not None, f'Could not find service badge for "{service_name_b}"'
        service_badge_b.click()

        # .. assign the same security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find security badge for "{security_name}" (channel B)'
        security_badge.click()

        submit_create_form(page)

        row_selector_b = f'#data-table tbody tr:has(td:text-is("{channel_name_b}"))'
        page.wait_for_selector(row_selector_b, state='visible', timeout=5000)

        # .. verify channel A only exposes service A ..
        url_a = f'http://127.0.0.1:{server_port}{url_path_a}'
        auth = (security_username, security_password)
        headers = {'Content-Type': 'application/json'}

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url_a, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'Channel A initialize failed: {initialize_response.status_code}'

        session_id_a = initialize_response.headers['Mcp-Session-Id']
        headers_a = {'Content-Type': 'application/json', 'Mcp-Session-Id': session_id_a}

        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_response_a = requests.post(url_a, data=request_body, headers=headers_a, auth=auth, timeout=10)
        assert tools_response_a.status_code == OK, f'Channel A tools/list failed: {tools_response_a.status_code}'

        json_body_a = tools_response_a.json()
        result_a = json_body_a['result']
        tools_a = result_a['tools']

        tool_names_a = set()
        for tool in tools_a:
            tool_names_a.add(tool['name'])

        logger.info('[test_two_channels_different_allow_lists] channel A tools: %s', tool_names_a)

        assert service_name_a in tool_names_a, \
            f'Expected "{service_name_a}" in channel A tools, got: {tool_names_a}'
        assert service_name_b not in tool_names_a, \
            f'Channel A should NOT expose "{service_name_b}", got: {tool_names_a}'

        # .. verify channel B only exposes service B ..
        url_b = f'http://127.0.0.1:{server_port}{url_path_b}'

        request_body = make_jsonrpc_initialize()
        initialize_response = requests.post(url_b, data=request_body, headers=headers, auth=auth, timeout=10)
        assert initialize_response.status_code == OK, f'Channel B initialize failed: {initialize_response.status_code}'

        session_id_b = initialize_response.headers['Mcp-Session-Id']
        headers_b = {'Content-Type': 'application/json', 'Mcp-Session-Id': session_id_b}

        request_body = json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2})
        tools_response_b = requests.post(url_b, data=request_body, headers=headers_b, auth=auth, timeout=10)
        assert tools_response_b.status_code == OK, f'Channel B tools/list failed: {tools_response_b.status_code}'

        json_body_b = tools_response_b.json()
        result_b = json_body_b['result']
        tools_b = result_b['tools']

        tool_names_b = set()
        for tool in tools_b:
            tool_names_b.add(tool['name'])

        logger.info('[test_two_channels_different_allow_lists] channel B tools: %s', tool_names_b)

        assert service_name_b in tool_names_b, \
            f'Expected "{service_name_b}" in channel B tools, got: {tool_names_b}'
        assert service_name_a not in tool_names_b, \
            f'Channel B should NOT expose "{service_name_a}", got: {tool_names_b}'

        # .. the channels must not outlive the hot-deployed services their allow lists reference,
        # otherwise a fresh server start would fail rebuilding the MCP tool registries,
        # so delete channel A first ..
        mcp_list_url = f'{_Page_Url_Pattern}&query={_Test_Name_Prefix}allow-'
        navigate_to_page(page, base_url, mcp_list_url)

        row_a = page.wait_for_selector(row_selector_a, state='visible', timeout=5000)
        item_id_cell_a = row_a.query_selector('td[class*="item_id_"]')
        item_id_a = item_id_cell_a.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id_a}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector_a, state='hidden', timeout=5000)

        # .. then delete channel B ..
        row_b = page.wait_for_selector(row_selector_b, state='visible', timeout=5000)
        item_id_cell_b = row_b.query_selector('td[class*="item_id_"]')
        item_id_b = item_id_cell_b.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id_b}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector_b, state='hidden', timeout=5000)

        # .. delete the shared basic auth definition ..
        basic_auth_page_url = f'/zato/security/basic-auth/?cluster=1&query={security_name}'
        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_security = f'#data-table tbody tr:has(td:text-is("{security_name}"))'
        row_security = page.wait_for_selector(row_selector_security, state='visible', timeout=5000)
        item_id_cell_security = row_security.query_selector('td[class*="item_id_"]')
        item_id_security = item_id_cell_security.inner_text().strip()

        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id_security}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector_security, state='hidden', timeout=5000)

        # .. and only now remove the deployed service files.
        os.remove(service_file_path_a)
        os.remove(service_file_path_b)

# ################################################################################################################################

    def test_mcp_delete_channel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, deletes it via the UI confirm dialog,
        then verifies the row is gone from the table and the URL returns 404.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'del'
        url_path = '/mcp/delete-test/' + rand_string()

        # Create a basic auth so we can verify the channel works before deletion ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'del')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. verify the channel is live ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK before delete, got {response.status_code}'

        # .. get the item id for the delete call ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        # .. delete the channel via UI ..
        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')

        # .. wait for the row to disappear ..
        page.wait_for_selector(row_selector, state='hidden', timeout=5000)

        # .. verify the row is gone ..
        row_after_delete = page.query_selector(row_selector)
        assert row_after_delete is None, f'Row "{channel_name}" should be gone after delete'

        # .. verify the URL returns 404 ..
        page.wait_for_timeout(1000)
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == NOT_FOUND, \
            f'Expected NOT_FOUND after delete, got {response.status_code}'

# ################################################################################################################################

    def test_mcp_delete_channel_cleans_channel_rest(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, deletes it via the UI,
        then verifies no orphan REST channel with the same name remains in the ODB.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'orphan'
        url_path = '/mcp/orphan-test/' + rand_string()

        # Create a basic auth ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'orphan')
        security_name = security_info['name']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

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
            if item['name'] == channel_name:
                found_before = True
                break

        assert found_before, f'REST channel "{channel_name}" should exist before deletion'

        # .. delete the MCP channel ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(row_selector, state='hidden', timeout=5000)

        # .. wait for cleanup to propagate ..
        page.wait_for_timeout(1000)

        # .. verify no orphan REST channel remains ..
        rest_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert rest_response.status_code == OK, f'API get-list failed after delete: {rest_response.status_code}'

        rest_channels = rest_response.json()
        found_after = False

        for item in rest_channels:
            if item['name'] == channel_name:
                found_after = True
                break

        assert not found_after, f'Orphan REST channel "{channel_name}" still exists after MCP channel deletion'

# ################################################################################################################################

    def test_mcp_delete_cancel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, clicks delete but cancels the confirmation dialog.
        Verifies the row remains in the table and the URL still works.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'del-cancel'
        url_path = '/mcp/delete-cancel/' + rand_string()

        # Create a basic auth ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'del-cancel')
        security_name = security_info['name']
        security_username = security_info['username']
        security_password = security_info['password']

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name}"'
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. get the item id ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        # .. click delete but cancel ..
        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_cancel')

        # .. wait for the popup to close ..
        page.wait_for_selector('#popup_container', state='hidden', timeout=5000)

        # .. verify the row is still there ..
        row_after_cancel = page.query_selector(row_selector)
        assert row_after_cancel is not None, f'Row "{channel_name}" should still exist after cancel'

        # .. verify the URL still works ..
        response = _post_mcp(server_port, url_path, auth=(security_username, security_password))
        assert response.status_code == OK, f'Expected OK after cancel, got {response.status_code}'

# ################################################################################################################################

    def test_mcp_list_pagination(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates 45 MCP channels via UI to span 3 pages (page size = 20).
        Navigates forward through all pages using Next, then backward using Previous,
        verifying each page displays rows and correct pagination info.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _channel_count = 45
        _page_size = 20

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create 45 channels ..
        for idx in range(_channel_count):
            channel_name = _Test_Name_Prefix + f'pag-{idx:02d}'
            url_path = f'/mcp/pagination-{idx:02d}/' + rand_string()

            open_create_dialog(page)
            page.fill('#id_name', channel_name)
            page.fill('#id_url_path', url_path)
            submit_create_form(page)

            row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
            page.wait_for_selector(row_selector, state='visible', timeout=5000)

        logger.info('[test_mcp_list_pagination] created %d channels', _channel_count)

        # .. reload to get a fresh paginated view, filtered to this test's channels only,
        # otherwise channels left over from other tests in this file would add extra pages ..
        pagination_list_url = f'{_Page_Url_Pattern}&query={_Test_Name_Prefix}pag-'
        navigate_to_page(page, base_url, pagination_list_url)
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

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
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()
        assert 'Page 2' in panel_text, f'Should be on page 2, got: {panel_text}'

        rows_page_2 = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows_page_2) == _page_size, f'Page 2 should have {_page_size} rows, got {len(rows_page_2)}'

        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is not None, 'Next link should be present on page 2'

        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Previous link should be present on page 2'

        # .. navigate to page 3 ..
        next_link.click()
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()
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
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()
        assert 'Page 2' in panel_text, f'Should be back on page 2, got: {panel_text}'

        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Previous link should be present on page 2'

        # .. navigate back to page 1 ..
        prev_link.click()
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()
        assert 'Page 1' in panel_text, f'Should be back on page 1, got: {panel_text}'

        # .. no Previous link on page 1 ..
        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is None, 'Previous link should NOT be present on page 1'

# ################################################################################################################################

    def test_mcp_list_search(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates channels with distinct name suffixes, uses the search box to filter,
        and verifies only matching rows appear in the table.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        unique_token = rand_string()
        channel_name_match = _Test_Name_Prefix + 'srch-' + unique_token
        channel_name_other = _Test_Name_Prefix + 'srch-other'

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a channel with the unique token in its name ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_match)
        page.fill('#id_url_path', '/mcp/search-match/' + rand_string())
        submit_create_form(page)

        row_selector_match = f'#data-table tbody tr:has(td:text-is("{channel_name_match}"))'
        page.wait_for_selector(row_selector_match, state='visible', timeout=5000)

        # .. create another channel without the token ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name_other)
        page.fill('#id_url_path', '/mcp/search-other/' + rand_string())
        submit_create_form(page)

        row_selector_other = f'#data-table tbody tr:has(td:text-is("{channel_name_other}"))'
        page.wait_for_selector(row_selector_other, state='visible', timeout=5000)

        # .. search for the unique token ..
        search_input = page.query_selector('input[name="query"]')
        assert search_input is not None, 'Search input should exist'

        search_input.fill(unique_token)
        page.click('input[type="submit"][value="Show channels"]')
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        # .. the matching channel should appear ..
        row_match = page.query_selector(row_selector_match)
        assert row_match is not None, f'Channel "{channel_name_match}" should appear in search results'

        # .. the other channel should not ..
        row_other = page.query_selector(row_selector_other)
        assert row_other is None, f'Channel "{channel_name_other}" should NOT appear when searching for "{unique_token}"'

# ################################################################################################################################

    def test_mcp_full_lifecycle_via_ui(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ End-to-end lifecycle: create with security, verify live, rename, verify new URL live
        and old URL dead, verify non-member rejected, deactivate, verify dead, reactivate,
        verify live again, delete, verify dead. All state transitions driven via UI.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'lifecycle'
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

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # 1. CREATE with security ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{security_name_member}"]'
        security_badge = page.query_selector(badge_selector)
        assert security_badge is not None, f'Could not find badge for "{security_name_member}"'
        security_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # 2. POST with member creds -> 200 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK with member creds, got {response.status_code}'

        # 3. EDIT RENAME via UI ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.fill('#edit-div #id_edit-name', new_name)
        page.fill('#edit-div #id_edit-url_path', new_url_path)
        submit_edit_form(page)

        new_row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
        page.wait_for_selector(new_row_selector, state='visible', timeout=5000)

        # 4. POST new URL with member creds -> 200 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK at new URL, got {response.status_code}'

        # 5. Old URL -> 404 ..
        response = _post_mcp(server_port, url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at old URL, got {response.status_code}'

        # 6. Non-member -> 403 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_nonmember, security_password_nonmember))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for non-member, got {response.status_code}'

        # 7. EDIT DEACTIVATE via UI ..
        row = page.wait_for_selector(new_row_selector, state='visible', timeout=5000)
        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        page.uncheck('#edit-div #id_edit-is_active')
        submit_edit_form(page)

        # 8. URL -> 404 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after deactivation, got {response.status_code}'

        # 9. EDIT REACTIVATE via UI ..
        row = page.wait_for_selector(new_row_selector, state='visible', timeout=5000)
        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        page.check('#edit-div #id_edit-is_active')
        submit_edit_form(page)

        # 10. URL -> 200 ..
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == OK, f'Expected OK after reactivation, got {response.status_code}'

        # 11. DELETE via UI ..
        row = page.wait_for_selector(new_row_selector, state='visible', timeout=5000)
        page.evaluate(f'$.fn.zato.channel.mcp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        page.wait_for_selector(new_row_selector, state='hidden', timeout=5000)

        # 12. URL -> 404 ..
        page.wait_for_timeout(1000)
        response = _post_mcp(server_port, new_url_path, auth=(security_username_member, security_password_member))
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after delete, got {response.status_code}'

# ################################################################################################################################

    def test_mcp_concurrent_edit_via_ui_and_api(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel via UI, edits its url_path via the API, refreshes the UI page,
        asserts the new url_path is displayed in the table, then edits via UI again
        to confirm no stale data issues.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'conc-edit'
        original_url_path = '/mcp/concurrent-original/' + rand_string()
        api_url_path = '/mcp/concurrent-api/' + rand_string()
        ui_url_path = '/mcp/concurrent-ui/' + rand_string()

        # .. navigate to MCP channels ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create the channel via UI ..
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', original_url_path)
        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. get the channel's ID from the API ..
        api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
        api_auth = ('admin.invoke', zato_dashboard['password'])
        api_headers = {'Content-Type': 'application/json'}
        api_payload = json.dumps({'cluster_id': 1, 'type_': 'channel-mcp'})

        list_response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert list_response.status_code == OK, f'get-list failed: {list_response.status_code}'

        channel_data = None
        for item in list_response.json():
            if item['name'] == channel_name:
                channel_data = item
                break

        assert channel_data is not None, f'Channel "{channel_name}" not found via API'
        channel_id = channel_data['id']

        # .. edit url_path via API ..
        edit_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.edit'
        edit_payload = json.dumps({
            'id': channel_id,
            'name': channel_name,
            'type_': 'channel-mcp',
            'is_active': True,
            'is_internal': False,
            'is_channel': True,
            'is_outconn': False,
            'url_path': api_url_path,
        })

        edit_response = requests.post(edit_url, data=edit_payload, headers=api_headers, auth=api_auth, timeout=10)
        assert edit_response.status_code == OK, f'API edit failed: {edit_response.status_code} {edit_response.text}'

        # .. refresh the UI page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)
        page.wait_for_selector('#data-table', state='visible', timeout=5000)

        # .. the table should show the API-set url_path ..
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        row_text = row.inner_text()
        assert api_url_path in row_text, \
            f'Expected API url_path "{api_url_path}" in row, got: {row_text}'

        # .. verify the API-set URL is live (403 = no security but routable) ..
        response = _post_mcp(server_port, api_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at API url, got {response.status_code}'

        # .. original URL should be gone ..
        response = _post_mcp(server_port, original_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at original url, got {response.status_code}'

        # .. now edit via UI to change url_path again ..
        item_id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = item_id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.channel.mcp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.fill('#edit-div #id_edit-url_path', ui_url_path)
        submit_edit_form(page)

        # .. verify UI-set URL is live ..
        response = _post_mcp(server_port, ui_url_path)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN at UI url, got {response.status_code}'

        # .. API-set URL should now be gone ..
        response = _post_mcp(server_port, api_url_path)
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at API url after UI edit, got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
