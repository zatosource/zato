# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# httpx
import httpx

# Zato
from zato.common.as2.inbound import handle, StoredMDN
from zato.common.as2.outbound import send
from zato.common.as2.partnership import new_partnership

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# Where each side's AS2 endpoint lives - the sending side delivers to the partner's endpoint,
# and the receiving side's own partnership names the sender's, which is where it delivers to.
Endpoint_URL        = 'https://partnercorp.example.com/as2'
Sender_Endpoint_URL = 'https://zatoretail.example.com/as2'

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

Payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

# ################################################################################################################################
# ################################################################################################################################

def make_sender_partnership() -> 'any_':
    """ The relationship as our own, sending side sees it.
    """
    out = new_partnership()

    out.as2_from = Sender_Identifier
    out.as2_to = Receiver_Identifier
    out.endpoint_url = Endpoint_URL

    return out

# ################################################################################################################################

def make_receiver_partnership() -> 'any_':
    """ The same relationship as the partner's, receiving side sees it - the identities swap places
    and the endpoint is the sender's own, which is where this side delivers messages to.
    """
    out = new_partnership()

    out.as2_from = Receiver_Identifier
    out.as2_to = Sender_Identifier
    out.endpoint_url = Sender_Endpoint_URL

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Exchange:
    """ One simulated wire between a sender and a receiver - the receiver runs the real inbound
    pipeline behind an HTTP mock transport, with a duplicate store and full wire captures.
    """
    sender_partnership: 'any_'
    receiver_partnerships: 'anylist'
    sender_keystore: 'any_'
    receiver_keystore: 'any_'

    # Everything that went over the wire and everything the receiver decided.
    requests: 'anylist'
    bodies: 'anylist'
    results: 'anylist'

    # The duplicate store, keyed on the identity pair and the Message-ID.
    duplicate_store: 'anydict'

    client: 'httpx.Client'

# ################################################################################################################################

def new_exchange(parties:'TestParties') -> 'any_':
    """ Wires a sender and a receiver together over a mock HTTP transport.
    """

    out = Exchange()

    out.sender_partnership = make_sender_partnership()
    out.receiver_partnerships = [make_receiver_partnership()]
    out.sender_keystore = parties.sender
    out.receiver_keystore = parties.receiver

    out.requests = []
    out.bodies = []
    out.results = []
    out.duplicate_store = {}

    def _is_duplicate(as2_from:'any_', as2_to:'any_', message_id:'any_') -> 'any_':
        result = out.duplicate_store.get((as2_from, as2_to, message_id))
        return result

    def _handler(request:'httpx.Request') -> 'any_':

        body = request.read()

        out.requests.append(request)
        out.bodies.append(body)

        headers = dict(request.headers)
        result = handle(body, headers, out.receiver_partnerships, out.receiver_keystore, _is_duplicate)
        out.results.append(result)

        # A clean first delivery lands in the duplicate store so a replay
        # can be answered with the exact same bytes.
        if not result.is_duplicate:
            if not result.is_error:
                if result.message_id:
                    stored = StoredMDN()
                    stored.status_code = result.status_code
                    stored.body = result.body
                    stored.headers = result.headers

                    out.duplicate_store[(result.as2_from, result.as2_to, result.message_id)] = stored

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)
    out.client = httpx.Client(transport=transport)

    return out

# ################################################################################################################################

def set_security(exchange:'any_', sign:'any_', encrypt:'any_') -> 'None':
    """ Agrees the signing and encryption terms on both sides of the exchange. Two partners
    configure one relationship, so the receiver enforces the same terms the sender applies -
    setting them on the sending side alone would have the receiver reject the message.
    """
    exchange.sender_partnership.sign = sign
    exchange.sender_partnership.encrypt = encrypt

    for partnership in exchange.receiver_partnerships:
        partnership.sign = sign
        partnership.encrypt = encrypt

# ################################################################################################################################

def use_responder(exchange:'any_', responder:'any_') -> 'None':
    """ Replaces the receiver behind the wire with one that answers however a test needs it to,
    which is how a receipt that does not confirm the message is put on the response.
    """
    transport = httpx.MockTransport(responder)
    exchange.client = httpx.Client(transport=transport)

# ################################################################################################################################

def do_send(
    exchange:'any_',
    payload:'any_' = Payload,
    filename:'any_' = None,
    message_id:'any_' = None,
    ) -> 'any_':
    """ Delivers one message through the exchange's mock wire.
    """
    partnership = exchange.sender_partnership
    keystore = exchange.sender_keystore
    client = exchange.client

    out = send(partnership, keystore, payload, filename, client, message_id=message_id)

    return out

# ################################################################################################################################
# ################################################################################################################################
