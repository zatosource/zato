# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import main

# requests
import requests

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerUnsubscribeTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server unsubscribe functionality.
    """

    def test_subscribe_then_unsubscribe(self):
        """ Test subscribing to a topic and then unsubscribing.
        """
        # Skip automatic unsubscribe in tearDown since this test handles it manually
        self.skip_auto_unsubscribe = True

        topic = self.test_topics[0]  # demo.1

        # Subscribe to topic
        response = requests.post(
            f'{self.base_url}/pubsub/subscribe/topic/{topic}',
            auth=self.auth
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_ok'])

        # Check diagnostics after subscribe - should show subscription
        diagnostics_after_subscribe = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_subscribe)
        self.assertTrue(diagnostics_after_subscribe['is_ok'])
        self.assertIn('data', diagnostics_after_subscribe)

        # Verify subscription exists
        subscriptions = diagnostics_after_subscribe['data']['subscriptions']
        self.assertIn(topic, subscriptions)
        self.assertIn('demo_sec_def', subscriptions[topic])
        self.assertIn('sub_key', subscriptions[topic]['demo_sec_def'])

        # Unsubscribe from all topics
        for topic_name in self.test_topics:
            response = requests.post(
                f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}',
                auth=self.auth
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['is_ok'])

            # Check diagnostics after each unsubscribe
            diagnostics_after_unsubscribe = self._call_diagnostics()
            self.assertIsNotNone(diagnostics_after_unsubscribe)
            self.assertTrue(diagnostics_after_unsubscribe['is_ok'])
            self.assertIn('data', diagnostics_after_unsubscribe)

            # Verify subscription no longer exists for this topic
            subscriptions = diagnostics_after_unsubscribe['data']['subscriptions']
            self.assertNotIn(topic_name, subscriptions)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
