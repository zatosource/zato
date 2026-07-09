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

# Everything AS4 channels routed to the receiver service since the last clear request -
# a module-level list because the loopback tests read it back through the invoker below.
_received = []

# ################################################################################################################################
# ################################################################################################################################

class AS4Receiver(Service):
    """ The routing target of AS4 channels under test - records every message
    the channel hands over, exactly as a production subscriber would receive it.
    """

    name = 'test.as4.receiver'

    def handle(self):
        message = self.request.raw_request
        _received.append(message)

# ################################################################################################################################
# ################################################################################################################################

class AS4Invoker(Service):
    """ Drives outgoing AS4 connections from inside the server, which is the same
    code path production services use. Tests invoke it through the IDE in the browser.
    """

    name = 'test.as4.invoke'

    def handle(self):

        # The IDE invoker delivers the payload as a raw JSON string.
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        mode = request['mode']

        # The readiness probe - tests keep invoking it until the module deploys.
        if mode == 'ping':
            out = {'is_ready': True}

        # Send one message over the named connection and report the receipt.
        # Errors go back as a reply field - the caller retries while the pair
        # configured a moment ago in the browser propagates to the server.
        elif mode == 'send':
            connection_name = request['connection']
            payload = request['payload']

            try:
                result = self.as4[connection_name].send(payload)
            except Exception as send_error:
                out = {'error': repr(send_error)}
            else:
                out = {
                    'is_ok': result.is_ok,
                    'message_id': result.message_id,
                    'receipt_ref': result.receipt.ref_to_message_id if result.receipt else None,
                    'http_status': result.http_status,
                }

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
