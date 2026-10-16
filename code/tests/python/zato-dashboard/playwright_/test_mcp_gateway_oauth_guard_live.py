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
from http.client import FORBIDDEN, UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth, get_item_id, navigate_to_page, submit_edit_form

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_oauth_live as oauth_live
import _mcp_wizard as wizard_page

from bearer_token import Bearer_Page_Url, delete_definition, edit_definition, fill_edit_form, move_group_members
from mcp_gateway_live import assert_status, basic_auth_headers, bearer_headers, call_echo, confirm_refused_delete, \
    Echo_Service, get_group_id, get_group_member_names, Group_Edit_Log_Patterns, Group_Log_Patterns, Group_Name_Prefix, \
    HTTP_Timeout, make_url_path, Propagation_Poll_Interval, Propagation_Timeout, submit_refused_edit

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.oauth.guard.' + CryptoManager.generate_hex_string(16) + '.'

# The list page with all the Basic Auth definitions
_basic_auth_page_url = '/zato/security/basic-auth/'

# The list page with all the API client security groups
_groups_page_url = '/zato/groups/group/zato-api-creds/'

# The issuer of a bearer definition that verifies tokens of an authorization server other than Keycloak
_second_issuer = 'https://issuer.example.com/realms/second'

# What the server logs when it refuses a change that would leave an OAuth gateway with no verifying definition
# What the server logs when a channel's groups hold no active definition
_no_active_members_log_pattern = 'is protected by security groups that have no members'

