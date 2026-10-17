# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import Sec_Def_Type
from zato.server.groups.ctx import SecurityGroupsCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

_group_id = 111
_group_id2 = 112

# A group that no channel in these tests is assigned
_group_id_unassigned = 119

_security_id1 = 201
_security_id2 = 202

_header_default = 'HTTP_X_API_KEY'
_header_custom = 'HTTP_X_CUSTOM_TOKEN'

_header_value1 = 'key-value-0001'
_header_value2 = 'key-value-0002'

_username = 'user.0001'
_password = 'password.0001'

# ################################################################################################################################
# ################################################################################################################################

def _make_ctx() -> 'SecurityGroupsCtx':
    """ Builds a SecurityGroupsCtx with a mocked server.
    """
    server = MagicMock()
    out = SecurityGroupsCtx(server)
    out.channel_id = 1
    return out

# ################################################################################################################################
# ################################################################################################################################

class APIKeyHeaderInvariantTestCase(unittest.TestCase):
    """ Tests for the one-header-per-channel invariant of SecurityGroupsCtx.apikey_header.
    """

# ################################################################################################################################

    def test_initial_header_is_none(self) -> 'None':
        """ A newly built ctx has no API key header configured.
        """
        ctx = _make_ctx()

        self.assertIsNone(ctx.apikey_header)

# ################################################################################################################################

    def test_first_member_sets_header(self) -> 'None':
        """ The first API key member sets apikey_header to its own header.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)

        self.assertEqual(ctx.apikey_header, _header_custom)
        self.assertIn(ctx._apikey_index_key(_header_value1), ctx.apikey_credentials)

# ################################################################################################################################

    @patch('zato.server.groups.ctx.logger')
    def test_second_member_with_different_header_is_rejected(self, mock_logger:'MagicMock') -> 'None':
        """ A second member whose header differs from the channel-wide one is rejected and logged.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.on_apikey_created(_group_id, _security_id2, _header_default, _header_value2)

        # The header stays as set by the first member ..
        self.assertEqual(ctx.apikey_header, _header_custom)

        # .. the second member's credentials were not stored ..
        self.assertNotIn(ctx._apikey_index_key(_header_value2), ctx.apikey_credentials)

        # .. and the conflict was logged as an error.
        mock_logger.error.assert_called_once()

# ################################################################################################################################

    def test_second_member_with_same_header_is_accepted(self) -> 'None':
        """ A second member using the same header is accepted.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.on_apikey_created(_group_id, _security_id2, _header_custom, _header_value2)

        self.assertEqual(ctx.apikey_header, _header_custom)
        self.assertIn(ctx._apikey_index_key(_header_value1), ctx.apikey_credentials)
        self.assertIn(ctx._apikey_index_key(_header_value2), ctx.apikey_credentials)

# ################################################################################################################################

    def test_deleting_last_member_resets_header(self) -> 'None':
        """ Deleting the last API key member resets apikey_header to None.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.on_apikey_deleted(_security_id1)

        self.assertIsNone(ctx.apikey_header)
        self.assertEqual(ctx.apikey_credentials, {})

# ################################################################################################################################

    def test_deleting_one_of_two_members_keeps_header(self) -> 'None':
        """ Deleting one member while another remains keeps the header in place.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.on_apikey_created(_group_id, _security_id2, _header_custom, _header_value2)
        ctx.on_apikey_deleted(_security_id1)

        self.assertEqual(ctx.apikey_header, _header_custom)
        self.assertIn(ctx._apikey_index_key(_header_value2), ctx.apikey_credentials)

# ################################################################################################################################

    def test_group_deleted_resets_header(self) -> 'None':
        """ Deleting the whole group removes its API key members and resets the header.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.on_group_deleted(_group_id)

        self.assertIsNone(ctx.apikey_header)
        self.assertEqual(ctx.apikey_credentials, {})

# ################################################################################################################################

    def test_set_current_apikey_header_rekeys(self) -> 'None':
        """ set_current_apikey_header replaces the header while keeping the same key value.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_default, _header_value1)
        ctx.set_current_apikey_header(_security_id1, _header_custom)

        self.assertEqual(ctx.apikey_header, _header_custom)

        sec_info = ctx.apikey_credentials[ctx._apikey_index_key(_header_value1)]
        self.assertEqual(sec_info.header, _header_custom)
        self.assertEqual(sec_info.security_id, _security_id1)

# ################################################################################################################################

    def test_password_change_keeps_header(self) -> 'None':
        """ set_current_apikey (password change) stores the new value under the same header.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)
        ctx.set_current_apikey(_security_id1, _header_value2)

        self.assertEqual(ctx.apikey_header, _header_custom)
        self.assertNotIn(ctx._apikey_index_key(_header_value1), ctx.apikey_credentials)

        sec_info = ctx.apikey_credentials[ctx._apikey_index_key(_header_value2)]
        self.assertEqual(sec_info.header, _header_custom)
        self.assertEqual(sec_info.security_id, _security_id1)

