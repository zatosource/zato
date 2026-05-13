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
from zato.common.facade import PubSubFacade, _service_name_to_topic, _service_topic_prefix, _service_sub_key_prefix
from zato.common.pubsub.redis_backend import PublishResult

# ################################################################################################################################
# ################################################################################################################################

class TestServiceNameToTopic(unittest.TestCase):

    def test_transforms_service_name_to_topic(self) -> 'None':
        """ The transform prefixes the service name with the service topic prefix.
        """
        out = _service_name_to_topic('my.api.customer.new')
        self.assertEqual(out, 'zato.s.to.my.api.customer.new')

# ################################################################################################################################

    def test_prefix_is_preserved_for_simple_name(self) -> 'None':
        """ Even a single-segment name gets the prefix.
        """
        out = _service_name_to_topic('invoker')
        self.assertEqual(out, 'zato.s.to.invoker')

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubFacadePublish(unittest.TestCase):

    def setUp(self) -> 'None':

        # Build a mock server with the attributes that PubSubFacade.publish relies on ..
        self.server = MagicMock()
        self.server._service_topic_cache = set()
        self.server._service_topic_lock = threading.RLock()
        self.server._push_subs = {}

        # .. the service store knows about two services ..
        self.server.service_store.name_to_impl_name = {
            'my.api.customer.new': 'my_api_customer_new.MyApiCustomerNew',
            'my.api.order.create': 'my_api_order_create.MyApiOrderCreate',
        }

        # .. set up the Redis mock to return a PublishResult ..
        publish_result = PublishResult()
        publish_result.msg_id = 'test-message-id-001'
        self.server.pubsub_redis.publish.return_value = publish_result

        self.facade = PubSubFacade(self.server)

# ################################################################################################################################

    def test_publish_to_service_calls_subscribe(self) -> 'None':
        """ Publishing to a known service name triggers subscribe with the correct sub_key and topic.
        """
        self.facade.publish('my.api.customer.new', 'test data')

        expected_topic = _service_topic_prefix + 'my.api.customer.new'
        expected_sub_key = _service_sub_key_prefix + 'my.api.customer.new'

        self.server.pubsub_redis.subscribe.assert_called_once_with(expected_sub_key, expected_topic)

# ################################################################################################################################

    def test_publish_to_service_publishes_to_computed_topic(self) -> 'None':
        """ The message is published to the computed service topic, not the raw service name.
        """
        self.facade.publish('my.api.customer.new', 'test data')

        expected_topic = _service_topic_prefix + 'my.api.customer.new'
        call_args = self.server.pubsub_redis.publish.call_args

        self.assertEqual(call_args[0][0], expected_topic)
        self.assertEqual(call_args[0][1], 'test data')

# ################################################################################################################################

    def test_publish_to_unknown_name_uses_original_topic(self) -> 'None':
        """ Publishing to a name that is not a known service uses the original name as the topic.
        """
        self.facade.publish('customer.events.new', 'test data')

        self.server.pubsub_redis.subscribe.assert_not_called()

        call_args = self.server.pubsub_redis.publish.call_args

        self.assertEqual(call_args[0][0], 'customer.events.new')

# ################################################################################################################################

    def test_second_publish_does_not_subscribe_again(self) -> 'None':
        """ The second publish to the same service name reuses the cached setup.
        """
        self.facade.publish('my.api.customer.new', 'first message')
        self.facade.publish('my.api.customer.new', 'second message')

        self.server.pubsub_redis.subscribe.assert_called_once()

        publish_call_count = self.server.pubsub_redis.publish.call_count
        self.assertEqual(publish_call_count, 2)

# ################################################################################################################################

    def test_push_subs_populated_after_first_publish(self) -> 'None':
        """ After first publish to a service, _push_subs contains the correct entry.
        """
        self.facade.publish('my.api.customer.new', 'test data')

        expected_sub_key = _service_sub_key_prefix + 'my.api.customer.new'
        expected_topic = _service_topic_prefix + 'my.api.customer.new'

        self.assertIn(expected_sub_key, self.server._push_subs)

        config_list = self.server._push_subs[expected_sub_key]
        config_list_len = len(config_list)

        self.assertEqual(config_list_len, 1)

        config = config_list[0]

        self.assertEqual(config['sub_key'], expected_sub_key)
        self.assertEqual(config['topic_name'], expected_topic)
        self.assertEqual(config['push_type'], 'service')
        self.assertEqual(config['push_service_name'], 'my.api.customer.new')

