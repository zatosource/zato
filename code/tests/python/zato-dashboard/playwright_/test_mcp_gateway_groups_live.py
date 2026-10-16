# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from http.client import FORBIDDEN, OK

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
import _mcp_wizard_masking as masking_page

from mcp_gateway_live import assert_channel_status, assert_status, basic_auth_headers, call_echo, delete_gateway, \
    delete_group, Echo_Service, get_channel_group_ids, get_gateway_names, get_group_id, get_group_id_by_name, \
    get_group_member_names, get_group_member_names_by_name, Group_Log_Patterns, Group_Name_Prefix, import_enmasse, \
    inline_edit, make_url_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.groups.live.' + CryptoManager.generate_hex_string(16) + '.'

# What the dashboard and the server log when they refuse a save that would take over a security group
_refused_group_log_patterns = ('is already in use by', 'already exists')

# ################################################################################################################################
# ################################################################################################################################

def _create_basic_auth_gateway(page:'Page', base_url:'str', label:'str') -> 'anydict':
    """ Creates a Basic Auth definition and a gateway authenticating with it through the wizard,
    and returns the gateway's name, id, path and the definition's name and credentials.
    """
    definition = create_basic_auth(page, base_url, _test_name_prefix, label)

    gateway_name = _test_name_prefix + label + '.gateway'
    url_path = make_url_path('groups-live/' + label)

    gateway_id = wizard_page.create_gateway(
        page, base_url, gateway_name, url_path, services=[Echo_Service], security=[definition['name']])

    out = {
        'gateway_name': gateway_name,
        'gateway_id': gateway_id,
        'url_path': url_path,
        'definition_name': definition['name'],
        'auth_headers': basic_auth_headers(definition['username'], definition['password']),
    }

    return out

# ################################################################################################################################

def _make_basic_auth_yaml(definition_name:'str') -> 'anydict':
    """ Returns the YAML lines and the credentials of a Basic Auth definition for an enmasse import.
    """
    username = 'user.' + definition_name
    password = 'password.' + CryptoManager.generate_hex_string()

    yaml_content = f"""
  - name: {definition_name}
    type: basic_auth
    username: {username}
    password: "{password}"
"""

    out = {
        'yaml': yaml_content,
        'auth_headers': basic_auth_headers(username, password),
    }

    return out

# ################################################################################################################################

def _rename_in_wizard(page:'Page', base_url:'str', gateway_name:'str', new_name:'str') -> 'None':
    """ Opens the edit wizard of a gateway and types in a new name, without saving it.
    """
    wizard_page.open_wizard_edit(page, base_url, gateway_name)
    page.fill(wizard_page.field_selector('name', is_edit=True), new_name)

# ################################################################################################################################

