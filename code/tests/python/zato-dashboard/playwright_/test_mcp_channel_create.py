# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
from http.client import FORBIDDEN, NOT_FOUND, OK

# requests
import requests

# Zato
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import create_basic_auth, navigate_to_page, open_create_dialog, \
    submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anynone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Page_Url_Pattern = '/zato/channel/mcp/?cluster=1'

_Test_Name_Prefix = 'test.mcp.pw.' + os.urandom(4).hex() + '.'

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

        header_texts = []  # type: list

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
        url_path = '/mcp/pw-test/' + os.urandom(4).hex()

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
        url_path = '/mcp/pw-test-svc/' + os.urandom(4).hex()

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
        url_path = '/mcp/pw-test-sec/' + os.urandom(4).hex()

        # Create a basic auth definition via the UI so we know the credentials ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'mcp-sec')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        sec_password = sec_info['password']

        logger.info('[test_create_with_security] created sec def: name=%s username=%s', sec_name, sec_username)

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
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        assert sec_badge is not None, f'Could not find badge for sec def "{sec_name}"'

        sec_badge.click()

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
        response = _post_mcp(server_port, url_path, auth=(sec_username, sec_password))
        assert response.status_code == OK, f'Expected OK with valid creds, got {response.status_code}: {response.text}'

        # .. POST with invalid creds - should get FORBIDDEN ..
        response = _post_mcp(server_port, url_path, auth=('bogus_user', 'bogus_pass'))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN with invalid creds, got {response.status_code}: {response.text}'

