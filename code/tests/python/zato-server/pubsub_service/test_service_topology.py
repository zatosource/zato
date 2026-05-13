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
_pad = 5

def _service_name(number:'int') -> 'str':
    out = f'service-{number:0{_pad}d}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestServiceTopology(unittest.TestCase):

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = ZatoClient(TestConfig.base_url, TestConfig.password)

        # .. wipe all service Redis streams and server caches from any previous run ..
        _ = class_.client.invoke('test.pubsub.reset-service-streams')

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.client.invoke('test.pubsub.clear-service-received')

# ################################################################################################################################

    def _poll_service_received(self, field:'str', expected_count:'int'=1, timeout:'int'=0) -> 'dict':
        """ Polls get-service-received until the specified field reaches expected_count.
        """

        effective_timeout = timeout if timeout else _delivery_poll_timeout
        deadline = time.monotonic() + effective_timeout

        while time.monotonic() < deadline:
            raw = self.client.invoke('test.pubsub.get-service-received')
            result = json.loads(raw) if isinstance(raw, str) else raw

            if result[field] >= expected_count:
                return result

            time.sleep(_delivery_poll_interval)

        raw = self.client.invoke('test.pubsub.get-service-received')
        result = json.loads(raw) if isinstance(raw, str) else raw
        return result

# ################################################################################################################################

    def test_linear_five_hop_chain(self) -> 'None':
        """ Publishing to service-00001 delivers through all five hops to service-00005.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(1)}',
            'data': 'ping',
        })

        sink = _service_name(5)
        result = self._poll_service_received(f'{sink}_count', 1)

        self.assertGreaterEqual(result[f'{sink}_count'], 1, f'{sink} should have received at least one message')
        self.assertIn('ping-via-00001-via-00002-via-00003-via-00004-via-00005', result[sink][0])

# ################################################################################################################################

    def test_fanout_one_to_four(self) -> 'None':
        """ Publishing to service-00006 delivers to all four fanout targets.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(6)}',
            'data': 'broadcast',
        })

        result = self._poll_service_received(f'{_service_name(7)}_count', 1)

        for number in [7, 8, 9, 10]:
            name = _service_name(number)
            self.assertGreaterEqual(result[f'{name}_count'], 1, f'{name} should have received a message')

        self.assertIn(f'broadcast-via-00006-via-00007', result[_service_name(7)][0])
        self.assertIn(f'broadcast-via-00006-via-00008', result[_service_name(8)][0])
        self.assertIn(f'broadcast-via-00006-via-00009', result[_service_name(9)][0])
        self.assertIn(f'broadcast-via-00006-via-00010', result[_service_name(10)][0])

# ################################################################################################################################

    def test_fanin_four_to_one(self) -> 'None':
        """ Publishing to each of service-00011 through service-00014 delivers all four to service-00015.
        """

        for number in [11, 12, 13, 14]:
            _ = self.client.invoke('test.pubsub.publish-to-service', {
                'topic_name': f'test.pubsub.{_service_name(number)}',
                'data': f'src-{number}',
            })

        sink = _service_name(15)
        result = self._poll_service_received(f'{sink}_count', 4)

        self.assertGreaterEqual(result[f'{sink}_count'], 4, f'{sink} should have received at least four messages')

        # .. verify all four sources contributed ..
        all_received = ' '.join(result[sink])
        self.assertIn('-via-00011', all_received)
        self.assertIn('-via-00012', all_received)
        self.assertIn('-via-00013', all_received)
        self.assertIn('-via-00014', all_received)

# ################################################################################################################################

    def test_diamond_merge(self) -> 'None':
        """ Publishing to service-00016 delivers through both arms of the diamond to service-00019.
        """

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(16)}',
            'data': 'diamond',
        })

        sink = _service_name(19)
        result = self._poll_service_received(f'{sink}_count', 2)

        self.assertGreaterEqual(result[f'{sink}_count'], 2, f'{sink} should have received at least two messages')

        # .. verify both arms of the diamond ..
        all_received = ' '.join(result[sink])
        self.assertIn('diamond-via-00016-via-00017-via-00019', all_received)
        self.assertIn('diamond-via-00016-via-00018-via-00019', all_received)

