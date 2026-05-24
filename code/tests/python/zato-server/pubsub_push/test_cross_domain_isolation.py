# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import threading
import time
import unittest

# local
from _client import PublishClient
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.cross_domain_isolation')

# ################################################################################################################################
# ################################################################################################################################

class TestCrossDomainIsolation(unittest.TestCase):
    """ Tests for cross-domain isolation - messages go only to their subscribed endpoints.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_publish_to_topic_a_delivers_nothing_to_endpoint_b(self) -> 'None':
        """ Publish a message to one topic, wait generously, verify that a different
        topic's receiver got zero deliveries.
        """

        source_topic = 'iam.user.created'
        unrelated_topic = 'order.shipped'

        source_receiver = TestConfig.endpoints[source_topic].receiver
        unrelated_receiver = TestConfig.endpoints[unrelated_topic].receiver

        # Publish a message to the source topic ..
        publish_data:'anydict' = {'user_id': 'isolation_test', 'source': 'test_cross_domain'}
        _ = self.publisher.publish(source_topic, publish_data)
        logger.info('Published to %s', source_topic)

        # .. wait for the source receiver to get its message ..
        delivery_timeout = 30.0
        source_messages = source_receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        source_count = len(source_messages)
        logger.info('Source receiver (%s) delivered %d message(s) -> %s', source_topic, source_count, source_messages)

        # .. verify the source got it ..
        self.assertEqual(source_count, 1)

        # .. now wait generously and check the unrelated receiver ..
        isolation_wait = 10.0
        time.sleep(isolation_wait)

        unrelated_messages = unrelated_receiver.get_delivered_messages()
        unrelated_count = len(unrelated_messages)
        logger.info('Unrelated receiver (%s) delivered %d message(s) -> %s', unrelated_topic, unrelated_count, unrelated_messages)

        # .. verify the unrelated endpoint got nothing.
        self.assertEqual(unrelated_count, 0)

# ################################################################################################################################

    def test_one_per_topic_delivers_exactly_one_to_each(self) -> 'None':
        """ Publish one unique message to each of the 10 configured topics,
        verify each receiver got exactly 1 message with the correct payload.
        """

        # Build a unique payload per topic ..
        topics_and_payloads:'list[tuple[str, anydict]]' = []

        for topic_name in TestConfig.endpoints:
            payload:'anydict' = {'topic': topic_name, 'marker': f'unique_{topic_name}'}
            topics_and_payloads.append((topic_name, payload))

        # Publish one message to each topic ..
        for topic_name, payload in topics_and_payloads:
            _ = self.publisher.publish(topic_name, payload)

        topic_count = len(topics_and_payloads)
        logger.info('Published 1 message to each of %d topics', topic_count)

        # .. wait for each receiver to get its message and verify ..
        delivery_timeout = 30.0

        for topic_name, expected_payload in topics_and_payloads:
            receiver = TestConfig.endpoints[topic_name].receiver
            messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
            delivered_count = len(messages)
            logger.info('Receiver for %s delivered %d message(s) -> %s', topic_name, delivered_count, messages)

            # .. exactly 1 message ..
            self.assertEqual(delivered_count, 1)

            # .. verify payload matches (no cross-contamination) ..
            message = messages[0]
            received_data = message['data']

            if isinstance(received_data, str):
                received_data = json.loads(received_data)

            expected_marker = expected_payload['marker']
            received_marker = received_data['marker']
            logger.info('Expected marker -> %s, received -> %s', expected_marker, received_marker)
            self.assertEqual(received_marker, expected_marker)

# ################################################################################################################################

    def test_single_publish_no_duplicate_after_generous_wait(self) -> 'None':
        """ Publish a single message to one topic, wait for delivery,
        then wait an additional 30 seconds and verify still exactly 1 delivery.
        """

        topic_name = 'iam.role.assigned'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Publish a single message ..
        publish_data:'anydict' = {'role': 'admin', 'source': 'test_no_dup_single'}
        _ = self.publisher.publish(topic_name, publish_data)
        logger.info('Published 1 message to %s', topic_name)

        # .. wait for the delivery ..
        delivery_timeout = 30.0
        messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        self.assertEqual(delivered_count, 1)

        # .. wait generously to confirm no re-delivery ..
        generous_wait = 30.0
        time.sleep(generous_wait)

        all_messages = receiver.get_delivered_messages()
        final_count = len(all_messages)
        logger.info('Final count after %s second wait -> %d message(s) -> %s', generous_wait, final_count, all_messages)

        # .. verify still exactly 1.
        self.assertEqual(final_count, 1)

# ################################################################################################################################

    def test_concurrent_publishes_from_threads(self) -> 'None':
        """ Spawn 10 threads each publishing one message to the same topic,
        wait for all to be delivered, verify all 10 arrived with unique msg_ids.
        """

        topic_name = 'iam.password.changed'
        receiver = TestConfig.endpoints[topic_name].receiver
        thread_count = 10
        errors:'list[str]' = []

        # Each thread publishes one message ..
        def _publish_one(idx:'int') -> 'None':
            try:
                payload:'anydict' = {'thread_idx': idx, 'source': 'test_concurrent'}
                _ = self.publisher.publish(topic_name, payload)
            except Exception as exc:
                errors.append(f'Thread {idx} failed: {exc}')

        # Spawn all threads ..
        threads:'list[threading.Thread]' = []

        for idx in range(thread_count):
            thread = threading.Thread(target=_publish_one, args=(idx,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        logger.info('All %d threads completed, errors -> %s', thread_count, errors)
        self.assertEqual(len(errors), 0)

        # .. wait for all messages to be delivered ..
        delivery_timeout = 60.0
        messages = receiver.wait_for_delivery(expected_count=thread_count, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify all arrived ..
        self.assertEqual(delivered_count, thread_count)

        # .. verify all msg_ids are unique (no duplicates, no lost messages).
        msg_ids = [message['msg_id'] for message in messages]
        unique_count = len(set(msg_ids))
        logger.info('Unique msg_ids -> %d out of %d', unique_count, delivered_count)
        self.assertEqual(unique_count, delivered_count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
