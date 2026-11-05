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
    from zato.common.typing_ import any_, anydict, anydictnone, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.common.test.client')

# ################################################################################################################################
# ################################################################################################################################

class PublishResult(NamedTuple):
    status_code: int
    body: 'anydict'

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

    def _invoke(self, service_name:'str', payload:'anydictnone'=None) -> 'tuple':
        """ Invokes a service and returns both the parsed body and response headers.
        """
        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode() if payload else b'{}'

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                data = response.read()
                headers = dict(response.headers)
        except HTTPError as error:
            data = error.read()
            error_text = data.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not data:
            return {}, headers

        out = json.loads(data)
        return out, headers

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'anydictnone'=None) -> 'anydict':
        """ Invokes a Zato service and returns the response.
        """
        out, _ = self._invoke(service_name, payload)
        return out

# ################################################################################################################################

    def create(self, service_name:'str', **kwargs:'any_') -> 'anydict':
        """ Convenience wrapper that invokes a create service.
        """
        return self.invoke(service_name, kwargs)

# ################################################################################################################################

    def edit(self, service_name:'str', **kwargs:'any_') -> 'anydict':
        """ Convenience wrapper that invokes an edit service.
        """
        return self.invoke(service_name, kwargs)

# ################################################################################################################################

    def delete(self, service_name:'str', **kwargs:'any_') -> 'anydict':
        """ Convenience wrapper that invokes a delete service.
        """
        return self.invoke(service_name, kwargs)

# ################################################################################################################################

    def get_list(self, service_name:'str', **kwargs:'any_') -> 'tuple':
        """ Invokes a get-list service and returns (data_list, meta_dict).
        """
        response, headers = self._invoke(service_name, kwargs)

        meta:'anydict' = {}

        if cur_page := headers.get('X-Zato-Page-Current'):
            meta['cur_page'] = cur_page

        if page_size := headers.get('X-Zato-Page-Size'):
            meta['page_size'] = page_size

        if num_pages := headers.get('X-Zato-Page-Total'):
            meta['num_pages'] = num_pages

        if total := headers.get('X-Zato-Result-Total'):
            meta['total'] = total

        out = response, meta
        return out

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

    def _publish(self, topic_name:'str', data:'any_', username:'str'='', password:'str'='') -> 'PublishResult':
        """ Publishes with custom credentials and returns a PublishResult.
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

        logger.info('Publishing to %s (username=%s)', topic_name, username)

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

        logger.info('Publish result: status=%d, body=%s', status_code, response_body)

        out = PublishResult(status_code=status_code, body=response_body)
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

    def _post(self, path:'str', payload:'anydict') -> 'anydict':
        """ Sends one authenticated request to a pub/sub endpoint and returns the response dict.
        """
        url = f'{self.base_url}{path}'

        serialized = json.dumps(payload)
        body = serialized.encode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{path} returned HTTP {error.code}: {error_text}')

        out = json.loads(raw)
        return out

# ################################################################################################################################

    def pull(self, max_messages:'int'=0, max_len:'int'=0, needs_ack:'bool'=True) -> 'anydict':
        """ Pulls messages and returns the response dict. With needs_ack, the messages are acknowledged
        as soon as they are received, otherwise the caller acknowledges them through ack.
        """
        payload:'anydict' = {}

        if max_messages:
            payload['max_messages'] = max_messages

        if max_len:
            payload['max_len'] = max_len

        logger.info('Pulling messages: %s', payload)

        out = self._post('/pubsub/messages/get', payload)
        logger.info('Pull response: %s', out)

        if needs_ack:
            msg_ids:'strlist' = []

            for message in out['messages']:
                msg_ids.append(message['meta']['msg_id'])

            if msg_ids:
                _ = self.ack(msg_ids)

        return out

# ################################################################################################################################

    def ack(self, msg_ids:'strlist') -> 'anydict':
        """ Acknowledges pulled messages and returns the response dict.
        """
        out = self._post('/pubsub/messages/ack', {'msg_ids': msg_ids})
        logger.info('Ack response: %s', out)
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
