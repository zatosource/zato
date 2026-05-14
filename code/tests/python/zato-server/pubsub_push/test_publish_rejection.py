# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BasePushTestCase
from config import _active_endpoints

# ################################################################################################################################
# ################################################################################################################################

class TestPublishRejection(BasePushTestCase):
    """ Negative tests - verify the server rejects invalid publish requests.
    """

    def test_publish_bad_credentials(self) -> 'None':
        """ Publishing with invalid credentials must be rejected by the server.
        """
        topic_name = _active_endpoints[0]

        base_url = self.config.base_url
        url = f'{base_url}/pubsub/topic/{topic_name}'
        credentials = ('wrong_user', 'wrong_password')
        data = {'rejection_test': 'bad_credentials'}

        response = self.publish_raw(url, data, credentials)

        # The server must reject the request with 403 ..
        self.assertEqual(response.status_code, 403)

# ################################################################################################################################

    def test_publish_nonexistent_topic(self) -> 'None':
        """ Publishing to a topic that does not exist must be rejected.
        """
        base_url = self.config.base_url
        url = f'{base_url}/pubsub/topic/nonexistent.topic.xyz'

        username = self.config.publisher_username
        password = self.config.publisher_password
        credentials = (username, password)
        data = {'rejection_test': 'nonexistent_topic'}

        response = self.publish_raw(url, data, credentials)

        # The server must reject with a non-2xx status ..
        self.assertGreaterEqual(response.status_code, 400)

# ################################################################################################################################

    def test_publish_empty_payload(self) -> 'None':
        """ Publishing with an empty data dict must still be accepted by the
        server - this verifies the publish path does not crash on empty payloads.
        """
        topic_name = _active_endpoints[0]
        data = {}

        base_url = self.config.base_url
        url = f'{base_url}/pubsub/topic/{topic_name}'

        username = self.config.publisher_username
        password = self.config.publisher_password
        credentials = (username, password)

        response = self.publish_raw(url, data, credentials)

        # The server should handle an empty payload without a 500 ..
        self.assertNotEqual(response.status_code, 500)

# ################################################################################################################################
# ################################################################################################################################
