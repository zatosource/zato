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
from zato.server.generic.api.outconn_wsx import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnConnectTestCase(CommandLineTestCase):

# ################################################################################################################################

    def get_wsx_channel_address(self) -> 'str':

        # Command to invoke ..
        cli_params = ['wsx', 'create-channel']

        # .. get its response as a dict ..
        out = self.run_zato_cli_json_command(cli_params) # type: anydict

        # .. extract an address of a newly created WSX channel ..
        address = out['address']

        # .. and return it to our caller.
        return address

# ################################################################################################################################

    def test_connect_ok(self) -> 'None':

        # A newly created channel for us to connect to
        wsx_channel_address = self.get_wsx_channel_address()

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

        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
