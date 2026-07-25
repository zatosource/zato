# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Non-repudiation evidence recording - every AS4 exchange lands in the shared audit log with the
# complete wire bytes, the eb:MessageId, the conversation id, the eb:Service and eb:Action and the
# party pair, because the partner's signed receipt plus the retained message is what resolves
# a dispute over what was delivered.

from __future__ import annotations

# stdlib
from base64 import b64decode, b64encode

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import SignalDetails, UserMessageDetails
    from zato.common.as4.inbound import InboundResult
    from zato.common.as4.outbound import PullResult, SendResult
    from zato.common.as4.reconcile import ReceiptReconciler
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, stranydict
    from zato.common.util.xml_.mime_ import part_list
    anylist = anylist
    AuditLog = AuditLog
    InboundResult = InboundResult
    part_list = part_list
    PullResult = PullResult
    ReceiptReconciler = ReceiptReconciler
    SendResult = SendResult
    SignalDetails = SignalDetails
    stranydict = stranydict
    UserMessageDetails = UserMessageDetails

# ################################################################################################################################
# ################################################################################################################################

def encode_wire_bytes(data:'bytes') -> 'str':
    """ Encodes the bytes of one message for storage inside an event's JSON data.
    """
    encoded = b64encode(data)

    out = encoded.decode('ascii')
    return out

# ################################################################################################################################

def decode_wire_bytes(value:'str') -> 'bytes':
    """ Decodes the bytes of one message stored with an event.
    """
    out = b64decode(value)
    return out

# ################################################################################################################################
# ################################################################################################################################

def party_pair(from_party:'str', to_party:'str') -> 'str':
    """ Returns the object name an AS4 exchange is recorded under - the two eb:PartyId values
    of the exchange, in the direction the user message travelled.
    """
    from_party = from_party.strip()
    to_party = to_party.strip()

    out = f'{from_party}:{to_party}'
    return out

# ################################################################################################################################

def encode_payload_document(data:'bytes', content_type:'str', content_id:'str') -> 'stranydict':
    """ Encodes one payload part for storage as an event's payload entry.

    The bytes are base64-encoded because an event's data is JSON and JSON carries text. A payload
    that was never text - a compressed archive or a signed PDF - does not survive being decoded as
    UTF-8 with replacement characters, and a resubmit works from these entries.
    """
    out:'stranydict' = {
        'data': encode_wire_bytes(data),
        'content_type': content_type,
        'content_id': content_id,
    }

    return out

# ################################################################################################################################

def encode_payloads(payloads:'part_list') -> 'anylist':
    """ Encodes every payload part of one message for storage with its event.
    """

    # Our response to produce
    out:'anylist' = []

    for payload in payloads:
        document = encode_payload_document(payload.data, payload.mime_type, payload.content_id)
        out.append(document)

    return out

# ################################################################################################################################

def decode_payload_documents(details:'stranydict') -> 'anylist':
    """ Returns every payload stored with an event, each as a (bytes, content type, content id)
    tuple, in the order they arrived or were sent.
    """

    # Our response to produce
    out:'anylist' = []

    documents = details.get('payloads')

    if documents is None:
        documents = []

    for document in documents:
        data = decode_wire_bytes(document['data'])
        out.append((data, document['content_type'], document['content_id']))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _payload_size(payloads:'part_list') -> 'int':
    """ Returns the combined length of every payload part of one message.
    """

    # Our response to produce
    out = 0

    for payload in payloads:
        out += len(payload.data)

    return out

# ################################################################################################################################

def _first_payload_text(payloads:'part_list') -> 'str':
    """ Returns the readable view of the first payload of a message, which is what the audit log
    page displays. A message with no payloads at all reads as an empty string.
    """
    if payloads:
        first = payloads[0]
        out = first.data.decode('utf8', 'replace')
    else:
        out = ''

    return out

# ################################################################################################################################

