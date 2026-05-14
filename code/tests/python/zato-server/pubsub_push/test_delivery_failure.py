# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time

# PyPI
import pytest # type: ignore[reportMissingImports]

# local
from base import BasePushTestCase
from config import _active_endpoints

# ################################################################################################################################
# ################################################################################################################################

_active_endpoint_count = len(_active_endpoints)

_skip_fewer_than_two = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    _active_endpoint_count < 2,
    reason='Delivery failure tests require at least 2 active endpoints',
)

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveryFailure(BasePushTestCase):
    """ Rainy-day tests for push delivery under failure conditions.
    """

    def setUp(self) -> 'None':
        """ Reset all receivers to accept mode BEFORE clearing output
        directories, so retrying messages from a prior test do not
        land on disk after the parent setUp clears them.
        """

        for behavior in self.config.receiver_controls.values():
            behavior.set_accept() # type: ignore[union-attr]

        super().setUp()

# ################################################################################################################################

    def _poll_for_marker(self, topic_name:'str', marker:'str', timeout:'int'=30) -> 'bool':
        """ Poll the output directory until a message whose data field
        contains the given marker value appears. Parses JSON and checks
        the marker key specifically to avoid false positives from
        substring matching on raw file content.
        """

        # Set up the polling parameters ..
        output_directory = self.config.endpoint_output_dirs[topic_name]
        deadline = time.monotonic() + timeout

        # .. and keep scanning until the marker is found or the deadline passes.
        while time.monotonic() < deadline:

            for entry in os.listdir(output_directory):
                if entry.endswith('.json'):
                    file_path = os.path.join(output_directory, entry)

                    with open(file_path, 'r') as message_file:
                        message = json.load(message_file)

                    # The push payload is a raw Redis stream entry
                    # where the data field is a JSON string ..
                    data_json = message.get('data', '')

                    try:
                        data = json.loads(data_json)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    if data.get('marker') == marker:
                        return True

            time.sleep(0.5)

        return False

