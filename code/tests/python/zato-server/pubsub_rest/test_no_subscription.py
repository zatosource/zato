# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestNoSubscription(BaseTestCase):

    def test_get_messages_without_subscription(self):
        """ An authenticated user who never subscribed must receive a 401
        with a 'No subscription found for user' message.
        """
        client = self.get_client(self.config.user3_username, self.config.user3_password)

        result = client.get_messages()
        self.assertFalse(result['is_ok'])
        self.assertEqual(result['http_status_code'], 401)
        self.assertEqual(result['status'], '401 Unauthorized')
        self.assertEqual(result['details'], 'No subscription found for user')

# ################################################################################################################################
# ################################################################################################################################
