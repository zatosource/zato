# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Resubmit - the operator half of the delivery taxonomy, distinct from the repeat delivery that
# reception awareness performs under the eb:MessageId of the attempt it repeats. A resend takes the
# payloads stored with a message-sent event and delivers them as a message of their own with a new
# eb:MessageId, and a reprocess takes a message-received event and routes its payloads again, for
# when the system behind the channel was down. Either way the new attempt lands as its own audit
# event linked to the original one by the correlation id.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as4.audit import decode_payload_documents, record_message_received, record_send_result
from zato.common.as4.common import AS4Exception
from zato.common.as4.ebms import UserMessageDetails
from zato.common.as4.outbound import new_part
from zato.common.as4.resend import ResendCandidate
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.audit_log.resubmit import Action_Reprocess, Action_Resend, load_event as load_event_core, \
    register_resubmit_handler, require_event_type, ResubmitException, StoredEvent
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.outbound import SendResult
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, callable_, dictlist, stranydict
    from zato.common.util.xml_.mime_ import part_list
    anylist = anylist
    AuditLog = AuditLog
    callable_ = callable_
    dictlist = dictlist
    part_list = part_list
    SendResult = SendResult
    StoredEvent = StoredEvent
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReprocessResult:
    """ What one reprocess did - every message that was routed again, one per payload
    of the delivery it was made from.
    """
    messages: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def new_send_report() -> 'stranydict':
    """ Returns an empty delivery report - the shape a completed delivery and a failed attempt
    share, so callers always read the same keys.
    """
    out:'stranydict' = {
        'is_ok': False,
        'message_id': '',
        'http_status': 0,
        'has_receipt': False,

        # What the partner answered with instead of acknowledging the message.
        'errors': [],

        # Why the message never left at all, the description of the exception raised.
        'error': '',
    }

    return out

# ################################################################################################################################

def describe_send_result(result:'SendResult') -> 'stranydict':
    """ Turns one delivery into a report of what came back for it - the transport outcome, whether
    a receipt arrived and whatever error signals the partner returned.
    """

    # Our response to produce
    out = new_send_report()

    out['is_ok'] = result.is_ok
    out['message_id'] = result.message_id
    out['http_status'] = result.http_status
    out['has_receipt'] = bool(result.receipt)

    errors:'anylist' = []

    for error in result.errors:
        errors.append({
            'error_code': error.error_code,
            'severity': error.severity,
            'short_description': error.short_description,
            'detail': error.detail,
        })

    out['errors'] = errors

    return out

# ################################################################################################################################
# ################################################################################################################################

def load_event(event_id:'int') -> 'StoredEvent':
    """ Reads one audit event by its id, along with its parsed JSON data. The loading itself lives
    in the shared resubmit core - this wrapper only keeps the AS4 error contract, where everything
    AS4-related raises AS4Exception.
    """
    try:
        out = load_event_core(event_id)
    except ResubmitException as e:
        raise AS4Exception(e.args[0])

    return out

# ################################################################################################################################

def _require_event_type(event:'StoredEvent', expected:'str', action:'str') -> 'None':
    """ Confirms an event is of the one type an action applies to, under the AS4 error contract.
    """
    try:
        require_event_type(event, expected, action)
    except ResubmitException as e:
        raise AS4Exception(e.args[0])

# ################################################################################################################################

def _get_stored_documents(event:'StoredEvent') -> 'anylist':
    """ Returns every payload stored with an event, each as a (bytes, content type, content id)
    tuple - an event recorded without any cannot be resubmitted.
    """
    out = decode_payload_documents(event.details)

    if not out:
        raise AS4Exception(f'Audit event `{event.id}` does not carry a payload to resubmit')

    return out

# ################################################################################################################################

def build_parts(documents:'anylist') -> 'part_list':
    """ Wraps the payloads stored with an event in MIME parts again, each keeping the content type
    it was received or sent as. The Content-IDs are fresh because this is a message of its own.
    """

    # Our response to produce
    out:'part_list' = []

    for data, content_type, _ in documents:
        part = new_part(data, content_type)
        out.append(part)

    return out

# ################################################################################################################################

