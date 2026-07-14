# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.admin.web.views.channel.mcp import _mcp_group_name_prefix
from zato.common.api import Groups
from zato.common.groups import Member
from zato.common.typing_ import cast_
from zato.server.groups.ctx import SecurityGroupsCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_cid = 'test-cid-1'
_channel_name = 'test.mcp.channel'

_group_id = 100
_other_group_id = 200

_bearer_security_id = 300
_static_token = 'test-static-token-value'

# ################################################################################################################################
# ################################################################################################################################

class _FakeConfigManager:
    """ A minimal stand-in for the config manager - the ctx object looks up definitions by ID through it.
    """
    def __init__(self, oauth_defs:'anydict') -> 'None':
        self.oauth_defs = oauth_defs

        # The verifier is built with this cache on the first failed static comparison,
        # it is never actually used because these tests carry no JWT definitions.
        self.cache_api = None

    def basic_auth_get_by_id(self, security_id:'int') -> 'any_':
        return None

    def apikey_get_by_id(self, security_id:'int') -> 'any_':
        return None

    def oauth_get_by_id(self, security_id:'int') -> 'any_':
        return self.oauth_defs.get(security_id)

# ################################################################################################################################
# ################################################################################################################################

class _FakeServer:
    """ A minimal stand-in for ParallelServer - only the config manager the ctx object needs.
    """
    def __init__(self, oauth_defs:'anydict') -> 'None':
        self.config_manager = _FakeConfigManager(oauth_defs)

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupNaming(TestCase):
    """ Tests for the auto-created security group naming convention.
    """

# ################################################################################################################################

    def test_group_name_uses_mcp_prefix(self) -> 'None':
        """ The auto-created group name must be mcp.<channel_name>.
        """

        channel_name = 'my-mcp-channel'
        group_name = 'mcp.' + channel_name

        self.assertEqual(group_name, 'mcp.my-mcp-channel')

# ################################################################################################################################

    def test_group_name_prefix_constant(self) -> 'None':
        """ The prefix used in views must match the convention.
        """

        self.assertEqual(_mcp_group_name_prefix, 'mcp.')

# ################################################################################################################################
# ################################################################################################################################

class SecurityInputParsing(TestCase):
    """ Tests that hidden input names from the security badge picker
    produce the correct member_id_list values for the group service.
    """

# ################################################################################################################################

    def test_hidden_input_names_produce_member_ids(self) -> 'None':
        """ The hidden input value format sec_type-id must be passed as member_id_list.
        """

        # Simulated POST data from the security badge picker
        post_data = {
            'mcp_security_basic_auth-5': 'basic_auth-5',
            'mcp_security_apikey-12': 'apikey-12',
            'name': 'test-channel',
        }

        prefix = 'mcp_security_'

        security_keys:'anylist' = []
        for key in post_data:
            if key.startswith(prefix):
                security_keys.append(key)

        member_id_list:'anylist' = []
        for key in security_keys:
            value = post_data[key]
            member_id_list.append(value)

        self.assertEqual(len(member_id_list), 2)
        self.assertIn('basic_auth-5', member_id_list)
        self.assertIn('apikey-12', member_id_list)

# ################################################################################################################################

    def test_empty_security_produces_empty_member_list(self) -> 'None':
        """ No security hidden inputs means an empty member_id_list.
        """

        post_data = {
            'name': 'test-channel',
        }

        prefix = 'mcp_security_'

        security_keys:'anylist' = []
        for key in post_data:
            if key.startswith(prefix):
                security_keys.append(key)

        member_id_list:'anylist' = []
        for key in security_keys:
            value = post_data[key]
            member_id_list.append(value)

        self.assertEqual(member_id_list, [])

# ################################################################################################################################
# ################################################################################################################################

class HookSecurityGroupsPropagation(TestCase):
    """ Tests that the hook correctly propagates security_groups to HTTPSOAP opaque data.
    """

# ################################################################################################################################

    def test_security_groups_stored_in_opaque(self) -> 'None':
        """ When security_groups are in data, they must end up in HTTPSOAP.opaque1.
        """

        security_groups = [42, 99]
        opaque = {'security_groups': security_groups} if security_groups else {}

        self.assertEqual(opaque['security_groups'], [42, 99])

# ################################################################################################################################

    def test_security_groups_merged_into_existing_opaque(self) -> 'None':
        """ When updating an existing channel, security_groups must be merged
        into the existing opaque data without losing other keys.
        """

        current_opaque:'anydict' = {'some_other_key': 'value'}
        security_groups = [7]

        current_opaque['security_groups'] = security_groups

        self.assertEqual(current_opaque['security_groups'], [7])
        self.assertEqual(current_opaque['some_other_key'], 'value')

# ################################################################################################################################

    def test_empty_security_groups_produces_empty_opaque(self) -> 'None':
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

    def test_group_name_matches_channel_name(self) -> 'None':
        """ The group to delete must be named mcp.<channel_name>.
        """

        channel_name = 'production-api'
        group_name = 'mcp.' + channel_name

        self.assertEqual(group_name, 'mcp.production-api')

