# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to run as soon as possible
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
from unittest import main
from uuid import uuid4

# Zato
from zato.common.test.wsx_ import WSXChannelManager, WSXOutconnBaseCase
from zato.common.util.api import fs_safe_now
from zato.server.generic.api.outconn.wsx.base import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnConnectTestCase(WSXOutconnBaseCase):

    def test_connect_credentials_needed_not_needed(self) -> 'None':

        with WSXChannelManager(self) as ctx:

            config = self._get_config(
                'test_connect_credentials_needed_not_needed',
                ctx.wsx_channel_address
            )

            wrapper = OutconnWSXWrapper(config, self._get_test_server()) # type: ignore
            wrapper.build_queue()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=True)

# ################################################################################################################################

    def test_connect_credentials_needed_and_provided(self) -> 'None':

        now = fs_safe_now()

        username = 'test.wsx.username.{}'.format(now)
        password = 'test.wsx.password.{}.{}'.format(now, uuid4().hex)

        with WSXChannelManager(self, username, password, needs_credentials=True) as ctx:

            config = self._get_config(
                'test_connect_credentials_needed_and_provided',
                ctx.wsx_channel_address,
                username,
                password
            )

            wrapper = OutconnWSXWrapper(config, self._get_test_server()) # type: ignore
            wrapper.build_queue()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=True, should_be_authenticated=True)

# ################################################################################################################################

    def test_connect_credentials_needed_and_not_provided(self) -> 'None':

        now = fs_safe_now()

        username = 'test.wsx.username.{}'.format(now)
        password = 'test.wsx.password.{}.{}'.format(now, uuid4().hex)

        with WSXChannelManager(self, username, password, needs_credentials=True) as ctx:

            # Note that we are not providing our credentials here,
            # which means that will be attempting to connect without credentials
            # to a channel with a security definition attached and that should fail
            config = self._get_config(
                'test_connect_credentials_needed_and_not_provided',
                ctx.wsx_channel_address,
                queue_build_cap=1
            )

            wrapper = OutconnWSXWrapper(config, self._get_test_server()) # type: ignore
            wrapper.build_queue()
            wrapper.delete_queue_connections()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=False)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
