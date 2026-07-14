# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FORBIDDEN, OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from bearer_token import create_static_definition, edit_group_members
from rest_channel import create_channel, create_security_group, invoke_channel, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.bearer.groups.' + CryptoManager.generate_hex_string(32) + '.'

_Echo_Service = 'demo.echo'

# Log patterns produced by the server when group credentials are rejected
_Group_Log_Patterns = (
    'Invalid bearer token (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
)

# The group-name uniqueness probe queries a groups table missing from the quickstart ODB,
# so the dashboard middleware logs this warning whenever a group is created via the UI
_Group_Create_Log_Patterns = ('nDetails: ··· Error ···',)

# ################################################################################################################################
# ################################################################################################################################

def _bearer_headers(token:'str') -> 'anydict':
    """ Returns HTTP headers carrying the given bearer token.
    """

    out = {'Authorization': f'Bearer {token}'}
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBearerTokenGroups:
    """ Tests for Bearer token members of security groups assigned to REST channels,
    with membership changes reflected in live enforcement without a server restart.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns, *_Group_Create_Log_Patterns)
    def test_membership_changes_reflected_live(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a group with one static bearer member and a channel with that group,
        then swaps the membership via the groups page and verifies enforcement follows
        each change without a restart.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        member_name = _Test_Name_Prefix + 'member'
        other_name = _Test_Name_Prefix + 'other'
        group_name = _Test_Name_Prefix + 'group'
        channel_name = _Test_Name_Prefix + 'channel'
        url_path = '/test/bearer/groups/' + CryptoManager.generate_hex_string()

        member_token = 'token.' + CryptoManager.generate_hex_string()
        other_token = 'token.' + CryptoManager.generate_hex_string()

        # Create two static definitions, each with its own token ..
        _ = create_static_definition(page, base_url, member_name, member_token)
        _ = create_static_definition(page, base_url, other_name, other_token)

        # .. create the group with only the first one as a member ..
        create_security_group(page, base_url, group_name, [member_name])

        # .. and create the channel with the group checked.
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security_groups': [group_name],
        })

        # The member's token passes ..
        member_headers = _bearer_headers(member_token)

        response = invoke_until_status(server_port, url_path, OK, data='{"member": true}', headers=member_headers)
        assert response.status_code == OK, f'Expected OK for a member token, got {response.status_code}: {response.text}'

        # .. the non-member's token is rejected ..
        other_headers = _bearer_headers(other_token)

        response = invoke_channel(server_port, url_path, data='{"member": false}', headers=other_headers)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for a non-member token, got {response.status_code}'

        # .. and so is an anonymous client.
        response = invoke_channel(server_port, url_path, data='{"member": null}')
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for an anonymous client, got {response.status_code}'

        # Swap the membership - the other definition joins and the original one leaves ..
        edit_group_members(page, base_url, group_name, add_names=[other_name], remove_names=[member_name])

        # .. the new member's token now passes ..
        response = invoke_until_status(server_port, url_path, OK, data='{"swapped": true}', headers=other_headers)
        assert response.status_code == OK, f'Expected OK for the new member, got {response.status_code}: {response.text}'

        # .. and the removed member's token is rejected, all without a restart.
        response = invoke_until_status(server_port, url_path, FORBIDDEN, data='{"swapped": false}', headers=member_headers)
        assert response.status_code == FORBIDDEN, f'Expected FORBIDDEN for the removed member, got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