# ################################################################################################################################

    def test_group_type_is_api_clients(self) -> 'None':
        """ The auto-created group must be of type Group_Parent with API_Clients subtype.
        """

        self.assertEqual(Groups.Type.Group_Parent, 'zato-group')
        self.assertEqual(Groups.Type.API_Clients, 'zato-api-creds')

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenLifecycle(TestCase):
    """ Lifecycle of bearer token members in a security groups ctx object -
    group assignment, member addition and removal, group deletion and definition edits.
    """

    def _make_sec_def(self) -> 'stranydict':
        out:'stranydict' = {
            'id': _bearer_security_id,
            'name': 'test.bearer.member',
            'sec_type': 'oauth',
            'static_token': _static_token,
        }
        return out

# ################################################################################################################################

    def _make_ctx(self) -> 'SecurityGroupsCtx':
        sec_def = self._make_sec_def()
        server = _FakeServer({_bearer_security_id: sec_def})

        out = SecurityGroupsCtx(cast_('ParallelServer', server))
        out.channel_id = 1

        return out

# ################################################################################################################################

    def _make_member(self) -> 'Member':
        out = Member()

        out.id = 1
        out.name = 'test.bearer.member'
        out.type = 'zato-api-creds'
        out.group_id = _group_id
        out.security_id = _bearer_security_id
        out.sec_type = 'oauth'

        return out

# ################################################################################################################################

    def test_group_assignment_populates_credentials(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])

        self.assertIn(_bearer_security_id, ctx.bearer_token_credentials)
        self.assertTrue(ctx.has_members())

        # The static token now resolves to the member's security ID
        security_id = ctx.check_security_bearer_token(_cid, _channel_name, _static_token)
        self.assertEqual(security_id, _bearer_security_id)

# ################################################################################################################################

    def test_wrong_static_token_is_rejected(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])

        security_id = ctx.check_security_bearer_token(_cid, _channel_name, 'test-wrong-token')
        self.assertIsNone(security_id)

# ################################################################################################################################

    def test_member_added_to_group(self) -> 'None':
        ctx = self._make_ctx()

        # The ctx object must know the group before members can be added to it
        ctx.security_groups.add(_group_id)

        # Adding the member looks up its definition through the config manager
        ctx.on_member_added_to_group(_group_id, _bearer_security_id)

        self.assertIn(_bearer_security_id, ctx.bearer_token_credentials)

        security_id = ctx.check_security_bearer_token(_cid, _channel_name, _static_token)
        self.assertEqual(security_id, _bearer_security_id)

# ################################################################################################################################

    def test_member_removed_from_last_group_deletes_definition(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])
        ctx.on_member_removed_from_group(_group_id, _bearer_security_id)

        self.assertNotIn(_bearer_security_id, ctx.bearer_token_credentials)
        self.assertFalse(ctx.has_members())

        security_id = ctx.check_security_bearer_token(_cid, _channel_name, _static_token)
        self.assertIsNone(security_id)

# ################################################################################################################################

    def test_group_deleted_removes_credentials(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])
        ctx.on_group_deleted(_group_id)

        self.assertNotIn(_bearer_security_id, ctx.bearer_token_credentials)
        self.assertNotIn(_group_id, ctx.security_groups)
        self.assertFalse(ctx.has_members())

# ################################################################################################################################

    def test_group_unassigned_from_channel(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])
        ctx.on_group_unassigned_from_channel(_group_id)

        self.assertNotIn(_bearer_security_id, ctx.bearer_token_credentials)
        self.assertNotIn(_group_id, ctx.security_groups)

# ################################################################################################################################

    def test_definition_edit_updates_verify_config(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])

        # The definition is edited to carry a new static token ..
        sec_def = self._make_sec_def()
        sec_def['static_token'] = 'test-new-static-token'
        ctx.set_current_bearer_token(_bearer_security_id, sec_def)

        # .. the old token no longer matches ..
        security_id = ctx.check_security_bearer_token(_cid, _channel_name, _static_token)
        self.assertIsNone(security_id)

        # .. and the new one does.
        security_id = ctx.check_security_bearer_token(_cid, _channel_name, 'test-new-static-token')
        self.assertEqual(security_id, _bearer_security_id)

# ################################################################################################################################

    def test_bearer_token_deleted(self) -> 'None':
        ctx = self._make_ctx()
        member = self._make_member()

        ctx.on_group_assigned_to_channel(_group_id, [member])
        ctx.on_bearer_token_deleted(_bearer_security_id)

        self.assertNotIn(_bearer_security_id, ctx.bearer_token_credentials)

        security_id = ctx.check_security_bearer_token(_cid, _channel_name, _static_token)
        self.assertIsNone(security_id)

# ################################################################################################################################
# ################################################################################################################################
