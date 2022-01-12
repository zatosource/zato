# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep

# Zato
from zato.common import PUBSUB
from zato.common.pubsub import MSG_PREFIX, prefix_sk, skip_to_external
from zato.common.test import rand_date_utc
from zato.common.test.rest_client import _RESTClient, RESTClientTestCase
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

sec_name   = _default.DEMO_SECDEF_NAME
username   = _default.DEMO_USERNAME
topic_name = '/zato/demo/sample'

class config:
    path_publish     = f'/zato/pubsub/topic/{topic_name}'
    path_receive     = f'/zato/pubsub/topic/{topic_name}'
    path_subscribe   = f'/zato/pubsub/subscribe/topic/{topic_name}'
    path_unsubscribe = f'/zato/pubsub/subscribe/topic/{topic_name}'

# ################################################################################################################################
# ################################################################################################################################

class PubSubAPIRestImpl:
    def __init__(self, test:'PubAPITestCase', rest_client:'_RESTClient') -> 'None':
        self.test = test
        self.rest_client = rest_client

# ################################################################################################################################

    def _publish(self, data:'any_') -> 'stranydict':
        request = {'data': data}
        response = self.rest_client.post(config.path_publish, request) # type: stranydict
        sleep(0.1)
        return response

# ################################################################################################################################

    def _receive(self, needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':

        # If required, wait a moment to make sure a previously published message is delivered -
        # # the server's delivery task runs once in 2 seconds.
        if needs_sleep:
            sleep(2.1)

        return cast_('anylist', self.rest_client.patch(config.path_receive, expect_ok=expect_ok))

# ################################################################################################################################

    def _subscribe(self, needs_unsubscribe:'bool'=False) -> 'str':
        if needs_unsubscribe:
            self._unsubscribe()
        response = self.rest_client.post(config.path_subscribe)
        sleep(1.1)
        return response['sub_key']

# ################################################################################################################################

    def _unsubscribe(self) -> 'anydict':

        # Delete a potential subscription based on our credentials
        response = self.rest_client.delete(config.path_unsubscribe) # type: anydict

        # Wait a moment to make sure the subscription is deleted
        sleep(0.1)

        # We always expect an empty dict on reply from unsubscribe
        self.test.assertDictEqual(response, {})

        # Our caller may want to run its own assertion too
        return response

# ################################################################################################################################
# ################################################################################################################################

class FullPathTester:

    def __init__(self, test:'PubAPITestCase', sub_before_publish:'bool') -> 'None':
        self.test = test
        self.sub_before_publish = sub_before_publish
        self.sub_after_publish = not self.sub_before_publish

# ################################################################################################################################

    def run(self):

        # For type checking
        sub_key = None

        # Always make sure that we are unsubscribed before the test runs
        self.test._unsubscribe()

        # We may potentially need to subscribe before the publication
        if self.sub_before_publish:
            sub_key = self.test._subscribe()

        # Publish the message
        data = cast_(str, rand_date_utc(True))
        response_publish = self.test._publish(data)

        # We expect to have a correct message ID on output
        msg_id = response_publish['msg_id'] # type: str
        self.test.assertTrue(msg_id.startswith(MSG_PREFIX.MSG_ID))

        # We may potentially need to subscribe after the publication
        if self.sub_after_publish:
            sub_key = self.test._subscribe()

        # Now, read the message back from our own queue - we can do it because
        # we know that we are subscribed already.
        response_received = self.test._receive()

        # We do not know how many messages we receive because it is possible
        # that there may be some left over from previous tests. However, we still
        # expect that the message that we have just published will be the first one
        # because messages are returned in the Last-In-First-Out order (LIFO).
        msg_received = response_received[0]

        self.test.assertEqual(msg_received['data'], data)
        self.test.assertEqual(msg_received['size'], len(data))
        self.test.assertEqual(msg_received['sub_key'], sub_key)
        self.test.assertEqual(msg_received['delivery_count'], 1)
        self.test.assertEqual(msg_received['priority'],   PUBSUB.PRIORITY.DEFAULT)
        self.test.assertEqual(msg_received['mime_type'],  PUBSUB.DEFAULT.MIME_TYPE)
        self.test.assertEqual(msg_received['expiration'], PUBSUB.DEFAULT.EXPIRATION)
        self.test.assertEqual(msg_received['topic_name'], topic_name)

        # Dates will start with 2nnn, e.g. 2022, or 2107, depending on a particular field
        date_start = '2'

        self.test.assertTrue(msg_received['pub_time_iso'].startswith(date_start))
        self.test.assertTrue(msg_received['expiration_time_iso'].startswith(date_start))
        self.test.assertTrue(msg_received['recv_time_iso'].startswith(date_start))

        # Make sure that keys that are not supposed to be returned to external callers
        # are not returned in the message.
        for name in skip_to_external:
            if name in msg_received:
                self.test.fail(f'Key `{name}` should not be in message {msg_received}')

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

    def _publish(self, data:'any_') -> 'stranydict':
        return self.api_impl._publish(data)

# ################################################################################################################################

    def _receive(self, needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':
        return self.api_impl._receive(needs_sleep, expect_ok)

# ################################################################################################################################

    def _subscribe(self, needs_unsubscribe:'bool'=False) -> 'str':
        return self.api_impl._subscribe(needs_unsubscribe)

# ################################################################################################################################

    def _unsubscribe(self) -> 'anydict':
        return self.api_impl._unsubscribe()

# ################################################################################################################################

    def xtest_self_subscribe(self):

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe()

        response_initial = self.rest_client.post(config.path_subscribe)

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

    def xtest_full_path_subscribe_before_publication(self):
        tester = FullPathTester(self, True)
        tester.run()

# ################################################################################################################################

    def test_full_path_subscribe_after_publication(self):
        tester = FullPathTester(self, False)
        tester.run()

# ################################################################################################################################

    def xtest_receive_has_no_sub(self):

        # Make sure we are not subscribed
        self._unsubscribe()

        # Try to receive messages without a subscription
        response = cast_('anydict', self._receive(False, False))

        self.assertIsNotNone(response['cid'])
        self.assertEqual(response['result'], 'Error')
        self.assertEqual(response['details'], f'You are not subscribed to topic `{topic_name}`')

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
