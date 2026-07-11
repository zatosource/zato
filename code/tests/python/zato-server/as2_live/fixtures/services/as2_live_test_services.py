# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from json import dumps, loads

# httpx
import httpx

# Zato
from zato.common.as2.outbound import build_message, describe_send_result
from zato.server.service import Service
from zato.x12.envelope import X12Interchange
from zato.x12.retail import PurchaseOrder850
from zato.x12.retail.messages import PurchaseOrderLine

# ################################################################################################################################
# ################################################################################################################################

# Everything AS2 channels routed to the receiver service since the last clear request -
# a module-level list because the loopback tests read it back through the invoker below.
_received = []

# How long a send may block while the connection pool is still being built.
_pool_block_timeout = 30

# The EDI identities the typed 850 travels under.
_buyer_edi_id    = 'ZATORETAIL'
_supplier_edi_id = 'PARTNERCORP'

# ################################################################################################################################
# ################################################################################################################################

def build_purchase_order():
    """ Builds a typed 850 with the retail dictionary, the way a production service would -
    the envelope computes its counts and control numbers when serialized.
    """
    order = PurchaseOrder850()
    order.beg.purpose_code = '00'
    order.beg.po_type = 'NE'
    order.beg.po_number = 'PO-4529'
    order.beg.date = '20260711'

    line = PurchaseOrderLine()
    line.po1.line_number = '1'
    line.po1.quantity = '10'
    line.po1.unit = 'EA'
    line.po1.unit_price = '9.75'
    order.lines = [line]

    interchange = X12Interchange()
    interchange.isa.sender_id = _buyer_edi_id
    interchange.isa.receiver_id = _supplier_edi_id

    interchange.add(order)

    out = interchange.serialize()
    return out

# ################################################################################################################################
# ################################################################################################################################

class AS2LiveReceiver(Service):
    """ The routing target of AS2 partnerships under test - records every message
    the channel hands over, exactly as a production subscriber would receive it.
    """

    name = 'test.as2live.receiver'

    def handle(self):
        message = self.request.raw_request
        _received.append(message)

# ################################################################################################################################
# ################################################################################################################################

class AS2LiveInvoker(Service):
    """ Drives outgoing AS2 connections from inside the server, which is the same
    code path production services use. Tests invoke it through the IDE in the browser.
    """

    name = 'test.as2live.invoke'

    def handle(self):

        # The IDE invoker delivers the payload as a raw JSON string.
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        mode = request['mode']

        # The readiness probe - tests keep invoking it until the module deploys.
        if mode == 'ping':
            out = {'is_ready': True}

        # Build a typed 850 in this service and deliver it over the named connection -
        # the 13.4.1 shape, a service using the X12 dictionaries and self.as2 together.
        elif mode == 'send-850':
            out = self._send(request, build_purchase_order())

        # Deliver an arbitrary payload - the wire-shape tests read the raw MIME back.
        elif mode == 'send':
            out = self._send(request, request['payload'])

        # Deliver a message whose signed content was corrupted after signing.
        elif mode == 'send-tampered':
            out = self._send_tampered(request)

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

    def _send(self, request, payload):
        """ Delivers one payload over the named connection and reports the MDN outcome
        along with the raw MIME body that went over the wire. Errors go back as a reply
        field - the caller retries while the pair configured a moment ago in the browser
        propagates to the server.
        """
        connection_name = request['connection']

        try:
            result = self.as2[connection_name].send(payload, 'orders-850.edi')
        except Exception as send_error:
            out = {'error': repr(send_error)}
        else:
            out = describe_send_result(result)
            out['payload'] = payload
            out['request_body'] = b64encode(result.request_body).decode('ascii')

        return out

# ################################################################################################################################

    def _send_tampered(self, request):
        """ Builds one AS2 message with the named connection's own partnership and keystore,
        corrupts the signed content after signing and delivers it over the real wire -
        the receiving channel has to answer with an integrity failure MDN.
        """
        connection_name = request['connection']
        payload = request['payload']
        token = request['token']
        replacement = request['replacement']

        wrapper = self.as2[connection_name].conn

        # Building the message needs the partnership and keystore of one pooled connection.
        with wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as connection:
            body, headers, message_id, _ = build_message(connection.partnership, connection.keystore, payload.encode('utf8'))
            endpoint_url = connection.partnership.endpoint_url

        # The signature stays as it is while the signed content changes underneath it.
        tampered = body.replace(token.encode('utf8'), replacement.encode('utf8'))

        try:
            response = httpx.post(endpoint_url, content=tampered, headers=headers)
        except Exception as post_error:
            out = {'error': repr(post_error)}
        else:
            out = {
                'http_status': response.status_code,
                'message_id': message_id,
                'mdn_body': response.content.decode('utf8', 'replace'),
            }

        return out

# ################################################################################################################################
# ################################################################################################################################