# ################################################################################################################################

    def _count_files_with_marker(self, topic_name:'str', marker:'str') -> 'int':
        """ Count JSON files in the output directory whose parsed data
        field contains the given marker value.
        """

        # Look up the output directory ..
        output_directory = self.config.endpoint_output_dirs[topic_name]
        count = 0

        # .. scan each file and parse the data field ..
        for entry in os.listdir(output_directory):
            if entry.endswith('.json'):
                file_path = os.path.join(output_directory, entry)

                with open(file_path, 'r') as message_file:
                    message = json.load(message_file)

                data_json = message.get('data', '')

                try:
                    data = json.loads(data_json)
                except (json.JSONDecodeError, TypeError):
                    continue

                if data.get('marker') == marker:
                    count += 1

        # .. and return the total.
        out = count
        return out

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_transient_503_then_recovery(self) -> 'None':
        """ A receiver that returns 503 three times then recovers must
        eventually receive the pushed message.
        """
        topic_name = _active_endpoints[0]
        behavior = self.config.receiver_controls[topic_name]

        behavior.set_reject_503(reject_count=3) # type: ignore[union-attr]

        data = {'failure_test': 'transient_503', 'marker': 'recover-after-3'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        found = self._poll_for_marker(topic_name, 'recover-after-3', timeout=30)
        self.assertTrue(found, 'Message with marker recover-after-3 was not delivered')

        # Verify Zato sent a real payload during the rejected attempts ..
        rejected_count = behavior.rejected_count # type: ignore[union-attr]
        self.assertGreaterEqual(rejected_count, 1)

        last_body = behavior.last_rejected_body # type: ignore[union-attr]
        self.assertIn('recover-after-3', last_body)

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_receiver_down_then_back_up(self) -> 'None':
        """ A message published while the receiver is down must be delivered
        after the receiver is restarted.
        """
        topic_name = _active_endpoints[0]
        receiver = self.config.receiver_servers[topic_name]

        # Shut down the receiver so the server gets connection refused
        receiver.shutdown() # type: ignore[union-attr]

        data = {'failure_test': 'down_then_up', 'marker': 'survived-outage'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Let the server accumulate a few failed delivery attempts
        time.sleep(5)

        # Bring the receiver back up on the same port
        receiver.restart() # type: ignore[union-attr]

        found = self._poll_for_marker(topic_name, 'survived-outage', timeout=30)
        self.assertTrue(found, 'Message with marker survived-outage was not delivered')

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_slow_receiver_still_delivers(self) -> 'None':
        """ A receiver that takes 5 seconds to respond must still receive
        the pushed message.
        """
        topic_name = _active_endpoints[0]
        behavior = self.config.receiver_controls[topic_name]

        behavior.set_hang(hang_seconds=5) # type: ignore[union-attr]

        data = {'failure_test': 'slow_receiver', 'marker': 'waited-for-slow'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        found = self._poll_for_marker(topic_name, 'waited-for-slow', timeout=10)
        self.assertTrue(found, 'Message with marker waited-for-slow was not delivered')

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_expired_message_not_pushed(self) -> 'None':
        """ A message published with a 1-second TTL must not be pushed
        to the receiver if delivery is delayed past the TTL.
        """
        topic_name = _active_endpoints[0]
        behavior = self.config.receiver_controls[topic_name]

        # Make the receiver hang long enough for the message to expire
        # before the push delivery completes ..
        behavior.set_hang(hang_seconds=5) # type: ignore[union-attr]

        data = {'failure_test': 'push_ttl', 'marker': 'should-expire-push'}

        result = self.publish(topic_name, data, expiration=1)
        self.assertTrue(result['is_ok'])

        # Wait for the TTL to expire and delivery attempts to settle ..
        time.sleep(10)

        # Reset the receiver to accept mode ..
        behavior.set_accept() # type: ignore[union-attr]

        # Wait a bit more for any late delivery ..
        time.sleep(5)

        # The expired message must not have been written to disk ..
        count = self._count_files_with_marker(topic_name, 'should-expire-push')
        self.assertEqual(count, 0, 'Expired message was delivered to the push endpoint')

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_failure_on_one_endpoint_does_not_block_another(self) -> 'None':
        """ When one receiver is rejecting, messages to a different topic
        must still be delivered to its healthy receiver.
        """
        failing_topic = _active_endpoints[0]
        healthy_topic = _active_endpoints[1]

        failing_behavior = self.config.receiver_controls[failing_topic]
        failing_behavior.set_reject_503() # type: ignore[union-attr]

        data_failing = {'failure_test': 'isolation', 'target': 'failing'}
        data_healthy = {'failure_test': 'isolation', 'target': 'healthy', 'marker': 'delivered-despite-other-failure'}

        result_failing = self.publish(failing_topic, data_failing)
        self.assertTrue(result_failing['is_ok'])

        result_healthy = self.publish(healthy_topic, data_healthy)
        self.assertTrue(result_healthy['is_ok'])

        found = self._poll_for_marker(healthy_topic, 'delivered-despite-other-failure', timeout=10)
        self.assertTrue(found, 'Healthy endpoint did not receive its message')

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_no_duplicate_on_retry(self) -> 'None':
        """ A message retried after two 503 rejections must be delivered
        exactly once, not duplicated.
        """
        topic_name = _active_endpoints[0]
        behavior = self.config.receiver_controls[topic_name]

        behavior.set_reject_503(reject_count=2) # type: ignore[union-attr]

        data = {'failure_test': 'no_duplicate', 'marker': 'exactly-once'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Wait for delivery after retries ..
        found = self._poll_for_marker(topic_name, 'exactly-once', timeout=30)
        self.assertTrue(found, 'Message with marker exactly-once was not delivered')

        # Wait 15 seconds (1.5x Zato's max retry interval of 10s)
        # for any delayed duplicate to arrive ..
        time.sleep(15)

        duplicate_count = self._count_files_with_marker(topic_name, 'exactly-once')
        self.assertEqual(duplicate_count, 1)

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_burst_with_intermittent_failure(self) -> 'None':
        """ Publishing 10 messages while the receiver rejects the first 3
        must still result in all 10 messages being delivered.
        """
        topic_name = _active_endpoints[0]
        behavior = self.config.receiver_controls[topic_name]

        behavior.set_reject_503(reject_count=3) # type: ignore[union-attr]

        for message_index in range(10):

            data = {'failure_test': 'burst_intermittent', 'index': message_index, 'marker': 'burst-item'}

            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        # Wait until all 10 messages with our marker arrive ..
        deadline = time.monotonic() + 30

        while time.monotonic() < deadline:
            count = self._count_files_with_marker(topic_name, 'burst-item')
            if count >= 10:
                break
            time.sleep(0.5)

        final_count = self._count_files_with_marker(topic_name, 'burst-item')
        self.assertEqual(final_count, 10)

# ################################################################################################################################
# ################################################################################################################################
