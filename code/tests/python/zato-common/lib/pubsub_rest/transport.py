# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# requests
from requests import Session

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The REST paths of pub/sub - publication, pulling and acknowledgment.
Publish_Path_Prefix = '/pubsub/topic/'
Pull_Path = '/pubsub/messages/get'
Ack_Path = '/pubsub/messages/ack'

# How long one request may take, in seconds.
_request_timeout = 120

# The lowest status code of an error response.
_min_error_status = 400

# ################################################################################################################################
# ################################################################################################################################

class Credentials(NamedTuple):
    """ The basic authentication credentials of one API client.
    """
    username: 'str'
    password: 'str'

credentials_list = list[Credentials]

# ################################################################################################################################

class Response(NamedTuple):
    """ The status code and the parsed body of one response.
    """
    status: 'int'
    body: 'any_'

# ################################################################################################################################
# ################################################################################################################################

class RESTClient:
    """ One API client of the pub/sub REST interface of a server, with a persistent connection of its own.
    """

    def __init__(self, base_url:'str', credentials:'Credentials') -> 'None':
        self.base_url = base_url
        self.credentials = credentials

        self.session = Session()
        self.session.auth = (credentials.username, credentials.password)

# ################################################################################################################################

    def post(self, path:'str', payload:'anydict') -> 'Response':
        """ Sends one request and returns its status code and its body, whatever the status code is.
        """
        url = f'{self.base_url}{path}'
        response = self.session.post(url, json=payload, timeout=_request_timeout)

        if response.content:
            body = response.json()
        else:
            body = {}

        out = Response(response.status_code, body)
        return out

# ################################################################################################################################

    def post_ok(self, path:'str', payload:'anydict') -> 'anydict':
        """ Sends one request and returns its body, raising an exception on an error response.
        """
        response = self.post(path, payload)

        if response.status >= _min_error_status:
            raise Exception(f'{path} returned HTTP {response.status}: {response.body}')

        out = response.body
        return out

# ################################################################################################################################

    def publish(self, topic_name:'str', payload:'anydict') -> 'anydict':
        """ Publishes one message and returns the body of the response, which holds its msg_id.
        """
        path = f'{Publish_Path_Prefix}{topic_name}'

        out = self.post_ok(path, payload)
        return out

# ################################################################################################################################

    def pull(self, max_messages:'int', max_len:'int') -> 'anydict':
        """ Pulls the messages of the subscriptions of this client, leasing them until they are acknowledged.
        """
        payload = {
            'max_messages': max_messages,
            'max_len': max_len,
        }

        out = self.post_ok(Pull_Path, payload)
        return out

# ################################################################################################################################

    def ack(self, msg_ids:'any_') -> 'anydict':
        """ Acknowledges pulled messages, which removes them from the queues of this client.
        """
        out = self.post_ok(Ack_Path, {'msg_ids': msg_ids})
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################