def _stored_group_ids(zato_dashboard:'anydict', gateway_name:'str') -> 'list':
    """ Returns the security group ids the stored gateway lists, as text.
    """
    stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

    out = []

    for group_id in stored['security_groups']:
        out.append(str(group_id))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPGatewayGroupsLive:
    """ The security group of each gateway follows the gateway through renames and deletions,
    and groups the dashboard does not manage are kept.
    """

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_wizard_rename_keeps_one_group(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A rename in the wizard leaves one group under the new name, the caller keeps its access,
        and deleting the gateway removes the group.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'wizard-rename')
        new_name = gateway['gateway_name'] + '.renamed'

        # The gateway is renamed in the wizard ..
        _rename_in_wizard(page, base_url, gateway['gateway_name'], new_name)
        wizard_page.save_edit(page)

        # .. one group exists, under the new name, with the member it had ..
        old_group_id = get_group_id(zato_dashboard, gateway['gateway_name'])
        assert old_group_id is None, f'Expected no group under the old name, got id {old_group_id}'

        member_names = get_group_member_names(zato_dashboard, new_name)
        assert member_names == [gateway['definition_name']], member_names

        # .. the caller is still accepted ..
        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

        # .. and the group is gone with the gateway.
        delete_gateway(page, base_url, new_name, gateway['gateway_id'])

        new_group_id = get_group_id(zato_dashboard, new_name)
        assert new_group_id is None, f'Expected the group to be deleted with the gateway, got id {new_group_id}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_inline_rename_then_new_gateway_under_old_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A gateway renamed on the list page keeps its own callers, and a new gateway created under
        the old name gets a group of its own.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        first = _create_basic_auth_gateway(page, base_url, 'inline-rename')
        new_name = first['gateway_name'] + '.renamed'

        # The first gateway is renamed on the list page ..
        _ = wizard_page.go_to_list(page, base_url, first['gateway_name'])

        response = inline_edit(page, first['gateway_id'], {'name': new_name})
        assert response['status'] == OK, response

        # .. and a second gateway is created under the old name with a definition of its own ..
        second_definition = create_basic_auth(page, base_url, _test_name_prefix, 'inline-rename-second')
        second_headers = basic_auth_headers(second_definition['username'], second_definition['password'])
        second_url_path = make_url_path('groups-live/inline-rename-second')

        _ = wizard_page.create_gateway(page, base_url, first['gateway_name'], second_url_path,
            services=[Echo_Service], security=[second_definition['name']])

        # .. each gateway accepts its own caller ..
        call_echo(server_port, first['url_path'], first['auth_headers'])
        call_echo(server_port, second_url_path, second_headers)

        # .. and refuses the other one.
        _ = assert_status(server_port, first['url_path'], second_headers, FORBIDDEN)
        _ = assert_status(server_port, second_url_path, first['auth_headers'], FORBIDDEN)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_group_log_patterns)
    def test_create_over_group_in_use_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A gateway cannot be created under a name whose group another channel uses,
        and the other gateway keeps its members and its callers.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        new_gateway_name = _test_name_prefix + 'group-in-use'
        group_name = Group_Name_Prefix + new_gateway_name

        other_gateway_name = _test_name_prefix + 'group-in-use.other'
        other_url_path = make_url_path('groups-live/group-in-use-other')

        definition_name = _test_name_prefix + 'group-in-use.basic-auth'
        definition = _make_basic_auth_yaml(definition_name)

        # Another gateway uses the group under the name the new gateway would have ..
        import_enmasse(zato_dashboard, f"""
security:
{definition['yaml']}
groups:
  - name: {group_name}
    members:
      - {definition_name}

mcp_gateway:
  - name: {other_gateway_name}
    url_path: {other_url_path}
    services:
      - {Echo_Service}
    security_groups:
      - {group_name}
""")

        call_echo(server_port, other_url_path, definition['auth_headers'])

        # .. so a create under that name is refused ..
        new_definition = create_basic_auth(page, base_url, _test_name_prefix, 'group-in-use-new')
        new_url_path = make_url_path('groups-live/group-in-use-new')

        wizard_page.open_wizard_create(page, base_url)
        page.fill(wizard_page.field_selector('name'), new_gateway_name)
        page.fill(wizard_page.field_selector('url_path'), new_url_path)
        wizard_page.assign_badge(page, 'services', Echo_Service)
        wizard_page.assign_badge(page, 'security', new_definition['name'])

        wizard_page.go_to_step(page, wizard_page.Review_Step)
        oauth_live.attempt_refused_save(page, '#mcp-wizard-next')

        # .. no gateway is stored under that name ..
        stored_names = get_gateway_names(zato_dashboard)
        assert new_gateway_name not in stored_names, stored_names

        # .. and the other gateway keeps its member and its caller.
        member_names = get_group_member_names_by_name(zato_dashboard, group_name)
        assert member_names == [definition_name], member_names

        call_echo(server_port, other_url_path, definition['auth_headers'])

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns, *_refused_group_log_patterns)
    def test_rename_onto_existing_group_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A rename onto a name whose group exists already is refused, and both groups and the gateway are unchanged.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'rename-onto-group')

        target_name = _test_name_prefix + 'rename-onto-group.target'
        target_group_name = Group_Name_Prefix + target_name

        target_definition_name = _test_name_prefix + 'rename-onto-group.target-basic-auth'
        target_definition = _make_basic_auth_yaml(target_definition_name)

        # A group exists under the name the gateway is to be renamed to ..
        import_enmasse(zato_dashboard, f"""
security:
{target_definition['yaml']}
groups:
  - name: {target_group_name}
    members:
      - {target_definition_name}
""")

        # .. so the rename is refused ..
        _rename_in_wizard(page, base_url, gateway['gateway_name'], target_name)
        oauth_live.attempt_refused_save(page, '#mcp-wizard-save')

        # .. the gateway keeps its name and its group ..
        stored_names = get_gateway_names(zato_dashboard)
        assert gateway['gateway_name'] in stored_names, stored_names
        assert target_name not in stored_names, stored_names

        member_names = get_group_member_names(zato_dashboard, gateway['gateway_name'])
        assert member_names == [gateway['definition_name']], member_names

        # .. the other group keeps its member ..
        member_names = get_group_member_names_by_name(zato_dashboard, target_group_name)
        assert member_names == [target_definition_name], member_names

        # .. and the gateway's caller is still accepted.
        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_enmasse_group_kept_by_wizard_save(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A gateway imported with a group of its own keeps that group through a wizard save,
        the list counts its member, and its caller is accepted.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'enmasse-group'
        url_path = make_url_path('groups-live/enmasse-group')
        new_url_path = make_url_path('groups-live/enmasse-group-moved')

        group_name = _test_name_prefix + 'enmasse-group.own'

        definition_name = _test_name_prefix + 'enmasse-group.basic-auth'
        definition = _make_basic_auth_yaml(definition_name)

        import_enmasse(zato_dashboard, f"""
security:
{definition['yaml']}
groups:
  - name: {group_name}
    members:
      - {definition_name}

mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
    security_groups:
      - {group_name}
""")

        call_echo(server_port, url_path, definition['auth_headers'])

        # The gateway is saved in the wizard with a new path ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        page.fill(wizard_page.field_selector('url_path', is_edit=True), new_url_path)
        wizard_page.save_edit(page)

        # .. it still lists its own group ..
        group_id = get_group_id_by_name(zato_dashboard, group_name)
        stored_group_ids = _stored_group_ids(zato_dashboard, gateway_name)
        assert str(group_id) in stored_group_ids, stored_group_ids

        # .. the list counts the group's member ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name)
        gateway_id = wizard_page.get_gateway_id(page, gateway_name)

        member_count = page.inner_text(f'#mcp-security-cell-{gateway_id}').strip()
        assert member_count == '1', member_count

        # .. and the caller is accepted at the new path.
        call_echo(server_port, new_url_path, definition['auth_headers'])

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_group_deleted_on_groups_page(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A gateway whose group is deleted under Security, Groups refuses the former member,
        no longer lists the group, and still opens and saves in the wizard.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway = _create_basic_auth_gateway(page, base_url, 'group-deleted')
        call_echo(server_port, gateway['url_path'], gateway['auth_headers'])

        # The gateway's group is deleted on the groups page ..
        group_id = get_group_id(zato_dashboard, gateway['gateway_name'])
        group_id = str(group_id)

        delete_group(page, base_url, group_id)

        # .. the former member is refused ..
        _ = assert_status(server_port, gateway['url_path'], gateway['auth_headers'], FORBIDDEN)

        # .. the gateway no longer lists the group ..
        stored_group_ids = _stored_group_ids(zato_dashboard, gateway['gateway_name'])
        assert group_id not in stored_group_ids, stored_group_ids

        # .. and the wizard opens and saves it.
        wizard_page.open_wizard_edit(page, base_url, gateway['gateway_name'])
        wizard_page.save_edit(page)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*Group_Log_Patterns)
    def test_gateway_delete_updates_other_channels(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Deleting a gateway removes its group from a REST channel that also uses it,
        and the REST channel then refuses the group's former member.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        gateway_name = _test_name_prefix + 'delete-shared'
        group_name = Group_Name_Prefix + gateway_name
        url_path = make_url_path('groups-live/delete-shared')

        other_group_name = _test_name_prefix + 'delete-shared.other'
        channel_name = _test_name_prefix + 'delete-shared.rest'
        channel_url_path = make_url_path('groups-live-rest/delete-shared')

        member_name = _test_name_prefix + 'delete-shared.member'
        member = _make_basic_auth_yaml(member_name)

        other_member_name = _test_name_prefix + 'delete-shared.other-member'
        other_member = _make_basic_auth_yaml(other_member_name)

        # The REST channel uses the gateway's group and a group of its own ..
        import_enmasse(zato_dashboard, f"""
security:
{member['yaml']}
{other_member['yaml']}
groups:
  - name: {group_name}
    members:
      - {member_name}

  - name: {other_group_name}
    members:
      - {other_member_name}

mcp_gateway:
  - name: {gateway_name}
    url_path: {url_path}
    services:
      - {Echo_Service}
    security_groups:
      - {group_name}

channel_rest:
  - name: {channel_name}
    service: {Echo_Service}
    url_path: {channel_url_path}
    groups:
      - {group_name}
      - {other_group_name}
""")

        assert_channel_status(server_port, channel_url_path, member['auth_headers'], OK)
        call_echo(server_port, url_path, member['auth_headers'])

        # The gateway is deleted ..
        _ = wizard_page.go_to_list(page, base_url, gateway_name)
        gateway_id = wizard_page.get_gateway_id(page, gateway_name)

        delete_gateway(page, base_url, gateway_name, gateway_id)

        # .. the REST channel lists only its own group ..
        other_group_id = get_group_id_by_name(zato_dashboard, other_group_name)
        assert other_group_id is not None, other_group_name

        channel_group_ids = get_channel_group_ids(zato_dashboard, channel_name)
        assert channel_group_ids == [int(other_group_id)], channel_group_ids

        # .. it refuses the former member of the gateway's group ..
        assert_channel_status(server_port, channel_url_path, member['auth_headers'], FORBIDDEN)

        # .. and still accepts the member of its own group.
        assert_channel_status(server_port, channel_url_path, other_member['auth_headers'], OK)

# ################################################################################################################################
# ################################################################################################################################
