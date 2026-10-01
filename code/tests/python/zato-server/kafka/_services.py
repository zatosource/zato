# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services of the Kafka backend suite - the receivers the channels under test route to, each remembering what it was
# invoked with and failing or dawdling when a test tells it to, and the invoker a test drives the outgoing connections through.

# stdlib
from json import dumps, loads
from time import monotonic, sleep

# Zato
from zato.common.pubsub.outgoing import InboundType, OutgoingType
from zato.server.generic.api.channel_kafka import channel_config_defaults
from zato.server.generic.api.outconn_kafka import outconn_config_defaults
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Every invocation of a receiver since the last clear - what it got and what it did with it
_received:'anylist' = []

# How each receiver behaves right now, by service name - how many more invocations fail, whether every one does,
# and how long each one sleeps before answering
_behaviour:'anydict' = {}

# The columns of a generic connection an edit sends back as they are
_own_fields = ('id', 'name', 'type_', 'address', 'pool_size', 'is_active', 'is_internal', 'is_channel', 'is_outconn')

# The opaque attributes of each kind of connection, which an edit that leaves them out would clear
_security_fields = ('security_id', 'security_name', 'auth_type')
_channel_opaque_fields = tuple(channel_config_defaults) + _security_fields
_outgoing_opaque_fields = tuple(outconn_config_defaults) + _security_fields

_no_error = ''

# ################################################################################################################################
# ################################################################################################################################

def _record(service:'Service', outcome:'str', error:'str'='') -> 'None':
    """ Remembers one invocation of a receiver.
    """
    raw = service.request.raw_request

    if isinstance(raw, bytes):
        try:
            data = raw.decode('utf8')
        except UnicodeDecodeError:
            data = raw.hex()
    else:
        data = raw

    _received.append({
        'service': service.name,
        'cid': service.cid,
        'data': data,
        'headers': dict(service.request.headers or {}),
        'outcome': outcome,
        'error': error,
        'time': monotonic(),
    })

# ################################################################################################################################

def _behave(service:'Service') -> 'None':
    """ Fails or sleeps as the receiver was told to, recording the invocation either way.
    """
    settings = _behaviour.get(service.name) or {}

    if sleep_time := settings.get('sleep'):
        sleep(sleep_time)

    # A receiver that parses its input fails on input that is not JSON
    if settings.get('parse_json'):
        try:
            _ = loads(service.request.raw_request)
        except Exception as e:
            _record(service, 'failed', str(e))
            raise

    fail_times = settings.get('fail_times', 0)

    if settings.get('fail_always') or fail_times > 0:

        if fail_times > 0:
            settings['fail_times'] = fail_times - 1

        error = f'Receiver {service.name} failed on purpose'
        _record(service, 'failed', error)

        raise ValueError(error)

    _record(service, 'ok')

# ################################################################################################################################
# ################################################################################################################################

class Receiver(Service):
    """ The service most channels under test route to.
    """
    name = 'test.kafka.receiver'

    def handle(self) -> 'None':
        _behave(self)

# ################################################################################################################################

class ReceiverTwo(Service):
    """ A second receiver for routing rules and for a second channel to be told apart from the first.
    """
    name = 'test.kafka.receiver.two'

    def handle(self) -> 'None':
        _behave(self)

# ################################################################################################################################

class ReceiverThree(Service):
    """ A third receiver, for a routing rule picked by a header.
    """
    name = 'test.kafka.receiver.three'

    def handle(self) -> 'None':
        _behave(self)

# ################################################################################################################################
# ################################################################################################################################

def _find_connection(service:'Service', name:'str') -> 'tuple[str, str, any_]':
    """ A Kafka channel or outgoing connection by name, as its kind, its DLQ connection type and its configuration.
    """
    config_manager = service.server.config_manager

    if item := config_manager.channel_kafka.get(name):
        return ('channel', InboundType.KAFKA, item)

    if item := config_manager.outconn_kafka.get(name):
        return ('outgoing', OutgoingType.KAFKA, item)

    raise Exception(f'No Kafka connection named `{name}`')

# ################################################################################################################################

