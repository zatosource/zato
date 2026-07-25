# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Delivering one message and reconciling the receipt that rides back on the response, so that
a delivery which left successfully and is still unacknowledged says why.
"""

# Zato
from zato.common.as2.common import AS2Exception, is_digest_equal, MDNMode, SendError
from zato.common.as2.mdn import DispositionType, ModifierKind, normalize_message_id, parse_mdn
from zato.common.as2.outbound.common import SendResult
from zato.common.as2.outbound.message import build_message
from zato.common.as2.outbound.transport import post
from zato.common.as2.partnership import active_verification_certificates

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import httpx
    from zato.common.as2.outbound.common import send_payload
    from zato.common.as2.partnership import Partnership
    from zato.common.typing_ import strnone
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    httpx = httpx
    send_payload = send_payload
    strnone = strnone
    certificate_list = certificate_list
    Keystore = Keystore
    Partnership = Partnership

# ################################################################################################################################
# ################################################################################################################################

def _reconcile_sync_mdn(
    result:'SendResult',
    keystore:'Keystore',
    response:'httpx.Response',
    accepted_certificates:'certificate_list | None' = None,
    ) -> 'None':
    """ Parses and verifies the synchronous MDN riding on the HTTP response. A response whose body
    fails MDN parsing or signature verification counts as no MDN received, an Original-Message-ID
    or Received-Content-MIC mismatch is a delivery failure. A non-empty accepted_certificates list
    is the trust decision for the MDN's signer - during a rotation window it holds both
    the partner's old and new certificate.

    Every way out of here that leaves the message unacknowledged names itself in result.mdn_error,
    because they look identical to an operator otherwise - the delivery left, the partner
    answered, and the message is still not delivered.
    """
    if not (content_type := response.headers.get('content-type')):
        result.mdn_error = SendError.No_Content_Type
        return

    # A body that does not parse and verify as an MDN counts as no MDN received ..
    try:
        mdn = parse_mdn(response.content, content_type, keystore, accepted_certificates)
    except AS2Exception:
        result.mdn_error = SendError.Unparseable_MDN
        return

    result.mdn = mdn

    # .. the MDN must answer the message that was actually sent ..
    answered_id = normalize_message_id(mdn.original_message_id)
    sent_id = normalize_message_id(result.message_id)

    if answered_id != sent_id:
        result.mdn_error = SendError.Message_ID_Mismatch
        return

    # .. a receipt refusing the message itself says so with a Failure modifier, which is the
    # partner rejecting what was asked of them rather than failing at it ..
    if mdn.modifier_kind == ModifierKind.Failure:
        result.mdn_error = SendError.Failure_Modifier
        return

    # .. an error modifier is the partner failing to process content they accepted ..
    if mdn.modifier_kind == ModifierKind.Error:
        result.mdn_error = SendError.Error_Modifier
        return

    # .. the disposition must report processing at all - a warning still counts as processed ..
    if mdn.disposition != DispositionType.Processed:
        result.mdn_error = SendError.Not_Processed
        return

    # .. and the Received-Content-MIC must match what was computed at send time.
    if mdn.mic:
        sent_digest, _, sent_algorithm = result.mic.partition(', ')

        if not is_digest_equal(mdn.mic, sent_digest):
            result.mdn_error = SendError.MIC_Mismatch
            return

        if mdn.mic_algorithm != sent_algorithm:
            result.mdn_error = SendError.MIC_Algorithm_Mismatch
            return

    result.is_ok = True

# ################################################################################################################################

def send(
    partnership:'Partnership',
    keystore:'Keystore',
    payload:'send_payload',
    filename:'strnone' = None,
    client:'httpx.Client | None' = None,
    *,
    message_id:'strnone' = None,
    ) -> 'SendResult':
    """ Delivers one AS2 message and reconciles the synchronous MDN when one was requested.
    Passing the message_id of an earlier delivery makes this a resend - the same content travels
    under the same Message-ID because no MDN arrived for the original attempt.
    """

    # Our response to produce
    out = SendResult()

    body, headers, sent_message_id, mic = build_message(partnership, keystore, payload, filename, message_id)

    out.message_id = sent_message_id
    out.mic = mic
    out.request_body = body

    response = post(partnership, body, headers, client)

    out.http_status = response.status_code
    out.response_body = response.content

    # With a synchronous MDN requested, the response body is the proof of delivery -
    # the partner's rotation list says which certificates may have signed it.
    if partnership.mdn_mode == MDNMode.Sync:
        accepted_certificates = active_verification_certificates(partnership)
        _reconcile_sync_mdn(out, keystore, response, accepted_certificates)

    # .. otherwise transport-level success is all there is to check - an asynchronous MDN
    # arrives later through its own channel and reconciles against the stored MIC.
    else:
        out.is_ok = response.is_success

    return out

# ################################################################################################################################
# ################################################################################################################################