def find_connection_name(configs:'dictlist', from_party:'str', to_party:'str') -> 'str':
    """ Returns the name of the outgoing AS4 connection whose two eb:PartyId values form the given
    pair - the connection a stored message goes back out through on a resend.
    """
    for config in configs:
        if config['as4_from_party'] == from_party:
            if config['as4_to_party'] == to_party:
                out = config['name']
                break
    else:
        raise AS4Exception(f'No outgoing AS4 connection matches the pair `{from_party}:{to_party}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_detail(event:'StoredEvent', name:'str') -> 'str':
    """ Returns one detail an event was recorded with - an event of an older release
    carries nothing under a name that did not exist then.
    """
    value = event.details.get(name)

    if value is None:
        value = ''

    out = value
    return out

# ################################################################################################################################

def new_resend_candidate(event:'StoredEvent') -> 'ResendCandidate':
    """ Describes the delivery one stored message goes back out as - the business information and
    the four-corner addressing of the message it was made from, and no eb:MessageId at all, which
    is what makes it a message of its own rather than a repeat of that one.
    """
    documents = _get_stored_documents(event)
    from_party, to_party = event.object_name.split(':', 1)

    # Our response to produce
    out = ResendCandidate()

    out.from_party = from_party
    out.to_party = to_party
    out.conversation_id = _get_detail(event, 'conversation_id')
    out.service = _get_detail(event, 'service')
    out.action = _get_detail(event, 'action')
    out.original_sender = _get_detail(event, 'original_sender')
    out.final_recipient = _get_detail(event, 'final_recipient')
    out.documents = documents

    return out

# ################################################################################################################################

def new_user_message(event:'StoredEvent') -> 'UserMessageDetails':
    """ Rebuilds the ebMS header of one stored inbound message, which is what the routed messages
    of a reprocess carry - the identifiers subscribers see are the ones of the delivery that
    actually happened, not of the reprocess.
    """
    from_party, to_party = event.object_name.split(':', 1)

    # Our response to produce
    out = UserMessageDetails()

    out.message_id = event.msg_id
    out.conversation_id = _get_detail(event, 'conversation_id')
    out.from_party = from_party
    out.to_party = to_party
    out.service = _get_detail(event, 'service')
    out.action = _get_detail(event, 'action')
    out.message_properties = {}
    out.part_details = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def resend(event:'StoredEvent', send:'callable_', audit_log:'AuditLog', cid:'str') -> 'SendResult':
    """ Sends the payloads stored with an outbound event again, as a message of its own with a new
    eb:MessageId - an operator action, unlike the repeat delivery that reuses the eb:MessageId of
    the attempt it repeats when a receipt is overdue. The new attempt is recorded as its own
    message-sent event linked to the original one by the correlation id, which also makes it
    an exchange of its own for reception awareness to watch.
    """
    _require_event_type(event, AuditEvent.Message_Sent, 'resent')

    candidate = new_resend_candidate(event)
    parts = build_parts(candidate.documents)

    # Deliver through the real pipeline - a fresh eb:MessageId is assigned inside ..
    out = send(candidate)

    # .. and the attempt becomes its own event, linked to the original by its CID. The parts are
    # encoded from what was submitted rather than from what went on the wire, so a further resubmit
    # works from the documents themselves rather than from their compressed form.
    record_send_result(audit_log, candidate.from_party, candidate.to_party, out, payloads=parts,
        service=candidate.service, action=candidate.action, original_sender=candidate.original_sender,
        final_recipient=candidate.final_recipient, cid=cid, correl_id=event.cid)

    return out

# ################################################################################################################################

def reprocess(event:'StoredEvent', route:'callable_', audit_log:'AuditLog', cid:'str') -> 'ReprocessResult':
    """ Routes every payload stored with an inbound event again - for when the system behind the
    channel was down and the documents that were already received are to flow once more. A delivery
    of several payloads is routed the way it was the first time, one message per payload. The new
    attempt is recorded as its own message-received event linked to the original one by the
    correlation id.
    """
    _require_event_type(event, AuditEvent.Message_Received, 'reprocessed')

    documents = _get_stored_documents(event)
    parts = build_parts(documents)

    user_message = new_user_message(event)

    # Our response to produce
    out = ReprocessResult()
    out.messages = route(user_message, parts)

    record_message_received(audit_log, user_message, payloads=parts, cid=cid, correl_id=event.cid)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The AS4 handlers are found through the shared registry - the service layer supplies the callables
# when it wires the real connections and channels in.
register_resubmit_handler(AuditSource.AS4, Action_Resend, resend)
register_resubmit_handler(AuditSource.AS4, Action_Reprocess, reprocess)

# ################################################################################################################################
# ################################################################################################################################
