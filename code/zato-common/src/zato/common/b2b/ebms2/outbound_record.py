# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from datetime import datetime

# Zato
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.send_log import SentMessage
from zato.common.b2b.ebms2.common import Direction, PartyId
from zato.common.b2b.ebms2.compose import new_message_header
from zato.common.b2b.ebms2.outbound import OutboundMessage, OutboundState
from zato.common.b2b.ebms2.packaging import Package

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Agreement
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.typing_ import anylist, stranydict
    Agreement = Agreement
    anylist = anylist
    LocalKeys = LocalKeys
    party_id_list = party_id_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class _Detail:
    """ The keys of the details a sent message is recorded with, which rebuilding it requires.
    """
    From_Party_IDs             = 'from_party_ids'
    To_Party_IDs               = 'to_party_ids'
    Service                    = 'service'
    Service_Type               = 'service_type'
    Action                     = 'action'
    Conversation_ID            = 'conversation_id'
    Ref_To_Message_ID          = 'ref_to_message_id'
    Timestamp                  = 'timestamp'
    Time_To_Live               = 'time_to_live'
    Duplicate_Elimination      = 'duplicate_elimination'
    Is_Ack_Requested           = 'is_ack_requested'
    Is_Ack_Signature_Requested = 'is_ack_signature_requested'
    Is_Sync_Reply              = 'is_sync_reply'
    Sent_Digests               = 'sent_digests'

# The state of an exchange that ended, by the final state it ended in.
_completed_states = {
    FinalState.Delivered:  OutboundState.Acknowledged,
    FinalState.Answered:   OutboundState.Answered,
    FinalState.Failed:     OutboundState.Failed,
    FinalState.Superseded: OutboundState.Failed,
}

# ################################################################################################################################
# ################################################################################################################################

def _party_ids_to_list(party_ids:'party_id_list') -> 'anylist':
    out:'anylist' = []

    for party_id in party_ids:
        item = [party_id.value, party_id.id_type]
        out.append(item)

    return out

# ################################################################################################################################

def _party_ids_from_list(items:'anylist') -> 'party_id_list':
    out:'party_id_list' = []

    for value, id_type in items:
        party_id = PartyId()
        party_id.value = value
        party_id.id_type = id_type
        out.append(party_id)

    return out

# ################################################################################################################################

def new_sent_message(outbound:'OutboundMessage', wire:'Package') -> 'SentMessage':
    """ Returns how a message that goes on the wire in the given form is recorded in a send log,
    with the details that restore_outbound rebuilds it from.
    """
    binding = outbound.binding
    header = outbound.header
    message_data = header.message_data

    if time_to_live := message_data.time_to_live:
        time_to_live = time_to_live.isoformat()

    from_party_ids = _party_ids_to_list(header.from_party.party_ids)
    to_party_ids = _party_ids_to_list(header.to_party.party_ids)
    timestamp = message_data.timestamp.isoformat()

    details:'stranydict' = {
        _Detail.From_Party_IDs: from_party_ids,
        _Detail.To_Party_IDs: to_party_ids,
        _Detail.Service: header.service,
        _Detail.Service_Type: header.service_type,
        _Detail.Action: header.action,
        _Detail.Conversation_ID: header.conversation_id,
        _Detail.Ref_To_Message_ID: message_data.ref_to_message_id,
        _Detail.Timestamp: timestamp,
        _Detail.Time_To_Live: time_to_live,
        _Detail.Duplicate_Elimination: header.duplicate_elimination,
        _Detail.Is_Ack_Requested: outbound.is_ack_requested,
        _Detail.Is_Ack_Signature_Requested: outbound.is_ack_signature_requested,
        _Detail.Is_Sync_Reply: outbound.is_sync_reply,
        _Detail.Sent_Digests: outbound.sent_digests,
    }

    out = SentMessage()
    out.message_id = outbound.message_id
    out.cpa_id = binding.agreement.cpa_id
    out.from_party = binding.from_party.party_name
    out.to_party = binding.to_party.party_name
    out.endpoint = outbound.endpoint
    out.attrs = {B2BAttr.Service: header.service, B2BAttr.Action: header.action}
    out.policy = outbound.policy
    out.retry_state = outbound.retry_state
    out.outcome = outbound.outcome
    out.details = details
    out.wire_headers = wire.headers
    out.wire_body = wire.body

    return out

# ################################################################################################################################

def restore_outbound(agreement:'Agreement', local_keys:'LocalKeys', sent:'SentMessage') -> 'OutboundMessage':
    """ Rebuilds a message from its record in a send log, so that its exchange continues where the record says it stands.
    The header is rebuilt from the recorded details rather than read from the wire form, which may have been changed
    after the message was built.
    """
    details = sent.details

    # The binding is resolved again from the agreement the message was sent under ..
    from_party_ids = _party_ids_from_list(details[_Detail.From_Party_IDs])
    to_party_ids = _party_ids_from_list(details[_Detail.To_Party_IDs])
    service = details[_Detail.Service]
    service_type = details[_Detail.Service_Type]
    action = details[_Detail.Action]

    binding = agreement.resolve(from_party_ids, to_party_ids, service, service_type, action, Direction.Send)

    # .. the header is rebuilt with the values it was sent with ..
    timestamp = datetime.fromisoformat(details[_Detail.Timestamp])
    conversation_id = details[_Detail.Conversation_ID]
    ref_to_message_id = details[_Detail.Ref_To_Message_ID]

    header = new_message_header(binding, timestamp, conversation_id, sent.message_id, ref_to_message_id)
    header.duplicate_elimination = details[_Detail.Duplicate_Elimination]

    if time_to_live := details[_Detail.Time_To_Live]:
        header.message_data.time_to_live = datetime.fromisoformat(time_to_live)

    # .. the bytes are those of the first delivery ..
    package = Package()
    package.headers = sent.wire_headers
    package.body = sent.wire_body

    # .. and an exchange that ended is in the state its final state says.
    if sent.retry_state.is_answered:
        state = _completed_states[sent.outcome.final_state]
    else:
        state = OutboundState.Pending

    out = OutboundMessage()
    out.binding = binding
    out.local_keys = local_keys
    out.header = header
    out.message_id = sent.message_id
    out.package = package
    out.endpoint = sent.endpoint
    out.signature = None
    out.sent_digests = details[_Detail.Sent_Digests]
    out.is_ack_requested = details[_Detail.Is_Ack_Requested]
    out.is_ack_signature_requested = details[_Detail.Is_Ack_Signature_Requested]
    out.is_sync_reply = details[_Detail.Is_Sync_Reply]
    # The exchange continues on copies, so that the record read from the send log stays as it was read.
    out.policy = deepcopy(sent.policy)
    out.retry_state = deepcopy(sent.retry_state)
    out.state = state
    out.outcome = deepcopy(sent.outcome)

    return out

# ################################################################################################################################
# ################################################################################################################################
