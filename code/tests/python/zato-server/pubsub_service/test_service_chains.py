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

_delivery_poll_timeout  = 45
_delivery_poll_interval = 2.0

# ################################################################################################################################
# ################################################################################################################################

class TestServiceChains(unittest.TestCase):

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = ZatoClient(TestConfig.base_url, TestConfig.password)

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.client.invoke('test.pubsub.clear-chain-received')

# ################################################################################################################################

    def _poll_chain_received(self, field:'str', expected_count:'int'=1) -> 'dict':
        """ Polls get-chain-received until the specified field reaches expected_count.
        """

        deadline = time.monotonic() + _delivery_poll_timeout

        while time.monotonic() < deadline:
            raw = self.client.invoke('test.pubsub.get-chain-received')
            result = json.loads(raw) if isinstance(raw, str) else raw

            if result[field] >= expected_count:
                return result

            time.sleep(_delivery_poll_interval)

        raw = self.client.invoke('test.pubsub.get-chain-received')
        result = json.loads(raw) if isinstance(raw, str) else raw
        return result

# ################################################################################################################################

    def test_two_hop_chain(self) -> 'None':
        """ Publishing to chain-a delivers through chain-b with both suffixes appended.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.chain-a',
            'data': 'hello',
        })

        result = self._poll_chain_received('chain_count', 1)

        self.assertGreaterEqual(result['chain_count'], 1, 'chain-b should have received at least one message')
        self.assertIn('hello-via-a-via-b', result['chain'][0])

# ################################################################################################################################

    def test_fanout_to_two_services(self) -> 'None':
        """ Publishing to fanout-source delivers to both target-1 and target-2.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.fanout-source',
            'data': 'fan-msg',
        })

        result = self._poll_chain_received('fanout_1_count', 1)

        self.assertGreaterEqual(result['fanout_1_count'], 1, 'fanout-target-1 should have received a message')
        self.assertGreaterEqual(result['fanout_2_count'], 1, 'fanout-target-2 should have received a message')

# ################################################################################################################################

    def test_typed_model_through_chain(self) -> 'None':
        """ A CustomerInput dict published through typed-chain-source arrives parsed at the typed sink.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.typed-chain-source',
            'data': {'customer_name': 'Chain Corp', 'customer_id': 99},
        })

        result = self._poll_chain_received('typed_chain_count', 1)

        self.assertGreaterEqual(result['typed_chain_count'], 1, 'typed-chain-sink should have received a message')

        received_str = result['typed_chain'][0]
        self.assertIn('Chain Corp', received_str)
        self.assertIn('99', received_str)

# ################################################################################################################################

    def test_z_chain_creates_two_implicit_topics(self) -> 'None':
        """ After a two-hop chain, both implicit topics exist in Redis.
        """

        # .. trigger the chain ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.chain-a',
            'data': 'topic-check',
        })

        # .. wait for delivery to complete ..
        _ = self._poll_chain_received('chain_count', 1)

        # .. give Redis a moment ..
        time.sleep(1)

        raw = self.client.invoke('test.pubsub.check-redis-topics')
        result = json.loads(raw) if isinstance(raw, str) else raw
        topics = result['topics']

        self.assertIn('zato.s.to.test.pubsub.chain-a', topics)
        self.assertIn('zato.s.to.test.pubsub.chain-b', topics)

# ################################################################################################################################

    def test_z_fanout_creates_three_implicit_topics(self) -> 'None':
        """ After a fanout, three implicit topics exist (source + two targets).
        """

        # .. trigger the fanout ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': 'test.pubsub.fanout-source',
            'data': 'topic-check-fanout',
        })

        # .. wait for delivery ..
        _ = self._poll_chain_received('fanout_1_count', 1)

        # .. give Redis a moment ..
        time.sleep(1)

        raw = self.client.invoke('test.pubsub.check-redis-topics')
        result = json.loads(raw) if isinstance(raw, str) else raw
        topics = result['topics']

        self.assertIn('zato.s.to.test.pubsub.fanout-source', topics)
        self.assertIn('zato.s.to.test.pubsub.fanout-target-1', topics)
        self.assertIn('zato.s.to.test.pubsub.fanout-target-2', topics)

# ################################################################################################################################
# ################################################################################################################################
