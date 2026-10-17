# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import time
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.api import GENERIC
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth, navigate_to_page

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page
import _mcp_wizard_masking as masking_page

from mcp_gateway_live import basic_auth_headers, call_echo, Echo_Service, get_group_member_names, Group_Log_Patterns, \
    Group_Name_Prefix, HTTP_Timeout, import_enmasse, inline_edit, invoke_admin, list_tool_names, make_url_path, \
    Propagation_Poll_Interval, Propagation_Timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.integrity.' + CryptoManager.generate_hex_string(16) + '.'

# What the dashboard and the server log when they refuse a crafted member id or an id of another connection type
_refused_input_log_patterns = ('is not an MCP gateway', 'Invalid security group member', 'could not be saved')

# How long a hot-deployed service takes to appear in the service list, in seconds
_deployment_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_service(zato_dashboard:'anydict', service_name:'str') -> 'None':
    """ Waits until the service of the given name is deployed.
    """
    deadline = time.monotonic() + _deployment_timeout

    while True:
        service_list = invoke_admin(zato_dashboard, 'zato.service.get-list', {'name_filter': service_name, 'paginate': False})

        names = []

        for item in service_list:
            names.append(item['name'])

        if service_name in names:
            break

        assert time.monotonic() < deadline, f'Service `{service_name}` not deployed within {_deployment_timeout}s'
        time.sleep(Propagation_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

class TestMCPGatewayIntegrity:
    """ Saves made through the dashboard never lose or corrupt the configuration of a gateway,
    and input the dashboard pages never produce is refused.
    """

    def test_wizard_save_keeps_session_timeout_and_zero_caps(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A wizard save and a list page save keep the session TTL, the invocation timeout and caps of zero.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _test_name_prefix + 'kept-fields'
        url_path = make_url_path('integrity/kept-fields')

        import_enmasse(zato_dashboard, f"""
mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
    session_ttl: 1800
    invoke_timeout: 300
    max_response_size: 0
    min_size_threshold: 0
""")

        # The gateway is saved in the wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.save_edit(page)

        # .. and once more on the list page ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name)
        gateway_id = wizard_page.get_gateway_id(page, gateway_name)

        response = inline_edit(page, gateway_id, {'allow_agent_filters': 'true'})
        assert response['status'] == OK, response

        # .. and it keeps every field it was imported with.
        stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

        assert stored['session_ttl'] == 1800, stored
        assert stored['invoke_timeout'] == 300, stored
        assert stored['max_response_size'] == 0, stored
        assert stored['min_size_threshold'] == 0, stored

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_mixed_case_service_from_list_page(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A service whose name has capital letters, added on the list page, is stored and listed as a tool under that name.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        suffix = CryptoManager.generate_hex_string(8)
        service_name = 'test.mcp.integrity.MixedCase.' + suffix

        # A service with capital letters in its name is deployed ..
        pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')
        service_file_path = os.path.join(pickup_directory, f'_mcp_test_mixed_case_{suffix}.py')

        service_code = f'''\
from zato.server.service import Service

class MCPTestMixedCase(Service):
    name = '{service_name}'

    def handle(self):
        self.response.payload = '{{"status": "ok"}}'
'''

        with open(service_file_path, 'w') as service_file:
            _ = service_file.write(service_code)

        _wait_for_service(zato_dashboard, service_name)

        # .. a gateway exists ..
        definition = create_basic_auth(page, base_url, _test_name_prefix, 'mixed-case')
        auth_headers = basic_auth_headers(definition['username'], definition['password'])

        gateway_name = _test_name_prefix + 'mixed-case.gateway'
        url_path = make_url_path('integrity/mixed-case')

        gateway_id = wizard_page.create_gateway(
            page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

        # .. the service is added through the Services panel of its row ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name)
        page.click(f'#mcp-services-cell-{gateway_id}')

        badge_selector = f'#badge-zone-available-row .security-badge[data-id="{service_name}"]'
        page.click(badge_selector)

        assigned_selector = f'#badge-zone-assigned-row .security-badge[data-id="{service_name}"]'
        _ = page.wait_for_selector(assigned_selector, state='visible', timeout=HTTP_Timeout * 1000)

        page.evaluate('$.fn.zato.decision_lines.closePanel()')

        # .. the gateway stores it under its own name ..
        deadline = time.monotonic() + Propagation_Timeout

        while True:
            stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

            if len(stored['services']) == 2:
                break

            assert time.monotonic() < deadline, stored
            time.sleep(Propagation_Poll_Interval)

        assert sorted(stored['services']) == sorted([Echo_Service, service_name]), stored

        # .. and lists it as a tool.
        tool_names = list_tool_names(server_port, url_path, auth_headers)
        assert service_name in tool_names, tool_names

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_hidden_member_kept_by_wizard_save(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A member of the gateway's group that the picker does not show is kept by a wizard save.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'hidden-member'
        group_name = Group_Name_Prefix + gateway_name
        url_path = make_url_path('integrity/hidden-member')

        visible_name = _test_name_prefix + 'hidden-member.visible'
        hidden_name = _test_name_prefix + 'hidden-member.zato.internal'

        visible_username = 'user.' + visible_name
        visible_password = 'password.' + CryptoManager.generate_hex_string()

        hidden_password = 'password.' + CryptoManager.generate_hex_string()

        import_enmasse(zato_dashboard, f"""
security:
  - name: {visible_name}
    type: basic_auth
    username: {visible_username}
    password: "{visible_password}"

  - name: {hidden_name}
    type: basic_auth
    username: user.{hidden_name}
    password: "{hidden_password}"

groups:
  - name: {group_name}
    members:
      - {visible_name}
      - {hidden_name}

mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
    security_groups:
      - {group_name}
""")

        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.save_edit(page)

        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == sorted([visible_name, hidden_name]), member_names

        call_echo(server_port, url_path, basic_auth_headers(visible_username, visible_password))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_input_log_patterns)
    def test_crafted_member_id_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A member id of a type a group cannot hold is refused, and the gateway keeps its members and its callers.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition = create_basic_auth(page, base_url, _test_name_prefix, 'crafted-member')
        auth_headers = basic_auth_headers(definition['username'], definition['password'])

        gateway_name = _test_name_prefix + 'crafted-member.gateway'
        url_path = make_url_path('integrity/crafted-member')

        gateway_id = wizard_page.create_gateway(
            page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

        _ = wizard_page.go_to_list(page, base_url, gateway_name)

        response = inline_edit(page, gateway_id, {'security': '["jwt-12"]'})
        assert response['status'] != OK, response

        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == [definition['name']], member_names

        call_echo(server_port, url_path, auth_headers)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_refused_input_log_patterns)
    def test_other_connection_id_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The id of a connection that is not an MCP gateway is refused by the gateway pages, and the connection is unchanged.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        connection_name = _test_name_prefix + 'other-connection'

        # The connection is imported inactive, so it never connects to Discord
        import_enmasse(zato_dashboard, f"""
discord:
  - name: {connection_name}
    is_active: false
""")

        connection_list = invoke_admin(zato_dashboard, 'zato.generic.connection.get-list', {
            'type_': GENERIC.CONNECTION.TYPE.CHAT_DISCORD,
        })

        connection = None

        for item in connection_list:
            if item['name'] == connection_name:
                connection = item
                break

        assert connection, connection_list

        navigate_to_page(page, base_url, wizard_page.MCP_List_URL)

        response = inline_edit(page, str(connection['id']), {'is_active': 'true'})
        assert response['status'] != OK, response

        connection_list = invoke_admin(zato_dashboard, 'zato.generic.connection.get-list', {
            'type_': GENERIC.CONNECTION.TYPE.CHAT_DISCORD,
        })

        for item in connection_list:
            if item['name'] == connection_name:
                assert not item['is_active'], item
                assert 'max_response_size' not in item, item

# ################################################################################################################################
# ################################################################################################################################
