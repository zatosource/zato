# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to run as soon as possible
from gevent.monkey import patch_all
patch_all()

# stdlib
from unittest import main

# Zato
from zato.common.test import CommandLineTestCase
from zato.common.test.wsx_ import WSXChannelManager
from zato.server.generic.api.outconn_wsx import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnConnectTestCase(CommandLineTestCase):

# ################################################################################################################################

    def test_connect_ok(self) -> 'None':

        with WSXChannelManager(self) as wsx_channel_address:

            # A configuration dict for the outconn wrapper
            config = {}
            config['name'] = 'test_connect_ok'
            config['username'] = 'test_connect_ok'
            config['secret'] = 'test_connect_ok'
            config['auth_url'] = config['address'] = wsx_channel_address
            config['pool_size'] = 1
            config['is_zato'] = True
            config['is_active'] = True
            config['needs_spawn'] = False
            config['queue_build_cap'] = 30
            config['subscription_list'] = ''

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
