# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from http.client import FORBIDDEN, NOT_FOUND

# pytest
import pytest

# requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth
from zato.common.util.mcp_oauth import Metadata_Path_Prefix

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_oauth_live as oauth_live
import _mcp_wizard as wizard_page
import _mcp_wizard_masking as masking_page

from bearer_token import edit_group_members
from mcp_gateway_live import assert_status, bearer_headers, call_echo, Echo_Service, get_gateway_names, get_group_id, \
    get_group_member_names, Group_Edit_Log_Patterns, Group_Log_Patterns, Group_Name_Prefix, HTTP_Timeout, initialize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.oauth.live.' + CryptoManager.generate_hex_string(16) + '.'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def keycloak() -> 'None':
    oauth_live.keycloak_.ensure_keycloak()

# ################################################################################################################################
# ################################################################################################################################

def _create_bearer_definition(page:'Page', base_url:'str', label:'str') -> 'str':
    """ Creates a bearer token definition verifying the tokens Keycloak issues and returns its name.
    """
    out = _test_name_prefix + label
    _ = oauth_live.create_bearer_definition(page, base_url, out)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizardOAuthLive:
    """ Gateways with OAuth on, built and edited through the wizard and called with tokens Keycloak issues.
    """

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_create_and_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A bearer token definition picked in the wizard with OAuth on saves, the gateway publishes its metadata
        and answers a token, and an edit made through the wizard keeps the definition in the group.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'create-edit'
        url_path = '/mcp/oauth-live/' + CryptoManager.generate_hex_string(8)
        new_url_path = '/mcp/oauth-live-moved/' + CryptoManager.generate_hex_string(8)

        # The definition is picked in the wizard itself ..
        bearer_name = _create_bearer_definition(page, base_url, 'create-edit.bearer')

        oauth_live.create_oauth_gateway(page, base_url, gateway_name, url_path, [bearer_name])

        # .. the gateway is stored with OAuth on and the scopes, the definition in its group ..
        stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

        assert stored['oauth'], stored
        assert stored['oauth_scopes'] == ' '.join(oauth_live.Scopes), stored

        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == [bearer_name], member_names

        # .. a caller with no token is told where the metadata is, and a token is accepted.
        auth_headers = bearer_headers(oauth_live.get_token())

        oauth_live.assert_oauth_challenge(server_port, url_path)
        call_echo(server_port, url_path, auth_headers)

        # The edit wizard shows the definition as assigned ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        oauth_live.open_definitions_tab(page)

        assigned = wizard_page.get_assigned_badge_names(page, 'security')
        assert assigned == [bearer_name], assigned

        # .. an edit of the path saves with the definition still in the group ..
        page.fill(wizard_page.field_selector('url_path', is_edit=True), new_url_path)
        wizard_page.save_edit(page)

        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == [bearer_name], member_names

        # .. and the gateway answers at the new path as it did at the old one.
        oauth_live.assert_oauth_challenge(server_port, new_url_path)
        call_echo(server_port, new_url_path, auth_headers)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *Group_Edit_Log_Patterns)
    def test_definition_added_under_groups_survives_wizard_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A bearer token definition added to the gateway's group under Security > Groups is shown as assigned
        in the wizard, stays in the group after a wizard save, and lets OAuth be turned on.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'groups-page'
        url_path = '/mcp/oauth-live/' + CryptoManager.generate_hex_string(8)

        bearer_name = _create_bearer_definition(page, base_url, 'groups-page.bearer')

        # The gateway starts with OAuth off and the definition is added to its group on the groups page ..
        _ = wizard_page.create_gateway(page, base_url, gateway_name, url_path, services=[Echo_Service])
        edit_group_members(page, base_url, Group_Name_Prefix + gateway_name, add_names=[bearer_name])

        # .. the edit wizard shows it as assigned ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        oauth_live.open_definitions_tab(page)

        assigned = wizard_page.get_assigned_badge_names(page, 'security')
        assert assigned == [bearer_name], assigned

        # .. OAuth turned on there saves ..
        oauth_live.open_oauth_tab(page)
        page.check(wizard_page.field_selector('oauth', is_edit=True))
        oauth_live.type_scopes(page)

        wizard_page.save_edit(page)

        # .. with the definition still in the group, and the gateway answers as one with OAuth on.
        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == [bearer_name], member_names

        oauth_live.assert_oauth_challenge(server_port, url_path)
        call_echo(server_port, url_path, bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *oauth_live.Refused_Save_Log_Patterns)
    def test_refused_edit_keeps_group(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An edit that removes the only bearer token definition of a gateway with OAuth on is refused,
        and the group keeps both of its members, so the gateway keeps accepting the token.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'refused-edit'
        url_path = '/mcp/oauth-live/' + CryptoManager.generate_hex_string(8)

        bearer_name = _create_bearer_definition(page, base_url, 'refused-edit.bearer')
        basic_auth_name = create_basic_auth(page, base_url, _test_name_prefix, 'refused-edit')['name']

        oauth_live.create_oauth_gateway(page, base_url, gateway_name, url_path, [bearer_name, basic_auth_name])

        expected_members = sorted([bearer_name, basic_auth_name])

        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == expected_members, member_names

        # The bearer definition is removed in the edit wizard and the save is refused ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.remove_assigned_badge(page, 'security', bearer_name)

        oauth_live.attempt_refused_save(page, '#mcp-wizard-save')

        # .. the group still holds both definitions ..
        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == expected_members, member_names

        # .. and the gateway still accepts the token.
        call_echo(server_port, url_path, bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*oauth_live.Refused_Save_Log_Patterns)
    def test_refused_create_leaves_nothing_behind(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A create with OAuth on and no bearer token definition is refused, and neither the gateway
        nor its group is left behind.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'refused-create'
        url_path = '/mcp/oauth-live/' + CryptoManager.generate_hex_string(8)

        basic_auth_name = create_basic_auth(page, base_url, _test_name_prefix, 'refused-create')['name']

        # The only definition is a Basic Auth one, so the save is refused ..
        oauth_live.fill_oauth_gateway(page, base_url, gateway_name, url_path, [basic_auth_name])

        wizard_page.go_to_step(page, wizard_page.Review_Step)
        oauth_live.attempt_refused_save(page, '#mcp-wizard-next')

        # .. no group of the gateway exists ..
        group_id = get_group_id(zato_dashboard, gateway_name)
        assert group_id is None, f'Expected no group left behind, got id {group_id}'

        # .. no gateway is stored ..
        stored_names = get_gateway_names(zato_dashboard)
        assert gateway_name not in stored_names, stored_names

        # .. and nothing answers at the path.
        response = initialize(server_port, url_path)
        assert response.status_code == NOT_FOUND, f'Expected 404, got {response.status_code} -> {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_oauth_turned_off_keeps_definition(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ OAuth turned off in the edit wizard stops the challenge and the metadata, while the bearer token
        definition stays in the group and the token is still accepted.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'oauth-off'
        url_path = '/mcp/oauth-live/' + CryptoManager.generate_hex_string(8)

        bearer_name = _create_bearer_definition(page, base_url, 'oauth-off.bearer')

        oauth_live.create_oauth_gateway(page, base_url, gateway_name, url_path, [bearer_name])
        oauth_live.assert_oauth_challenge(server_port, url_path)

        # OAuth is turned off in the edit wizard ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        oauth_live.open_oauth_tab(page)
        page.uncheck(wizard_page.field_selector('oauth', is_edit=True))
        wizard_page.save_edit(page)

        # .. a caller with no token is refused without a challenge ..
        response = assert_status(server_port, url_path, None, FORBIDDEN)
        assert 'WWW-Authenticate' not in response.headers, response.headers

        # .. the metadata document is gone ..
        metadata_url = f'http://127.0.0.1:{server_port}{Metadata_Path_Prefix}{url_path}'
        response = requests.get(metadata_url, timeout=HTTP_Timeout)
        assert response.status_code == NOT_FOUND, f'Expected 404, got {response.status_code} -> {response.text}'

        # .. and the definition, still in the group, keeps accepting the token.
        member_names = get_group_member_names(zato_dashboard, gateway_name)
        assert member_names == [bearer_name], member_names

        call_echo(server_port, url_path, bearer_headers(oauth_live.get_token()))

# ################################################################################################################################
# ################################################################################################################################
