# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to be done as soon as possible
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from unittest import main

# gevent
from gevent import sleep

# Zato
from zato.common import PUBSUB
from zato.common.test.config import TestConfig
from zato.common.test.unittest_ import BasePubSubRestTestCase, PubSubConfig, PubSubAPIRestImpl
from zato.common.typing_ import cast_
from zato.scheduler.cleanup.core import run_cleanup

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

sec_name = _default.TEST_SECDEF_NAME
username = _default.TEST_USERNAME

# ################################################################################################################################
# ################################################################################################################################

class PubSubCleanupTestCase(BasePubSubRestTestCase):

    should_init_rest_client = False

    def setUp(self) -> None:
        self.rest_client.init(username=username, sec_name=sec_name)
        self.api_impl = PubSubAPIRestImpl(self, self.rest_client)
        super().setUp()

# ################################################################################################################################

    def test_cleanup_old_subscriptions_no_sub_keys(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_test

        # Make sure we are not subscribed to anything
        self._unsubscribe(topic_name)

        # Indicate after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        delta = 1

        # Export a variable with delta as required by the underlying cleanup implementation
        os.environ['ZATO_SCHED_DELTA_NOT_INTERACT'] = str(delta)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup()

        self.assertEqual(cleanup_result.total_messages, 0)
        self.assertListEqual(cleanup_result.sk_list, [])

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_test

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe(topic_name)

        # Subscribe to the topic
        response_initial = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)

        # Wait a moment to make sure the subscription data is created
        sleep(2)

        sub_key = response_initial['sub_key']
        sub_key

        data = 'abc'
        len_messages = 2

        for _ in range(len_messages):
            self._publish(topic_name, data)

        # Because each publication is synchronous, we now know that all of them are in the subscriber's queue
        # which means that we can delete them already.

        # Indicate after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        delta = 1

        # Export a variable with delta as required by the underlying cleanup implementation
        os.environ['ZATO_SCHED_DELTA_NOT_INTERACT'] = str(delta)

        # Sleep a little bit longer to make sure that we actually exceed the delta
        sleep_extra = delta * 0.1
        sleep(delta + sleep_extra)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup()

        self.assertEqual(cleanup_result.total_messages, len_messages)
        self.assertListEqual(cleanup_result.sk_list, [sub_key])

        # The cleanup procedure invoked the server which in turn deleted our subscription,
        # which means that we can sleep for a moment now to make sure that it is actually
        # deleted and then we can try to get message for the now-already-deleted sub_key.
        # We expect that it will result in a permissioned denied, as though this sub_key never existed.

        # Wait a moment ..
        sleep(0.1)

        receive_result = cast_('anydict', self._receive(topic_name, expect_ok=False))

        cid = receive_result['cid']

        self.assertIsInstance(cid, str)
        self.assertTrue(len(cid) >= 20)

        self.assertEqual(receive_result['result'], 'Error')
        self.assertEqual(receive_result['details'], f'You are not subscribed to topic `{topic_name}`')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
