# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestAuth(BaseTestCase):

    def test_publish_with_wrong_password(self):
        topic = self.config.topic_allowed
        client = self.get_client(self.config.user1_username, 'wrong_password')

        result = client.publish(topic, 'test message')
        self.assertFalse(result.get('is_ok'), 'Publish with wrong password should fail')
        self.assertEqual(result.get('status'), '401 Unauthorized')
        self.assertEqual(result.get('http_status_code'), 401)

    def test_subscribe_with_wrong_password(self):
        topic = self.config.topic_allowed
        client = self.get_client(self.config.user1_username, 'wrong_password')

        result = client.subscribe(topic)
        self.assertFalse(result.get('is_ok'), 'Subscribe with wrong password should fail')
        self.assertEqual(result.get('status'), '401 Unauthorized')
        self.assertEqual(result.get('http_status_code'), 401)

    def test_publish_with_nonexistent_user(self):
        topic = self.config.topic_allowed
        client = self.get_client('nonexistent_user', 'some_password')

        result = client.publish(topic, 'test message')
        self.assertFalse(result.get('is_ok'), 'Publish with non-existent user should fail')
        self.assertEqual(result.get('status'), '401 Unauthorized')
        self.assertEqual(result.get('http_status_code'), 401)

    def test_get_messages_with_wrong_password(self):
        client = self.get_client(self.config.user1_username, 'wrong_password')

        result = client.get_messages()
        self.assertFalse(result['is_ok'])
        self.assertEqual(result['status'], '401 Unauthorized')
        self.assertEqual(result['http_status_code'], 401)

    def test_get_messages_with_nonexistent_user(self):
        client = self.get_client('nonexistent_user', 'some_password')

        result = client.get_messages()
        self.assertFalse(result['is_ok'])
        self.assertEqual(result['status'], '401 Unauthorized')
        self.assertEqual(result['http_status_code'], 401)

# ################################################################################################################################
# ################################################################################################################################