def _error_summary(errors:'anylist') -> 'anylist':
    """ Turns the eb:Error entries of a signal into the entries stored with an event.
    """

    # Our response to produce
    out:'anylist' = []

    for error in errors:
        entry = {
            'error_code': error.error_code,
            'severity': error.severity,
            'short_description': error.short_description,
            'detail': error.detail,
        }
        out.append(entry)

    return out

# ################################################################################################################################
# ################################################################################################################################

def record_message_sent(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    result:'SendResult',
    *,
    payloads:'part_list',
    service:'str',
    action:'str',
    original_sender:'str' = '',
    final_recipient:'str' = '',
    cid:'str' = '',
    ) -> 'None':
    """ Records that a user message was pushed to the partner, with every payload stored alongside
    so a later resend or resubmit can send all of them again and with the request bytes kept as the
    evidence of what was signed.

    The four-corner endpoints travel with the event because a repeat delivery of a message that was
    addressed through discovery has to be addressed the same way again, and the recipient it was
    addressed to is not in the payload the store hands back.
    """
    if result.is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    details = {
        'payload': _first_payload_text(payloads),
        'payloads': encode_payloads(payloads),
        'conversation_id': result.conversation_id,
        'service': service,
        'action': action,
        'original_sender': original_sender,
        'final_recipient': final_recipient,
        'errors': _error_summary(result.errors),
        'http_status': result.http_status,
        'raw_message': encode_wire_bytes(result.request_body),
    }
    data = dumps(details)

    values = {
        'cid': cid,
        'msg_id': result.message_id,
        'correl_id': result.conversation_id,
        'outcome': outcome,
        'size': _payload_size(payloads),
        'data': data,
        'attrs': {'service': service, 'action': action, 'conversation_id': result.conversation_id},
    }

    _ = audit_log.insert(AuditSource.AS4, AuditEvent.Message_Sent, party_pair(from_party, to_party), **values)

# ################################################################################################################################

def record_receipt_received(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    receipt:'SignalDetails',
    *,
    ref_to_message_id:'str',
    raw_message:'bytes' = b'',
    errors:'anylist | None' = None,
    is_matched:'bool' = True,
    cid:'str' = '',
    ) -> 'None':
    """ Records that a receipt came back for a message sent earlier - the half of the pair that
    says the partner acknowledged what was delivered. The event is stored under the message id of
    the user message it refers to, which is what pairs it with the send.

    A receipt that arrives with error signals next to it is recorded as a failure, because the
    exchange did not complete on the terms it was sent under. One that answers no message this side
    has open is recorded as unmatched, which is how an operator tells a repeated or misdirected
    receipt from one that closed an exchange.
    """
    if errors is None:
        errors = []

    if errors:
        outcome = AuditOutcome.Error
    else:
        outcome = AuditOutcome.OK

    details = {
        'receipt_message_id': receipt.message_id,
        'timestamp': receipt.timestamp,
        'errors': _error_summary(errors),
        'is_matched': is_matched,
        'raw_message': encode_wire_bytes(raw_message),
    }
    data = dumps(details)

    values = {'cid': cid, 'msg_id': ref_to_message_id, 'outcome': outcome, 'data': data}

    _ = audit_log.insert(AuditSource.AS4, AuditEvent.Receipt_Received, party_pair(from_party, to_party), **values)

# ################################################################################################################################

def record_errors_received(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    *,
    ref_to_message_id:'str',
    errors:'anylist',
    raw_message:'bytes' = b'',
    is_matched:'bool' = True,
    cid:'str' = '',
    ) -> 'None':
    """ Records that the partner answered a sent message with error signals and no receipt at all.
    The row sits on the receipt half of the pair so the message it refers to stops counting
    as outstanding while still reading as failed.
    """
    details = {
        'receipt_message_id': '',
        'timestamp': '',
        'errors': _error_summary(errors),
        'is_matched': is_matched,
        'raw_message': encode_wire_bytes(raw_message),
    }
    data = dumps(details)

    values = {'cid': cid, 'msg_id': ref_to_message_id, 'outcome': AuditOutcome.Error, 'data': data}

    _ = audit_log.insert(AuditSource.AS4, AuditEvent.Receipt_Received, party_pair(from_party, to_party), **values)

