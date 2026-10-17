# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import URL_TYPE
from zato.server.openapi_console.spec import get_accepted_security_id, is_channel_documented, is_channel_visible

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, intlist

# ################################################################################################################################
# ################################################################################################################################

# The caller's own definition and another one
_caller_id = 301
_other_id = 302

# A third definition that accepts the caller's credentials too
_second_caller_id = 303

# ################################################################################################################################
# ################################################################################################################################

def _make_groups_ctx(member_ids:'intlist') -> 'any_':
    """ The security groups of a channel, with the given definitions as their members.
    """
    out = MagicMock()

    def has_security_id(security_id:'int') -> 'bool':
        result = security_id in member_ids
        return result

    out.has_members.return_value = bool(member_ids)
    out.has_security_id.side_effect = has_security_id

    return out

# ################################################################################################################################

def _make_channel_item(security_id:'int | None', member_ids:'intlist | None') -> 'anydict':
    """ A REST channel with the given definition of its own and the given members of its security groups,
    where None means no definition or no groups.
    """
    out:'anydict' = {
        'connection': 'channel',
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': True,
        'is_internal': False,
        'service_name': 'api.orders.get',
        'security_id': security_id,
    }

    if member_ids is not None:
        out['security_groups_ctx'] = _make_groups_ctx(member_ids)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelVisibilityTestCase(TestCase):
    """ A channel is visible to a console caller exactly when the channel itself accepts the caller's definition.
    """

# ################################################################################################################################

    def test_the_channels_own_definition(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        self.assertTrue(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_another_definition(self) -> 'None':
        channel_item = _make_channel_item(_other_id, None)
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_another_definition_that_is_a_group_member(self) -> 'None':
        """ The channel checks its own definition and its groups alike, so membership alone is not enough.
        """
        channel_item = _make_channel_item(_other_id, [_caller_id])
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_the_own_definition_outside_the_groups(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, [_other_id])
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_the_own_definition_inside_the_groups(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, [_caller_id, _other_id])
        self.assertTrue(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_the_own_definition_with_groups_without_members(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, [])
        self.assertTrue(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_groups_alone_with_the_caller(self) -> 'None':
        channel_item = _make_channel_item(None, [_caller_id])
        self.assertTrue(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_groups_alone_without_the_caller(self) -> 'None':
        channel_item = _make_channel_item(None, [_other_id])
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_groups_alone_without_members(self) -> 'None':
        channel_item = _make_channel_item(None, [])
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################

    def test_no_security_at_all(self) -> 'None':
        channel_item = _make_channel_item(None, None)
        self.assertFalse(is_channel_visible(channel_item, {_caller_id}))

# ################################################################################################################################
# ################################################################################################################################

class AcceptedSecurityIdTestCase(TestCase):
    """ Credentials that several definitions accept reach each channel that accepts one of these definitions,
    and the channel decides which one it is.
    """

# ################################################################################################################################

    def test_the_channels_own_definition_among_several(self) -> 'None':
        channel_item = _make_channel_item(_second_caller_id, None)
        security_id = get_accepted_security_id(channel_item, {_caller_id, _second_caller_id})

        self.assertEqual(security_id, _second_caller_id)

# ################################################################################################################################

    def test_the_group_member_among_several(self) -> 'None':
        channel_item = _make_channel_item(None, [_other_id, _second_caller_id])
        security_id = get_accepted_security_id(channel_item, {_caller_id, _second_caller_id})

        self.assertEqual(security_id, _second_caller_id)

# ################################################################################################################################

    def test_two_group_members_resolve_to_the_lower_id(self) -> 'None':
        channel_item = _make_channel_item(None, [_caller_id, _second_caller_id])
        security_id = get_accepted_security_id(channel_item, {_second_caller_id, _caller_id})

        self.assertEqual(security_id, _caller_id)

# ################################################################################################################################

    def test_none_of_the_definitions(self) -> 'None':
        channel_item = _make_channel_item(_other_id, None)
        security_id = get_accepted_security_id(channel_item, {_caller_id, _second_caller_id})

        self.assertIsNone(security_id)

# ################################################################################################################################
# ################################################################################################################################

class ChannelDocumentedTestCase(TestCase):
    """ The channels that OpenAPI documents describe, which are the channels the console can invoke.
    """

# ################################################################################################################################

    def test_a_channel_without_the_flag_is_documented(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        self.assertTrue(is_channel_documented(channel_item))

# ################################################################################################################################

    def test_a_channel_with_the_flag_on_is_documented(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        channel_item['should_include_in_openapi'] = True

        self.assertTrue(is_channel_documented(channel_item))

# ################################################################################################################################

    def test_a_channel_with_the_flag_off_is_not_documented(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        channel_item['should_include_in_openapi'] = False

        self.assertFalse(is_channel_documented(channel_item))

# ################################################################################################################################

    def test_an_inactive_channel_is_not_documented(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        channel_item['is_active'] = False

        self.assertFalse(is_channel_documented(channel_item))

# ################################################################################################################################

    def test_an_internal_channel_is_not_documented(self) -> 'None':
        channel_item = _make_channel_item(_caller_id, None)
        channel_item['is_internal'] = True

        self.assertFalse(is_channel_documented(channel_item))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
