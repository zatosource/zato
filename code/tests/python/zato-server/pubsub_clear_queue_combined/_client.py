# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue_combined.client')

# ################################################################################################################################
# ################################################################################################################################

class PublishClient:
    """ Publishes messages to a Zato pub/sub topic via REST.
    """

    def __init__(self, base_url:'str', username:'str', password:'str') -> 'None':
        self.base_url = base_url
        credentials = f'{username}:{password}'
        self._auth = b64encode(credentials.encode()).decode()

# ################################################################################################################################

    def publish(self, topic_name:'str', data:'any_', expiration:'int'=0) -> 'anydict':
        """ Publishes a message to the given topic.
        """
        url = f'{self.base_url}/pubsub/topic/{topic_name}'

        payload:'anydict' = {'data': data}

        if expiration:
            payload['expiration'] = expiration

        body = json.dumps(payload).encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'Publish to {topic_name} returned HTTP {error.code}: {error_text}')

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PullClient:
    """ Pulls messages from Zato pub/sub via REST.
    """

    def __init__(self, base_url:'str', username:'str', password:'str') -> 'None':
        self.base_url = base_url
        credentials = f'{username}:{password}'
        self._auth = b64encode(credentials.encode()).decode()

# ################################################################################################################################

    def pull(self, max_messages:'int'=50) -> 'anydict':
        """ Pulls messages and returns the response dict.
        """
        url = f'{self.base_url}/pubsub/messages/get'

        payload:'anydict' = {'max_messages': max_messages}
        body = json.dumps(payload).encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'Pull returned HTTP {error.code}: {error_text}')

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class AdminClient:
    """ Invokes Zato admin services via the REST API.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        credentials = f'admin.invoke:{password}'
        self._auth = b64encode(credentials.encode()).decode()

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'anydict'=None) -> 'anydict':
        """ Invokes a Zato service and returns the response.
        """
        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode() if payload else b'{}'

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################
