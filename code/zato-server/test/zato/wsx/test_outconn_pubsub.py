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
from zato.common.test.wsx_ import WSXChannelManager, WSXOutconnBaseCase
from zato.server.generic.api.outconn_wsx import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnPubSubTestCase(WSXOutconnBaseCase):

    def test_pubsub_get_topics_service(self) -> 'None':

        with WSXChannelManager(self) as ctx:

            config = self._get_config(
                'test_pubsub_get_topics_service',
                ctx.wsx_channel_address
            )

            wrapper = OutconnWSXWrapper(config, None) # type: ignore
            wrapper.build_queue()

            # Confirm that the client is connected
            self._check_connection_result(
                wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=True)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
