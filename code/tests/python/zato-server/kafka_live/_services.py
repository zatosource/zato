# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Every message the channels under test routed to the receiver since the last clear request
_received:'strlist' = []

# What a call that succeeded reports as its error
_no_error = ''

# ################################################################################################################################
# ################################################################################################################################

class KafkaLiveReceiver(Service):
    """ The service the Kafka channels under test route to - records every message handed over.
    """
    name = 'test.kafka.live.receiver'

    def handle(self) -> 'None':
        data = self.request.raw_request.decode('utf-8')
        _received.append(data)

# ################################################################################################################################
# ################################################################################################################################

class KafkaLiveInvoker(Service):
    """ Drives the outgoing Kafka connections under test from inside the server.
    """
    name = 'test.kafka.live.invoke'
    input = 'mode', '-connection', '-payload'

# ################################################################################################################################

    def _ping(self) -> 'anydict':
        out = {'is_ready': True}
        return out

# ################################################################################################################################

    def _send(self) -> 'anydict':
        connection = self.request.input.connection

        try:
            self.out.kafka[connection].send(self.request.input.payload)
        except Exception as e:
            out = {'is_ok': False, 'error': repr(e)}
        else:
            out = {'is_ok': True, 'error': _no_error}

        return out

# ################################################################################################################################

    def _ping_connection(self) -> 'anydict':
        connection = self.request.input.connection

        try:
            self.out.kafka[connection].ping()
        except Exception as e:
            out = {'is_ok': False, 'error': repr(e)}
        else:
            out = {'is_ok': True, 'error': _no_error}

        return out

# ################################################################################################################################

    def _get_received(self) -> 'anydict':
        out = {'received': list(_received)}
        return out

# ################################################################################################################################

    def _clear_received(self) -> 'anydict':
        _received.clear()

        out = {'is_cleared': True}
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # Look up what the mode maps to ..
        mode = self.request.input.mode

        # .. run it ..
        if handler := _mode_handlers.get(mode):
            out = handler(self)

        # .. or report a mode this service does not know ..
        else:
            out = {'error': f'Unknown mode `{mode}`'}

        # .. and return the result as JSON.
        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

_mode_handlers = {
    'ping':            KafkaLiveInvoker._ping,
    'send':            KafkaLiveInvoker._send,
    'ping-connection': KafkaLiveInvoker._ping_connection,
    'get-received':    KafkaLiveInvoker._get_received,
    'clear-received':  KafkaLiveInvoker._clear_received,
}

# ################################################################################################################################
# ################################################################################################################################
