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

    def test_pubsub_get_topics_service_was_called(self) -> 'None':

        run_cli = False
        queue_build_cap = 0.1
        wsx_channel_address = 'ws://zato-invalid-test:1234'

        with WSXChannelManager(self, run_cli=run_cli) as ctx:

            ctx = ctx

            config = self._get_config(
                'test_pubsub_get_topics_service',
                wsx_channel_address,
                queue_build_cap=queue_build_cap,
            )

            config['max_connect_attempts'] = 1

            wrapper = OutconnWSXWrapper(config, None) # type: ignore
            wrapper.build_queue()

            # Confirm that the client is connected
            # self._check_connection_result(
            #    wrapper, ctx.wsx_channel_address, needs_credentials=False, should_be_authenticated=True)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
