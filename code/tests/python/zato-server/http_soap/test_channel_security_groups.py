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
from zato.common.ext.bunch import Bunch
from zato.server.connection.http_soap.url_data import URLData
from zato.server.service.internal.http_soap import Edit

# ################################################################################################################################
# ################################################################################################################################

_channel_id = 4001
_channel_name = 'api.orders'
_url_path = '/api/orders'
_match_target = ':::(GET):::ZATO_ANY_INTERNAL:::/api/orders'

_group_id1 = 501
_group_id2 = 502

_group_name1 = 'orders.clients'

# ################################################################################################################################
# ################################################################################################################################

def _make_url_data() -> 'URLData':
    """ A URLData holding only what building a channel item out of a message needs.
    """
    out = object.__new__(URLData)
    out.config_manager = MagicMock()

    return out

# ################################################################################################################################

def _make_msg(**kwargs) -> 'Bunch':
    """ The shape of a channel create or edit message. Every field the channel item is built from
    is optional in the message, so only the ones a test cares about are set.
    """
    out = Bunch()
    out.id = _channel_id
    out.name = _channel_name
    out.url_path = _url_path
    out.service_name = 'api.orders.get'
    out.transport = URL_TYPE.PLAIN_HTTP
    out.match_slash = True

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################

def _make_old_data(**kwargs) -> 'Bunch':
    """ The channel item a channel held until the edit arrived.
    """
    out = Bunch()
    out.id = _channel_id
    out.name = _channel_name

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelItemSecurityGroupsTestCase(TestCase):
    """ How the security groups of a channel are resolved when a create or edit message arrives.

    A channel may be protected by security groups instead of by a security definition of its own,
    and an edit reaches the runtime as a delete followed by a create, so the groups a channel keeps
    come either from the message or from what the channel held until then.
    """

# ################################################################################################################################

    def test_groups_in_the_message_are_used(self) -> 'None':
        url_data = _make_url_data()
        builder = url_data.config_manager.server.security_groups_ctx_builder

        msg = _make_msg(security_groups=[_group_id1, _group_id2])
        channel_item = url_data._channel_item_from_msg(msg, _match_target, {})

        self.assertEqual(channel_item['security_groups'], [_group_id1, _group_id2])

        builder.build_ctx.assert_called_once_with(_channel_id, [_group_id1, _group_id2])
        self.assertIs(channel_item['security_groups_ctx'], builder.build_ctx.return_value)

# ################################################################################################################################

    def test_a_message_without_groups_keeps_the_ones_already_there(self) -> 'None':
        # An edit that does not mention security groups says nothing about them, so the channel
        # keeps the ones it had. Without this, a channel with no security definition of its own
        # would come out of the edit with nothing protecting it.
        url_data = _make_url_data()
        builder = url_data.config_manager.server.security_groups_ctx_builder

        msg = _make_msg()
        old_data = _make_old_data(security_groups=[_group_id1])

        channel_item = url_data._channel_item_from_msg(msg, _match_target, old_data)

        self.assertEqual(channel_item['security_groups'], [_group_id1])

        builder.build_ctx.assert_called_once_with(_channel_id, [_group_id1])
        self.assertIs(channel_item['security_groups_ctx'], builder.build_ctx.return_value)

# ################################################################################################################################

    def test_an_empty_list_in_the_message_clears_the_groups(self) -> 'None':
        # This is what the Dashboard sends once the operator unchecks every group.
        url_data = _make_url_data()
        builder = url_data.config_manager.server.security_groups_ctx_builder

        msg = _make_msg(security_groups=[])
        old_data = _make_old_data(security_groups=[_group_id1])

        channel_item = url_data._channel_item_from_msg(msg, _match_target, old_data)

        self.assertEqual(channel_item['security_groups'], [])
        self.assertIsNone(channel_item['security_groups_ctx'])

        builder.build_ctx.assert_not_called()

# ################################################################################################################################

    def test_a_channel_being_created_has_no_previous_groups_to_keep(self) -> 'None':
        url_data = _make_url_data()
        builder = url_data.config_manager.server.security_groups_ctx_builder

        msg = _make_msg()
        channel_item = url_data._channel_item_from_msg(msg, _match_target, {})

        self.assertIsNone(channel_item['security_groups'])
        self.assertIsNone(channel_item['security_groups_ctx'])

        builder.build_ctx.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class PreprocessSecurityGroupsTestCase(TestCase):
    """ What a channel's Create and Edit make of the security groups their input carries.

    An optional field that the caller never sent arrives as None, while one sent as an empty list
    arrives as that list, and the two mean different things - the first says nothing about the
    channel's groups, the second says it has none.
    """

# ################################################################################################################################

    def test_a_field_that_was_not_sent_leaves_the_stored_groups_alone(self) -> 'None':
        service = MagicMock()

        input = Bunch()
        input.security_groups = None

        skip_opaque = []

        out = Edit._preprocess_security_groups(service, input, skip_opaque)

        # None travels on to the servers, which is what tells them to keep what they have ..
        self.assertIsNone(out)

        # .. and listing the field here is what keeps the write from overwriting what is stored.
        self.assertEqual(skip_opaque, ['security_groups'])

        service.invoke.assert_not_called()

# ################################################################################################################################

    def test_an_empty_list_is_written_through(self) -> 'None':
        service = MagicMock()

        input = Bunch()
        input.security_groups = []

        skip_opaque = []

        out = Edit._preprocess_security_groups(service, input, skip_opaque)

        self.assertEqual(out, [])
        self.assertEqual(skip_opaque, [])

        service.invoke.assert_not_called()

# ################################################################################################################################

    def test_group_ids_are_carried_over(self) -> 'None':
        service = MagicMock()
        service.invoke.return_value = [{'id':_group_id1, 'name':_group_name1}]

        input = Bunch()
        input.security_groups = [_group_id1]

        skip_opaque = []

        out = Edit._preprocess_security_groups(service, input, skip_opaque)

        self.assertEqual(out, [_group_id1])
        self.assertEqual(skip_opaque, [])

# ################################################################################################################################

    def test_group_names_are_turned_into_ids(self) -> 'None':
        service = MagicMock()
        service.invoke.return_value = [{'id':_group_id1, 'name':_group_name1}]

        input = Bunch()
        input.security_groups = [_group_name1]

        skip_opaque = []

        out = Edit._preprocess_security_groups(service, input, skip_opaque)

        self.assertEqual(out, [_group_id1])
        self.assertEqual(skip_opaque, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
