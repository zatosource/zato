# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Non-repudiation evidence recording - every AS2 exchange lands in the shared audit log
# with the complete raw MIME body, the Message-ID, the MIC with its algorithm,
# the AS2-From/AS2-To pair and the disposition, because the partner's signed MDN
# plus the retained original message is what resolves a dispute.

from __future__ import annotations

# stdlib
from base64 import b64decode, b64encode

# Zato
from zato.common.as2.mdn import normalize_message_id
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.inbound import InboundResult
    from zato.common.as2.outbound import SendResult
    from zato.common.as2.partnership import Partnership
    from zato.common.as2.reconcile import MDNReconciler
    from zato.common.audit_log.api import AuditLog
    AuditLog = AuditLog
    InboundResult = InboundResult
    MDNReconciler = MDNReconciler
    Partnership = Partnership
    SendResult = SendResult

# ################################################################################################################################
# ################################################################################################################################

def encode_raw_mime(data:'bytes') -> 'str':
    """ Encodes raw MIME bytes for storage inside an event's JSON data.
    """
    encoded = b64encode(data)

    out = encoded.decode('ascii')
    return out

# ################################################################################################################################

def decode_raw_mime(value:'str') -> 'bytes':
    """ Decodes the raw MIME bytes stored with an event.
    """
    out = b64decode(value)
    return out

# ################################################################################################################################
# ################################################################################################################################

def record_message_received(
    audit_log:'AuditLog',
    as2_from:'str',
    as2_to:'str',
    message_id:'str',
    *,
    payload:'str' = '',
    filename:'str' = '',
    content_type:'str' = '',
    cid:'str' = '',
    correl_id:'str' = '',
    raw_mime:'str' = '',
    mic:'str' = '',
    error:'str' = '',
    outcome:'str' = AuditOutcome.OK,
    ) -> 'None':
    """ Records that a message arrived from the partner, with the clear payload stored alongside
    so a later reprocess can re-publish it, and the raw MIME body kept as delivery evidence.
    A reprocess of a stored message links back to the original event through the correlation id.
    """
    as2_from = as2_from.strip()
    as2_to = as2_to.strip()

    pair = f'{as2_from}:{as2_to}'
    message_id = normalize_message_id(message_id)

    details = {'payload': payload, 'filename': filename, 'content_type': content_type, 'raw_mime': raw_mime,
        'mic': mic, 'error': error}
    data = dumps(details)

    audit_log.insert(AuditSource.AS2, AuditEvent.Message_Received, pair, cid=cid, msg_id=message_id, correl_id=correl_id,
        outcome=outcome, data=data)

# ################################################################################################################################

def record_mdn_sent(
    audit_log:'AuditLog',
    as2_from:'str',
    as2_to:'str',
    message_id:'str',
    *,
    disposition:'str' = '',
    modifier_kind:'str' = '',
    modifier:'str' = '',
    mic:'str' = '',
    raw_mime:'str' = '',
    cid:'str' = '',
    outcome:'str' = AuditOutcome.OK,
    ) -> 'None':
    """ Records that an MDN went back to the partner - the receipt half of an inbound exchange,
    with the disposition it reported and the raw MDN bytes kept as delivery evidence.
    """
    as2_from = as2_from.strip()
    as2_to = as2_to.strip()

    pair = f'{as2_from}:{as2_to}'
    message_id = normalize_message_id(message_id)

    details = {'disposition': disposition, 'modifier_kind': modifier_kind, 'modifier': modifier, 'mic': mic,
        'raw_mime': raw_mime}
    data = dumps(details)

    audit_log.insert(AuditSource.AS2, AuditEvent.MDN_Sent, pair, cid=cid, msg_id=message_id, outcome=outcome, data=data)

# ################################################################################################################################
# ################################################################################################################################

def record_send_result(
    reconciler:'MDNReconciler',
    as2_from:'str',
    as2_to:'str',
    result:'SendResult',
    *,
    payload:'str' = '',
    filename:'str' = '',
    async_mdn_url:'str' = '',
    cid:'str' = '',
    correl_id:'str' = '',
    ) -> 'None':
    """ Records everything one outbound delivery produced - the message-sent event with the raw
    MIME body and the MIC computed at send time, plus the mdn-received event when a synchronous
    MDN rode back on the response, which also closes the exchange for reconciliation.
    """

    # The send half of the reconciliation pair, with the full evidence tuple in its data ..
    raw_mime = encode_raw_mime(result.request_body)

    reconciler.record_message_sent(
        as2_from,
        as2_to,
        result.message_id,
        mic=result.mic,
        async_mdn_url=async_mdn_url,
        cid=cid,
        correl_id=correl_id,
        payload=payload,
        filename=filename,
        raw_mime=raw_mime,
    )

    # .. and with no synchronous MDN there is nothing more to record -
    # an asynchronous one arrives later through its own channel.
    mdn = result.mdn
    if not mdn:
        return

    # The receipt itself is evidence too, disposition and raw bytes included.
    if result.is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    mdn_raw_mime = encode_raw_mime(result.response_body)

    mdn_details = {'disposition': mdn.disposition, 'modifier_kind': mdn.modifier_kind, 'modifier': mdn.modifier,
        'mic': mdn.mic, 'raw_mime': mdn_raw_mime}
    mdn_data = dumps(mdn_details)

    reconciler.record_mdn_received(result.message_id, outcome=outcome, cid=cid, data=mdn_data)

# ################################################################################################################################

def record_inbound_result(audit_log:'AuditLog', result:'InboundResult', body:'bytes', cid:'str') -> 'None':
    """ Records everything one inbound request produced - the message-received event with the raw
    MIME body as it arrived, plus the mdn-sent event when an MDN went back, synchronously
    or through the asynchronous delivery the caller performs.
    """

    # A replay was recorded when the message arrived the first time - nothing new happened.
    if result.is_duplicate:
        return

    # The clear payload of the first document travels with the event, which is what
    # a later reprocess runs on - the raw MIME preserves the complete exchange either way.
    if result.payloads:
        first_payload = result.payloads[0]
        payload = first_payload.data.decode('utf8', 'replace')
        filename = first_payload.filename
        content_type = first_payload.content_type
    else:
        payload = ''
        filename = ''
        content_type = ''

    if result.is_error:
        outcome = AuditOutcome.Error
        error = result.error_modifier
        if error is None:
            error = ''
    else:
        outcome = AuditOutcome.OK
        error = ''

    raw_mime = encode_raw_mime(body)

    record_message_received(
        audit_log,
        result.as2_from,
        result.as2_to,
        result.message_id,
        payload=payload,
        filename=filename,
        content_type=content_type,
        cid=cid,
        raw_mime=raw_mime,
        mic=result.mic,
        error=error,
        outcome=outcome,
    )

    # The MDN that went back, when one was produced at all - it rides on the HTTP response
    # for a synchronous receipt and through its own delivery for an asynchronous one.
    if pending := result.pending_async_mdn:
        mdn_body = pending.body
    else:
        mdn_body = result.body

    if not mdn_body:
        return

    disposition = result.disposition

    if not disposition:
        return

    mdn_raw_mime = encode_raw_mime(mdn_body)

    record_mdn_sent(
        audit_log,
        result.as2_from,
        result.as2_to,
        result.message_id,
        disposition=disposition.disposition_type,
        modifier_kind=disposition.modifier_kind,
        modifier=disposition.modifier,
        mic=result.mic,
        raw_mime=mdn_raw_mime,
        cid=cid,
        outcome=outcome,
    )

# ################################################################################################################################
# ################################################################################################################################
