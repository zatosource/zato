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
from http.client import NOT_FOUND, OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_oauth_live as oauth_live
import _mcp_wizard as wizard_page

from mcp_gateway_live import assert_channel_status, assert_status, basic_auth_headers, call_echo, Echo_Service, \
    get_channel, get_gateway_names, Group_Log_Patterns, import_enmasse, initialize, inline_edit, list_tool_names, \
    make_url_path, post_session_request, Propagation_Poll_Interval, Propagation_Timeout, run_enmasse_import

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from requests import Response
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.channels.live.' + CryptoManager.generate_hex_string(16) + '.'

# What the server logs when it refuses a gateway that would take over another channel or its path
_refused_channel_log_patterns = ('already exists', 'has the URL path', 'already uses the URL path')

# What the server logs when a gateway lists a service that is not deployed
_missing_service_log_patterns = ('is not deployed',)

# How long a hot-deployed service takes to appear in a gateway's tools, in seconds
_deployment_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def _create_basic_auth_gateway(page:'Page', base_url:'str', label:'str') -> 'anydict':
    """ Creates a Basic Auth definition and a gateway authenticating with it through the wizard,
    and returns the gateway's name, id, path and the credentials.
    """
    definition = create_basic_auth(page, base_url, _test_name_prefix, label)

    gateway_name = _test_name_prefix + label + '.gateway'
    url_path = make_url_path('channels-live/' + label)

    gateway_id = wizard_page.create_gateway(
        page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

    out = {
        'gateway_name': gateway_name,
        'gateway_id': gateway_id,
        'url_path': url_path,
        'auth_headers': basic_auth_headers(definition['username'], definition['password']),
    }

    return out

# ################################################################################################################################

def _attempt_refused_create(page:'Page', base_url:'str', gateway_name:'str', url_path:'str') -> 'None':
    """ Answers the create wizard with the given name and path and expects the save to be refused.
    """
    wizard_page.open_wizard_create(page, base_url)

    page.fill(wizard_page.field_selector('name'), gateway_name)
    page.fill(wizard_page.field_selector('url_path'), url_path)
    wizard_page.assign_badge(page, 'services', Echo_Service)

    wizard_page.go_to_step(page, wizard_page.Review_Step)
    oauth_live.attempt_refused_save(page, '#mcp-wizard-next')

# ################################################################################################################################

def _session_request_until_status(
    server_port:'int',
    url_path:'str',
    auth_headers:'strdict',
    session_id:'str',
    expected_status:'int',
    ) -> 'Response':
    """ Sends tools/list within a session until the expected status arrives and returns the last response.
    """
    deadline = time.monotonic() + Propagation_Timeout

    while True:
        out = post_session_request(server_port, url_path, auth_headers, session_id, 'tools/list', {})

        if out.status_code == expected_status:
            break

        if time.monotonic() >= deadline:
            break

        time.sleep(Propagation_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPGatewayChannelsLive:
    """ Gateways never take over the channels or the paths of other channels, unknown sessions are reported
    as such, and services deployed after a gateway was built become its tools.
    """

    @pytest.mark.expect_log_errors(*_refused_channel_log_patterns)
    def test_gateway_named_after_rest_channel_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A gateway cannot be created under the name of a REST channel, which keeps answering at its path.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _test_name_prefix + 'rest-name'
        channel_url_path = make_url_path('channels-live-rest/rest-name')

        import_enmasse(zato_dashboard, f"""
channel_rest:
  - name: {channel_name}
    service: {Echo_Service}
    url_path: {channel_url_path}
""")

        assert_channel_status(server_port, channel_url_path, {}, OK)

        # A gateway under the channel's name is refused ..
        _attempt_refused_create(page, base_url, channel_name, make_url_path('channels-live/rest-name'))

        stored_names = get_gateway_names(zato_dashboard)
        assert channel_name not in stored_names, stored_names

        # .. and the channel keeps its service and its path.
        channel = get_channel(zato_dashboard, channel_name)
        assert channel['service_name'] == Echo_Service, channel
        assert channel['url_path'] == channel_url_path, channel

        assert_channel_status(server_port, channel_url_path, {}, OK)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_channel_log_patterns)
    def test_duplicate_gateway_name_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A second gateway under the name of an existing one is refused, and the existing one keeps its path.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'duplicate-name')
        other_url_path = make_url_path('channels-live/duplicate-name-other')

        _attempt_refused_create(page, base_url, gateway['gateway_name'], other_url_path)

        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

        response = initialize(server_port, other_url_path, gateway['auth_headers'])
        assert response.status_code == NOT_FOUND, f'Expected 404, got {response.status_code} -> {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_rest_channel_on_gateway_path_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A REST channel with a method of its own cannot be imported at a gateway's path.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'rest-on-path')
        channel_name = _test_name_prefix + 'rest-on-path.rest'

        result = run_enmasse_import(zato_dashboard, f"""
channel_rest:
  - name: {channel_name}
    service: {Echo_Service}
    url_path: {gateway['url_path']}
    method: POST
""")

        assert result.returncode != 0, f'Expected the import to be refused:\nstdout: {result.stdout}'

        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

