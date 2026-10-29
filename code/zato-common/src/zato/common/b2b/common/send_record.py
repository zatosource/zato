# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.outcome import outcome_from_dict
from zato.common.b2b.common.recovery import read_attrs, read_events
from zato.common.b2b.common.retry import RetryPolicy, RetryState
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.outcome import Outcome
    from zato.common.typing_ import anylist, stranydict, strlist, strstrdict
    anylist = anylist
    Connection = Connection
    Outcome = Outcome
    stranydict = stranydict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

sent_message_list = list['SentMessage']

# ################################################################################################################################
# ################################################################################################################################

class SentData:
    """ The keys of the data documents the events of a sent message have.
    """
    Retries        = 'retries'
    Retry_Interval = 'retry_interval_seconds'
    Expires_At     = 'expires_at'
    Headers        = 'headers'
    Details        = 'details'
    Outcome        = 'outcome'
    Severity       = 'severity'
    Attempts       = 'attempts'
    Signals        = 'signals'
    Signal_Kind    = 'signal_kind'
    Error_Code     = 'error_code'
    Attempt_At     = 'attempt_at'

# ################################################################################################################################
# ################################################################################################################################

class SentInternalData:
    """ The keys of the internal data documents the events of a sent message have, which the free-text search does not cover.
    """
    Details         = 'details'
    Payload_Digests = 'payload_digests'

# ################################################################################################################################
# ################################################################################################################################

# The event types that make up the record of one sent message.
Message_Event_Types = (AuditEvent.Message_Sent, AuditEvent.Message_Resent, AuditEvent.Message_Completed)

# The attributes the first delivery of every message has, whatever its protocol.
_common_attr_names = {B2BAttr.From_Party, B2BAttr.To_Party, B2BAttr.Attempt, B2BAttr.Attempt_At, B2BAttr.Deadline_At}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SentMessage:
    """ One outgoing message as its send log records it - who it is from and to, how it is retried,
    where its delivery stands and what went on the wire.
    """
    message_id: str
    cpa_id:     str
    from_party: str
    to_party:   str
    endpoint:   str

    # The protocol's own searchable attributes of the message.
    attrs: 'stranydict'

    policy:      'RetryPolicy'
    retry_state: 'RetryState'
    outcome:     'Outcome'

    # The protocol's own data that rebuilding the message requires ..
    details: 'stranydict'

    # .. and the part of it that the free-text search does not cover.
    internal_details: 'stranydict'

    # The wire form of the message. The bytes are held only until the first delivery takes them,
    # and are read again by the identifier of the event they are stored with.
    wire_headers:  'strstrdict'
    wire_body:     bytes
    wire_event_id: int = 0

# ################################################################################################################################
# ################################################################################################################################

def new_sent_message(events:'anylist', attrs:'stranydict') -> 'SentMessage':
    """ Builds a message out of its events, the first of which is its first delivery. A resend that reopened
    the exchange after its completion makes the message pending again, with a new retry budget.
    """
    first = events[0]
    first_data = loads(first.data)
    first_internal_data = loads(first.internal_data)

    completion = None
    resend = None

    for event in events[1:]:
        if event.event_type == AuditEvent.Message_Completed:
            completion = event
        elif event.event_type == AuditEvent.Message_Resent:
            completion = None
            resend = event

    # The searchable attributes of the protocol are those the record has on top of the ones every message has.
    protocol_attrs:'stranydict' = {}

    for name, value in attrs.items():
        if name not in _common_attr_names:
            protocol_attrs[name] = value

    policy = RetryPolicy()
    policy.retries = first_data[SentData.Retries]
    policy.retry_interval = timedelta(seconds=first_data[SentData.Retry_Interval])

    retry_state = RetryState()
    retry_state.attempt_count = 1
    retry_state.last_attempt_at = datetime.fromisoformat(attrs[B2BAttr.Attempt_At])

    if expires_at := first_data[SentData.Expires_At]:
        retry_state.expires_at = datetime.fromisoformat(expires_at)

    # A completed message has the outcome its exchange ended with and the deliveries it was made in ..
    if completion:
        completion_data = loads(completion.data)
        completion_internal_data = loads(completion.internal_data)
        payload_digests = completion_internal_data[SentInternalData.Payload_Digests]
        outcome = outcome_from_dict(completion_data[SentData.Outcome], payload_digests)

        if attempts := completion_data[SentData.Attempts]:
            retry_state.attempt_count = len(attempts)
            retry_state.last_attempt_at = datetime.fromisoformat(attempts[-1])

        retry_state.is_answered = True

    # .. while a pending one has the outcome it was sent with, and its deliveries count from its latest resend, if any.
    else:
        payload_digests = first_internal_data[SentInternalData.Payload_Digests]
        outcome = outcome_from_dict(first_data[SentData.Outcome], payload_digests)

        if resend:
            resend_data = loads(resend.data)
            retry_state.last_attempt_at = datetime.fromisoformat(resend_data[SentData.Attempt_At])

    out = SentMessage()
    out.message_id = first.msg_id
    out.cpa_id = first.object_name
    out.from_party = attrs[B2BAttr.From_Party]
    out.to_party = attrs[B2BAttr.To_Party]
    out.endpoint = first.endpoint
    out.attrs = protocol_attrs
    out.policy = policy
    out.retry_state = retry_state
    out.outcome = outcome
    out.details = first_data[SentData.Details]
    out.internal_details = first_internal_data[SentInternalData.Details]
    out.wire_headers = first_data[SentData.Headers]
    out.wire_body = b''
    out.wire_event_id = first.id

    return out

# ################################################################################################################################

def read_stored(connection:'Connection', source:'str', server_name:'str', message_ids:'strlist') -> 'sent_message_list':
    """ Reads the given messages from the audit log, each from its latest first delivery onwards.
    """
    events_by_message = read_events(connection, source, server_name, message_ids, Message_Event_Types)

    message_events:'dict[str, anylist]' = {}
    first_event_ids:'list[int]' = []

    for message_id, events in events_by_message.items():

        current:'anylist' = []

        # A first delivery starts the record anew, and everything recorded after it belongs to it.
        for event in events:
            if event.event_type == AuditEvent.Message_Sent:
                current = []
            current.append(event)

        if current:
            message_events[message_id] = current
            first_event_ids.append(current[0].id)

    attrs_by_event = read_attrs(connection, first_event_ids)

    out:'sent_message_list' = []

    for events in message_events.values():
        first = events[0]
        attrs = attrs_by_event[first.id]
        sent = new_sent_message(events, attrs)
        out.append(sent)

    return out

# ################################################################################################################################
# ################################################################################################################################
