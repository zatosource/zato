# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps as json_dumps, loads as json_loads

# Zato
from zato.common.test.received_store import clear as _clear, read_items as _read, record as _record
from zato.input_output import ServiceInput
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

# This file is hot-deployed into a test Zato server by conftest.py.
# It defines receiver and chain services used by the pubsub_service live tests.

_store_simple      = 'simple'
_store_typed       = 'typed'
_store_input       = 'input'
_store_chain       = 'chain'
_store_fanout_1    = 'fanout-1'
_store_fanout_2    = 'fanout-2'
_store_typed_chain = 'typed-chain'

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestSimpleReceiver(Service):
    """ Receives a pub/sub push message and stores the raw request input.
    """

    name = 'test.pubsub.simple-receiver'

    def handle(self) -> 'None':
        _record(self, _store_simple, str(self.request.raw_request))

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
        _record(self, _store_typed, str(self.request.input))

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OrderEvent(Model):
    order_id: str = ''
    status: str = ''
    amount: float = 0.0

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestInputReceiver(Service):
    """ Receives a pub/sub push message and stores what the request's input and raw attributes hold.
    """

    name = 'test.pubsub.input-receiver'

    def handle(self) -> 'None':

        input = self.request.input

        # The input is reported as a dict for both a ServiceInput and a Model, and as it is otherwise
        if isinstance(input, (Model, ServiceInput)):
            input_value = input.to_dict()
        else:
            input_value = input

        _record(self, _store_input, {
            'input_type': type(input).__name__,
            'input': input_value,
            'raw_type': type(self.request.raw).__name__,
            'raw': str(self.request.raw),
        })

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestPublishEvent(Service):
    """ Publishes to the input receiver a dict, a text or an OrderEvent instance, as the kind field says.
    """

    name = 'test.pubsub.publish-event'

    def handle(self) -> 'None':
        kind = self.request.input.kind
        data = self.request.input.data

        if kind == 'model':
            event = OrderEvent()
            event.order_id = data['order_id']
            event.status = data['status']
            event.amount = data['amount']
            data = event

        result = self.pubsub.publish('test.pubsub.input-receiver', data)

        self.response.payload = json_dumps({'msg_id': result.msg_id})

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetInputReceived(Service):
    """ Returns what the input receiver has collected so far.
    """

    name = 'test.pubsub.get-input-received'

    def handle(self) -> 'None':
        received = _read(self, _store_input)

        out = {
            'count': len(received),
            'received': received,
        }

        self.response.payload = json_dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearInputReceived(Service):
    """ Clears what the input receiver has collected.
    """

    name = 'test.pubsub.clear-input-received'

    def handle(self) -> 'None':
        _clear(self, _store_input)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetReceived(Service):
    """ Returns what the simple and typed receivers have collected so far.
    """

    name = 'test.pubsub.get-received'

    def handle(self) -> 'None':
        simple = _read(self, _store_simple)
        typed = _read(self, _store_typed)

        out = {
            'simple_count': len(simple),
            'typed_count': len(typed),
            'simple': simple,
            'typed': typed,
        }

        self.response.payload = json_dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearReceived(Service):
    """ Clears the received message stores.
    """

    name = 'test.pubsub.clear-received'

    def handle(self) -> 'None':
        _clear(self, _store_simple)
        _clear(self, _store_typed)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestPublishToService(Service):
    """ Publishes a message to a topic_name via the pubsub facade.
    Called by the test harness via admin.invoke.
    """

    name = 'test.pubsub.publish-to-service'

    def handle(self) -> 'None':
        topic_name = self.request.raw_request['topic_name']
        data = self.request.raw_request['data']

        result = self.pubsub.publish(topic_name, data)

        out = {
            'msg_id': result.msg_id,
        }

        self.response.payload = json_dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCheckTopics(Service):
    """ Returns the names of the service topics that hold any rows in the pub/sub database.
    Used by tests to verify implicit topic creation.
    """

    name = 'test.pubsub.check-topics'

    def handle(self) -> 'None':
        prefix = 'zato.s.to.'
        all_topics = self.server.pubsub_backend.get_topics_with_messages()

        topic_names = []

        for topic_name in all_topics:
            if topic_name.startswith(prefix):
                topic_names.append(topic_name)

        self.response.payload = json_dumps({'topics': topic_names})

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCheckSubscriptions(Service):
    """ Returns the subscription keys of service topics that the pub/sub database holds.
    """

    name = 'test.pubsub.check-subscriptions'

    def handle(self) -> 'None':

        sub_keys = self.server.pubsub_backend.get_sub_keys_by_prefix('zato.service.')

        self.response.payload = json_dumps({
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
        _record(self, _store_chain, result)

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
        _record(self, _store_fanout_1, str(self.request.raw_request))

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestFanoutTarget2(Service):
    """ Second fanout target. Stores received data.
    """

    name = 'test.pubsub.fanout-target-2'

    def handle(self) -> 'None':
        _record(self, _store_fanout_2, str(self.request.raw_request))

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestTypedChainSource(Service):
    """ Receives data and publishes it to a typed sink service.
    """

    name = 'test.pubsub.typed-chain-source'

    def handle(self) -> 'None':
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
            _record(self, _store_typed_chain, str(customer))
        else:
            _record(self, _store_typed_chain, str(data))

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestGetChainReceived(Service):
    """ Returns what the chain, fanout, and typed-chain receivers have collected.
    """

    name = 'test.pubsub.get-chain-received'

    def handle(self) -> 'None':
        chain = _read(self, _store_chain)
        fanout_1 = _read(self, _store_fanout_1)
        fanout_2 = _read(self, _store_fanout_2)
        typed_chain = _read(self, _store_typed_chain)

        out = {
            'chain_count': len(chain),
            'fanout_1_count': len(fanout_1),
            'fanout_2_count': len(fanout_2),
            'typed_chain_count': len(typed_chain),
            'chain': chain,
            'fanout_1': fanout_1,
            'fanout_2': fanout_2,
            'typed_chain': typed_chain,
        }

        self.response.payload = json_dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearChainReceived(Service):
    """ Clears all chain-related received message stores.
    """

    name = 'test.pubsub.clear-chain-received'

    def handle(self) -> 'None':
        _clear(self, _store_chain)
        _clear(self, _store_fanout_1)
        _clear(self, _store_fanout_2)
        _clear(self, _store_typed_chain)

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

    def handle(self:'Service') -> 'None':
        data = self.request.raw_request
        if isinstance(data, dict):
            data = data.get('data', data)
        result = str(data) + suffix
        _record(self, short_name, result)

    return handle

# ################################################################################################################################

def _make_ring_handle(short_name:'str') -> 'object':
    """ Builds a handle method for the ring topology that decrements TTL and republishes to itself.
    """

    suffix = '-via-' + short_name.split('-')[1]
    full_name = 'test.pubsub.' + short_name

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
            _record(self, short_name, payload)

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
        out = {}

        for short_name in _service_routing:
            received = _read(self, short_name)
            out[short_name + '_count'] = len(received)
            out[short_name] = received

        self.response.payload = json_dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestClearServiceReceived(Service):
    """ Clears all service received message stores.
    """

    name = 'test.pubsub.clear-service-received'

    def handle(self) -> 'None':
        for short_name in _service_routing:
            _clear(self, short_name)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestResetServiceTopics(Service):
    """ Deletes all service-related topics from the pub/sub database and removes
    their entries from the server's push subscription and topic caches,
    so the next publish recreates everything from scratch.
    """

    name = 'test.pubsub.reset-service-topics'

    def handle(self) -> 'None':
        backend = self.server.pubsub_backend
        prefix = 'zato.s.to.test.pubsub.service-'

        # Collect the service topics that hold any message rows ..
        topic_names = set()

        for topic_name in backend.get_topics_with_messages():
            if topic_name.startswith(prefix):
                topic_names.add(topic_name)

        # .. and the ones the service subscribers are still subscribed to ..
        for short_name in _service_routing:
            sub_key = 'zato.service.test.pubsub.' + short_name

            for topic_name in backend.get_subscribed_topics(sub_key):
                topic_names.add(topic_name)

        # .. remove each of them together with its messages, deliveries and subscriptions ..
        for topic_name in topic_names:
            backend.delete_topic(topic_name)

        # .. also clean up the server's in-memory caches ..
        for short_name in _service_routing:
            service_name = 'test.pubsub.' + short_name
            sub_key = 'zato.service.' + service_name

            # .. stop the delivery greenlet if running ..
            self.server.pubsub_push_delivery.stop_sub_key(sub_key)

            # .. remove from push subs ..
            _ = self.server.config_manager._push_subs.pop(sub_key, None)

            # .. remove from topic cache ..
            _ = self.server.config_manager._service_topic_cache.discard(service_name)

        # .. clear the received stores too ..
        for short_name in _service_routing:
            _clear(self, short_name)

        deleted_count = len(topic_names)

        self.response.payload = json_dumps({'deleted_topics': deleted_count})

# ################################################################################################################################
# ################################################################################################################################
