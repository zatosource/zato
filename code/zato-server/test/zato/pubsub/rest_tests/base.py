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

    def __init__(self, username:'str', password:'str') -> 'None':
        self.base_url = TestConfig.base_url
        self.auth = (username, password)
        self.sub_key = None

# ################################################################################################################################

    def publish(self, topic_name:'str', data:'any_') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {'data': data}
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def publish_json(self, topic_name:'str', data:'any_') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {'data': data}
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def publish_empty(self, topic_name:'str') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(url, json={}, auth=self.auth)
        return {'status_code': response.status_code}

# ################################################################################################################################

    def publish_with_priority(self, topic_name:'str', data:'any_', priority:'int') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {
            'data': data,
            'priority': priority
        }
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def publish_with_expiration(self, topic_name:'str', data:'any_', expiration:'int') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {
            'data': data,
            'expiration': expiration
        }
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def publish_with_pub_time(self, topic_name:'str', data:'any_', pub_time:'str') -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {
            'data': data,
            'pub_time': pub_time
        }
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def publish_with_metadata(
        self,
        topic_name:'str',
        data:'any_',
        correl_id:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None
    ) -> 'dict':
        url = f'{self.base_url}/pubsub/topic/{topic_name}'
        payload = {'data': data}
        if correl_id:
            payload['correl_id'] = correl_id
        if in_reply_to:
            payload['in_reply_to'] = in_reply_to
        if ext_client_id:
            payload['ext_client_id'] = ext_client_id
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def subscribe(self, topic_name:'str') -> 'dict':
        url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(url, auth=self.auth)
        response_data = response.json()
        result = response_data.get('response', {})
        if result.get('sub_key'):
            self.sub_key = result['sub_key']
        return result

# ################################################################################################################################

    def get_messages(self, sub_key:'strnone'=None) -> 'dict':
        url = f'{self.base_url}/pubsub/messages/get'
        payload = {'sub_key': sub_key or self.sub_key}
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def get_messages_with_limit(self, max_messages:'intnone'=None, max_len:'intnone'=None) -> 'dict':
        url = f'{self.base_url}/pubsub/messages/get'
        payload = {'sub_key': self.sub_key}
        if max_messages is not None:
            payload['max_messages'] = max_messages
        if max_len is not None:
            payload['max_len'] = max_len
        response = requests.post(url, json=payload, auth=self.auth)
        result = response.json()
        return result.get('response', {})

# ################################################################################################################################

    def unsubscribe(self, topic_name:'str') -> 'dict':
        url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        response = requests.post(url, auth=self.auth)
        response_data = response.json()
        result = response_data.get('response', {})
        if result.get('is_ok'):
            self.sub_key = None
        return result

# ################################################################################################################################
# ################################################################################################################################

class BaseTestCase(unittest.TestCase):

    config = TestConfig

# ################################################################################################################################

    def get_client(self, username:'strnone'=None, password:'strnone'=None) -> 'PubSubTestClient':
        username = username or self.config.user1_username
        password = password or self.config.user1_password
        return PubSubTestClient(username, password)

# ################################################################################################################################

    def get_client2(self) -> 'PubSubTestClient':
        return PubSubTestClient(self.config.user2_username, self.config.user2_password)

# ################################################################################################################################
# ################################################################################################################################
