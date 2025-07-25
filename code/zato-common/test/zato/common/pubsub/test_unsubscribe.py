# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# requests
import requests

# Zato
from zato.common.pubsub.server.rest import PubSubRESTServer

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubscribe(unittest.TestCase):

    def setUp(self):
        self.server = PubSubRESTServer('localhost', 8080)
        self.server.setup()
        
        # Mock auth
        self.server.users = {'demo': 'demo'}
        
        # Create test topic and subscription
        self.topic_name = 'test.topic'
        self.username = 'demo'
        self.sub_key = 'test-sub-key'
        
        self.server.backend.create_topic('test-cid', 'test', self.topic_name)
        self.server.backend.register_subscription('test-cid', self.topic_name, self.username, self.sub_key)

    def test_unsubscribe_success(self):
        url = f'http://localhost:8080/unsubscribe/{self.topic_name}'
        auth = ('demo', 'demo')
        
        response = requests.post(url, auth=auth, json={'sub_key': self.sub_key})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

# ################################################################################################################################
# ################################################################################################################################
