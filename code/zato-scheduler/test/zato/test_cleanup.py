# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# gevent
from gevent import sleep

# Zato
from zato.common import PUBSUB
from zato.common.test.config import TestConfig
from zato.common.test.unittest_ import BasePubSubRestTestCase, PubSubConfig, PubSubAPIRestImpl

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

    def test_cleanup_old_subscriptions(self):

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_test

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe(topic_name)

        # Subscribe to the topic
        response_initial = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)

        # Wait a moment to make sure the subscription data is created
        sleep(0.2)

        sub_key = response_initial['sub_key']
        sub_key

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
