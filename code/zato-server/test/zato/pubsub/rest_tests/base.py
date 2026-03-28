# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

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

    def publish_json(self, topic_name, data):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={'data': data}, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def publish_empty(self, topic_name):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={}, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def publish_with_priority(self, topic_name, data, priority):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={'data': data, 'priority': priority}, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def publish_with_expiration(self, topic_name, data, expiration):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={'data': data, 'expiration': expiration}, auth=self.auth)
        return response.json().get('response', {})

# ################################################################################################################################

    def publish_with_metadata(self, topic_name, data, correl_id=None, in_reply_to=None, ext_client_id=None):
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {'data': data}
        if correl_id:
            payload['correl_id'] = correl_id
        if in_reply_to:
            payload['in_reply_to'] = in_reply_to
        if ext_client_id:
            payload['ext_client_id'] = ext_client_id
        response = requests.post(url, json=payload, auth=self.auth)
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

    def get_messages_with_limit(self, max_messages=None, max_len=None):
        url = f'{self.base_url}/pubsub/messages/get'
        payload = {'sub_key': self.sub_key}
        if max_messages is not None:
            payload['max_messages'] = max_messages
        if max_len is not None:
            payload['max_len'] = max_len
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

class BaseTestCase(unittest.TestCase):

    config = TestConfig

# ################################################################################################################################

    def get_client(self, username=None, password=None):
        username = username or self.config.user1_username
        password = password or self.config.user1_password
        return PubSubTestClient(username, password)

# ################################################################################################################################
# ################################################################################################################################
