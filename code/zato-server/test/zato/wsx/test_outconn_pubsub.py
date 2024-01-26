# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to run as soon as possible
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
from unittest import main

# Zato
from zato.common.api import GENERIC
from zato.common.test.wsx_ import WSXChannelManager, WSXOutconnBaseCase
from zato.common.typing_ import cast_
from zato.common.util.api import fs_safe_now
from zato.distlock import LockManager
from zato.server.connection.pool_wrapper import ConnectionPoolWrapper
from zato.server.generic.api.outconn.wsx.base import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class Config:
    OnSubscribeServiceID   = 123
    OnSubscribeServiceName = 'zato.test.on-subscribe'
    SubscribeToTopics = ['/test1', '/test2']

# ################################################################################################################################
# ################################################################################################################################

class TestServer:
    def __init__(self, topics:'strlist') -> 'None':
        self.topics = topics
        self.ctx = []
        self.zato_lock_manager = LockManager('zato-pass-through', 'zato', cast_('any_', None))
        self.wsx_connection_pool_wrapper = ConnectionPoolWrapper(cast_('any_', self), GENERIC.CONNECTION.TYPE.OUTCONN_WSX)

# ################################################################################################################################

    def is_service_wsx_adapter(self, _ignored_service_name:'str') -> 'bool':
        return True

# ################################################################################################################################

    def is_active_outconn_wsx(self, _ignored_conn_id:'str') -> 'bool':
        return True

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
        return self.topics

# ################################################################################################################################

    def on_wsx_outconn_stopped_running(self, conn_id:'str') -> 'None':
        pass

# ################################################################################################################################

    def on_wsx_outconn_connected(self, conn_id:'str') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnPubSubTestCase(WSXOutconnBaseCase):

    def test_pubsub_on_subscribe_service(self) -> 'None':

        now = fs_safe_now()

        topic1 = f'/wsx.pubsub.test.{now}.1'
        topic2 = f'/wsx.pubsub.test.{now}.2'

        topics = [topic1, topic2]

        run_cli = True
        server = TestServer(topics)

        with WSXChannelManager(self, needs_pubsub=True, run_cli=run_cli, topics=topics) as ctx:

            config = self._get_config(
                'test_pubsub_on_subscribe_service',
                ctx.wsx_channel_address,
            )

            # config['max_connect_attempts'] = 1
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
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