# ################################################################################################################################

    def test_two_enmasse_gateways_on_one_path_refused(self, zato_dashboard:'anydict') -> 'None':
        """ Two gateways cannot be imported at one path.
        """
        url_path = make_url_path('channels-live/two-gateways')

        first_name = _test_name_prefix + 'two-gateways.first'
        second_name = _test_name_prefix + 'two-gateways.second'

        result = run_enmasse_import(zato_dashboard, f"""
mcp_gateway:
  - name: {first_name}
    url_path: {url_path}
    services:
      - {Echo_Service}

  - name: {second_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
""")

        assert result.returncode != 0, f'Expected the import to be refused:\nstdout: {result.stdout}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_session_unknown_after_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A session opened before a gateway edit is reported as unknown afterwards, and a new one is accepted.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'session-edit')

        response = assert_status(server_port, gateway['url_path'], gateway['auth_headers'], OK)
        session_id = response.headers['Mcp-Session-Id']

        # The gateway is edited on the list page ..
        _ = wizard_page.go_to_list(page, base_url, gateway['gateway_name'])

        response = inline_edit(page, gateway['gateway_id'], {'allow_agent_filters': 'true'})
        assert response['status'] == OK, response

        # .. the old session is unknown ..
        response = _session_request_until_status(
            server_port, gateway['url_path'], gateway['auth_headers'], session_id, NOT_FOUND)
        assert response.status_code == NOT_FOUND, f'Expected 404, got {response.status_code} -> {response.text}'

        # .. and a new one is accepted.
        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_missing_service_log_patterns)
    def test_service_deployed_after_gateway(self, zato_dashboard:'anydict') -> 'None':
        """ A gateway that lists a service not yet deployed serves its other tools, and lists the service
        once it is deployed.
        """
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        suffix = CryptoManager.generate_hex_string(8)
        service_name = 'test.mcp.channels.live.deployed-later.' + suffix

        gateway_name = _test_name_prefix + 'deployed-later'
        url_path = make_url_path('channels-live/deployed-later')

        group_name = _test_name_prefix + 'deployed-later.group'
        definition_name = _test_name_prefix + 'deployed-later.basic-auth'
        username = 'user.' + definition_name
        password = 'password.' + CryptoManager.generate_hex_string()

        import_enmasse(zato_dashboard, f"""
security:
  - name: {definition_name}
    type: basic_auth
    username: {username}
    password: "{password}"

groups:
  - name: {group_name}
    members:
      - {definition_name}

mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
      - {service_name}
    security_groups:
      - {group_name}
""")

        auth_headers = basic_auth_headers(username, password)

        # The gateway serves the tool that is deployed ..
        tool_names = list_tool_names(server_port, url_path, auth_headers)
        assert tool_names == [Echo_Service], tool_names

        # .. the other service is deployed ..
        pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')
        service_file_path = os.path.join(pickup_directory, f'_mcp_test_deployed_later_{suffix}.py')

        service_code = f'''\
from zato.server.service import Service

class MCPTestDeployedLater(Service):
    name = '{service_name}'

    def handle(self):
        self.response.payload = '{{"status": "ok"}}'
'''

        with open(service_file_path, 'w') as service_file:
            _ = service_file.write(service_code)

        # .. and it becomes a tool of the gateway.
        deadline = time.monotonic() + _deployment_timeout

        while True:
            tool_names = list_tool_names(server_port, url_path, auth_headers)

            if service_name in tool_names:
                break

            if time.monotonic() >= deadline:
                break

            time.sleep(Propagation_Poll_Interval)

        assert sorted(tool_names) == sorted([Echo_Service, service_name]), tool_names

# ################################################################################################################################
# ################################################################################################################################
