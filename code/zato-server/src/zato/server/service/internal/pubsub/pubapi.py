# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# rapidjson
from rapidjson import dumps, loads

# Zato
from zato.common import CONTENT_TYPE, PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden
from zato.common.odb.model import PubSubTopic, PubSubEndpoint
from zato.server.service import Int, Service

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY

# ################################################################################################################################

def parse_basic_auth(auth, prefix = 'Basic '):
    if not auth.startswith(prefix):
        raise ValueError('Missing Basic Auth prefix')

    _, auth = auth.split(prefix)
    auth = auth.strip().decode('base64')

    return auth.split(':', 1)

# ################################################################################################################################

class Msg(object):
    __slots__ = ('data', 'topic_name', 'expiration', 'mime_type', 'priority')

    def __init__(self, data=None, topic_name=None, expiration=None, mime_type=None, priority=None):
        self.data = data
        self.topic_name = topic_name
        self.expiration = expiration
        self.mime_type = mime_type
        self.priority = priority

# ################################################################################################################################

class TopicService(Service):
    """ Main service responsible for publications to a given topic. Handles security and distribution
    of messages to target queues.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = (Int('priority'), Int('expiration'), 'mime_type')

# ################################################################################################################################

    def handle_POST(self, _pri_min=_PRIORITY.MIN, _pri_max=_PRIORITY.MAX, _pri_def=_PRIORITY.DEFAULT):

        # Check credentials first
        auth = self.wsgi_environ.get('HTTP_AUTHORIZATION')
        if not auth:
            raise Forbidden(self.cid)

        try:
            username, password = parse_basic_auth(auth)
        except ValueError:
            raise Forbidden(self.cid)

        worker_store = self.server.worker_store
        basic_auth = worker_store.request_dispatcher.url_data.basic_auth_config.itervalues()

        for item in basic_auth:
            config = item['config']
            if config['is_active']:
                if config['username'] == username and config['password'] == password:
                    auth_ok = True
                    security_id = config['id']
                    break
        else:
            auth_ok = False

        if not auth_ok:
            raise Forbidden(self.cid)

        # Local alias
        input = self.request.input

        # Credentials are fine, now check whether that user has access to the topic given on input
        topic_name = input.topic_name

        # Confirm if this client may publish at all to the topic it chose
        if not worker_store.pubsub.is_allowed_pub_topic(topic_name, security_id=security_id):
            raise Forbidden(self.cid)

        # Regardless of mime-type, we always accept it in JSON payload
        try:
            data = loads(self.request.raw_request)
        except ValueError:
            raise BadRequest(self.cid, 'JSON input could not be parsed')

        # Ignore the header set by curl and similar tools
        mime_type = self.wsgi_environ.get('CONTENT_TYPE')
        mime_type = mime_type if mime_type != 'application/x-www-form-urlencoded' else CONTENT_TYPE.JSON

        # Get and validate priority
        priority = input.get('priority')
        if priority:
            if priority < _pri_min or priority > _pri_max:
                raise BadRequest(self.cid, 'Priority `{}` outside of allowed range {}-{}'.format(priority, _pri_min, _pri_max))
        else:
            priority = _pri_def

        # Get and validate expiration
        expiration = input.get('expiration')
        if expiration is not None and expiration < 0:
            raise BadRequest(self.cid, 'Expiration `{}` must not be negative'.format(expiration))

        # Construct the message object now that we have everything validated
        msg = Msg()
        msg.data = data
        msg.topic_name = topic_name
        msg.expiration = expiration
        msg.mime_type = mime_type
        msg.priority = priority

        print(msg.data)

# ################################################################################################################################

