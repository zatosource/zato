# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.server.groups.ctx import SecurityGroupsCtx

# ################################################################################################################################
# ################################################################################################################################

_group_id = 111
_other_group_id = 112

_security_id1 = 201
_security_id2 = 202

_header = 'HTTP_X_API_KEY'

_apikey1 = 'key-value-0001'
_apikey2 = 'key-value-0002'

_username1 = 'orders.client'
_username2 = 'invoices.client'

_password1 = 'password-0001'
_password2 = 'password-0002'

_cid = 'test-cid-1'
_channel_name = 'test.channel'

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

class APIKeyUniquenessTestCase(TestCase):
    """ One API key belongs to one definition within a channel's groups.

    The container is keyed by what an API key indexes to, so two definitions configured with the
    same key would land under the same entry - the first one to arrive keeps it and the second is
    left out, rather than the outcome depending on the order the members happen to be iterated in.
    """

# ################################################################################################################################

    @patch('zato.server.groups.ctx.logger')
    def test_a_second_definition_with_the_same_key_is_left_out(self, mock_logger:'MagicMock') -> 'None':
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header, _apikey1)
        ctx.on_apikey_created(_other_group_id, _security_id2, _header, _apikey1)

        # The key still resolves to the definition that had it first ..
        security_id = ctx.check_security_apikey(_cid, _channel_name, _apikey1)
        self.assertEqual(security_id, _security_id1)

        # .. only one entry was stored ..
        self.assertEqual(len(ctx.apikey_credentials), 1)

        # .. the second definition is not a member of the channel at all ..
        self.assertFalse(ctx.has_security_id(_security_id2))

        # .. and the operator was told.
        mock_logger.error.assert_called_once()

# ################################################################################################################################

    def test_the_same_definition_may_be_recreated(self) -> 'None':
        # A definition arriving twice, which is what happens when it belongs to two of the
        # channel's groups, is not a conflict with itself.
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header, _apikey1)
        ctx.on_apikey_created(_other_group_id, _security_id1, _header, _apikey1)

        security_id = ctx.check_security_apikey(_cid, _channel_name, _apikey1)
        self.assertEqual(security_id, _security_id1)

        self.assertEqual(len(ctx.apikey_credentials), 1)

        # It is a member through both groups
        self.assertIn(_security_id1, ctx.group_to_sec_map[_group_id])
        self.assertIn(_security_id1, ctx.group_to_sec_map[_other_group_id])

# ################################################################################################################################

    def test_a_refused_key_does_not_claim_the_channel_header(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header, _apikey1)
        ctx.on_apikey_created(_other_group_id, _security_id2, _header, _apikey1)

        # The header comes from the definition that was actually stored ..
        self.assertEqual(ctx.apikey_header, _header)

        # .. and deleting that one definition leaves nothing behind.
        ctx.on_apikey_deleted(_security_id1)

        self.assertIsNone(ctx.apikey_header)
        self.assertEqual(ctx.apikey_credentials, {})

# ################################################################################################################################

    def test_distinct_keys_are_both_stored(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header, _apikey1)
        ctx.on_apikey_created(_group_id, _security_id2, _header, _apikey2)

        self.assertEqual(ctx.check_security_apikey(_cid, _channel_name, _apikey1), _security_id1)
        self.assertEqual(ctx.check_security_apikey(_cid, _channel_name, _apikey2), _security_id2)

# ################################################################################################################################
# ################################################################################################################################

class APIKeyIndexTestCase(TestCase):
    """ What the API key container is keyed by.
    """

# ################################################################################################################################

    def test_the_key_itself_is_not_a_container_key(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_apikey_created(_group_id, _security_id1, _header, _apikey1)

        self.assertNotIn(_apikey1, ctx.apikey_credentials)

# ################################################################################################################################

    def test_two_context_objects_index_the_same_key_differently(self) -> 'None':
        # Each context object derives its own index key, so what one holds an API key under
        # says nothing about what another one holds it under.
        first = _make_ctx()
        second = _make_ctx()

        self.assertNotEqual(first._apikey_index_key(_apikey1), second._apikey_index_key(_apikey1))

# ################################################################################################################################

    def test_one_context_object_indexes_a_key_the_same_way_every_time(self) -> 'None':
        ctx = _make_ctx()

        self.assertEqual(ctx._apikey_index_key(_apikey1), ctx._apikey_index_key(_apikey1))
        self.assertNotEqual(ctx._apikey_index_key(_apikey1), ctx._apikey_index_key(_apikey2))

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthUniquenessTestCase(TestCase):
    """ One username belongs to one definition within a channel's groups.

    Credentials are looked up by username, so two definitions sharing one would land under the same
    entry - and since each carries its own password, whichever of them was stored last would decide
    which password opens the channel for that username.
    """

# ################################################################################################################################

    @patch('zato.server.groups.ctx.logger')
    def test_a_second_definition_with_the_same_username_is_left_out(self, mock_logger:'MagicMock') -> 'None':
        ctx = _make_ctx()

        ctx.on_basic_auth_created(_group_id, _security_id1, _username1, _password1)
        ctx.on_basic_auth_created(_other_group_id, _security_id2, _username1, _password2)

        # The username still resolves to the definition that had it first, with its own password ..
        security_id = ctx.check_security_basic_auth(_cid, _channel_name, _username1, _password1)
        self.assertEqual(security_id, _security_id1)

        # .. the second definition's password does not open the channel ..
        self.assertIsNone(ctx.check_security_basic_auth(_cid, _channel_name, _username1, _password2))

        # .. only one entry was stored ..
        self.assertEqual(len(ctx.basic_auth_credentials), 1)

        # .. the second definition is not a member of the channel at all ..
        self.assertFalse(ctx.has_security_id(_security_id2))

        # .. and the operator was told.
        mock_logger.error.assert_called_once()

# ################################################################################################################################

    def test_the_same_definition_may_be_recreated(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_basic_auth_created(_group_id, _security_id1, _username1, _password1)
        ctx.on_basic_auth_created(_other_group_id, _security_id1, _username1, _password1)

        security_id = ctx.check_security_basic_auth(_cid, _channel_name, _username1, _password1)
        self.assertEqual(security_id, _security_id1)

        self.assertEqual(len(ctx.basic_auth_credentials), 1)

        self.assertIn(_security_id1, ctx.group_to_sec_map[_group_id])
        self.assertIn(_security_id1, ctx.group_to_sec_map[_other_group_id])

# ################################################################################################################################

    def test_distinct_usernames_are_both_stored(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_basic_auth_created(_group_id, _security_id1, _username1, _password1)
        ctx.on_basic_auth_created(_group_id, _security_id2, _username2, _password2)

        self.assertEqual(ctx.check_security_basic_auth(_cid, _channel_name, _username1, _password1), _security_id1)
        self.assertEqual(ctx.check_security_basic_auth(_cid, _channel_name, _username2, _password2), _security_id2)

# ################################################################################################################################

    def test_a_username_freed_by_a_delete_can_be_taken(self) -> 'None':
        ctx = _make_ctx()

        ctx.on_basic_auth_created(_group_id, _security_id1, _username1, _password1)
        ctx.on_basic_auth_deleted(_security_id1)

        ctx.on_basic_auth_created(_group_id, _security_id2, _username1, _password2)

        security_id = ctx.check_security_basic_auth(_cid, _channel_name, _username1, _password2)
        self.assertEqual(security_id, _security_id2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
