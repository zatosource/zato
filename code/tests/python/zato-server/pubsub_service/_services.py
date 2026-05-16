# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This file is hot-deployed into a test Zato server by conftest.py.
# It defines receiver and chain services used by the pubsub_service live tests.

_simple_received = []
_typed_received = []

_chain_received = []
_fanout_1_received = []
_fanout_2_received = []
_typed_chain_received = []

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
        from json import dumps

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

class PubSubTestChainA(Service):
    """ First hop in a two-service chain. Appends '-via-a' and publishes to chain-b.
    """

    name = 'test.pubsub.chain-a'

    def handle(self) -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        forwarded = str(data) + '-via-a'
        _ = self.pubsub.publish('test.pubsub.chain-b', forwarded)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestChainB(Service):
    """ Second hop in a two-service chain. Appends '-via-b' and stores the result.
    """

    name = 'test.pubsub.chain-b'

    def handle(self) -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        result = str(data) + '-via-b'
        _chain_received.append(result)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestFanoutSource(Service):
    """ Receives a message and publishes it to two target services.
    """

    name = 'test.pubsub.fanout-source'

    def handle(self) -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        _ = self.pubsub.publish('test.pubsub.fanout-target-1', data)
        _ = self.pubsub.publish('test.pubsub.fanout-target-2', data)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestFanoutTarget1(Service):
    """ First fanout target. Stores received data.
    """

    name = 'test.pubsub.fanout-target-1'

    def handle(self) -> 'None':
        _fanout_1_received.append(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestFanoutTarget2(Service):
    """ Second fanout target. Stores received data.
    """

    name = 'test.pubsub.fanout-target-2'

    def handle(self) -> 'None':
        _fanout_2_received.append(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestTypedChainSource(Service):
    """ Receives data and publishes it to a typed sink service.
    """

    name = 'test.pubsub.typed-chain-source'

    def handle(self) -> 'None':
        from json import loads as json_loads

        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)

        # .. if the data is a JSON string, parse it into a dict
        # .. so the downstream typed service can parse it against IO.input ..
        if isinstance(data, str):
            try:
                data = json_loads(data)
            except (ValueError, TypeError):
                pass

        _ = self.pubsub.publish('test.pubsub.typed-chain-sink', data)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestTypedChainSink(Service):
    """ Typed sink that receives a CustomerInput dict from a chain and validates the fields.
    """

    name = 'test.pubsub.typed-chain-sink'

    def handle(self) -> 'None':
        from json import loads as json_loads

        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)

        # .. if data is a JSON string, parse it ..
        if isinstance(data, str):
            try:
                data = json_loads(data)
            except (ValueError, TypeError):
                pass

        # .. create a CustomerInput from the data dict ..
        if isinstance(data, dict):
            customer = CustomerInput()
            customer.customer_name = data['customer_name']
            customer.customer_id = data['customer_id']
            _typed_chain_received.append(customer)
        else:
            _typed_chain_received.append(data)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetChainReceived(Service):
    """ Returns what the chain, fanout, and typed-chain receivers have collected.
    """

    name = 'test.pubsub.get-chain-received'

    def handle(self) -> 'None':
        from json import dumps

        out = {
            'chain_count': len(_chain_received),
            'fanout_1_count': len(_fanout_1_received),
            'fanout_2_count': len(_fanout_2_received),
            'typed_chain_count': len(_typed_chain_received),
            'chain': [str(item) for item in _chain_received],
            'fanout_1': [str(item) for item in _fanout_1_received],
            'fanout_2': [str(item) for item in _fanout_2_received],
            'typed_chain': [str(item) for item in _typed_chain_received],
        }

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearChainReceived(Service):
    """ Clears all chain-related received message stores.
    """

    name = 'test.pubsub.clear-chain-received'

    def handle(self) -> 'None':
        _chain_received.clear()
        _fanout_1_received.clear()
        _fanout_2_received.clear()
        _typed_chain_received.clear()

# ################################################################################################################################
# ################################################################################################################################
#
#  20 auto-generated services for pub/sub stress testing
#
# ################################################################################################################################
# ################################################################################################################################

# .. routing table for 20 services that publish to each other ..
# .. keys are short names like 'service-01', values are lists of downstream targets ..
# .. an empty list means the service is a sink ..
# .. the string '_ring' means the service republishes to itself with a TTL counter ..

_pad = 5

def _service_name(number:'int') -> 'str':
    """ Returns a zero-padded service short name like 'service-00001'. """
    out = f'service-{number:0{_pad}d}'
    return out

_service_routing = {
    _service_name(1):  [_service_name(2)],
    _service_name(2):  [_service_name(3)],
    _service_name(3):  [_service_name(4)],
    _service_name(4):  [_service_name(5)],
    _service_name(5):  [],
    _service_name(6):  [_service_name(7), _service_name(8), _service_name(9), _service_name(10)],
    _service_name(7):  [],
    _service_name(8):  [],
    _service_name(9):  [],
    _service_name(10): [],
    _service_name(11): [_service_name(15)],
    _service_name(12): [_service_name(15)],
    _service_name(13): [_service_name(15)],
    _service_name(14): [_service_name(15)],
    _service_name(15): [],
    _service_name(16): [_service_name(17), _service_name(18)],
    _service_name(17): [_service_name(19)],
    _service_name(18): [_service_name(19)],
    _service_name(19): [],
    _service_name(20): '_ring',
}