# ################################################################################################################################
# ################################################################################################################################

def record_message_received(
    audit_log:'AuditLog',
    user_message:'UserMessageDetails',
    *,
    payloads:'part_list',
    raw_message:'bytes' = b'',
    error:'str' = '',
    outcome:'str' = AuditOutcome.OK,
    cid:'str' = '',
    ) -> 'None':
    """ Records that a user message arrived from the partner, with every payload stored losslessly
    so a later reprocess can re-publish all of them, and the wire bytes kept as delivery evidence.
    """
    details = {
        'payload': _first_payload_text(payloads),
        'payloads': encode_payloads(payloads),
        'conversation_id': user_message.conversation_id,
        'service': user_message.service,
        'action': user_message.action,
        'error': error,
        'raw_message': encode_wire_bytes(raw_message),
    }
    data = dumps(details)

    attrs = {
        'service': user_message.service,
        'action': user_message.action,
        'conversation_id': user_message.conversation_id,
    }

    values = {
        'cid': cid,
        'msg_id': user_message.message_id,
        'correl_id': user_message.conversation_id,
        'outcome': outcome,
        'size': _payload_size(payloads),
        'data': data,
        'attrs': attrs,
    }

    pair = party_pair(user_message.from_party, user_message.to_party)

    _ = audit_log.insert(AuditSource.AS4, AuditEvent.Message_Received, pair, **values)

# ################################################################################################################################

def record_receipt_sent(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    *,
    ref_to_message_id:'str',
    raw_message:'bytes' = b'',
    error_code:'str' = '',
    cid:'str' = '',
    ) -> 'None':
    """ Records the signal that went back to the partner - a receipt when the message was accepted
    and an ebMS error signal when it was not, with the bytes of it kept as delivery evidence.
    """
    if error_code:
        outcome = AuditOutcome.Error
    else:
        outcome = AuditOutcome.OK

    details = {'error_code': error_code, 'raw_message': encode_wire_bytes(raw_message)}
    data = dumps(details)

    values = {'cid': cid, 'msg_id': ref_to_message_id, 'outcome': outcome, 'data': data}

    _ = audit_log.insert(AuditSource.AS4, AuditEvent.Receipt_Sent, party_pair(from_party, to_party), **values)

# ################################################################################################################################
# ################################################################################################################################

def _resolve_signal_pair(
    reconciler:'ReceiptReconciler | None',
    ref_to_message_id:'str',
    own_party:'str',
    partner_party:'str',
    ) -> 'tuple[str, str, bool]':
    """ Returns the party pair one standalone signal is recorded under, plus whether the message it
    answers was found at all. A signal echoes only the id of that message, so the pair comes from
    the message that went out under it - which is what makes an asynchronous receipt land on the
    same pair as its own send even when it arrives on a channel of a different pair.

    Without a store to ask, and for a signal answering nothing this side has open, the pair of the
    channel the signal arrived on is what places it.
    """
    if reconciler:
        pending = reconciler.match(ref_to_message_id)

        if pending:
            out = pending.from_party, pending.to_party, True
            return out

    out = own_party, partner_party, False
    return out

# ################################################################################################################################
# ################################################################################################################################

