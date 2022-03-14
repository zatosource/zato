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
from uuid import uuid4

# Zato
from zato.common.test import CommandLineTestCase
from zato.common.test.wsx_ import WSXChannelManager
from zato.common.util.api import fs_safe_now
from zato.server.generic.api.outconn_wsx import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.server.generic.api.outconn_wsx import _ZatoWSXClientImpl

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnConnectTestCase(CommandLineTestCase):

# ################################################################################################################################

    def _get_config(
        self,
        wsx_channel_address:'str',
        username:'str' = '',
        secret:'str' = '',
    ) -> 'stranydict':

        config = {}
        config['name'] = 'test_connect_ok'
        config['username'] = username
        config['secret'] = secret
        config['pool_size'] = 1
        config['is_zato'] = True
        config['is_active'] = True
        config['needs_spawn'] = False
        config['queue_build_cap'] = 30
        config['subscription_list'] = ''
        config['has_auto_reconnect'] = False

        config['auth_url'] = config['address'] = wsx_channel_address

        return config

# ################################################################################################################################

    def xtest_connect_ok_no_credentials_needed(self) -> 'None':

        with WSXChannelManager(self) as wsx_channel_address:

            config = self._get_config(wsx_channel_address)

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

    def test_connect_ok_credentials_needed(self) -> 'None':

        now = fs_safe_now()

        username = 'test.wsx.username.{}'.format(now)
        password = 'test.wsx.password.{}.{}'.format(now, uuid4().hex)

        with WSXChannelManager(self, username, password, needs_credentials=True) as ctx:

            config = self._get_config(ctx.wsx_channel_address, username, password)

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()

            outconn_wsx_queue = wrapper.client.queue.queue
            self.assertEqual(len(outconn_wsx_queue), 1)

            impl = outconn_wsx_queue[0].impl
            zato_client = impl._zato_client # type: _ZatoWSXClientImpl

            zato_client

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
