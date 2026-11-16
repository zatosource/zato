# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from base64 import b64encode
from http.client import OK
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from zato.common.test.exactly_once.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many messages one pull asks for
_pull_max_messages = 100

# How long a pull for one message is repeated and how often, in seconds
_pull_timeout = 30.0
_poll_seconds = 0.2

# ################################################################################################################################
# ################################################################################################################################

class HTTPResult(NamedTuple):
    """ The status code and the parsed body of one HTTP response.
    """
    status_code: 'int'
    body: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

def post_json(path:'str', username:'str', password:'str', payload:'any_') -> 'HTTPResult':
    """ Sends one request with basic authentication and returns its status code and its parsed body.
    """
    url = f'{TestConfig.base_url}{path}'

    # Serialize the request ..
    serialized = json.dumps(payload)
    body = serialized.encode()

    # .. build the credentials ..
    credentials = f'{username}:{password}'
    credentials = credentials.encode()
    credentials = b64encode(credentials)
    credentials = credentials.decode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {credentials}')
    request.add_header('Content-Type', 'application/json')

    # .. send the request, with an error status read in the same way as a success ..
    try:
        with urlopen(request) as response:
            response_data = response.read()
            status_code = response.status
    except HTTPError as error:
        response_data = error.read()
        status_code = error.code

    # .. and parse the response.
    if response_data:
        response_body = json.loads(response_data)
    else:
        response_body = {}

    out = HTTPResult(status_code, response_body)
    return out

# ################################################################################################################################

def publish(username:'str', password:'str', topic_name:'str', payload:'anydict') -> 'HTTPResult':
    """ Publishes one message over REST and returns the response.
    """
    path = f'/pubsub/topic/{topic_name}'

    out = post_json(path, username, password, payload)
    return out

# ################################################################################################################################

def pull(username:'str', password:'str') -> 'anylist':
    """ Pulls the messages that the queue of the user has, without acknowledging them.
    """
    payload = {'max_messages': _pull_max_messages}
    result = post_json('/pubsub/messages/get', username, password, payload)

    assert result.status_code == OK, result

    out = result.body['messages']
    return out

# ################################################################################################################################

def ack(username:'str', password:'str', payload:'anydict') -> 'HTTPResult':
    """ Sends one acknowledgement and returns the response.
    """
    out = post_json('/pubsub/messages/ack', username, password, payload)
    return out

# ################################################################################################################################

def drain(username:'str', password:'str') -> 'anylist':
    """ Pulls and acknowledges messages until the queue of the user is empty, and returns all of them.
    """
    out:'anylist' = []

    while True:
        messages = pull(username, password)

        if not messages:
            break

        msg_ids:'strlist' = []

        for message in messages:
            meta = message['meta']
            msg_ids.append(meta['msg_id'])

        payload = {'msg_ids': msg_ids}
        result = ack(username, password, payload)

        assert result.status_code == OK, result

        out.extend(messages)

    return out

# ################################################################################################################################

def pull_by_key(username:'str', password:'str', key:'str') -> 'anydict':
    """ Pulls messages without acknowledging them until one whose data has the given key is handed out, and returns it.
    """
    deadline = time.monotonic() + _pull_timeout

    out:'anydict' = {}

    while not out:

        messages = pull(username, password)

        for message in messages:
            data = message['data']
            if data['key'] == key:
                out = message
                break

        # A pull without the message is repeated after a while, until the deadline.
        else:
            if time.monotonic() > deadline:
                raise Exception(f'No message with key `{key}` within {_pull_timeout}s')

            time.sleep(_poll_seconds)

    return out

# ################################################################################################################################

def get_correl_ids(messages:'anylist', prefix:'str') -> 'strlist':
    """ Returns the correlation ID of each message that starts with the prefix, in the order of the messages.
    """
    out:'strlist' = []

    for message in messages:
        meta = message['meta']

        if correl_id := meta.get('correl_id'):
            if correl_id.startswith(prefix):
                out.append(correl_id)

    return out

# ################################################################################################################################
# ################################################################################################################################
