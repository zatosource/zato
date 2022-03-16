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

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class Config:
    OnSubscribeServiceID   = 123
    OnSubscribeServiceName = 'zato.test.on-subscribe'
    SubscribeToTopics = ['/zato/test/pubsub1', '/zato/test/pubsub2']

# ################################################################################################################################
# ################################################################################################################################

class TestServer:
    def __init__(self) -> 'None':
        self.ctx = []

# ################################################################################################################################

    def api_service_store_get_service_name_by_id(self, service_id:'int') -> 'str':
        self.ctx.append({
            'api_service_store_get_service_name_by_id':service_id
        })
        return Config.OnSubscribeServiceName

# ################################################################################################################################

    def invoke(self, service_name:'str') -> 'strlist':
        self.ctx.append({
            'invoke': service_name
        })
        return Config.SubscribeToTopics

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnPubSubTestCase(WSXOutconnBaseCase):

    def test_pubsub_get_topics_service_was_called(self) -> 'None':

        run_cli = True
        server = TestServer()
        queue_build_cap = 0.1

        with WSXChannelManager(self, run_cli=run_cli) as ctx:

            ctx = ctx

            config = self._get_config(
                'test_pubsub_get_topics_service',
                ctx.wsx_channel_address,
                queue_build_cap=queue_build_cap,
            )

            config['max_connect_attempts'] = 1
            config['on_subscribe_service_id'] = Config.OnSubscribeServiceID

            wrapper = OutconnWSXWrapper(config, server) # type: ignore
            wrapper.build_queue()

            # Confirm that the client invoked the expected subscription service.
            self.assertEqual(len(server.ctx), 2)

            ctx0 = server.ctx[0]
            ctx1 = server.ctx[1]

            self.assertDictEqual(ctx0, {
                'api_service_store_get_service_name_by_id': Config.OnSubscribeServiceID,
            })

            self.assertDictEqual(ctx1, {
                'invoke': Config.OnSubscribeServiceName,
            })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
