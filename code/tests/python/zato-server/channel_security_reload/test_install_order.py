# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# gevent
from gevent import sleep as gevent_sleep, spawn

# Zato
from zato.common.typing_ import cast_

# Local
from .helpers import get_channel_items, GroupsManagerStub, make_config_manager, make_config_store, make_member, \
    New_Password, New_Username, Previous_Password, Previous_Username, ServerStub, unlisten

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class _Probe:
    """ Reads the installed request dispatcher each time the installation gives up control,
    the way a request served in the meantime reads it.
    """
    def __init__(self, config_manager:'ConfigManager') -> 'None':
        self.config_manager = config_manager
        self.is_installing = True
        self.observation_count = 0
        self.unprotected_channels:'strlist' = []
        self.dispatchers_observed:'anylist' = []

    def run(self) -> 'None':
        while self.is_installing:
            self.observe()
            gevent_sleep(0)

    def observe(self) -> 'None':

        # The dispatcher a request would be served by at this point ..
        request_dispatcher = cast_('any_', self.config_manager.request_dispatcher)
        self.dispatchers_observed.append(request_dispatcher)

        # .. and every channel of that dispatcher that has security groups without their context.
        for channel_item in get_channel_items(self.config_manager):
            if channel_item.get('security_groups'):
                if not channel_item.get('security_groups_ctx'):
                    self.unprotected_channels.append(channel_item['name'])

        self.observation_count += 1

# ################################################################################################################################
# ################################################################################################################################

def _install_while_observed(config_manager:'ConfigManager') -> '_Probe':
    """ Installs the request dispatcher with a probe greenlet observing what requests would see in the meantime.
    """
    probe = _Probe(config_manager)
    greenlet = spawn(probe.run)

    try:
        config_manager._install_request_dispatcher()
    finally:
        probe.is_installing = False

    _ = greenlet.join()

    return probe

# ################################################################################################################################
# ################################################################################################################################

class InstallOrderTestCase(TestCase):
    """ What a request served while a request dispatcher is being installed finds on its channel.
    """

    def setUp(self) -> 'None':
        member = make_member()
        groups_manager = GroupsManagerStub([member])

        self.server = ServerStub(groups_manager)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        unlisten(self.config_manager)

# ################################################################################################################################

    def test_first_installation(self) -> 'None':

        config_store = make_config_store(New_Username, New_Password)
        self.config_manager = make_config_manager(self.server, config_store)

        probe = _install_while_observed(self.config_manager)

        # The installation gave up control while it was building the security groups contexts ..
        self.assertGreater(probe.observation_count, 0)

        # .. no dispatcher was visible until the installation completed ..
        for request_dispatcher in probe.dispatchers_observed:
            self.assertIsNone(request_dispatcher)

        # .. so no request could reach a channel without its context.
        self.assertEqual(probe.unprotected_channels, [])

        channel_items = get_channel_items(self.config_manager)
        channel_item = channel_items[0]

        self.assertIsNotNone(channel_item['security_groups_ctx'])

# ################################################################################################################################

    def test_configuration_reload(self) -> 'None':

        # The configuration the server runs with before the reload ..
        previous_config_store = make_config_store(Previous_Username, Previous_Password)
        self.config_manager = make_config_manager(self.server, previous_config_store)
        self.config_manager._install_request_dispatcher()

        previous_dispatcher = self.config_manager.request_dispatcher

        # .. the configuration the reload installs ..
        new_config_store = make_config_store(New_Username, New_Password)
        self.config_manager.config_store = new_config_store

        probe = _install_while_observed(self.config_manager)

        # .. the installation gave up control while it was building the security groups contexts ..
        self.assertGreater(probe.observation_count, 0)

        # .. the previous dispatcher served every request until the new one was complete ..
        for request_dispatcher in probe.dispatchers_observed:
            self.assertIs(request_dispatcher, previous_dispatcher)

        # .. no request could reach a channel without its context ..
        self.assertEqual(probe.unprotected_channels, [])

        # .. and the new dispatcher is installed with a context on its channel.
        self.assertIsNot(self.config_manager.request_dispatcher, previous_dispatcher)

        channel_items = get_channel_items(self.config_manager)
        channel_item = channel_items[0]

        self.assertIsNotNone(channel_item['security_groups_ctx'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
