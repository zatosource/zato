# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestInvalidTopicName(BaseTestCase):

    def test_topic_name_with_hash_rejected(self):
        client = self.get_client()
        topic = 'invalid#topic'

        result = client.publish(topic, 'test message')

        self.assertFalse(result.get('is_ok'), 'Publish to topic with # should fail')

    def test_topic_name_too_long_rejected(self):
        client = self.get_client()
        topic = 'a' * 201

        result = client.publish(topic, 'test message')

        self.assertFalse(result.get('is_ok'), 'Publish to topic > 200 chars should fail')

# ################################################################################################################################
# ################################################################################################################################
