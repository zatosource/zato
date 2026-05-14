# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests
import requests

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestDisabledEndpoints(BaseTestCase):

    def test_subscribe_endpoint_disabled(self):
        """ The subscribe endpoint must not be usable - the channel is not
        registered so the server should reject the request.
        """
        topic = self.config.topic_allowed
        url = f'{self.config.base_url}/pubsub/subscribe/topic/{topic}'
        auth = (self.config.user1_username, self.config.user1_password)

        response = requests.post(url, auth=auth)

        # The endpoint is not registered, so Zato returns a non-2xx status
        self.assertNotEqual(response.status_code, 200)

    def test_unsubscribe_endpoint_disabled(self):
        """ The unsubscribe endpoint must not be usable - the channel is not
        registered so the server should reject the request.
        """
        topic = self.config.topic_allowed
        url = f'{self.config.base_url}/pubsub/unsubscribe/topic/{topic}'
        auth = (self.config.user1_username, self.config.user1_password)

        response = requests.post(url, auth=auth)

        # The endpoint is not registered, so Zato returns a non-2xx status
        self.assertNotEqual(response.status_code, 200)

# ################################################################################################################################
# ################################################################################################################################
