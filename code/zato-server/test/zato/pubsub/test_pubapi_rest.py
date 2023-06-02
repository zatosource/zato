# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from time import sleep

# Zato
from zato.common.pubsub import prefix_sk
from zato.common.test.config import TestConfig
from zato.common.test.pubsub.common import FullPathTester
from zato.common.test.unittest_ import BasePubSubRestTestCase, PubSubConfig
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class PubAPITestCase(BasePubSubRestTestCase):

    def xtest_self_subscribe(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_shared

        # Before subscribing, make sure we are not currently subscribed
        _ = self._unsubscribe(topic_name)

        # Subscribe to the topic
        response_initial = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)

        # Wait a moment to make sure the subscription data is created
        sleep(0.2)

        sub_key = response_initial['sub_key']
        queue_depth = response_initial['queue_depth']

        #
        # Validate sub_key
        #

        self.assertIsInstance(sub_key, str)
        self.assertTrue(sub_key.startswith(prefix_sk))

        len_sub_key = len(sub_key)
        len_prefix  = len(prefix_sk)

        self.assertTrue(len_sub_key >= len_prefix + 5) # We expect at least a few random characters here

        #
        # Validate queue_depth
        #

        self.assertIsInstance(queue_depth, int)

        # Subscribe once more - this should be allowed although we expect an empty response now
        response_already_subscribed = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)

        self.assertDictEqual(response_already_subscribed, {})

# ################################################################################################################################

    def xtest_self_unsubscribe(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_shared

        # Unsubscribe once ..
        response = self._unsubscribe(topic_name)

        # .. we expect an empty dict on reply
        self.assertDictEqual(response, {})

        # .. unsubscribe once more - it is not an error to unsubscribe
        # .. even if we are already unsubscribed.
        response = self._unsubscribe(topic_name)
        self.assertDictEqual(response, {})

# ################################################################################################################################

    def xtest_full_path_subscribe_before_publication(self):
        tester = FullPathTester(self, True) # type: ignore
        tester.run()

# ################################################################################################################################

    def xtest_full_path_subscribe_after_publication(self):

        prefix = '/zato/demo/unique.'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # .. get its response as a dict ..
        out = self.run_zato_cli_json_command(cli_params) # type: anydict
        topic_name = out['name']

        tester = FullPathTester(self, False, topic_name) # type: ignore
        tester.run()

# ################################################################################################################################

    def xtest_receive_has_no_sub(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_shared

        # Make sure we are not subscribed
        _ = self._unsubscribe(topic_name)

        # Try to receive messages without a subscription
        response = cast_('anydict', self._receive(topic_name, False, False))

        self.assertIsNotNone(response['cid'])
        self.assertEqual(response['result'], 'Error')
        self.assertEqual(response['details'], 'You are not subscribed to topic `{}`'.format(topic_name))

# ################################################################################################################################

    def test_receive_many(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_shared

        # Make sure we are subscribed
        _ = self._subscribe(topic_name, needs_unsubscribe=True)

        data1 = '111'
        data2 = '222'
        data3 = '333'

        # Publish #1
        response1 = self._publish(topic_name, data1)
        expected_msg_id1 = response1['msg_id']

        # Publish #2
        response2 = self._publish(topic_name, data2)
        expected_msg_id2 = response2['msg_id']

        # Publish #3
        response3 = self._publish(topic_name, data3)
        expected_msg_id3 = response3['msg_id']

        # Receive and confirm the order of messages received. This will be a list of messages
        # and we expect to find all of them, in LIFO order.
        received = self._receive(topic_name)

        received_msg1 = received[0]
        received_msg2 = received[1]
        received_msg3 = received[2]

        self.assertEqual(expected_msg_id3, received_msg1['msg_id'])
        self.assertEqual(expected_msg_id2, received_msg2['msg_id'])
        self.assertEqual(expected_msg_id1, received_msg3['msg_id'])

        self.assertEqual(data3, received_msg1['data'])
        self.assertEqual(data2, received_msg2['data'])
        self.assertEqual(data1, received_msg3['data'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