# ################################################################################################################################

    def test_service_topic_cache_updated(self) -> 'None':
        """ The service topic cache contains the service name after publish.
        """
        self.facade.publish('my.api.customer.new', 'test data')

        self.assertIn('my.api.customer.new', self.server._service_topic_cache)

# ################################################################################################################################

    def test_two_different_services_get_separate_subscriptions(self) -> 'None':
        """ Publishing to two different services creates separate subscriptions.
        """
        self.facade.publish('my.api.customer.new', 'customer data')
        self.facade.publish('my.api.order.create', 'order data')

        subscribe_call_count = self.server.pubsub_redis.subscribe.call_count
        self.assertEqual(subscribe_call_count, 2)

        sub_key_customer = _service_sub_key_prefix + 'my.api.customer.new'
        sub_key_order = _service_sub_key_prefix + 'my.api.order.create'

        self.assertIn(sub_key_customer, self.server._push_subs)
        self.assertIn(sub_key_order, self.server._push_subs)

# ################################################################################################################################

    def test_publish_returns_publish_result(self) -> 'None':
        """ Publish returns the PublishResult from the Redis backend.
        """
        out = self.facade.publish('my.api.customer.new', 'test data')

        self.assertIsInstance(out, PublishResult)
        self.assertEqual(out.msg_id, 'test-message-id-001')

# ################################################################################################################################

    def test_publish_passes_all_keyword_arguments(self) -> 'None':
        """ All optional keyword arguments are forwarded to the Redis backend.
        """
        self.facade.publish(
            'customer.events',
            'test data',
            priority=9,
            expiration=7200,
            correl_id='correl-123',
            in_reply_to='reply-456',
            ext_client_id='ext-789',
            publisher='test-publisher',
            pub_time='2026-05-13T12:00:00',
        )

        call_kwargs = self.server.pubsub_redis.publish.call_args[1]

        self.assertEqual(call_kwargs['priority'], 9)
        self.assertEqual(call_kwargs['expiration'], 7200)
        self.assertEqual(call_kwargs['correl_id'], 'correl-123')
        self.assertEqual(call_kwargs['in_reply_to'], 'reply-456')
        self.assertEqual(call_kwargs['ext_client_id'], 'ext-789')
        self.assertEqual(call_kwargs['publisher'], 'test-publisher')
        self.assertEqual(call_kwargs['pub_time'], '2026-05-13T12:00:00')

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubFacadePublishInputModel(unittest.TestCase):
    """ Tests that confirm how published data flows into a service's request.input.
    The actual parsing is done by the server.invoke pipeline (Request.init -> parse_input),
    so here we verify that the facade passes the data through unchanged.
    """

    def setUp(self) -> 'None':

        self.server = MagicMock()
        self.server._service_topic_cache = set()
        self.server._service_topic_lock = threading.RLock()
        self.server._push_subs = {}
        self.server.service_store.name_to_impl_name = {
            'my.typed.service': 'my_typed_service.MyTypedService',
        }

        publish_result = PublishResult()
        publish_result.msg_id = 'test-typed-msg-001'
        self.server.pubsub_redis.publish.return_value = publish_result

        self.facade = PubSubFacade(self.server)

# ################################################################################################################################

    def test_dict_data_passed_through_unchanged(self) -> 'None':
        """ A dict payload is forwarded to Redis backend exactly as provided.
        """
        input_data = {
            'customer_name': 'Test Corp',
            'customer_id': 42,
            'is_active': True,
        }

        self.facade.publish('my.typed.service', input_data)

        call_args = self.server.pubsub_redis.publish.call_args

        self.assertEqual(call_args[0][1], input_data)

# ################################################################################################################################

    def test_string_data_passed_through_unchanged(self) -> 'None':
        """ A plain string payload is forwarded exactly as provided.
        """
        self.facade.publish('my.typed.service', 'plain text message')

        call_args = self.server.pubsub_redis.publish.call_args

        self.assertEqual(call_args[0][1], 'plain text message')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
