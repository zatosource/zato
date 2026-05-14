# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    reason='Cross-domain tests require at least 2 active endpoints',
)

# ################################################################################################################################
# ################################################################################################################################

class TestCrossDomainIsolation(BasePushTestCase):
    """ Routing isolation tests - each endpoint must receive only its own topic's messages.
    """

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_endpoint_receives_only_own_topic(self) -> 'None':
        """ Publishing to the first topic must not deliver anything to the second endpoint.
        """
        first_topic = _active_endpoints[0]
        second_topic = _active_endpoints[1]

        # Record the second endpoint's file count BEFORE any publishes ..
        second_count_before = self.count_files_in_output_directory(second_topic)

        data = {'isolation_test': 'own_topic_only', 'target': first_topic}

        result = self.publish(first_topic, data)
        self.assertTrue(result['is_ok'])

        # Wait long enough for any erroneous cross-delivery to happen ..
        time.sleep(5)

        # .. the second endpoint must have received zero new files.
        second_count_after = self.count_files_in_output_directory(second_topic)
        self.assertEqual(second_count_before, second_count_after)

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_all_active_endpoints_receive_own_messages(self) -> 'None':
        """ Publishing one message per active topic must deliver exactly one new message
        to each corresponding endpoint.
        """

        # Record the current file counts for each endpoint ..
        counts_before = {}

        for topic_name in _active_endpoints:
            count = self.count_files_in_output_directory(topic_name)
            counts_before[topic_name] = count

        # .. publish one message per active topic ..
        for topic_name in _active_endpoints:
            data = {'routing_test': 'all_endpoints', 'topic': topic_name}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        # .. wait for delivery ..
        time.sleep(10)

        # .. each endpoint must have received exactly one new message.
        for topic_name in _active_endpoints:
            count_after = self.count_files_in_output_directory(topic_name)
            new_messages = count_after - counts_before[topic_name]
            self.assertEqual(new_messages, 1, f'Expected 1 new message for {topic_name}, got {new_messages}')

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_no_message_duplication(self) -> 'None':
        """ Publishing a single message must result in exactly one delivery to the endpoint.
        """
        topic_name = _active_endpoints[0]

        count_before = self.count_files_in_output_directory(topic_name)

        data = {'duplication_test': 'single_publish', 'unique_marker': 'no-dup-check'}
        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Wait generously for any duplicate delivery to happen ..
        time.sleep(10)

        count_after = self.count_files_in_output_directory(topic_name)
        new_messages = count_after - count_before
        self.assertEqual(new_messages, 1)

# ################################################################################################################################

    @_skip_fewer_than_two # type: ignore[reportUntypedFunctionDecorator]
    def test_concurrent_publishers(self) -> 'None':
        """ Publishing 10 messages simultaneously from separate threads
        must deliver all 10 to the endpoint.
        """
        topic_name = _active_endpoints[0]

        count_before = self.count_files_in_output_directory(topic_name)

        def _publish_one(index:'int') -> 'bool':
            data = {'concurrent_test': 'parallel_publish', 'index': index}
            result = self.publish(topic_name, data)

            out = result['is_ok']
            return out

        # Fire 10 publishes concurrently ..
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            for message_index in range(10):
                future = executor.submit(_publish_one, message_index)
                futures.append(future)

            for future in as_completed(futures):
                self.assertTrue(future.result())

        # Wait for all deliveries ..
        time.sleep(15)

        count_after = self.count_files_in_output_directory(topic_name)
        new_messages = count_after - count_before
        self.assertEqual(new_messages, 10)

# ################################################################################################################################
# ################################################################################################################################