# .. add service-00021 through service-00320 as sinks for the 300-parallel test ..
for _number in range(21, 321):
    _service_routing[_service_name(_number)] = []

# .. per-service received lists, keyed by short name ..
_service_received = {}

for _short_name in _service_routing:
    _service_received[_short_name] = []

# ################################################################################################################################
# ################################################################################################################################

def _make_forwarder_handle(short_name:'str', targets:'list | str') -> 'object':
    """ Builds a handle method that appends a suffix and publishes to downstream targets.
    """

    suffix = '-via-' + short_name.split('-')[1]
    full_targets = []
    for target in targets:
        full_targets.append('test.pubsub.' + target)

    def handle(self:'Service') -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        forwarded = str(data) + suffix
        for target_name in full_targets:
            _ = self.pubsub.publish(target_name, forwarded)

    return handle

# ################################################################################################################################

def _make_sink_handle(short_name:'str') -> 'object':
    """ Builds a handle method that appends a suffix and stores the result.
    """

    suffix = '-via-' + short_name.split('-')[1]
    received_list = _service_received[short_name]

    def handle(self:'Service') -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        result = str(data) + suffix
        received_list.append(result)

    return handle

# ################################################################################################################################

def _make_ring_handle(short_name:'str') -> 'object':
    """ Builds a handle method for the ring topology that decrements TTL and republishes to itself.
    """

    from json import dumps as json_dumps
    from json import loads as json_loads

    suffix = '-via-' + short_name.split('-')[1]
    full_name = 'test.pubsub.' + short_name
    received_list = _service_received[short_name]

    def handle(self:'Service') -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)

        # .. parse the JSON envelope with data and ttl fields ..
        if isinstance(data, str):
            try:
                parsed = json_loads(data)
            except (ValueError, TypeError):
                parsed = {'data': data, 'ttl': 0}
        else:
            parsed = data

        payload = str(parsed['data']) + suffix
        ttl = int(parsed['ttl'])

        # .. if ttl is still positive, republish to self with decremented ttl ..
        if ttl > 1:
            envelope = json_dumps({'data': payload, 'ttl': ttl - 1})
            _ = self.pubsub.publish(full_name, envelope)
        else:
            received_list.append(payload)

    return handle

# ################################################################################################################################

# .. dynamically create all 20 service classes ..

for _short_name, _targets in _service_routing.items():

    _full_service_name = 'test.pubsub.' + _short_name
    _class_name = 'PubSubTestService' + _short_name.replace('-', '').title()

    if _targets == '_ring':
        _handle = _make_ring_handle(_short_name)
    elif _targets:
        _handle = _make_forwarder_handle(_short_name, _targets)
    else:
        _handle = _make_sink_handle(_short_name)

    _cls = type(_class_name, (Service,), {
        'name': _full_service_name,
        'handle': _handle,
    })

    globals()[_class_name] = _cls

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetServiceReceived(Service):
    """ Returns what all service sink services have collected.
    """

    name = 'test.pubsub.get-service-received'

    def handle(self) -> 'None':
        from json import dumps

        out = {}

        for short_name, received_list in _service_received.items():
            out[short_name + '_count'] = len(received_list)
            items = []
            for item in received_list:
                items.append(str(item))
            out[short_name] = items

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearServiceReceived(Service):
    """ Clears all service received message stores.
    """

    name = 'test.pubsub.clear-service-received'

    def handle(self) -> 'None':
        for received_list in _service_received.values():
            received_list.clear()

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestResetServiceStreams(Service):
    """ Deletes all service-related Redis streams and consumer groups, and removes
    their entries from the server's push subscription and topic caches,
    so the next publish recreates everything from scratch.
    """

    name = 'test.pubsub.reset-service-streams'

    def handle(self) -> 'None':
        from json import dumps

        redis = self.server.pubsub_redis.redis
        prefix = 'zato:pubsub:stream:zato.s.to.test.pubsub.service-'
        keys = redis.keys(prefix + '*')

        deleted_count = 0

        for key in keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            _ = redis.delete(key)
            deleted_count += 1

        # .. also clean up the server's in-memory caches ..
        for short_name in _service_routing:
            service_name = 'test.pubsub.' + short_name
            sub_key = 'zato.service.' + service_name

            # .. stop the delivery greenlet if running ..
            if hasattr(self.server, 'pubsub_push_delivery'):
                self.server.pubsub_push_delivery.stop_sub_key(sub_key)

            # .. remove from push subs ..
            _ = self.server._push_subs.pop(sub_key, None)

            # .. remove from topic cache ..
            _ = self.server._service_topic_cache.discard(service_name)

        # .. clear the in-memory received lists too ..
        for received_list in _service_received.values():
            received_list.clear()

        self.response.payload = dumps({'deleted_streams': deleted_count})

# ################################################################################################################################
# ################################################################################################################################
