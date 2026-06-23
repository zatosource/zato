# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
from http.client import FORBIDDEN, OK

# requests
import requests

# Zato
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Page_Url_Pattern = '/zato/channel/mcp/?cluster=1'

_Test_Name_Prefix = 'test.mcp.pw.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _post_mcp(server_port:'int', url_path:'str', auth:'tuple | None'=None) -> 'requests.Response':
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
        channel_data = None

        for item in items:
            if item['name'] == channel_name:
                channel_data = item
                break

        assert channel_data is not None, f'Channel "{channel_name}" not found in ODB'

        stored_services = set(channel_data.get('services') or [])
        logger.info('[test_create_with_services] stored_services=%s', stored_services)

        assert service_name_1 in stored_services, \
            f'Expected "{service_name_1}" in stored services, got: {stored_services}'

        assert service_name_2 in stored_services, \
            f'Expected "{service_name_2}" in stored services, got: {stored_services}'

# ################################################################################################################################
# ################################################################################################################################
