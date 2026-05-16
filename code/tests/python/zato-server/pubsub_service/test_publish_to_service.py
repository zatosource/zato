# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
import unittest

# local
from _client import ZatoClient
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

_delivery_poll_timeout  = 10
_delivery_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

class TestPublishToService(unittest.TestCase):

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = ZatoClient(TestConfig.base_url, TestConfig.password)

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.client.invoke('test.pubsub.clear-received')

# ################################################################################################################################

    def _wait_for_simple_delivery(self, expected_count:'int'=1) -> 'dict':
        """ Polls the get-received service until the expected number of simple messages arrive.
        """

        deadline = time.monotonic() + _delivery_poll_timeout

        while time.monotonic() < deadline:
            raw = self.client.invoke('test.pubsub.get-received')
            result = json.loads(raw) if isinstance(raw, str) else raw

            simple_count = result['simple_count']
            if simple_count >= expected_count:
                return result

            time.sleep(_delivery_poll_interval)

        raw = self.client.invoke('test.pubsub.get-received')
        result = json.loads(raw) if isinstance(raw, str) else raw
        return result

# ################################################################################################################################

    def _wait_for_typed_delivery(self, expected_count:'int'=1) -> 'dict':
        """ Polls the get-received service until the expected number of typed messages arrive.
        """

        deadline = time.monotonic() + _delivery_poll_timeout

        while time.monotonic() < deadline:
            raw = self.client.invoke('test.pubsub.get-received')
            result = json.loads(raw) if isinstance(raw, str) else raw

            typed_count = result['typed_count']
            if typed_count >= expected_count:
                return result

            time.sleep(_delivery_poll_interval)

        raw = self.client.invoke('test.pubsub.get-received')
        result = json.loads(raw) if isinstance(raw, str) else raw
        return result

# ################################################################################################################################

    def test_publish_to_simple_service(self) -> 'None':
        """ Publishing to a simple service by name delivers the message to that service.
        """

        # Publish via the facade ..
        publish_result = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.simple-receiver',
            'data': 'hello from test',
        })

        publish_data = json.loads(publish_result) if isinstance(publish_result, str) else publish_result
        self.assertIn('msg_id', publish_data)

        # .. wait for delivery ..
        received = self._wait_for_simple_delivery()

        self.assertGreaterEqual(received['simple_count'], 1, 'Simple receiver should have received at least one message')

# ################################################################################################################################

    def test_publish_to_typed_service(self) -> 'None':
        """ Publishing a dict to a typed service delivers the data parsed against the input model.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.typed-receiver',
            'data': {'customer_name': 'Test Corp', 'customer_id': 42},
        })

        received = self._wait_for_typed_delivery()

        self.assertGreaterEqual(received['typed_count'], 1, 'Typed receiver should have received at least one message')

# ################################################################################################################################

    def test_implicit_topic_created(self) -> 'None':
        """ After publishing to a service, the implicit zato.s.to.{name} topic exists in Redis.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.simple-receiver',
            'data': 'topic creation test',
        })

        # .. give Redis a moment to process ..
        time.sleep(1)

        raw = self.client.invoke('test.pubsub.check-redis-topics')
        result = json.loads(raw) if isinstance(raw, str) else raw
        topics = result['topics']

        expected_topic = 'zato.s.to.test.pubsub.simple-receiver'

        self.assertIn(expected_topic, topics)

# ################################################################################################################################

    def test_second_publish_reuses_topic(self) -> 'None':
        """ Publishing twice to the same service does not create a second subscription.
        """

        # Publish twice ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.simple-receiver',
            'data': 'first message',
        })

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.simple-receiver',
            'data': 'second message',
        })

        # .. check subscriptions ..
        raw = self.client.invoke('test.pubsub.check-subscriptions')
        result = json.loads(raw) if isinstance(raw, str) else raw

        # .. there should be exactly one sub_key for simple-receiver ..
        expected_sub_key = 'zato.service.test.pubsub.simple-receiver'

        matching_keys = []

        for key in result['sub_keys']:
            if key == expected_sub_key:
                matching_keys.append(key)

        matching_count = len(matching_keys)
        self.assertEqual(matching_count, 1, f'Expected exactly one subscription for simple-receiver, got {matching_count}')

# ################################################################################################################################

    def test_publish_to_nonexistent_service(self) -> 'None':
        """ Publishing to a name that is not a known service treats it as a regular topic.
        """

        # This name is not a deployed service ..
        publish_result = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'not.a.real.service.name',
            'data': 'should go to regular topic',
        })

        publish_data = json.loads(publish_result) if isinstance(publish_result, str) else publish_result

        # .. publish should still succeed (regular topic auto-creates the stream) ..
        self.assertIn('msg_id', publish_data)

        # .. but no service subscription should be created for this name ..
        raw = self.client.invoke('test.pubsub.check-subscriptions')
        result = json.loads(raw) if isinstance(raw, str) else raw

        unexpected_sub_key = 'zato.service.not.a.real.service.name'

        self.assertNotIn(unexpected_sub_key, result['sub_keys'])

# ################################################################################################################################
# ################################################################################################################################