_refused_change_log_patterns = (
    'verifies tokens for MCP gateway',
    'Bearer token definition could not be deleted',
    'Bearer token definition could not be updated',
    'Could not delete groups',
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def keycloak() -> 'None':
    oauth_live.keycloak_.ensure_keycloak()

# ################################################################################################################################
# ################################################################################################################################

def _create_oauth_gateway(page:'Page', base_url:'str', label:'str') -> 'anydict':
    """ Creates a bearer definition verifying Keycloak tokens and a gateway with OAuth on that uses it,
    and returns the names, the id of the definition and the gateway's path.
    """
    bearer_name = _test_name_prefix + label + '.bearer'
    bearer_id = oauth_live.create_bearer_definition(page, base_url, bearer_name)

    gateway_name = _test_name_prefix + label + '.gateway'
    url_path = make_url_path('oauth-guard/' + label)

    oauth_live.create_oauth_gateway(page, base_url, gateway_name, url_path, [bearer_name])

    out = {
        'bearer_name': bearer_name,
        'bearer_id': bearer_id,
        'gateway_name': gateway_name,
        'url_path': url_path,
    }

    return out

# ################################################################################################################################

def _wait_for_issuers(server_port:'int', url_path:'str', expected:'strlist') -> 'strlist':
    """ Reads the gateway's metadata until it lists the expected issuers and returns the last list it read.
    """
    expected = sorted(expected)
    deadline = time.monotonic() + Propagation_Timeout

    while True:
        document = oauth_live.get_metadata(server_port, url_path)
        out = sorted(document['authorization_servers'])

        if out == expected:
            break

        if time.monotonic() >= deadline:
            break

        time.sleep(Propagation_Poll_Interval)

    return out

# ################################################################################################################################

def _edit_basic_auth(page:'Page', base_url:'str', definition_name:'str', script:'str') -> 'None':
    """ Opens the edit dialog of a Basic Auth definition, runs the script that changes its form and submits it.
    """
    navigate_to_page(page, base_url, _basic_auth_page_url)
    definition_id = get_item_id(page, definition_name)

    page.evaluate(f'$.fn.zato.security.basic_auth.edit("{definition_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=HTTP_Timeout * 1000)

    page.evaluate(script)
    submit_edit_form(page)

# ################################################################################################################################
# ################################################################################################################################

class TestMCPGatewayOAuthGuardLive:
    """ Changes made outside the wizard never leave a gateway with OAuth on without a verifying definition,
    and changes to definitions take effect on the gateways that use them.
    """

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_change_log_patterns)
    def test_last_bearer_delete_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The only verifying definition of a gateway with OAuth on cannot be deleted.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_oauth_gateway(page, base_url, 'last-delete')

        # The deletion is refused with the gateway named ..
        navigate_to_page(page, base_url, Bearer_Page_Url)
        page.evaluate(f'$.fn.zato.security.oauth.delete_("{gateway["bearer_id"]}")')
        _ = page.wait_for_selector('#popup_container', state='visible', timeout=HTTP_Timeout * 1000)

        message = confirm_refused_delete(page)
        assert gateway['gateway_name'] in message, message

        # .. and the token is still accepted.
        call_echo(server_port, gateway['url_path'], bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_change_log_patterns)
    def test_last_bearer_audience_removal_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The only verifying definition of a gateway with OAuth on cannot lose its audience.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_oauth_gateway(page, base_url, 'last-audience')

        fill_edit_form(page, base_url, gateway['bearer_id'], {'audience': ''})

        message = submit_refused_edit(page)
        assert gateway['gateway_name'] in message, message

        call_echo(server_port, gateway['url_path'], bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *Group_Edit_Log_Patterns, *_refused_change_log_patterns)
    def test_last_bearer_group_removal_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The only verifying definition of a gateway with OAuth on cannot be removed from its group on the groups page.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_oauth_gateway(page, base_url, 'last-member')
        group_name = Group_Name_Prefix + gateway['gateway_name']

        move_group_members(page, base_url, group_name, remove_names=[gateway['bearer_name']])

        message = submit_refused_edit(page)
        assert gateway['gateway_name'] in message, message

        member_names = get_group_member_names(zato_dashboard, gateway['gateway_name'])
        assert member_names == [gateway['bearer_name']], member_names

        call_echo(server_port, gateway['url_path'], bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_change_log_patterns)
    def test_oauth_gateway_group_delete_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The group of a gateway with OAuth on cannot be deleted on the groups page.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_oauth_gateway(page, base_url, 'group-delete')
        group_id = get_group_id(zato_dashboard, gateway['gateway_name'])

        navigate_to_page(page, base_url, _groups_page_url)
        page.evaluate(f'$.fn.zato.groups.delete_("{group_id}")')
        _ = page.wait_for_selector('#popup_container', state='visible', timeout=HTTP_Timeout * 1000)

        message = confirm_refused_delete(page)
        assert gateway['gateway_name'] in message, message

        member_names = get_group_member_names(zato_dashboard, gateway['gateway_name'])
        assert member_names == [gateway['bearer_name']], member_names

        call_echo(server_port, gateway['url_path'], bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_other_bearer_delete_allowed(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A verifying definition that is not the only one can be deleted, and the metadata
        no longer lists its issuer.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        keycloak_bearer_name = _test_name_prefix + 'other-delete.keycloak'
        _ = oauth_live.create_bearer_definition(page, base_url, keycloak_bearer_name)

        second_bearer_name = _test_name_prefix + 'other-delete.second'
        second_bearer_id = oauth_live.create_bearer_definition(page, base_url, second_bearer_name, {
            'issuer': _second_issuer,
            'audience': 'second',
        })

        gateway_name = _test_name_prefix + 'other-delete.gateway'
        url_path = make_url_path('oauth-guard/other-delete')

        oauth_live.create_oauth_gateway(page, base_url, gateway_name, url_path, [keycloak_bearer_name, second_bearer_name])

        keycloak_issuer = oauth_live.keycloak_.get_issuer()

        issuers = _wait_for_issuers(server_port, url_path, [keycloak_issuer, _second_issuer])
        assert issuers == sorted([keycloak_issuer, _second_issuer]), issuers

        # The second definition is deleted ..
        navigate_to_page(page, base_url, Bearer_Page_Url)
        delete_definition(page, second_bearer_id)

        # .. and the metadata names only the remaining issuer.
        issuers = _wait_for_issuers(server_port, url_path, [keycloak_issuer])
        assert issuers == [keycloak_issuer], issuers

        call_echo(server_port, url_path, bearer_headers(oauth_live.get_token()))

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_bearer_audience_edit_takes_effect(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A bearer definition whose audience no longer matches the token stops accepting it,
        and accepts it again once the audience is restored.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_oauth_gateway(page, base_url, 'audience-edit')
        auth_headers = bearer_headers(oauth_live.get_token())

        call_echo(server_port, gateway['url_path'], auth_headers)

        edit_definition(page, base_url, gateway['bearer_id'], {'audience': 'another-audience'})
        _ = assert_status(server_port, gateway['url_path'], auth_headers, UNAUTHORIZED)

        edit_definition(page, base_url, gateway['bearer_id'], {'audience': oauth_live.keycloak_.Audience_Main})
        call_echo(server_port, gateway['url_path'], auth_headers)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_basic_auth_username_edit_takes_effect(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A Basic Auth definition whose username is changed is accepted under the new username only.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition = create_basic_auth(page, base_url, _test_name_prefix, 'username-edit')

        gateway_name = _test_name_prefix + 'username-edit.gateway'
        url_path = make_url_path('oauth-guard/username-edit')

        _ = wizard_page.create_gateway(
            page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

        old_headers = basic_auth_headers(definition['username'], definition['password'])
        call_echo(server_port, url_path, old_headers)

        new_username = definition['username'] + '.new'
        _edit_basic_auth(page, base_url, definition['name'], f'$("#id_edit-username").val("{new_username}")')

        new_headers = basic_auth_headers(new_username, definition['password'])

        _ = assert_status(server_port, url_path, old_headers, FORBIDDEN)
        call_echo(server_port, url_path, new_headers)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, _no_active_members_log_pattern)
    def test_inactive_definition_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A Basic Auth definition made inactive is refused by the gateways whose group holds it.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        definition = create_basic_auth(page, base_url, _test_name_prefix, 'inactive')

        gateway_name = _test_name_prefix + 'inactive.gateway'
        url_path = make_url_path('oauth-guard/inactive')

        _ = wizard_page.create_gateway(
            page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

        auth_headers = basic_auth_headers(definition['username'], definition['password'])
        call_echo(server_port, url_path, auth_headers)

        # The edit form carries is_active as a hidden input, so leaving it out submits the definition as inactive
        _edit_basic_auth(page, base_url, definition['name'], '$("#edit-form input[name=\'edit-is_active\']").remove()')

        _ = assert_status(server_port, url_path, auth_headers, FORBIDDEN)

# ################################################################################################################################
# ################################################################################################################################
