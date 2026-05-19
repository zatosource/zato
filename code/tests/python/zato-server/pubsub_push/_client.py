# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from base64 import b64encode
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.client')

# ################################################################################################################################
# ################################################################################################################################

class PublishRawResult(NamedTuple):
    status_code: int
    body: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

class PublishClient:
    """ Publishes messages to a Zato pub/sub topic via REST.
    """

    def __init__(self, base_url:'str', username:'str', password:'str') -> 'None':
        self.base_url = base_url
        credentials = f'{username}:{password}'
        credentials_bytes = credentials.encode()
        encoded = b64encode(credentials_bytes)
        self._auth = encoded.decode()

# ################################################################################################################################

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        priority:'int'=0,
        expiration:'int'=0,
        correl_id:'str'='',
        in_reply_to:'str'='',
        ext_client_id:'str'='',
        pub_time:'str'='',
        ) -> 'anydict':
        """ Publishes a message to the given topic and returns the response dict.
        """
        url = f'{self.base_url}/pubsub/topic/{topic_name}'

        payload:'anydict' = {
            'data': data,
        }

        if priority:
            payload['priority'] = priority

        if expiration:
            payload['expiration'] = expiration

        if correl_id:
            payload['correl_id'] = correl_id

        if in_reply_to:
            payload['in_reply_to'] = in_reply_to

        if ext_client_id:
            payload['ext_client_id'] = ext_client_id

        if pub_time:
            payload['pub_time'] = pub_time

        serialized = json.dumps(payload)
        body = serialized.encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        logger.info('Publishing to %s: %s', topic_name, payload)

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'Publish to {topic_name} returned HTTP {error.code}: {error_text}')

        out = json.loads(raw)
        logger.info('Publish response from %s: %s', topic_name, out)
        return out

# ################################################################################################################################

    def publish_raw(self, topic_name:'str', data:'any_', username:'str'='', password:'str'='') -> 'PublishRawResult':
        """ Publishes with custom credentials and returns a PublishRawResult.
        Used for negative tests with wrong credentials.
        """
        url = f'{self.base_url}/pubsub/topic/{topic_name}'

        payload:'anydict' = {
            'data': data,
        }

        serialized = json.dumps(payload)
        body = serialized.encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Content-Type', 'application/json')

        if username:
            credentials = f'{username}:{password}'
            credentials_bytes = credentials.encode()
            encoded = b64encode(credentials_bytes)
            auth = encoded.decode()
            request.add_header('Authorization', f'Basic {auth}')

        logger.info('Publishing raw to %s (username=%s)', topic_name, username)

        try:
            with urlopen(request) as response:
                raw = response.read()
                status_code = response.status
        except HTTPError as error:
            raw = error.read()
            status_code = error.code

        if raw:
            response_body = json.loads(raw)
        else:
            response_body = {}

        logger.info('Raw publish result: status=%d, body=%s', status_code, response_body)

        out = PublishRawResult(status_code=status_code, body=response_body)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PullClient:
    """ Pulls messages from Zato pub/sub via REST.
    """

    def __init__(self, base_url:'str', username:'str', password:'str') -> 'None':
        self.base_url = base_url
        credentials = f'{username}:{password}'
        credentials_bytes = credentials.encode()
        encoded = b64encode(credentials_bytes)
        self._auth = encoded.decode()

# ################################################################################################################################

    def pull(self, max_messages:'int'=0, max_len:'int'=0) -> 'anydict':
        """ Pulls messages and returns the response dict.
        """
        url = f'{self.base_url}/pubsub/messages/get'

        payload:'anydict' = {}

        if max_messages:
            payload['max_messages'] = max_messages

        if max_len:
            payload['max_len'] = max_len

        serialized = json.dumps(payload)
        body = serialized.encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        logger.info('Pulling messages: %s', payload)

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'Pull returned HTTP {error.code}: {error_text}')

        out = json.loads(raw)
        logger.info('Pull response: %s', out)
        return out

# ################################################################################################################################

    def drain(self) -> 'None':
        """ Pulls messages until the queue is empty.
        """
        drained_count = 0

        while True:
            result = self.pull(max_messages=50)
            message_count = result['message_count']
            if message_count == 0:
                break
            drained_count += message_count

        logger.info('Drained %d messages', drained_count)

# ################################################################################################################################
# ################################################################################################################################