# ################################################################################################################################

    def test_ring_with_ttl(self) -> 'None':
        """ Publishing to service-00020 with ttl=3 loops three times before storing the result.
        """

        ring = _service_name(20)

        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{ring}',
            'data': '{"data":"loop","ttl":3}',
        })

        result = self._poll_service_received(f'{ring}_count', 1)

        self.assertGreaterEqual(result[f'{ring}_count'], 1, f'{ring} should have stored the final result')

        # .. the data should have three -via-00020 suffixes appended ..
        received = result[ring][0]
        self.assertEqual(received.count('-via-00020'), 3)
        self.assertIn('loop', received)

# ################################################################################################################################

    def test_parallel_three_hundred_sinks(self) -> 'None':
        """ Publishes one message to each of service-00021 through service-00320 and verifies
        all 300 services receive their message in parallel.
        """

        for number in range(21, 321):
            name = _service_name(number)
            _ = self.client.invoke('test.pubsub.publish-to-service', {
                'topic_name': f'test.pubsub.{name}',
                'data': f'parallel-{number}',
            })

        # .. wait for every sink to receive its message, using a longer timeout
        # .. because 300 greenlets need time to set up and deliver ..
        for number in range(21, 321):
            name = _service_name(number)
            field = f'{name}_count'
            result = self._poll_service_received(field, 1, timeout=90)
            self.assertGreaterEqual(result[field], 1, f'{name} should have received at least one message')

        # .. verify data correctness for each ..
        raw = self.client.invoke('test.pubsub.get-service-received')
        result = json.loads(raw) if isinstance(raw, str) else raw

        for number in range(21, 321):
            name = _service_name(number)
            padded = f'{number:0{_pad}d}'
            expected_suffix = f'-via-{padded}'
            received_item = result[name][0]
            self.assertIn(f'parallel-{number}', received_item)
            self.assertIn(expected_suffix, received_item)

# ################################################################################################################################

    def test_z_all_twenty_topics_created(self) -> 'None':
        """ After running all topology tests, all 20 service topics exist in Redis.
        """

        # .. trigger any remaining topologies that may not have been tested yet ..
        # .. the linear chain covers service-00001 through service-00005 ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(1)}',
            'data': 'topic-check',
        })

        # .. fanout covers service-00006 through service-00010 ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(6)}',
            'data': 'topic-check',
        })

        # .. fan-in covers service-00011 through service-00015 ..
        for number in [11, 12, 13, 14]:
            _ = self.client.invoke('test.pubsub.publish-to-service', {
                'topic_name': f'test.pubsub.{_service_name(number)}',
                'data': 'topic-check',
            })

        # .. diamond covers service-00016 through service-00019 ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(16)}',
            'data': 'topic-check',
        })

        # .. ring covers service-00020 ..
        _ = self.client.invoke('test.pubsub.publish-to-service', {
            'topic_name': f'test.pubsub.{_service_name(20)}',
            'data': '{"data":"topic-check","ttl":1}',
        })

        # .. wait for all deliveries to complete ..
        _ = self._poll_service_received(f'{_service_name(5)}_count', 1)
        _ = self._poll_service_received(f'{_service_name(7)}_count', 1)
        _ = self._poll_service_received(f'{_service_name(15)}_count', 1)
        _ = self._poll_service_received(f'{_service_name(19)}_count', 1)
        _ = self._poll_service_received(f'{_service_name(20)}_count', 1)

        time.sleep(1)

        raw = self.client.invoke('test.pubsub.check-redis-topics')
        result = json.loads(raw) if isinstance(raw, str) else raw
        topics = result['topics']

        for number in range(1, 21):
            topic_name = f'zato.s.to.test.pubsub.{_service_name(number)}'
            self.assertIn(topic_name, topics, f'{topic_name} should exist in Redis')

# ################################################################################################################################
# ################################################################################################################################
