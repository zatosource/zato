# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Everything Kafka channels routed to the receiver service since the last clear request -
# a module-level list because the end-to-end tests read it back through the invoker below.
_received = []

# ################################################################################################################################
# ################################################################################################################################

class KafkaReceiver(Service):
    """ The routing target of Kafka channels under test - records every message the channel
    hands over, keeping both self.request.input and self.request.raw_request so the tests
    can confirm the payload arrives through both attributes.
    """

    name = 'test.kafka.receiver'

    def handle(self):

        input_data = self.request.input
        if isinstance(input_data, bytes):
            input_data = input_data.decode('utf-8')

        raw_data = self.request.raw_request
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')

        _received.append({
            'input': input_data,
            'raw_request': raw_data,
        })

# ################################################################################################################################
# ################################################################################################################################

class KafkaInvoker(Service):
    """ Drives outgoing Kafka connections from inside the server, which is the same
    code path production services use. Tests invoke it through the IDE in the browser.
    """

    name = 'test.kafka.invoke'

    def handle(self):

        # The IDE invoker delivers the payload as a raw JSON string.
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        mode = request['mode']

        # The readiness probe - tests keep invoking it until the module deploys.
        if mode == 'ping':
            out = {'is_ready': True}

        # Send one message over the named connection.
        # Errors go back as a reply field - the caller retries while the connection
        # configured a moment ago in the browser propagates to the server.
        elif mode == 'send':
            connection_name = request['connection']
            payload = request['payload']

            try:
                self.out.kafka[connection_name].send(payload)
            except Exception as send_error:
                out = {'error': repr(send_error)}
            else:
                out = {'is_ok': True}

        # Return everything the receiver service recorded so far.
        elif mode == 'get-received':
            out = {'received': _received}

        # Start a new exchange from a clean slate.
        elif mode == 'clear-received':
            _received.clear()
            out = {'is_cleared': True}

        else:
            out = {'error': f'Unknown mode `{mode}`'}

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################
