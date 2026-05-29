# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
import unittest

# local
from zato.common.test.client import PublishClient
from zato.common.test.config_pubsub_push import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.delivery_failure')

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveryFailure(unittest.TestCase):
    """ Tests for delivery failure scenarios - retries, recovery, and isolation.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_transient_503_then_recovery(self) -> 'None':
        """ Configure receiver to reject 3 times with HTTP 503, then auto-recover.
        Publish a message, wait for delivery to succeed after retries,
        verify the message arrives intact and 3 rejections were recorded.
        """

        topic_name = 'customer.registered'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Configure the receiver to reject 3 times then auto-recover ..
        reject_count = 3
        receiver.behavior.set_reject_503(auto_recover_after=reject_count)
        self.addCleanup(receiver.behavior.reset)

        # Publish a message ..
        publish_data:'anydict' = {'customer_id': 'retry_test', 'source': 'test_transient_503'}
        _ = self.publisher.publish(topic_name, publish_data)
        logger.info('Published message to %s with %d rejections configured', topic_name, reject_count)

        # .. wait for delivery to eventually succeed after retries ..
        delivery_timeout = 60.0
        messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify exactly 1 message arrived ..
        self.assertEqual(delivered_count, 1)

        # .. verify the rejection count matches what we configured.
        actual_reject_count = receiver.behavior.reject_count
        logger.info('Rejection count -> %d', actual_reject_count)
        self.assertEqual(actual_reject_count, reject_count)

# ################################################################################################################################

    def test_receiver_down_then_back_up(self) -> 'None':
        """ Stop the receiver, publish a message, restart the receiver on the same port,
        wait for the delivery task to retry and succeed.
        """

        topic_name = 'customer.updated'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Stop the receiver so the port becomes unreachable ..
        receiver.stop()
        logger.info('Stopped receiver for %s on port %d', topic_name, receiver.port)

        # .. publish a message while the receiver is down ..
        publish_data:'anydict' = {'customer_id': 'down_test', 'source': 'test_receiver_down'}
        _ = self.publisher.publish(topic_name, publish_data)
        logger.info('Published message to %s while receiver is down', topic_name)

        # .. wait a few seconds for at least one failed delivery attempt ..
        down_duration = 5.0
        time.sleep(down_duration)

        # .. restart the receiver on the same port ..
        receiver.start()
        logger.info('Restarted receiver for %s on port %d', topic_name, receiver.port)

        # .. wait for delivery to succeed after restart ..
        delivery_timeout = 60.0
        messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify exactly 1 message arrived (no duplicates).
        self.assertEqual(delivered_count, 1)

# ################################################################################################################################

    def test_slow_receiver(self) -> 'None':
        """ Configure receiver to delay 5 seconds before responding.
        Publish a message, wait for delivery, verify it arrives intact
        and no premature retry caused a duplicate.
        """

        topic_name = 'customer.deactivated'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Configure the receiver to hang for 5 seconds before responding ..
        hang_duration = 5.0
        receiver.behavior.set_hang(hang_duration)
        self.addCleanup(receiver.behavior.reset)

        # Publish a message ..
        publish_data:'anydict' = {'customer_id': 'slow_test', 'source': 'test_slow_receiver'}
        _ = self.publisher.publish(topic_name, publish_data)
        logger.info('Published message to %s with %s second hang configured', topic_name, hang_duration)

        # .. wait for delivery (longer than the hang duration) ..
        delivery_timeout = 60.0
        messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify exactly 1 message arrived (no duplicate from premature retry).
        self.assertEqual(delivered_count, 1)

# ################################################################################################################################

    def test_expired_message_not_pushed(self) -> 'None':
        """ Publish a message with 1-second TTL while the receiver is rejecting.
        The delivery task retries, but the TTL expires before a successful push.
        Verify the receiver got zero deliveries.
        """

        topic_name = 'order.placed'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Configure the receiver to reject indefinitely (no auto-recover) ..
        receiver.behavior.set_reject_503(auto_recover_after=0)
        self.addCleanup(receiver.behavior.reset)

        # Publish a message with a very short TTL ..
        ttl_seconds = 1
        publish_data:'anydict' = {'order_id': 'expired_test', 'source': 'test_expired_not_pushed'}
        _ = self.publisher.publish(topic_name, publish_data, expiration=ttl_seconds)
        logger.info('Published message to %s with TTL=%d second(s), receiver rejecting', topic_name, ttl_seconds)

        # .. wait for the message to expire and the delivery task to give up ..
        expiry_wait = 10.0
        time.sleep(expiry_wait)

        # .. now switch receiver to accept and clear output ..
        receiver.behavior.reset()
        receiver.clear_output()
        logger.info('Receiver switched to accept after expiry wait of %s seconds', expiry_wait)

        # .. wait generously to confirm no late delivery arrives ..
        post_recovery_wait = 10.0
        time.sleep(post_recovery_wait)

        # .. check what arrived ..
        messages = receiver.get_delivered_messages()
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) after expiry -> %s', delivered_count, messages)

        # .. verify nothing was delivered (message expired before successful push).
        self.assertEqual(delivered_count, 0)

# ################################################################################################################################

    def test_failure_isolation_between_endpoints(self) -> 'None':
        """ One receiver rejects all requests while another is healthy.
        Publish one message to each topic, verify the healthy endpoint
        gets its message regardless of the failing one.
        """

        failing_topic = 'order.placed'
        healthy_topic = 'order.shipped'

        failing_receiver = TestConfig.endpoints[failing_topic].receiver
        healthy_receiver = TestConfig.endpoints[healthy_topic].receiver

        # Configure the failing receiver to reject indefinitely ..
        failing_receiver.behavior.set_reject_503(auto_recover_after=0)
        self.addCleanup(failing_receiver.behavior.reset)

        # Publish one message to each topic ..
        failing_data:'anydict' = {'order_id': 'fail_iso', 'source': 'failing_endpoint'}
        healthy_data:'anydict' = {'order_id': 'healthy_iso', 'source': 'healthy_endpoint'}

        _ = self.publisher.publish(failing_topic, failing_data)
        _ = self.publisher.publish(healthy_topic, healthy_data)
        logger.info('Published to %s (rejecting) and %s (healthy)', failing_topic, healthy_topic)

        # .. wait for the healthy receiver to get its message ..
        delivery_timeout = 30.0
        messages = healthy_receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Healthy receiver delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify the healthy endpoint got exactly 1 message ..
        self.assertEqual(delivered_count, 1)

        # .. verify the failing receiver got nothing.
        failing_messages = failing_receiver.get_delivered_messages()
        failing_count = len(failing_messages)
        logger.info('Failing receiver delivered %d message(s) -> %s', failing_count, failing_messages)
        self.assertEqual(failing_count, 0)

# ################################################################################################################################

    def test_no_duplicates_on_retry(self) -> 'None':
        """ Configure receiver to reject 2 times then recover. Publish a single message,
        wait generously after delivery, verify exactly 1 copy arrived.
        """

        topic_name = 'order.shipped'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Configure the receiver to reject 2 times then auto-recover ..
        reject_count = 2
        receiver.behavior.set_reject_503(auto_recover_after=reject_count)
        self.addCleanup(receiver.behavior.reset)

        # Publish a single message ..
        publish_data:'anydict' = {'order_id': 'dup_test', 'source': 'test_no_duplicates'}
        _ = self.publisher.publish(topic_name, publish_data)
        logger.info('Published message to %s with %d rejections configured', topic_name, reject_count)

        # .. wait for delivery to succeed ..
        delivery_timeout = 60.0
        messages = receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        self.assertEqual(delivered_count, 1)

        # .. now wait generously to confirm no second delivery arrives ..
        generous_wait = 15.0
        time.sleep(generous_wait)

        # .. re-check the total count ..
        all_messages = receiver.get_delivered_messages()
        final_count = len(all_messages)
        logger.info('Final count after %s second wait -> %d message(s) -> %s', generous_wait, final_count, all_messages)

        # .. verify still exactly 1 (no duplicates).
        self.assertEqual(final_count, 1)

# ################################################################################################################################

    def test_burst_with_intermittent_failure(self) -> 'None':
        """ Configure receiver to reject 3 requests then accept all subsequent ones.
        Publish 10 messages in rapid succession, wait for all to be delivered,
        verify all 10 arrived with no duplicates.
        """

        topic_name = 'customer.registered'
        receiver = TestConfig.endpoints[topic_name].receiver

        # Configure the receiver to reject the first 3 requests then accept ..
        initial_reject_count = 3
        receiver.behavior.set_reject_503(auto_recover_after=initial_reject_count)
        self.addCleanup(receiver.behavior.reset)

        # Publish messages in rapid succession ..
        burst_count = 10

        for idx in range(burst_count):
            publish_data:'anydict' = {'customer_id': f'burst_{idx}', 'source': 'test_burst_intermittent'}
            _ = self.publisher.publish(topic_name, publish_data)

        logger.info('Published %d messages to %s with %d initial rejections configured',
            burst_count, topic_name, initial_reject_count)

        # .. wait for all messages to be delivered ..
        delivery_timeout = 120.0
        messages = receiver.wait_for_delivery(expected_count=burst_count, timeout=delivery_timeout)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify all messages arrived ..
        self.assertEqual(delivered_count, burst_count)

        # .. verify no duplicates by checking unique msg_ids ..
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
