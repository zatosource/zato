# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestJsonData(BaseTestCase):

    def test_json_object_preserved(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        json_data = {
            'order_id': 12345,
            'status': 'completed',
            'items': ['item1', 'item2'],
            'total': 99.99
        }
        result = client.publish_json(topic, json_data)
        self.assertTrue(result.get('is_ok'), 'Publish JSON should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        data = messages[0].get('data', '')
        if isinstance(data, str):
            data = json.loads(data)
        self.assertEqual(data.get('order_id'), 12345)
        self.assertEqual(data.get('status'), 'completed')

        client.unsubscribe(topic)

    def test_nested_json_preserved(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        json_data = {
            'customer': {
                'name': 'John Doe',
                'address': {
                    'city': 'New York',
                    'zip': '10001'
                }
            }
        }
        result = client.publish_json(topic, json_data)
        self.assertTrue(result.get('is_ok'), 'Publish nested JSON should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        data = messages[0].get('data', '')
        if isinstance(data, str):
            data = json.loads(data)
        self.assertEqual(data.get('customer', {}).get('name'), 'John Doe')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
