# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HL7 resubmit semantics on top of the shared resubmit core - a resend takes the payload
# stored with an outbound message-sent event and delivers it through the MLLP outgoing
# connection again, and a reprocess takes an inbound message-received event and re-routes it
# to the channel's service. Either way, the new attempt lands as its own audit event
# linked to the original one by the correlation id, with its attributes extracted afresh,
# so an edited payload is searchable by what it says now, not by what the original said.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import get_stored_payload, register_resubmit_handler, require_event_type, \
    Action_Reprocess, Action_Resend
from zato.common.hl7.audit import get_audit_attrs, get_control_id, interpret_ack
from zato.common.json_internal import dumps
from zato.hl7v2 import parse_hl7, validate_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.audit_log.resubmit import StoredEvent
    from zato.common.typing_ import any_, callable_, intnone, strnone
    from zato.hl7v2 import ValidationResult
    any_ = any_
    AuditLog = AuditLog
    callable_ = callable_
    intnone = intnone
    StoredEvent = StoredEvent
    strnone = strnone
    ValidationResult = ValidationResult

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResendResult:
    """ What one HL7 resend did - the new event, the control id that went out
    and the interpreted acknowledgment when one came back.
    """
    event_id: 'intnone' = None
    control_id: str = ''
    ack_status: str = ''
    ack_outcome: str = ''

# ################################################################################################################################

@dataclass(init=False)
class HL7ReprocessResult:
    """ What one HL7 reprocess did - the new event and the service the message was re-routed to.
    """
    event_id: 'intnone' = None
    control_id: str = ''
    service_name: str = ''

# ################################################################################################################################
# ################################################################################################################################

def validate_payload(payload:'str') -> 'ValidationResult':
    """ Validates an HL7 payload without executing anything - the Validate action
    of edit-then-resubmit. Parsing and validation come from the generated model,
    no validation logic lives here.
    """
    out = validate_message(payload)
    return out

# ################################################################################################################################

def _get_effective_payload(event:'StoredEvent', payload:'strnone') -> 'str':
    """ Returns what actually goes out - the edited payload when the operator supplied one,
    the stored payload otherwise.
    """
    if payload is None:
        out = get_stored_payload(event)
    else:
        out = payload

    return out

# ################################################################################################################################

def resend(
    event:'StoredEvent',
    send:'callable_',
    audit_log:'AuditLog',
    cid:'str',
    *,
    payload:'strnone' = None,
    ) -> 'ResendResult':
    """ Sends the payload stored with an outbound event through the MLLP outgoing connection
    again - for when the receiving system was down and the messages are to flow once more.
    The new attempt is its own message-sent event linked to the original by the correlation id,
    and when the send brings back an acknowledgment, it is interpreted and recorded too.
    """
    require_event_type(event, AuditEvent.Message_Sent, 'resent')

    effective_payload = _get_effective_payload(event, payload)

    # The attributes are extracted afresh so an edited payload is searchable
    # by what it says now - the model parses, nothing is parsed here.
    msg = parse_hl7(effective_payload, validate=False)
    attrs = get_audit_attrs(msg)
    control_id = get_control_id(msg)

    values = {
        'cid': cid,
        'msg_id': control_id,
        'correl_id': event.cid,
        'size': len(effective_payload),
        'data': dumps({'payload': effective_payload}),
        'attrs': attrs,
        'parents': [event.id],
    }

    # Deliver the payload through the real connection ..
    try:
        response = send(effective_payload)

    # .. a failed attempt is recorded too, as its own row with an error outcome,
    # so the delivery history has no holes - then the caller learns about it.
    except Exception as e:
        _ = audit_log.insert(
            AuditSource.HL7, AuditEvent.Message_Sent, event.object_name,
            outcome=AuditOutcome.Error, status=str(e), **values)
        raise

    # Our response to produce
    out = ResendResult()
    out.control_id = control_id

    out.event_id = audit_log.insert(
        AuditSource.HL7, AuditEvent.Message_Sent, event.object_name,
        outcome=AuditOutcome.OK, **values)

    # An acknowledgment that rode back on the send is interpreted and recorded
    # as its own event on the same cid, so the resend's ACK state is filterable too.
    if response:

        ack_message = parse_hl7(response, validate=False)
        ack_result = interpret_ack(ack_message)

        out.ack_status = ack_result.ack_status
        out.ack_outcome = ack_result.outcome

        _ = audit_log.insert(
            AuditSource.HL7, AuditEvent.Ack_Received, event.object_name,
            cid=cid,
            msg_id=control_id,
            correl_id=event.cid,
            size=len(response),
            outcome=ack_result.outcome,
            application_outcome=ack_result.application_outcome,
            classification=ack_result.classification,
            data=dumps({'payload': response}),
        )

    return out

# ################################################################################################################################

def reprocess(
    event:'StoredEvent',
    service_name:'str',
    invoke_service:'callable_',
    audit_log:'AuditLog',
    cid:'str',
    *,
    payload:'strnone' = None,
    ) -> 'HL7ReprocessResult':
    """ Re-routes the payload stored with an inbound event to the channel's service -
    for when the recipient system was down and the already-received messages
    are to flow through again. The new attempt is its own message-received event
    linked to the original by the correlation id.
    """
    require_event_type(event, AuditEvent.Message_Received, 'reprocessed')

    effective_payload = _get_effective_payload(event, payload)

    # Extracted afresh, same as on a resend
    msg = parse_hl7(effective_payload, validate=False)
    attrs = get_audit_attrs(msg)
    control_id = get_control_id(msg)

    # The channel's service receives the message the way a live delivery would arrive
    invoke_service(service_name, effective_payload)

    # Our response to produce
    out = HL7ReprocessResult()
    out.control_id = control_id
    out.service_name = service_name

    out.event_id = audit_log.insert(
        AuditSource.HL7, AuditEvent.Message_Received, event.object_name,
        cid=cid,
        msg_id=control_id,
        correl_id=event.cid,
        size=len(effective_payload),
        outcome=AuditOutcome.OK,
        data=dumps({'payload': effective_payload}),
        attrs=attrs,
        parents=[event.id],
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

# The HL7 handlers are found through the shared registry - the service layer
# supplies the callables when it wires the real connections in.
register_resubmit_handler(AuditSource.HL7, Action_Resend, resend)
register_resubmit_handler(AuditSource.HL7, Action_Reprocess, reprocess)

# ################################################################################################################################
# ################################################################################################################################
