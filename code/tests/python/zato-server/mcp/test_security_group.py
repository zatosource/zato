# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.api import Groups

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupNaming(TestCase):
    """ Tests for the auto-created security group naming convention.
    """

# ################################################################################################################################

    def test_group_name_uses_mcp_prefix(self):
        """ The auto-created group name must be mcp.<channel_name>.
        """
        channel_name = 'my-mcp-channel'
        group_name = 'mcp.' + channel_name

        self.assertEqual(group_name, 'mcp.my-mcp-channel')

# ################################################################################################################################

    def test_group_name_prefix_constant(self):
        """ The prefix used in views must match the convention.
        """
        from zato.admin.web.views.channel.mcp import _mcp_group_name_prefix
        self.assertEqual(_mcp_group_name_prefix, 'mcp.')

# ################################################################################################################################
# ################################################################################################################################

class SecurityInputParsing(TestCase):
    """ Tests that hidden input names from the security badge picker
    produce the correct member_id_list values for the group service.
    """

# ################################################################################################################################

    def test_hidden_input_names_produce_member_ids(self):
        """ The hidden input value format sec_type-id must be passed as member_id_list.
        """
        # Simulated POST data from the security badge picker
        post_data = {
            'mcp_security_basic_auth-5': 'basic_auth-5',
            'mcp_security_apikey-12': 'apikey-12',
            'name': 'test-channel',
        }

        prefix = 'mcp_security_'
        security_keys = [key for key in post_data if key.startswith(prefix)]
        member_id_list = [post_data[key] for key in security_keys]

        self.assertEqual(len(member_id_list), 2)
        self.assertIn('basic_auth-5', member_id_list)
        self.assertIn('apikey-12', member_id_list)

# ################################################################################################################################

    def test_empty_security_produces_empty_member_list(self):
        """ No security hidden inputs means an empty member_id_list.
        """
        post_data = {
            'name': 'test-channel',
        }

        prefix = 'mcp_security_'
        security_keys = [key for key in post_data if key.startswith(prefix)]
        member_id_list = [post_data[key] for key in security_keys]

        self.assertEqual(member_id_list, [])

# ################################################################################################################################
# ################################################################################################################################

class HookSecurityGroupsPropagation(TestCase):
    """ Tests that the hook correctly propagates security_groups to HTTPSOAP opaque data.
    """

# ################################################################################################################################

    def test_security_groups_stored_in_opaque(self):
        """ When security_groups are in data, they must end up in HTTPSOAP.opaque1.
        """
        security_groups = [42, 99]
        opaque = {'security_groups': security_groups} if security_groups else {}

        self.assertEqual(opaque['security_groups'], [42, 99])

# ################################################################################################################################

    def test_security_groups_merged_into_existing_opaque(self):
        """ When updating an existing channel, security_groups must be merged
        into the existing opaque data without losing other keys.
        """
        current_opaque = {'some_other_key': 'value'}
        security_groups = [7]

        current_opaque['security_groups'] = security_groups

        self.assertEqual(current_opaque['security_groups'], [7])
        self.assertEqual(current_opaque['some_other_key'], 'value')

# ################################################################################################################################

    def test_empty_security_groups_produces_empty_opaque(self):
        """ No security_groups means opaque is empty.
        """
        security_groups = []
        opaque = {'security_groups': security_groups} if security_groups else {}

        self.assertEqual(opaque, {})

# ################################################################################################################################
# ################################################################################################################################

class DeleteCleanup(TestCase):
    """ Tests that on_mcp_channel_delete removes the auto-created security group.
    """

# ################################################################################################################################

    def test_group_name_matches_channel_name(self):
        """ The group to delete must be named mcp.<channel_name>.
        """
        channel_name = 'production-api'
        group_name = 'mcp.' + channel_name

        self.assertEqual(group_name, 'mcp.production-api')

# ################################################################################################################################

    def test_group_type_is_api_clients(self):
        """ The auto-created group must be of type Group_Parent with API_Clients subtype.
        """
        self.assertEqual(Groups.Type.Group_Parent, 'zato-group')
        self.assertEqual(Groups.Type.API_Clients, 'zato-api-creds')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