# ################################################################################################################################

    def test_edit_rename(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an MCP channel, then edits it to change both name and url_path.
        Asserts the old URL returns 404 and the new URL is routable (403 = no security, but routable).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        old_name = _Test_Name_Prefix + 'rename-old'
        old_url_path = '/mcp/pw-rename-old/' + os.urandom(4).hex()
        new_name = _Test_Name_Prefix + 'rename-new'
        new_url_path = '/mcp/pw-rename-new/' + os.urandom(4).hex()

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
        old_url_path = '/mcp/pw-rensec-old/' + os.urandom(4).hex()
        new_url_path = '/mcp/pw-rensec-new/' + os.urandom(4).hex()

        # Create a basic auth definition via the UI ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rename-sec')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        sec_password = sec_info['password']

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
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        assert sec_badge is not None, f'Could not find badge for sec def "{sec_name}"'
        sec_badge.click()

        submit_create_form(page)

        # .. verify the channel works with valid creds at old URL ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        response = _post_mcp(server_port, old_url_path, auth=(sec_username, sec_password))
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
        response = _post_mcp(server_port, new_url_path, auth=(sec_username, sec_password))
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
        url_path = '/mcp/pw-deact/' + os.urandom(4).hex()

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
        url_path = '/mcp/pw-react/' + os.urandom(4).hex()

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

        channel_name = _Test_Name_Prefix + 'add-svc'
        url_path = '/mcp/pw-addsvc/' + os.urandom(4).hex()

        # Create a sec def so we can authenticate ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-svc')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        sec_password = sec_info['password']

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
        available_svc = page.query_selector_all('#badge-zone-available-create .badge-zone-body .security-badge')
        service_name_1 = available_svc[0].get_attribute('data-name')
        available_svc[0].click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        sec_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. initialize to confirm channel is live ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, sec_password))
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
        available_svc_edit = page.query_selector_all('#badge-zone-available-edit .badge-zone-body .security-badge')
        service_name_2 = available_svc_edit[0].get_attribute('data-name')
        available_svc_edit[0].click()

        logger.info('[test_edit_add_service] adding service: %s (already has: %s)', service_name_2, service_name_1)

        # .. submit edit ..
        submit_edit_form(page)

        # .. initialize a session, then send tools/list with the session ID ..
        url = f'http://127.0.0.1:{server_port}{url_path}'
        auth = (sec_username, sec_password)
        headers = {'Content-Type': 'application/json'}

        init_response = requests.post(url, data=json.dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1}),
            headers=headers, auth=auth, timeout=10)
        assert init_response.status_code == OK, f'initialize failed: {init_response.status_code}'

        session_id = init_response.headers['Mcp-Session-Id']

        headers['Mcp-Session-Id'] = session_id
        tl_response = requests.post(url, data=json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2}),
            headers=headers, auth=auth, timeout=10)
        assert tl_response.status_code == OK, f'tools/list failed: {tl_response.status_code}'

        tool_names = {t['name'] for t in tl_response.json()['result']['tools']}

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

        channel_name = _Test_Name_Prefix + 'rm-svc'
        url_path = '/mcp/pw-rmsvc/' + os.urandom(4).hex()

        # Create a sec def ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-svc')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        sec_password = sec_info['password']

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
        available_svc = page.query_selector_all('#badge-zone-available-create .badge-zone-body .security-badge')
        service_name_1 = available_svc[0].get_attribute('data-name')
        service_name_2 = available_svc[1].get_attribute('data-name')
        available_svc[0].click()
        available_svc[1].click()

        # .. assign security ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )
        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        sec_badge.click()

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
        auth = (sec_username, sec_password)
        headers = {'Content-Type': 'application/json'}

        init_response = requests.post(url, data=json.dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1}),
            headers=headers, auth=auth, timeout=10)
        assert init_response.status_code == OK, f'initialize failed: {init_response.status_code}'

        session_id = init_response.headers['Mcp-Session-Id']

        headers['Mcp-Session-Id'] = session_id
        tl_response = requests.post(url, data=json.dumps({'jsonrpc': '2.0', 'method': 'tools/list', 'id': 2}),
            headers=headers, auth=auth, timeout=10)
        assert tl_response.status_code == OK, f'tools/list failed: {tl_response.status_code}'

        tool_names = {t['name'] for t in tl_response.json()['result']['tools']}

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
        url_path = '/mcp/pw-addsec/' + os.urandom(4).hex()

        # Create two basic auth definitions ..
        sec_info_1 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-sec-1')
        sec_name_1 = sec_info_1['name']
        sec_username_1 = sec_info_1['username']
        sec_password_1 = sec_info_1['password']

        sec_info_2 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-sec-2')
        sec_name_2 = sec_info_2['name']
        sec_username_2 = sec_info_2['username']
        sec_password_2 = sec_info_2['password']

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

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name_1}"]'
        sec_badge = page.query_selector(badge_selector)
        assert sec_badge is not None, f'Could not find badge for "{sec_name_1}"'
        sec_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm first creds work, second does not ..
        response = _post_mcp(server_port, url_path, auth=(sec_username_1, sec_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(sec_username_2, sec_password_2))
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
        badge_selector = f'#badge-zone-available-sec-edit .badge-zone-body .security-badge[data-name="{sec_name_2}"]'
        sec_badge_2 = page.query_selector(badge_selector)
        assert sec_badge_2 is not None, f'Could not find badge for "{sec_name_2}" in edit available zone'
        sec_badge_2.click()

        submit_edit_form(page)

        logger.info('[test_edit_add_security_member] added sec def %s to channel %s', sec_name_2, channel_name)

        # .. both should now authenticate ..
        response = _post_mcp(server_port, url_path, auth=(sec_username_1, sec_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 after edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(sec_username_2, sec_password_2))
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
        url_path = '/mcp/pw-rmsec/' + os.urandom(4).hex()

        # Create two basic auth definitions ..
        sec_info_1 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-sec-1')
        sec_name_1 = sec_info_1['name']
        sec_username_1 = sec_info_1['username']
        sec_password_1 = sec_info_1['password']

        sec_info_2 = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-sec-2')
        sec_name_2 = sec_info_2['name']
        sec_username_2 = sec_info_2['username']
        sec_password_2 = sec_info_2['password']

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
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name_1}"]')
        badge_2 = page.query_selector(
            f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name_2}"]')
        assert badge_1 is not None, f'Could not find badge for "{sec_name_1}"'
        assert badge_2 is not None, f'Could not find badge for "{sec_name_2}"'
        badge_1.click()
        badge_2.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm both work ..
        response = _post_mcp(server_port, url_path, auth=(sec_username_1, sec_password_1))
        assert response.status_code == OK, f'Expected OK for sec_1 before edit, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(sec_username_2, sec_password_2))
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
        remove_selector = f'#badge-zone-assigned-sec-edit .badge-zone-body .security-badge[data-name="{sec_name_1}"]'
        badge_to_remove = page.query_selector(remove_selector)
        assert badge_to_remove is not None, f'Could not find badge "{sec_name_1}" in assigned sec zone'
        badge_to_remove.click()

        submit_edit_form(page)

        logger.info('[test_edit_remove_security_member] removed sec def %s from channel %s', sec_name_1, channel_name)

        # .. removed member should get 403, remaining should get 200 ..
        response = _post_mcp(server_port, url_path, auth=(sec_username_1, sec_password_1))
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for removed sec_1, got {response.status_code}'

        response = _post_mcp(server_port, url_path, auth=(sec_username_2, sec_password_2))
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
        url_path = '/mcp/pw-rmallsec/' + os.urandom(4).hex()

        # Create a basic auth definition ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-all-sec')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        sec_password = sec_info['password']

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

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        assert sec_badge is not None, f'Could not find badge for "{sec_name}"'
        sec_badge.click()

        submit_create_form(page)

        # .. verify row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. confirm creds work ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, sec_password))
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
        remove_selector = f'#badge-zone-assigned-sec-edit .badge-zone-body .security-badge[data-name="{sec_name}"]'
        badge_to_remove = page.query_selector(remove_selector)
        assert badge_to_remove is not None, f'Could not find badge "{sec_name}" in assigned sec zone'
        badge_to_remove.click()

        submit_edit_form(page)

        logger.info('[test_edit_remove_all_security] removed all security from channel %s', channel_name)

        # .. with valid creds should get 403 (no group = default deny) ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, sec_password))
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
        url_path_1 = '/mcp/pw-dup1/' + os.urandom(4).hex()
        url_path_2 = '/mcp/pw-dup2/' + os.urandom(4).hex()

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
        url_path = '/mcp/pw-dup-path/' + os.urandom(4).hex()

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

    def test_sec_def_password_change(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth, assigns it to an MCP channel's security group,
        verifies the original password works, changes the password via the basic auth UI,
        then verifies old password -> 403 and new password -> 200.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'pwd-chg'
        url_path = '/mcp/pw-chg/' + os.urandom(4).hex()

        # Create a basic auth definition ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pwd-chg')
        sec_name = sec_info['name']
        sec_username = sec_info['username']
        old_password = sec_info['password']

        # .. navigate to MCP channels and create a channel with this sec def ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)
        open_create_dialog(page)
        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', url_path)

        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-sec-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        badge_selector = f'#badge-zone-available-sec-create .badge-zone-body .security-badge[data-name="{sec_name}"]'
        sec_badge = page.query_selector(badge_selector)
        assert sec_badge is not None, f'Could not find badge for "{sec_name}"'
        sec_badge.click()

        submit_create_form(page)

        row_selector = f'#data-table tbody tr:has(td:text-is("{channel_name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. verify the original password works ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, old_password))
        assert response.status_code == OK, f'Expected OK with original password, got {response.status_code}'

        # .. navigate to the basic auth page and change the password ..
        new_password = 'changed.' + os.urandom(8).hex()
        basic_auth_page_url = '/zato/security/basic-auth/?cluster=1'

        navigate_to_page(page, base_url, basic_auth_page_url)

        row_selector_ba = f'#data-table tbody tr:has(td:text-is("{sec_name}"))'
        row = page.wait_for_selector(row_selector_ba, state='visible', timeout=5000)

        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', new_password)
        page.click('#change_password-div input[type="submit"]')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        logger.info('[test_sec_def_password_change] password changed for %s', sec_name)

        # .. wait for the password change to propagate to the security cache ..
        page.wait_for_timeout(2000)

        # .. old password should be rejected ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, old_password))
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN with old password after change, got {response.status_code}'

        # .. new password should work ..
        response = _post_mcp(server_port, url_path, auth=(sec_username, new_password))
        assert response.status_code == OK, f'Expected OK with new password, got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
