# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timezone

# Zato
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.keys import LocalKeys
from zato.common.b2b.common.store import new_memory_store
from zato.common.b2b.ebms2.common import Direction, MSHService, new_party_id
from zato.common.b2b.ebms2.cpa.parse import parse_cpa
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.inbound_common import new_receive_log
from zato.common.b2b.ebms2.outbound import accept_response, accept_signal, build
from zato.common.b2b.ebms2.packaging import Payload
from zato.common.test.b2b_cpa import build_cpa

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.outcome import Outcome
    from zato.common.b2b.common.receive_log import ReceiveLog
    from zato.common.b2b.common.store import MessageStore
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.outbound import OutboundMessage, SendOptions
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_cpa import AgreementSettings, PartySettings
    from zato.common.test.b2b_pki import TestParties, TestParty
    Agreement = Agreement
    AgreementSettings = AgreementSettings
    Binding = Binding
    InboundResult = InboundResult
    MessageStore = MessageStore
    Outcome = Outcome
    OutboundMessage = OutboundMessage
    PartySettings = PartySettings
    payload_list = payload_list
    ReceiveLog = ReceiveLog
    SendOptions = SendOptions
    TestParties = TestParties
    TestParty = TestParty

# ################################################################################################################################
# ################################################################################################################################

# The moment every exchange starts at, unless a test moves its clock.
Start_Time = datetime(2026, 1, 15, 9, 30, tzinfo=timezone.utc)

# The server whose receive log records what each party receives.
Server_Name = 'b2b-test-server'

Payload_Content_Type = 'application/xml'
Payload_Data = b'<Order xmlns="urn:zato:b2b:test"><Id>1</Id></Order>'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Side:
    """ One party of an exchange with its own keys and the receive log over its own message store.
    """
    settings:    'PartySettings'
    local_keys:  'LocalKeys'
    receive_log: 'ReceiveLog'

# ################################################################################################################################

@dataclass(init=False)
class Exchange:
    """ Two parties of one agreement that exchange messages in-process, under one clock.
    """
    settings:  'AgreementSettings'
    agreement: 'Agreement'
    clock:     'ManualClock'
    sender:    'Side'
    receiver:  'Side'

# ################################################################################################################################
# ################################################################################################################################

def new_local_keys(party:'TestParty') -> 'LocalKeys':
    """ Returns the keys a party signs with. The trust anchors come from the agreement.
    """
    out = LocalKeys()
    out.signing_key = party.key
    out.signing_certificate_chain = [party.certificate]

    return out

# ################################################################################################################################

def use_store(side:'Side', store:'MessageStore') -> 'None':
    """ Makes a party record what it receives in the given message store.
    """
    side.receive_log = new_receive_log(store, Server_Name)

# ################################################################################################################################

def new_side(settings:'PartySettings', party:'TestParty') -> 'Side':
    out = Side()
    out.settings = settings
    out.local_keys = new_local_keys(party)

    store = new_memory_store()
    use_store(out, store)

    return out

# ################################################################################################################################

def new_exchange(parties:'TestParties', settings:'AgreementSettings') -> 'Exchange':
    """ Returns an exchange under the agreement the settings describe.
    """
    data = build_cpa(settings)

    out = Exchange()
    out.settings = settings
    out.agreement = parse_cpa(data)
    out.clock = ManualClock(Start_Time)
    out.sender = new_side(settings.sender, parties.sender)
    out.receiver = new_side(settings.receiver, parties.receiver)

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_payload(data:'bytes'=Payload_Data, content_id:'str'='') -> 'Payload':
    out = Payload()
    out.content_id = content_id
    out.content_type = Payload_Content_Type
    out.data = data

    return out

# ################################################################################################################################

def resolve(exchange:'Exchange', action:'str'='', *, is_msh:'bool'=False, is_reverse:'bool'=False) -> 'Binding':
    """ Returns the binding of a message the sender sends to the receiver, or the other way around.
    """
    settings = exchange.settings

    if is_reverse:
        from_settings = exchange.receiver.settings
        to_settings = exchange.sender.settings
    else:
        from_settings = exchange.sender.settings
        to_settings = exchange.receiver.settings

    from_party_id = new_party_id(from_settings.party_id, from_settings.party_id_type)
    to_party_id = new_party_id(to_settings.party_id, to_settings.party_id_type)

    from_ids = [from_party_id]
    to_ids = [to_party_id]

    if is_msh:
        service = MSHService.Service
        service_type = ''
    else:
        service = settings.service
        service_type = settings.service_type

    if not action:
        action = settings.action

    out = exchange.agreement.resolve(from_ids, to_ids, service, service_type, action, Direction.Send)
    return out

# ################################################################################################################################

def send(
    exchange:'Exchange',
    payloads:'payload_list | None'=None,
    options:'SendOptions | None'=None,
    binding:'Binding | None'=None,
    ) -> 'OutboundMessage':
    """ Builds a message of the sender to the receiver.
    """
    if payloads is None:
        payloads = [new_payload()]

    if binding is None:
        binding = resolve(exchange)

    out = build(exchange.agreement, exchange.sender.local_keys, binding, payloads, exchange.clock, options)
    return out

# ################################################################################################################################

def deliver(exchange:'Exchange', outbound:'OutboundMessage', body:'bytes | None'=None) -> 'InboundResult':
    """ Passes a message of the sender to the receiver, with its bytes as built or as given.
    """
    if body is None:
        data = outbound.package.body
    else:
        data = body

    receiver = exchange.receiver

    out = receive(exchange.agreement, receiver.local_keys, outbound.package.headers, data, receiver.receive_log, exchange.clock)
    return out

# ################################################################################################################################

def confirm(exchange:'Exchange', result:'InboundResult') -> 'None':
    """ Confirms, as the application of the receiver does, that it processed each message a receipt delivered.
    """
    receive_log = exchange.receiver.receive_log

    for delivery in result.deliveries:
        receive_log.confirm(delivery.identity, delivery.cpa_id)

# ################################################################################################################################

def answer(exchange:'Exchange', outbound:'OutboundMessage', result:'InboundResult') -> 'Outcome':
    """ Passes what the receiver answered back to the sender - the HTTP response, then the asynchronous signal if any.
    """
    response = result.response

    out = accept_response(outbound, response.status_code, response.headers, response.body, exchange.clock)

    if async_signal := result.async_signal:
        out = accept_signal(outbound, async_signal.package.headers, async_signal.package.body, exchange.clock)

    return out

# ################################################################################################################################
# ################################################################################################################################
