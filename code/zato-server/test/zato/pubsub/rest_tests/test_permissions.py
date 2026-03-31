# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestPermissions(BaseTestCase):

    def test_publish_to_forbidden_topic(self):
        client = self.get_client()
        forbidden_topic = self.config.topic_forbidden

        result = client.publish(forbidden_topic, 'test message')
        self.assertFalse(result.get('is_ok'), 'Publish to forbidden topic should fail')
        self.assertEqual(result.get('status'), '401 Unauthorized')

    def test_subscribe_to_forbidden_topic(self):
        client = self.get_client()
        forbidden_topic = self.config.topic_forbidden

        result = client.subscribe(forbidden_topic)
        self.assertFalse(result.get('is_ok'), 'Subscribe to forbidden topic should fail')
        self.assertEqual(result.get('status'), '401 Unauthorized')

# ################################################################################################################################
# ################################################################################################################################
