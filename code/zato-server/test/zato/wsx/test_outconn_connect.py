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
        queue_build_cap:'int' = 30
    ) -> 'stranydict':

        config = {}
        config['name'] = 'test_connect_ok'
        config['username'] = username
        config['secret'] = secret
        config['pool_size'] = 1
        config['is_zato'] = True
        config['is_active'] = True
        config['needs_spawn'] = False
        config['queue_build_cap'] = queue_build_cap
        config['subscription_list'] = ''
        config['has_auto_reconnect'] = False

        config['auth_url'] = config['address'] = wsx_channel_address

        return config

# ################################################################################################################################

    def _check_connection_result(
        self,
        wrapper:'OutconnWSXWrapper',
        wsx_channel_address:'str',
        *,
        needs_credentials:'bool',
        should_be_authenticated:'bool',
    ) -> 'None':

        outconn_wsx_queue = wrapper.client.queue.queue
        self.assertEqual(len(outconn_wsx_queue), 1)

        impl = outconn_wsx_queue[0].impl
        zato_client = impl._zato_client # type: _ZatoWSXClientImpl

        self.assertEqual(zato_client.config.address, wsx_channel_address)

        if should_be_authenticated:
            self.assertTrue(zato_client.auth_token.startswith('zwsxt'))
            self.assertTrue(zato_client.is_connected)
            self.assertTrue(zato_client.is_authenticated)
            self.assertTrue(zato_client.keep_running)
        else:
            self.assertEqual(zato_client.auth_token, '')
            self.assertFalse(zato_client.is_connected)
            self.assertFalse(zato_client.is_authenticated)
            self.assertFalse(zato_client.keep_running)

        if needs_credentials:
            self.assertTrue(zato_client.needs_auth)
            self.assertTrue(zato_client.is_auth_needed)
        else:
            self.assertFalse(zato_client.needs_auth)
            self.assertFalse(zato_client.is_auth_needed)

# ################################################################################################################################

    def test_connect_credentials_needed_not_needed(self) -> 'None':

        with WSXChannelManager(self) as ctx:

            config = self._get_config(ctx.wsx_channel_address)

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=True)

# ################################################################################################################################

    def xtest_connect_credentials_needed_and_provided(self) -> 'None':

        now = fs_safe_now()

        username = 'test.wsx.username.{}'.format(now)
        password = 'test.wsx.password.{}.{}'.format(now, uuid4().hex)

        with WSXChannelManager(self, username, password, needs_credentials=True) as ctx:

            config = self._get_config(ctx.wsx_channel_address, username, password)

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=True, should_be_authenticated=True)

# ################################################################################################################################

    def xtest_connect_credentials_needed_and_not_provided(self) -> 'None':

        now = fs_safe_now()

        username = 'test.wsx.username.{}'.format(now)
        password = 'test.wsx.password.{}.{}'.format(now, uuid4().hex)

        with WSXChannelManager(self, username, password, needs_credentials=True) as ctx:

            # Note that we are not providing our credentials here,
            # which means that will be attempting to connect without credentials
            # to a channel with a security definition attached and that should fail
            config = self._get_config(ctx.wsx_channel_address, queue_build_cap=1)

            wrapper = OutconnWSXWrapper(config, None)
            wrapper.build_queue()
            wrapper.delete_queue_connections()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=False)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
