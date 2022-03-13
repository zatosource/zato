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

if 0:
    from zato.server.generic.api.outconn_wsx import _ZatoWSXClientImpl

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnConnectTestCase(CommandLineTestCase):

# ################################################################################################################################

    def test_connect_ok_no_credentials(self) -> 'None':

        with WSXChannelManager(self) as wsx_channel_address:

            # A configuration dict for the outconn wrapper
            config = {}
            config['name'] = 'test_connect_ok'
            config['username'] = ''
            config['secret'] = ''
            config['auth_url'] = config['address'] = wsx_channel_address
            config['pool_size'] = 1
            config['is_zato'] = True
            config['is_active'] = True
            config['needs_spawn'] = False
            config['queue_build_cap'] = 30
            config['subscription_list'] = ''
            config['has_auto_reconnect'] = False

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()

            outconn_wsx_queue = wrapper.client.queue.queue
            self.assertEqual(len(outconn_wsx_queue), 1)

            impl = outconn_wsx_queue[0].impl
            zato_client = impl._zato_client # type: _ZatoWSXClientImpl

            self.assertTrue(zato_client.auth_token.startswith('zwsxt'))
            self.assertEqual(zato_client.config.address, wsx_channel_address)

            self.assertTrue(zato_client.is_connected)
            self.assertTrue(zato_client.is_authenticated)
            self.assertTrue(zato_client.keep_running)

            self.assertFalse(zato_client.needs_auth)
            self.assertFalse(zato_client.is_auth_needed)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
