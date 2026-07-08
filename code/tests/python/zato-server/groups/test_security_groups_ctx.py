# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.server.groups.ctx import SecurityGroupsCtx

# ################################################################################################################################
# ################################################################################################################################

_group_id = 111

_security_id1 = 201
_security_id2 = 202

_header_default = 'HTTP_X_API_KEY'
_header_custom = 'HTTP_X_CUSTOM_TOKEN'

_header_value1 = 'key-value-0001'
_header_value2 = 'key-value-0002'

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
        self.assertIn(_header_value1, ctx.apikey_credentials)

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
        self.assertNotIn(_header_value2, ctx.apikey_credentials)

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
        self.assertIn(_header_value1, ctx.apikey_credentials)
        self.assertIn(_header_value2, ctx.apikey_credentials)

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
        self.assertIn(_header_value2, ctx.apikey_credentials)

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

        sec_info = ctx.apikey_credentials[_header_value1]
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
        self.assertNotIn(_header_value1, ctx.apikey_credentials)

        sec_info = ctx.apikey_credentials[_header_value2]
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

if __name__ == '__main__':
    unittest.main()
