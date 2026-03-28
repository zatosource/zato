# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests
import requests

# local
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClient:

    def __init__(self, username, password):
        self.base_url = TestConfig.base_url
        self.auth = (username, password)
        self.sub_key = None

# ################################################################################################################################

    def publish(self, topic_name, data):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={'data': data}, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def subscribe(self, topic_name):
        url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(url, auth=self.auth)
        result = response.json().get('response', {})
        if result.get('sub_key'):
            self.sub_key = result['sub_key']
        return result

# ################################################################################################################################

    def get_messages(self, sub_key=None):
        url = f'{self.base_url}/pubsub/messages/get'
        payload = {'sub_key': sub_key or self.sub_key}
        response = requests.post(url, json=payload, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def unsubscribe(self, topic_name):
        url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        response = requests.post(url, auth=self.auth)
        result = response.json().get('response', {})
        if result.get('is_ok'):
            self.sub_key = None
        return result

# ################################################################################################################################
# ################################################################################################################################

class BaseTestCase:

    def __init__(self):
        self.config = TestConfig
        self.errors = []

# ################################################################################################################################

    def get_client(self, username=None, password=None):
        username = username or self.config.user1_username
        password = password or self.config.user1_password
        return PubSubTestClient(username, password)

# ################################################################################################################################

    def assert_true(self, condition, message):
        if not condition:
            self.errors.append(message)
            print(f'FAIL: {message}')
            return False
        return True

# ################################################################################################################################

    def assert_false(self, condition, message):
        return self.assert_true(not condition, message)

# ################################################################################################################################

    def assert_equal(self, actual, expected, message):
        return self.assert_true(actual == expected, f'{message}: expected {expected}, got {actual}')

# ################################################################################################################################

    def run(self):
        raise NotImplementedError()

# ################################################################################################################################

    def execute(self):
        name = self.__class__.__name__
        print(f'=== {name} ===')
        print()

        try:
            self.run()
        except Exception as e:
            self.errors.append(f'Exception: {e}')
            print(f'FAIL: Exception raised: {e}')

        print()
        if self.errors:
            print(f'FAILED: {len(self.errors)} error(s)')
            return False
        else:
            print('PASSED')
            return True

# ################################################################################################################################
# ################################################################################################################################