def _connection_as_dict(kind:'str', conn_type:'str', config:'any_') -> 'stranydict':
    """ What a connection's configuration holds, as the fields an edit sends back.
    """
    out:'stranydict' = {'conn_type': conn_type, 'kind': kind}

    for field_name in _own_fields:
        out[field_name] = config[field_name]

    opaque_fields = _channel_opaque_fields if kind == 'channel' else _outgoing_opaque_fields

    for field_name in opaque_fields:
        if field_name in config:
            out[field_name] = config[field_name]

    return out

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with what a Kafka connection's configuration holds right now - under the name the shared
    queue delivery services look a connection up through.
    """
    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':
        conn_name = self.request.raw_request['conn_name']
        kind, conn_type, config = _find_connection(self, conn_name)

        self.response.payload = _connection_as_dict(kind, conn_type, config)

# ################################################################################################################################
# ################################################################################################################################

class Invoker(Service):
    """ Everything a test does from inside the server - sends, receivers' behaviour and connection edits.
    """
    name = 'test.kafka.invoke'

# ################################################################################################################################

    def _ping(self) -> 'anydict':
        return {'is_ready': True}

# ################################################################################################################################

    def _send(self) -> 'anydict':
        """ One send through an outgoing connection, with the result or the error it raised.
        """
        request = self.request.raw_request
        connection = request['connection']

        kwargs:'anydict' = {}

        for name in ('key', 'headers', 'partition'):
            if request.get(name) is not None:
                kwargs[name] = request[name]

        try:
            if request.get('is_tombstone'):
                result = self.out.kafka[connection].delete(request['key'], headers=kwargs.get('headers'))
            else:
                result = self.out.kafka[connection].send(request['payload'], **kwargs)

        except Exception as e:
            out = {'is_ok': False, 'error': repr(e), 'cid': self.cid}

        else:
            out = {'is_ok': True, 'error': _no_error, 'cid': self.cid}

            # A direct send says where the message landed, a queued one says whether it is in the queue.
            if hasattr(result, 'offset'):
                out.update({'topic': result.topic, 'partition': result.partition, 'offset': result.offset})
            else:
                out.update({'is_in_queue': result.is_in_queue, 'msg_id': result.msg_id, 'send_error': result.error})

        return out

# ################################################################################################################################

    def _ping_connection(self) -> 'anydict':
        connection = self.request.raw_request['connection']

        try:
            self.out.kafka[connection].ping()
        except Exception as e:
            out = {'is_ok': False, 'error': repr(e)}
        else:
            out = {'is_ok': True, 'error': _no_error}

        return out

# ################################################################################################################################

    def _get_received(self) -> 'anydict':
        return {'received': list(_received)}

# ################################################################################################################################

    def _clear_received(self) -> 'anydict':
        _received.clear()
        return {'is_cleared': True}

# ################################################################################################################################

    def _set_behaviour(self) -> 'anydict':
        """ Tells a receiver how to behave from now on - the settings given replace the ones it had.
        """
        request = self.request.raw_request
        service_name = request['service']

        settings = {
            'fail_times': request.get('fail_times', 0),
            'fail_always': request.get('fail_always', False),
            'sleep': request.get('sleep', 0),
            'parse_json': request.get('parse_json', False),
        }
        _behaviour[service_name] = settings

        return {'service': service_name, 'behaviour': settings}

# ################################################################################################################################

    def _get_connection(self) -> 'anydict':
        kind, conn_type, config = _find_connection(self, self.request.raw_request['connection'])
        out = _connection_as_dict(kind, conn_type, config)

        return out

# ################################################################################################################################

    def _edit_connection(self) -> 'anydict':
        """ Changes some fields of a connection as the Dashboard does.
        """
        request = self.request.raw_request
        kind, conn_type, config = _find_connection(self, request['connection'])

        edit_request = _connection_as_dict(kind, conn_type, config)
        _ = edit_request.pop('conn_type')
        _ = edit_request.pop('kind')
        edit_request.update(request['changes'])

        _ = self.invoke('zato.generic.connection.edit', edit_request)

        return {'id': config['id']}

# ################################################################################################################################

    def _delete_connection(self) -> 'anydict':
        _, _, config = _find_connection(self, self.request.raw_request['connection'])
        conn_id = config['id']

        _ = self.invoke('zato.generic.connection.delete', {'id': conn_id})

        return {'id': conn_id}

# ################################################################################################################################

    def _invoke_service(self) -> 'anydict':
        """ Invokes any service by name with a request dict.
        """
        request = self.request.raw_request
        response = self.invoke(request['service'], request.get('request') or {})

        return {'response': response}

# ################################################################################################################################

    def handle(self) -> 'None':
        mode = self.request.raw_request['mode']

        if handler := _mode_handlers.get(mode):
            out = handler(self)
        else:
            out = {'error': f'Unknown mode `{mode}`'}

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

_mode_handlers = {
    'ping':              Invoker._ping,
    'send':              Invoker._send,
    'ping-connection':   Invoker._ping_connection,
    'get-received':      Invoker._get_received,
    'clear-received':    Invoker._clear_received,
    'set-behaviour':     Invoker._set_behaviour,
    'get-connection':    Invoker._get_connection,
    'edit-connection':   Invoker._edit_connection,
    'delete-connection': Invoker._delete_connection,
    'invoke':            Invoker._invoke_service,
}

# ################################################################################################################################
# ################################################################################################################################
