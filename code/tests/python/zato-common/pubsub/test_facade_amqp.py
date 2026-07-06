# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.api import PubSub
from zato.common.facade import PubSubFacade, _service_topic_prefix
from zato.common.pubsub.redis_backend import PublishResult
from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManagerStub:
    """ Runs the real backend registry and AMQP publish code of ConfigManager
    with everything around it mocked out.
    """

    # The real methods under test, bound to this stub
    get_pubsub_topic_backend = ConfigManager.get_pubsub_topic_backend
    pubsub_publish_to_amqp = ConfigManager.pubsub_publish_to_amqp

    def __init__(self) -> 'None':
        self._topic_backends = {}
        self._service_topic_cache = set()
        self._service_topic_lock = threading.RLock()
        self._push_subs = {}
        self.amqp_invoke = MagicMock()

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubFacadeAMQPRouting(unittest.TestCase):

    def setUp(self) -> 'None':

        # Build a mock server whose config manager runs the real routing code ..
        self.server = MagicMock()
        self.config_manager = _ConfigManagerStub()
        self.server.config_manager = self.config_manager

        # .. no known services, all names are topics ..
        self.server.service_store.name_to_impl_name = {}

        # .. an AMQP-backed topic in the registry ..
        self.backend_config = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': 'my.outconn',
            'amqp_exchange': 'my.exchange',
            'amqp_routing_key': 'my.routing.key',
            'amqp_channel_name': '',
            'original_service_name': '',
        }
        self.config_manager._topic_backends['topic.amqp'] = self.backend_config

        # .. the built-in Redis backend returns its own result ..
        redis_result = PublishResult()
        redis_result.msg_id = 'redis-msg-001'
        self.server.pubsub_redis.publish.return_value = redis_result

        self.facade = PubSubFacade(self.server, 'test.service')

# ################################################################################################################################

    def test_amqp_topic_routes_to_amqp_invoke(self) -> 'None':
        """ An AMQP-backed topic goes to amqp_invoke with the configured
        outconn name, exchange, routing key and the given data.
        """
        _ = self.facade.publish('topic.amqp', 'amqp data')

        self.config_manager.amqp_invoke.assert_called_once_with(
            'my.outconn',
            'amqp data',
            exchange='my.exchange',
            routing_key='my.routing.key',
        )

        # The built-in backend is not involved at all
        self.server.pubsub_redis.publish.assert_not_called()

# ################################################################################################################################

    def test_amqp_topic_returns_publish_result_with_msg_id(self) -> 'None':
        """ The AMQP path returns a PublishResult with a msg_id
        in the standard format, shape identical to the built-in path.
        """
        out = self.facade.publish('topic.amqp', 'amqp data')

        self.assertIsInstance(out, PublishResult)
        self.assertTrue(out.msg_id.startswith('zpsm.'))

# ################################################################################################################################

    def test_builtin_topic_goes_to_redis(self) -> 'None':
        """ A topic absent from the registry goes to pubsub_redis.publish
        with unchanged arguments, amqp_invoke is not called.
        """
        out = self.facade.publish('topic.builtin', 'builtin data', priority=7)

        call_args = self.server.pubsub_redis.publish.call_args

        self.assertEqual(call_args[0][0], 'topic.builtin')
        self.assertEqual(call_args[0][1], 'builtin data')
        self.assertEqual(call_args[1]['priority'], 7)
        self.assertEqual(call_args[1]['publisher'], 'test.service')

        self.config_manager.amqp_invoke.assert_not_called()

        self.assertEqual(out.msg_id, 'redis-msg-001')

# ################################################################################################################################

    def test_service_auto_topics_stay_builtin(self) -> 'None':
        """ A zato.s.to.* topic name goes builtin even when
        the registry contains an entry for it.
        """
        service_topic = _service_topic_prefix + 'some.service'
        self.config_manager._topic_backends[service_topic] = self.backend_config

        _ = self.facade.publish(service_topic, 'service data')

        self.config_manager.amqp_invoke.assert_not_called()

        call_args = self.server.pubsub_redis.publish.call_args
        self.assertEqual(call_args[0][0], service_topic)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
