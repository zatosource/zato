# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FORBIDDEN, OK, UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import create_basic_auth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_apikey_definition, create_channel, create_security_group, edit_channel, \
    find_channel_row, get_row_cell_texts, invoke_channel, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.groups.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_API_Key_Header = 'X-API-Key'

# Row cell index with the channel's security groups info
_Cell_Security_Groups = 7

# Log patterns produced by the server when group credentials are rejected
_Group_Log_Patterns = (
    'Invalid API key (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
    'Received both Basic Auth and API key (groups)',
)

# Log patterns produced by the server when a security definition rejects credentials
_Auth_Log_Patterns = ('401 Unauthorized path_info', 'Unauthorized; path_info')

# The group-name uniqueness probe queries a groups table missing from the quickstart ODB,
# so the dashboard middleware logs this warning whenever a group is created via the UI
_Group_Create_Log_Patterns = ('nDetails: ··· Error ···',)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelGroups:
    """ Tests for security groups assigned to REST channels via the web admin UI.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Create_Log_Patterns)
    def test_group_enforcement(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a group with a Basic Auth member and an API key member, assigns it
        to a channel and verifies members pass while non-members and anonymous clients get 403.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'enforce'
        group_name = _Test_Name_Prefix + 'group-enforce'
        url_path = '/test/rest/groups-enforce/' + rand_string()

        # Create the member definitions ..
        member_basic_auth = create_basic_auth(page, base_url, _Test_Name_Prefix, 'member')
        member_apikey = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'member-key')

        # .. and one definition that stays outside the group ..
        non_member = create_basic_auth(page, base_url, _Test_Name_Prefix, 'non-member')

        # .. create the group with both members ..
        create_security_group(page, base_url, group_name, [member_basic_auth['name'], member_apikey['name']])

        # .. create the channel with the group checked ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security_groups': [group_name],
        })

        # .. the row summarizes the group and its members ..
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert cells[_Cell_Security_Groups] == '1 group, 2 clients', \
            f'Expected "1 group, 2 clients", got: "{cells[_Cell_Security_Groups]}"'

        # .. the Basic Auth member passes ..
        auth = (member_basic_auth['username'], member_basic_auth['password'])
        response = invoke_until_status(server_port, url_path, OK, data='{"member": "basic-auth"}', auth=auth)
        assert response.status_code == OK, f'Expected OK for a Basic Auth member, got {response.status_code}: {response.text}'

        # .. the API key member passes ..
        headers = {_API_Key_Header: member_apikey['key']}
        response = invoke_channel(server_port, url_path, data='{"member": "apikey"}', headers=headers)
        assert response.status_code == OK, f'Expected OK for an API key member, got {response.status_code}: {response.text}'

        # .. a non-member is rejected ..
        non_member_auth = (non_member['username'], non_member['password'])
        response = invoke_channel(server_port, url_path, data='{"member": false}', auth=non_member_auth)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for a non-member, got {response.status_code}'

        # .. a wrong API key is rejected ..
        wrong_headers = {_API_Key_Header: 'invalid.' + rand_string()}
        response = invoke_channel(server_port, url_path, data='{"member": false}', headers=wrong_headers)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for a wrong API key, got {response.status_code}'

        # .. and an anonymous client is rejected too.
        response = invoke_channel(server_port, url_path, data='{"member": null}')
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for an anonymous client, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Create_Log_Patterns)
    def test_group_removed_via_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with a group, then unchecks the group via edit and verifies
        the channel is open again and the groups column shows no groups.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'remove'
        group_name = _Test_Name_Prefix + 'group-remove'
        url_path = '/test/rest/groups-remove/' + rand_string()

        # Create a member and the group ..
        member = create_basic_auth(page, base_url, _Test_Name_Prefix, 'remove-member')
        create_security_group(page, base_url, group_name, [member['name']])

        # .. create the channel with the group checked ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security_groups': [group_name],
        })

        # .. group enforcement is on, so a member is needed ..
        auth = (member['username'], member['password'])
        response = invoke_until_status(server_port, url_path, OK, data='{"group": "on"}', auth=auth)
        assert response.status_code == OK, f'Expected OK for a member, got {response.status_code}: {response.text}'

        # .. uncheck the group via edit ..
        edit_channel(page, channel_id, {
            'security_groups_uncheck': [group_name],
        })

        # .. the groups column shows no groups ..
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert cells[_Cell_Security_Groups] == '0 groups, 0 clients', \
            f'Expected "0 groups, 0 clients", got: "{cells[_Cell_Security_Groups]}"'

        # .. and the channel is open now.
        response = invoke_until_status(server_port, url_path, OK, data='{"group": "off"}')
        assert response.status_code == OK, f'Expected OK for an anonymous client, got {response.status_code}: {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns, *_Group_Create_Log_Patterns)
    def test_group_and_definition_combined(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with both a Basic Auth definition and a group whose member
        is that same definition, then verifies the matching credentials pass while
        anonymous clients are rejected by the definition check first.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'combined'
        group_name = _Test_Name_Prefix + 'group-combined'
        url_path = '/test/rest/groups-combined/' + rand_string()

        # Create the definition and a group with it as the only member ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'combined-def')
        create_security_group(page, base_url, group_name, [definition['name']])

        # .. create the channel with both the definition and the group ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Basic Auth/{definition["name"]}',
            'security_groups': [group_name],
        })

        # .. credentials satisfying both checks pass ..
        auth = (definition['username'], definition['password'])
        response = invoke_until_status(server_port, url_path, OK, data='{"combined": true}', auth=auth)
        assert response.status_code == OK, f'Expected OK for matching credentials, got {response.status_code}: {response.text}'

        # .. and anonymous clients are rejected by the definition check.
        response = invoke_channel(server_port, url_path, data='{"combined": false}')
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED for an anonymous client, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Create_Log_Patterns)
    def test_group_custom_header(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a group whose API key member uses a custom header, assigns it to a channel
        and verifies the custom header passes while the default header carrying the same key
        is rejected and the Basic Auth member of the same group keeps working.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'custom-header'
        group_name = _Test_Name_Prefix + 'group-custom-header'
        url_path = '/test/rest/groups-custom-header/' + rand_string()
        custom_header = 'X-Custom-Token'

        # Create the member definitions, the API key one with a custom header ..
        member_basic_auth = create_basic_auth(page, base_url, _Test_Name_Prefix, 'custom-member')
        member_apikey = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'custom-member-key', custom_header)

        # .. create the group with both members ..
        create_security_group(page, base_url, group_name, [member_basic_auth['name'], member_apikey['name']])

        # .. create the channel with the group checked ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security_groups': [group_name],
        })

        # .. the API key member passes with the custom header ..
        headers = {custom_header: member_apikey['key']}
        response = invoke_until_status(server_port, url_path, OK, data='{"member": "apikey"}', headers=headers)
        assert response.status_code == OK, \
            f'Expected OK for the custom header, got {response.status_code}: {response.text}'

        # .. the same key in the default header is rejected ..
        default_headers = {_API_Key_Header: member_apikey['key']}
        response = invoke_channel(server_port, url_path, data='{"member": "default-header"}', headers=default_headers)
        assert response.status_code == FORBIDDEN, \
            f'Expected FORBIDDEN for the key in the default header, got {response.status_code}'

        # .. and the Basic Auth member of the same group keeps working.
        auth = (member_basic_auth['username'], member_basic_auth['password'])
        response = invoke_channel(server_port, url_path, data='{"member": "basic-auth"}', auth=auth)
        assert response.status_code == OK, \
            f'Expected OK for the Basic Auth member, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################
