# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep

# Zato
from zato.common import PUBSUB
from zato.common.pubsub import MSG_PREFIX, prefix_sk
from zato.common.test import rand_string
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict

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

class PubAPITestCase(RESTClientTestCase):

    needs_current_app     = False
    payload_only_messages = False

# ################################################################################################################################

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init(username=username, sec_name=sec_name)

# ################################################################################################################################

    def _subscribe(self) -> 'anydict':
        return self.rest_client.post(config.path_subscribe)

# ################################################################################################################################

    def _unsubscribe(self) -> 'anydict':
        response = self.rest_client.delete(config.path_unsubscribe) # type: anydict

        # We always expect an empty dict on reply from unsubscribe
        self.assertDictEqual(response, {})

        # Our caller may want to run its own assertion too
        return response

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

    def test_full_path_with_prior_subscription(self):

        # First, make sure that we are not subscribed so that we can receive a sub_key in the next step
        self._unsubscribe()

        # Wait a moment to make sure the subscription is deleted
        sleep(0.1)

        # Note that in this test we are subscribing upfront
        sub_response = self._subscribe()
        sub_key = sub_response['sub_key']

        data = rand_string()
        request = {'data': data}
        response_publish = self.rest_client.post(config.path_publish, request) # type: stranydict

        # We should have a correct message ID on output
        msg_id = response_publish['msg_id'] # type: str
        self.assertTrue(msg_id.startswith(MSG_PREFIX.MSG_ID))

        # Wait a moment to make sure the message is delivered - the server's delivery task runs once in 2 seconds
        sleep(2.1)

        # Now, read the message back from our own queue - we can do it because
        # we know that we are subscribed already.
        response_received = self.rest_client.patch(config.path_receive)

        # We do not know how many messages we receive because it is possible
        # that there may be some left over from previous tests. However, we still
        # expect that the message that we have just published will be the first one
        # because messages are returned in the Last-In-First-Out order (LIFO).
        msg_received = response_received[0]

        self.assertEqual(msg_received['data'], data)
        self.assertEqual(msg_received['size'], len(data))
        self.assertEqual(msg_received['sub_key'], sub_key)
        self.assertEqual(msg_received['delivery_count'], 1)
        self.assertEqual(msg_received['priority'],   PUBSUB.PRIORITY.DEFAULT)
        self.assertEqual(msg_received['mime_type'],  PUBSUB.DEFAULT.MIME_TYPE)
        self.assertEqual(msg_received['expiration'], PUBSUB.DEFAULT.EXPIRATION)
        self.assertEqual(msg_received['topic_name'], topic_name)

        self.assertTrue(msg_received['has_gd'])
        self.assertFalse(msg_received['is_in_sub_queue'])

        # Dates will start with 2nnn, e.g. 2022, or 2107, depending on a particular field
        date_start = '2'

        self.assertTrue(msg_received['pub_time_iso'].startswith(date_start))
        self.assertTrue(msg_received['expiration_time_iso'].startswith(date_start))
        # self.assertTrue(msg_received['recv_time_iso'].startswith(date_start))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