def record_send_result(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    result:'SendResult',
    *,
    payloads:'part_list',
    service:'str',
    action:'str',
    original_sender:'str' = '',
    final_recipient:'str' = '',
    cid:'str' = '',
    ) -> 'None':
    """ Records everything one push produced - the message-sent event with the request bytes and
    every payload, plus the receipt-received event when a receipt rode back on the response.

    A push whose receipt is to arrive asynchronously records the send alone, and the receipt
    is recorded by the channel it later arrives on.
    """
    record_message_sent(audit_log, from_party, to_party, result, payloads=payloads, service=service,
        action=action, original_sender=original_sender, final_recipient=final_recipient, cid=cid)

    receipt = result.receipt

    # The receipt half of the pair, with whatever the partner reported alongside it ..
    if receipt:
        record_receipt_received(audit_log, from_party, to_party, receipt,
            ref_to_message_id=result.message_id, raw_message=result.response_body,
            errors=result.errors, cid=cid)

    # .. and a response that carried errors instead of a receipt closes the pair too.
    elif result.errors:
        record_errors_received(audit_log, from_party, to_party, ref_to_message_id=result.message_id,
            errors=result.errors, raw_message=result.response_body, cid=cid)

# ################################################################################################################################

def record_inbound_result(
    audit_log:'AuditLog',
    result:'InboundResult',
    body:'bytes',
    cid:'str',
    *,
    own_party:'str' = '',
    partner_party:'str' = '',
    reconciler:'ReceiptReconciler | None' = None,
    ) -> 'None':
    """ Records everything one inbound request produced - the message-received event with the bytes
    as they arrived, the receipt-sent event for the signal that went back, and a receipt-received
    event for each standalone signal the partner delivered for a message sent earlier.

    A user message carries the pair it belongs to in its own header. A standalone signal does not,
    it only echoes the id of the message it answers, so the message that was sent under that id is
    what places it - and the two party identifiers of the channel it arrived on are the fallback
    for a signal answering nothing this side has open.

    A replay was recorded when the message first arrived, so nothing new is written for it.
    """
    user_message = result.user_message

    if user_message:
        if not result.is_duplicate:

            if result.is_error:
                outcome = AuditOutcome.Error
            else:
                outcome = AuditOutcome.OK

            error_code = result.error_code
            if error_code is None:
                error_code = ''

            record_message_received(audit_log, user_message, payloads=result.payloads,
                raw_message=body, error=error_code, outcome=outcome, cid=cid)

            # The signal that answered the message, whichever kind it was.
            record_receipt_sent(audit_log, user_message.from_party, user_message.to_party,
                ref_to_message_id=user_message.message_id, raw_message=result.body,
                error_code=error_code, cid=cid)

    # Signals delivered on their own belong to a message that was sent from here, so the pair
    # they close is the one the sending direction opened - which is this pair reversed.
    for signal in result.signals:

        ref_to_message_id = signal.ref_to_message_id
        if ref_to_message_id is None:
            ref_to_message_id = ''

        from_party, to_party, is_matched = _resolve_signal_pair(reconciler, ref_to_message_id, own_party, partner_party)

        if signal.is_receipt:
            record_receipt_received(audit_log, from_party, to_party, signal,
                ref_to_message_id=ref_to_message_id, raw_message=body, errors=signal.errors,
                is_matched=is_matched, cid=cid)

        elif signal.errors:
            record_errors_received(audit_log, from_party, to_party,
                ref_to_message_id=ref_to_message_id, errors=signal.errors, raw_message=body,
                is_matched=is_matched, cid=cid)

# ################################################################################################################################

def record_pull_result(
    audit_log:'AuditLog',
    from_party:'str',
    to_party:'str',
    result:'PullResult',
    cid:'str' = '',
    ) -> 'None':
    """ Records everything one pull produced - the message-received event for the message that was
    pulled and the receipt-sent event for the acknowledgement posted back for it. A pull that found
    an empty channel produced no message, so it records nothing.
    """
    user_message = result.user_message

    if not user_message:
        return

    record_message_received(audit_log, user_message, payloads=result.payloads,
        raw_message=result.response_body, cid=cid)

    if result.receipt_sent:
        record_receipt_sent(audit_log, from_party, to_party, ref_to_message_id=user_message.message_id,
            raw_message=result.receipt_body, cid=cid)

# ################################################################################################################################
# ################################################################################################################################
