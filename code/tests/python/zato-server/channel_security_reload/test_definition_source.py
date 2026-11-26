# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Local
from .helpers import Channel_Name, get_channel_items, GroupsManagerStub, make_config_manager, make_config_store, \
    make_member, New_Password, New_Username, Previous_Password, Previous_Username, Security_ID, ServerStub, unlisten

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.config_manager import ConfigManager
    from zato.server.groups.ctx import SecurityGroupsCtx

# ################################################################################################################################
# ################################################################################################################################

_cid = 'zcid-test-reload-0001'

# ################################################################################################################################
# ################################################################################################################################

def _get_security_groups_ctx(config_manager:'ConfigManager') -> 'SecurityGroupsCtx':
    """ The security groups context of the channel of the installed dispatcher.
    """
    channel_items = get_channel_items(config_manager)
    channel_item = channel_items[0]

    out = channel_item['security_groups_ctx']
    return out

# ################################################################################################################################
# ################################################################################################################################

class DefinitionSourceTestCase(TestCase):
    """ Which configuration the security definitions of a channel's groups are taken from during a reload,
    when the configuration being installed and the one being replaced define the same member differently.
    """

    def setUp(self) -> 'None':
        member = make_member()
        self.groups_manager = GroupsManagerStub([member])

        server = ServerStub(self.groups_manager)

        # The configuration the server runs with before the reload ..
        previous_config_store = make_config_store(Previous_Username, Previous_Password)
        self.config_manager = make_config_manager(server, previous_config_store)
        self.config_manager._install_request_dispatcher()

        self.previous_ctx = _get_security_groups_ctx(self.config_manager)

        # .. and the one the reload installs.
        new_config_store = make_config_store(New_Username, New_Password)
        self.config_manager.config_store = new_config_store
        self.config_manager._install_request_dispatcher()

        self.new_ctx = _get_security_groups_ctx(self.config_manager)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        unlisten(self.config_manager)

# ################################################################################################################################

    def test_previous_configuration_before_the_reload(self) -> 'None':

        security_id = self.previous_ctx.check_security_basic_auth(_cid, Channel_Name, Previous_Username, Previous_Password)
        self.assertEqual(security_id, Security_ID)

# ################################################################################################################################

    def test_credentials_of_the_new_configuration_are_accepted(self) -> 'None':

        security_id = self.new_ctx.check_security_basic_auth(_cid, Channel_Name, New_Username, New_Password)
        self.assertEqual(security_id, Security_ID)

# ################################################################################################################################

    def test_credentials_of_the_previous_configuration_are_rejected(self) -> 'None':

        security_id = self.new_ctx.check_security_basic_auth(_cid, Channel_Name, Previous_Username, Previous_Password)
        self.assertIsNone(security_id)

# ################################################################################################################################

    def test_members_are_resolved_through_the_new_url_data(self) -> 'None':

        # One member list query per installation ..
        url_data_count = len(self.groups_manager.url_data_received)
        self.assertEqual(url_data_count, 2)

        # .. and the second one received the URLData of the dispatcher it installed.
        url_data = self.groups_manager.url_data_received[1]
        self.assertIs(url_data, self.config_manager.request_dispatcher.url_data)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