# ################################################################################################################################

    def test_check_security_apikey_accepts_valid_key(self) -> 'None':
        """ A valid key value is matched regardless of which header carried it, as extraction happens upstream.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)

        self.assertEqual(result, _security_id1)

# ################################################################################################################################

    def test_check_security_apikey_rejects_invalid_key(self) -> 'None':
        """ An unknown key value is rejected.
        """
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header_custom, _header_value1)

        result = ctx.check_security_apikey('cid1', 'channel1', 'no-such-key')

        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################

class MemberRemovedFromGroupTestCase(unittest.TestCase):
    """ Tests that removing a definition from one of a channel's groups affects that group alone,
    and that the definition stops authenticating only when no group of the channel holds it anymore.
    """

# ################################################################################################################################

    def _make_apikey_ctx(self, group_id_list:'intlist') -> 'SecurityGroupsCtx':
        """ Builds a ctx whose API key definition belongs to each of the given groups.
        """
        ctx = _make_ctx()

        ctx.server.config_manager.basic_auth_get_by_id.return_value = None
        ctx.server.config_manager.apikey_get_by_id.return_value = {'sec_type': Sec_Def_Type.APIKEY}

        for group_id in group_id_list:
            ctx.on_apikey_created(group_id, _security_id1, _header_custom, _header_value1)

        return ctx

# ################################################################################################################################

    def _make_basic_auth_ctx(self, group_id_list:'intlist') -> 'SecurityGroupsCtx':
        """ Builds a ctx whose Basic Auth definition belongs to each of the given groups.
        """
        ctx = _make_ctx()

        ctx.server.config_manager.basic_auth_get_by_id.return_value = {'sec_type': Sec_Def_Type.BASIC_AUTH}

        for group_id in group_id_list:
            ctx.on_basic_auth_created(group_id, _security_id1, _username, _password)

        return ctx

# ################################################################################################################################

    def test_apikey_removed_from_one_of_two_groups_still_authenticates(self) -> 'None':
        """ An API key removed from one group keeps authenticating through the other group.
        """
        ctx = self._make_apikey_ctx([_group_id, _group_id2])

        ctx.on_member_removed_from_group(_group_id, _security_id1)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)
        self.assertEqual(result, _security_id1)

# ################################################################################################################################

    def test_apikey_removed_from_one_of_two_groups_stays_in_the_other(self) -> 'None':
        """ Removing an API key from one group leaves the other group's membership as it was.
        """
        ctx = self._make_apikey_ctx([_group_id, _group_id2])

        ctx.on_member_removed_from_group(_group_id, _security_id1)

        self.assertNotIn(_security_id1, ctx.group_to_sec_map[_group_id])
        self.assertIn(_security_id1, ctx.group_to_sec_map[_group_id2])
        self.assertTrue(ctx.has_security_id(_security_id1))

# ################################################################################################################################

    def test_apikey_removed_from_its_only_group_stops_authenticating(self) -> 'None':
        """ An API key removed from the one group that held it no longer authenticates.
        """
        ctx = self._make_apikey_ctx([_group_id])

        ctx.on_member_removed_from_group(_group_id, _security_id1)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)
        self.assertIsNone(result)

        self.assertEqual(ctx.apikey_credentials, {})
        self.assertIsNone(ctx.apikey_header)
        self.assertFalse(ctx.has_security_id(_security_id1))

# ################################################################################################################################

    def test_apikey_removed_from_both_groups_stops_authenticating(self) -> 'None':
        """ An API key removed from each of its groups in turn authenticates until the last removal and not after it.
        """
        ctx = self._make_apikey_ctx([_group_id, _group_id2])

        ctx.on_member_removed_from_group(_group_id, _security_id1)
        self.assertEqual(ctx.check_security_apikey('cid1', 'channel1', _header_value1), _security_id1)

        ctx.on_member_removed_from_group(_group_id2, _security_id1)
        self.assertIsNone(ctx.check_security_apikey('cid1', 'channel1', _header_value1))

# ################################################################################################################################

    def test_basic_auth_removed_from_one_of_two_groups_still_authenticates(self) -> 'None':
        """ A Basic Auth definition removed from one group keeps authenticating through the other group.
        """
        ctx = self._make_basic_auth_ctx([_group_id, _group_id2])

        ctx.on_member_removed_from_group(_group_id, _security_id1)

        result = ctx.check_security_basic_auth('cid1', 'channel1', _username, _password)
        self.assertEqual(result, _security_id1)

# ################################################################################################################################

    def test_basic_auth_removed_from_its_only_group_stops_authenticating(self) -> 'None':
        """ A Basic Auth definition removed from the one group that held it no longer authenticates.
        """
        ctx = self._make_basic_auth_ctx([_group_id])

        ctx.on_member_removed_from_group(_group_id, _security_id1)

        result = ctx.check_security_basic_auth('cid1', 'channel1', _username, _password)
        self.assertIsNone(result)

# ################################################################################################################################

    def test_group_unassigned_keeps_member_of_another_group(self) -> 'None':
        """ Unassigning one group from the channel leaves a definition the other group holds authenticating.
        """
        ctx = self._make_apikey_ctx([_group_id, _group_id2])

        ctx.on_group_unassigned_from_channel(_group_id)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)
        self.assertEqual(result, _security_id1)

        self.assertNotIn(_group_id, ctx.security_groups)
        self.assertIn(_security_id1, ctx.group_to_sec_map[_group_id2])

# ################################################################################################################################

    def test_group_unassigned_removes_member_of_no_other_group(self) -> 'None':
        """ Unassigning the one group that held a definition leaves the definition out of the channel.
        """
        ctx = self._make_apikey_ctx([_group_id])

        ctx.on_group_unassigned_from_channel(_group_id)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)
        self.assertIsNone(result)

# ################################################################################################################################

    def test_removal_from_a_group_not_on_the_channel_changes_nothing(self) -> 'None':
        """ A removal event for a group the channel does not use leaves the channel's definitions as they were.
        """
        ctx = self._make_apikey_ctx([_group_id])

        ctx.on_member_removed_from_group(_group_id_unassigned, _security_id1)

        result = ctx.check_security_apikey('cid1', 'channel1', _header_value1)
        self.assertEqual(result, _security_id1)
        self.assertIn(_security_id1, ctx.group_to_sec_map[_group_id])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
