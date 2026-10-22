# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.b2b.ebms2.common import Direction, EbMS2Exception, ErrorCode, MSHService, SyncReplyMode
from zato.common.b2b.ebms2.compose import compose, Composition, new_reply_header, signing_for
from zato.common.b2b.ebms2.security import sender_non_repudiation

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.packaging import Package
    from zato.common.b2b.ebms2.signals import Acknowledgment, ErrorList, StatusResponse
    Acknowledgment = Acknowledgment
    Agreement = Agreement
    Binding = Binding
    datetime = datetime
    ErrorList = ErrorList
    LocalKeys = LocalKeys
    MessageHeader = MessageHeader
    Package = Package
    StatusResponse = StatusResponse

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Reply:
    """ A message service handler message that answers a received message.
    """
    action: str

    acknowledgment:  'Acknowledgment | None' = None
    error_list:      'ErrorList | None' = None
    status_response: 'StatusResponse | None' = None

    is_signed: bool = False

# ################################################################################################################################
# ################################################################################################################################

def is_sync_reply(binding:'Binding') -> 'bool':
    """ Says whether the message service handler messages that answer a message with eb:SyncReply go back
    on the connection it arrived on, which the sending party's delivery channel decides.
    """
    mode = binding.send_channel.characteristics.sync_reply_mode

    out = mode != SyncReplyMode.Response_Only
    return out

# ################################################################################################################################

def wants_sync_reply(binding:'Binding') -> 'bool':
    """ Says whether a message sent under a binding asks for the replies on the same connection.
    """
    mode = binding.send_channel.characteristics.sync_reply_mode

    out = mode != SyncReplyMode.No_Reply
    return out

# ################################################################################################################################

def reply_binding(agreement:'Agreement', original:'MessageHeader', action:'str') -> 'Binding':
    """ Returns how a message service handler message answering another message is exchanged.
    """
    out = agreement.resolve(
        original.to_party.party_ids, original.from_party.party_ids, MSHService.Service, '', action, Direction.Send)

    return out

# ################################################################################################################################

def reply_endpoint(binding:'Binding') -> 'str':
    """ Returns the address an asynchronous message service handler message is sent to.
    """
    transport = binding.receive_channel.transport

    if not transport.endpoints:
        raise EbMS2Exception(
            ErrorCode.Delivery_Failure, f'Transport `{transport.transport_id}` of `{binding.to_party.party_name}` has no endpoint')

    out = transport.endpoint_uri
    return out

# ################################################################################################################################

def build_reply(
    agreement:'Agreement',
    local_keys:'LocalKeys',
    original:'MessageHeader',
    reply:'Reply',
    now:'datetime',
    ) -> 'Package':
    """ Returns a message service handler message that answers a received message.
    """
    composition = Composition()
    composition.header = new_reply_header(original, reply.action, now)
    composition.acknowledgment = reply.acknowledgment
    composition.error_list = reply.error_list
    composition.status_response = reply.status_response

    if reply.is_signed:
        binding = reply_binding(agreement, original, reply.action)
        non_repudiation = sender_non_repudiation(binding)
        composition.signing = signing_for(non_repudiation, local_keys)

    composed = compose(composition)

    out = composed.package
    return out

# ################################################################################################################################
# ################################################################################################################################
