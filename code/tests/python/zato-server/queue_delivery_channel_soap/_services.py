# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the SOAP channel suite - the target the channels point to, the hooked services and what the
# tests read the recordings back through.

# stdlib
from time import monotonic, sleep

# Zato
from zato.common.pubsub.outgoing import InboundType
from zato.common.soap.message import SOAPMessage
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# A refusal count meaning that the target refuses everything until it is told otherwise
_refuse_everything = -1

# The error the target raises while it refuses
_refused_error_text = 'The target refuses this invocation'

# What the hooked services put in front of the message id they answer with
_hook_response_prefix = 'hooked:'

# How long the slow hook sleeps before it answers
_slow_hook_delay = 2.0

# Every invocation of the target, in the order they were made
_invocations:'anylist' = []

# Every instantiation of the hooked service since the last clear
_hooked_instances:'anylist' = []

# How many more invocations the target refuses before it accepts again
_behaviour:'anydict' = {
    'refuse_left': 0,
}

# WSGI keeps the content type outside the prefixed headers
_wsgi_content_type = 'CONTENT_TYPE'

_connection = 'channel'
_transport = 'soap'

# ################################################################################################################################
# ################################################################################################################################

def _message_from(data:'anydict') -> 'SOAPMessage':
    """ A flat document as the message the channel wraps in the response envelope.
    """
    out = SOAPMessage()

    for name, value in data.items():
        setattr(out, name, value)

    return out

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ What the channels point to - it records every invocation, with the order its hooks ran in, and refuses
    as many invocations as it was told to.
    """

    name = 'test.queue-delivery.channel.target'

    def before_handle(self) -> 'None':

        http = self.request.http

        self.record:'stranydict' = {
            'time': monotonic(),
            'cid': self.cid,
            'method': http.method,
            'path': http.path,
            'path_params': dict(http.params),
            'query': dict(http.GET),
            'headers': dict(http.headers),
            'content_type': self.request_ctx[_wsgi_content_type],
            'payload': self.request.payload.to_dict(),
            'operation': self.request.soap.operation,
            'soap_version': self.request.soap.soap_version,
            'channel_type': self.channel.type,
            'channel_name': self.channel.name,
            'hooks': ['before_handle'],
            'is_accepted': True,
        }

        _invocations.append(self.record)

    def handle(self) -> 'None':

        self.record['hooks'].append('handle')
        self.record['handle_started_at'] = monotonic()

        refuse_left = _behaviour['refuse_left']

        if refuse_left == _refuse_everything:
            is_accepted = False

        elif refuse_left > 0:
            _behaviour['refuse_left'] = refuse_left - 1
            is_accepted = False

        else:
            is_accepted = True

        self.record['is_accepted'] = is_accepted

        if not is_accepted:
            raise Exception(_refused_error_text)

        self.response.payload = _message_from({
            'is_ok': True,
            'cid': self.cid,
            'echo': self.request.payload.order_id,
        })

    def after_handle(self) -> 'None':
        self.record['hooks'].append('after_handle')

# ################################################################################################################################
# ################################################################################################################################

class Hooked(Target):
    """ The target with the hook that shapes the response of a queued request - it echoes a field of the request
    along with the id of the message the queue has just stored.
    """

    name = 'test.queue-delivery.channel.hooked'

    def __init__(self) -> 'None':
        super().__init__()
        _hooked_instances.append(1)

    def get_queue_response(self) -> 'None':
        self.response.payload = _message_from({
            'echo': self.request.payload.order_id,
            'msg_id': self.request.queue.msg_id,
            'cid': self.cid,
            'text': _hook_response_prefix + self.request.queue.msg_id,
        })

# ################################################################################################################################
# ################################################################################################################################

class SlowHook(Target):
    """ The target with a hook that takes its time - handle records when it started, so a test can see that
    the delivery did not wait for the hook.
    """

    name = 'test.queue-delivery.channel.slow-hook'

    def get_queue_response(self) -> 'None':
        sleep(_slow_hook_delay)

        self.response.payload = _message_from({
            'msg_id': self.request.queue.msg_id,
            'cid': self.cid,
            'text': _hook_response_prefix + self.request.queue.msg_id,
        })

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the id and the queue type of a SOAP channel, which is what the shared services look up.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        url_data = self.server.config_manager.request_dispatcher.url_data

        for item in url_data.channel_data:
            if item['name'] == conn_name:
                self.response.payload = {
                    'id': item['id'],
                    'conn_type': InboundType.SOAP,
                    'connection': _connection,
                    'transport': _transport,
                }
                return

        raise Exception(f'No such channel `{conn_name}`')

# ################################################################################################################################
# ################################################################################################################################

class SetBehaviour(Service):
    """ Tells the target how many of the coming invocations to refuse - what it recorded so far stays.
    """

    name = 'test.queue-delivery.channel.set-behaviour'

    def handle(self) -> 'None':

        _behaviour['refuse_left'] = self.request.raw_request['refuse_count']

        self.response.payload = {'refuse_left': _behaviour['refuse_left']}

# ################################################################################################################################
# ################################################################################################################################

class GetReceived(Service):
    """ Every invocation the target has seen since it was last cleared, oldest first.
    """

    name = 'test.queue-delivery.channel.get-received'

    def handle(self) -> 'None':
        self.response.payload = {'invocations': list(_invocations)}

# ################################################################################################################################
# ################################################################################################################################

class Clear(Service):
    """ Forgets every invocation and every instantiation recorded so far and leaves the target accepting.
    """

    name = 'test.queue-delivery.channel.clear'

    def handle(self) -> 'None':

        _behaviour['refuse_left'] = 0
        _invocations.clear()
        _hooked_instances.clear()

        _ = self.invoke('test.queue-delivery.channel.clear-counting', {})

        self.response.payload = {'is_ok': True}

# ################################################################################################################################
# ################################################################################################################################

class GetCounts(Service):
    """ How many times the counting service and the hooked service were instantiated since the last clear.
    """

    name = 'test.queue-delivery.channel.get-counts'

    def handle(self) -> 'None':

        counting = self.invoke('test.queue-delivery.channel.get-counting', {})

        self.response.payload = {
            'counting': counting['count'],
            'hooked': len(_hooked_instances),
        }

# ################################################################################################################################
# ################################################################################################################################
