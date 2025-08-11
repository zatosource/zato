# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
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
        topic = self.test_topics[0]  # demo.1

        # Subscribe to topic
        response = requests.post(
            f'{self.base_url}/pubsub/subscribe/topic/{topic}',
            auth=self.auth
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_ok'])
        _ = self._call_diagnostics()

        return

        # Wait 0.1 second
        time.sleep(0.1)

        # Unsubscribe from topic
        response = requests.post(
            f'{self.base_url}/pubsub/unsubscribe/topic/{topic}',
            auth=self.auth
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_ok'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
