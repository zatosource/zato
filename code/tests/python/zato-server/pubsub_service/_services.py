# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This file is hot-deployed into a test Zato server by conftest.py.
# It defines two receiver services used by the pubsub_service live tests.

_simple_received = []
_typed_received = []

# ################################################################################################################################
# ################################################################################################################################

from dataclasses import dataclass

from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestSimpleReceiver(Service):
    """ Receives a pub/sub push message and stores the raw request input.
    """

    name = 'test.pubsub.simple-receiver'

    def handle(self) -> 'None':
        _simple_received.append(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CustomerInput(Model):
    customer_name: str = ''
    customer_id: int = 0

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestTypedReceiver(Service):
    """ Receives a pub/sub push message and stores the typed input.
    """

    name = 'test.pubsub.typed-receiver'

    class IO:
        input = CustomerInput

    def handle(self) -> 'None':
        _typed_received.append(self.request.input)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetReceived(Service):
    """ Returns what the simple and typed receivers have collected so far.
    """

    name = 'test.pubsub.get-received'

    def handle(self) -> 'None':
        from json import dumps

        out = {
            'simple_count': len(_simple_received),
            'typed_count': len(_typed_received),
            'simple': [str(item) for item in _simple_received],
            'typed': [str(item) for item in _typed_received],
        }

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearReceived(Service):
    """ Clears the received message stores.
    """

    name = 'test.pubsub.clear-received'

    def handle(self) -> 'None':
        _simple_received.clear()
        _typed_received.clear()

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestPublishToService(Service):
    """ Publishes a message to a topic_name via the pubsub facade.
    Called by the test harness via admin.invoke.
    """

    name = 'test.pubsub.publish-to-service'

    def handle(self) -> 'None':
        from json import dumps, loads

        topic_name = self.request.raw_request['topic_name']
        data = self.request.raw_request['data']

        result = self.pubsub.publish(topic_name, data)

        out = {
            'msg_id': result.msg_id,
        }

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCheckRedisTopics(Service):
    """ Returns a list of Redis stream keys matching the service topic prefix.
    Used by tests to verify implicit topic creation.
    """

    name = 'test.pubsub.check-redis-topics'

    def handle(self) -> 'None':
        from json import dumps

        redis = self.server.pubsub_redis.redis

        prefix = 'zato:pubsub:stream:zato.s.to.'
        keys = redis.keys(prefix + '*')

        topic_names = []

        for key in keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            topic_name = key.replace('zato:pubsub:stream:', '')
            topic_names.append(topic_name)

        self.response.payload = dumps({'topics': topic_names})

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCheckSubscriptions(Service):
    """ Returns the count of subscription keys in the server's _push_subs dict.
    """

    name = 'test.pubsub.check-subscriptions'

    def handle(self) -> 'None':
        from json import dumps

        push_subs = self.server._push_subs
        sub_keys = list(push_subs.keys())

        self.response.payload = dumps({
            'count': len(sub_keys),
            'sub_keys': sub_keys,
        })

# ################################################################################################################################
# ################################################################################################################################
