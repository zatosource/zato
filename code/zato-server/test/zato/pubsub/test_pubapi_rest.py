# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep

# Zato
from zato.common import PUBSUB
from zato.common.pubsub import prefix_sk
from zato.common.test.config import TestConfig
from zato.common.test.pubsub import FullPathTester
from zato.common.test.rest_client import _RESTClient, RESTClientTestCase
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

#topic_name = TestConfig.pubsub_topic_shared
sec_name   = _default.DEMO_SECDEF_NAME
username   = _default.DEMO_USERNAME

class config:
    path_publish     = '/zato/pubsub/topic/'
    path_receive     = '/zato/pubsub/topic/'
    path_subscribe   = '/zato/pubsub/subscribe/topic/'
    path_unsubscribe = '/zato/pubsub/subscribe/topic/'

# ################################################################################################################################
# ################################################################################################################################

class PubSubAPIRestImpl:
    def __init__(self, test:'PubAPITestCase', rest_client:'_RESTClient') -> 'None':
        self.test = test
        self.rest_client = rest_client

# ################################################################################################################################

    def _publish(self, topic_name:'str', data:'any_') -> 'stranydict':
        request = {'data': data}
        response = self.rest_client.post(config.path_publish + topic_name, request) # type: stranydict
        sleep(0.1)
        return response

# ################################################################################################################################

    def _receive(self, topic_name:'str', needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':

        # If required, wait a moment to make sure a previously published message is delivered -
        # # the server's delivery task runs once in 2 seconds.
        if needs_sleep:
            sleep(2.1)

        return cast_('anylist', self.rest_client.patch(config.path_receive + topic_name, expect_ok=expect_ok))

# ################################################################################################################################

    def _subscribe(self, topic_name:'str', needs_unsubscribe:'bool'=False) -> 'str':
        if needs_unsubscribe:
            self._unsubscribe(topic_name)
        response = self.rest_client.post(config.path_subscribe + topic_name)
        sleep(1.1)
        return response['sub_key']

# ################################################################################################################################

    def _unsubscribe(self, topic_name:'str') -> 'anydict':

        # Delete a potential subscription based on our credentials
        response = self.rest_client.delete(config.path_unsubscribe + topic_name) # type: anydict

        # Wait a moment to make sure the subscription is deleted
        sleep(0.1)

        # We always expect an empty dict on reply from unsubscribe
        self.test.assertDictEqual(response, {})

        # Our caller may want to run its own assertion too
        return response

# ################################################################################################################################
# ################################################################################################################################

class PubAPITestCase(RESTClientTestCase):

    needs_current_app     = False
    payload_only_messages = False

# ################################################################################################################################

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init(username=username, sec_name=sec_name)
        self.api_impl = PubSubAPIRestImpl(self, self.rest_client)

# ################################################################################################################################

    def _publish(self, topic_name:'str', data:'any_') -> 'stranydict':
        return self.api_impl._publish(topic_name, data)

# ################################################################################################################################

    def _receive(self, topic_name:'str', needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':
        return self.api_impl._receive(topic_name, needs_sleep, expect_ok)

# ################################################################################################################################

    def _subscribe(self, topic_name:'str', needs_unsubscribe:'bool'=False) -> 'str':
        return self.api_impl._subscribe(topic_name, needs_unsubscribe)

# ################################################################################################################################

    def _unsubscribe(self, topic_name:'str') -> 'anydict':
        return self.api_impl._unsubscribe(topic_name)

# ################################################################################################################################

    def xtest_self_subscribe(self):

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe()

        response_initial = self.rest_client.post(config.path_subscribe + topic_name)

        # Wait a moment to make sure the subscription data is created
        sleep(0.1)

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
        response_already_subscribed = self.rest_client.post(config.path_subscribe)

        self.assertDictEqual(response_already_subscribed, {})

# ################################################################################################################################

    def xtest_self_unsubscribe(self):

        # Unsubscribe once ..
        response = self._unsubscribe()

        # .. we expect an empty dict on reply
        self.assertDictEqual(response, {})

        # .. unsubscribe once more - it is not an error to unsubscribe
        # .. even if we are already unsubscribed.
        response = self._unsubscribe()
        self.assertDictEqual(response, {})

# ################################################################################################################################

    def test_full_path_subscribe_before_publication(self):
        tester = FullPathTester(self, True) # type: ignore
        tester.run()

# ################################################################################################################################

    def xtest_full_path_subscribe_after_publication(self):
        tester = FullPathTester(self, False) # type: ignore
        tester.run()

# ################################################################################################################################

    def xtest_receive_has_no_sub(self):

        # Make sure we are not subscribed
        self._unsubscribe()

        # Try to receive messages without a subscription
        response = cast_('anydict', self._receive(False, False))

        self.assertIsNotNone(response['cid'])
        self.assertEqual(response['result'], 'Error')
        self.assertEqual(response['details'], f'You are not subscribed to topic ``')

# ################################################################################################################################

    def xtest_receive_many(self):

        # Make sure we are subscribed
        self._subscribe(needs_unsubscribe=True)

        data1 = '111'
        data2 = '222'
        data3 = '333'

        # Publish #1
        response1 = self._publish(data1)
        expected_msg_id1 = response1['msg_id']

        # Publish #2
        response2 = self._publish(data2)
        expected_msg_id2 = response2['msg_id']

        # Publish #3
        response3 = self._publish(data3)
        expected_msg_id3 = response3['msg_id']

        # Receive and confirm the order of messages received. This will be a list of messages
        # and we expect to find all of them, in LIFO order.
        received = self._receive()

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
    main()

# ################################################################################################################################
# ################################################################################################################################
