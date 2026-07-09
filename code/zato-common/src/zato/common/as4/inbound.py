# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from http.client import OK

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError, Severity
from zato.common.as4.ebms import build_envelope, build_error, build_receipt, parse_messaging
from zato.common.as4.mime_ import decompress_part, parse_multipart
from zato.common.as4.security.sign import sign_envelope
from zato.common.as4.security.verify import decrypt_parts, verify_envelope
from zato.common.util.xml_.mime_ import part_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import signal_info_list, UserMessageInfo
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, callable_, strnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    callable_ = callable_
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

_soap_content_type = 'application/soap+xml; charset=UTF-8'

# ################################################################################################################################
# ################################################################################################################################

pmode_list = list['PMode']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundResult:
    """ What the transport should send back and what the application receives.
    """
    # The HTTP response - a signed receipt on success, an ebMS error signal otherwise.
    status_code:  int = OK
    content_type: str = _soap_content_type
    body:         bytes = b''

    # The parsed user message and its decrypted, decompressed payloads.
    user_message: 'UserMessageInfo | None' = None
    payloads: 'part_list'

    # Signals delivered to us - asynchronous receipts or errors from a previous exchange.
    signals: 'signal_info_list'

    # Whether the message was recognized as a duplicate - the receipt is still returned
    # but the payloads must not be processed a second time.
    is_duplicate: bool = False

    # Whether this message failed and the body is an error signal.
    is_error: bool = False
    error_code: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def _match_pmode(pmodes:'pmode_list', user_message:'UserMessageInfo') -> 'PMode':
    """ Finds the P-Mode that governs an incoming user message by its service and action,
    defaulting to the first configured one when nothing matches exactly.
    """
    for pmode in pmodes:
        if pmode.service == user_message.service:
            if pmode.action == user_message.action:
                out = pmode
                break
    else:
        if not pmodes:
            raise AS4ProtocolException(EbMSError.Processing_Mode_Mismatch, 'No P-Modes are configured')
        out = pmodes[0]

    return out

# ################################################################################################################################

def _serialize(envelope:'any_') -> 'bytes':
    """ Serializes a response envelope for the wire.
    """
    out = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def build_error_response(
    ref_to_message_id:'strnone',
    error_code:'str',
    detail:'str',
    keystore:'Keystore | None',
    pmode:'PMode | None',
    ) -> 'bytes':
    """ Builds the ebMS error signal that goes back on the HTTP response,
    signing it when the P-Mode calls for signed signals and signing is possible.
    """
    envelope = build_envelope()
    _ = build_error(envelope, ref_to_message_id, error_code, error_code, detail, Severity.Failure)

    if pmode:
        if keystore:
            if pmode.security.sign_receipts:
                if keystore.signing_key:
                    _ = sign_envelope(envelope, [], keystore, pmode.security)

    out = _serialize(envelope)
    return out

# ################################################################################################################################

def _restore_payloads(user_message:'UserMessageInfo', parts:'part_list') -> 'part_list':
    """ Matches decrypted MIME parts with their eb:PartInfo entries and undoes
    the AS4 compression, returning the payloads as the sender originally submitted them.
    """
    out:'part_list' = []

    for part_info in user_message.part_infos:

        # Only cid: references point at MIME parts - anything else would be
        # an (unsupported) external or body reference.
        if not part_info.href.startswith('cid:'):
            raise AS4ProtocolException(EbMSError.Value_Not_Recognized, f'Unsupported PartInfo href `{part_info.href}`')

        content_id = part_info.href[4:]

        for part in parts:
            if part.content_id == content_id:
                break
        else:
            raise AS4ProtocolException(
                EbMSError.Mime_Inconsistency, f'PartInfo `{part_info.href}` has no matching MIME part')

        if mime_type := part_info.properties.get('MimeType'):
            part.mime_type = mime_type

        if character_set := part_info.properties.get('CharacterSet'):
            part.character_set = character_set

        # The CompressionType property is the receiver's only signal that a part is compressed.
        if compression_type := part_info.properties.get('CompressionType'):
            part.content_type = compression_type
            part.compressed = True
            decompress_part(part)

        out.append(part)

    return out

# ################################################################################################################################

def handle(
    body:'bytes',
    content_type:'str',
    pmodes:'pmode_list',
    keystore:'Keystore',
    is_duplicate:'callable_ | None'=None,
    validate:'callable_ | None'=None,
    ) -> 'InboundResult':
    """ The transport-neutral inbound pipeline. Takes the raw HTTP body and content type
    of an incoming AS4 request and returns what to send back plus the delivered payloads.

    The is_duplicate callable, when given, receives an eb:MessageId and returns True
    if that message was already processed - the receipt is then repeated without
    delivering the payloads again.

    The validate callable, when given, receives the user message and the restored payloads
    once their signature is verified - it raises AS4ProtocolException to reject the message,
    which turns into a signed ebMS error signal on the response.
    """

    # Our response to produce
    out = InboundResult()
    out.payloads = []
    out.signals = []

    ref_to_message_id:'strnone' = None
    pmode:'PMode | None' = None

    try:
        # Take the envelope and attachments apart ..
        envelope_bytes, parts = parse_multipart(body, content_type)

        try:
            envelope = etree.fromstring(envelope_bytes)
        except Exception as e:
            raise AS4ProtocolException(EbMSError.Invalid_Header, f'Could not parse the SOAP envelope -> {e}')

        messaging = parse_messaging(envelope)

        # Signals without a user message are receipts or errors delivered to us asynchronously -
        # they are surfaced to the caller and acknowledged with an empty response.
        if not messaging.user_messages:

            for signal in messaging.signals:
                if signal.pull_mpc:
                    raise AS4ProtocolException(
                        EbMSError.Feature_Not_Supported, 'This endpoint does not serve pull requests')
                out.signals.append(signal)

            return out

        user_message = messaging.user_messages[0]
        ref_to_message_id = user_message.message_id
        pmode = _match_pmode(pmodes, user_message)

        # Reverse the security processing - decrypt the wire bytes first,
        # then verify the signature that covers the plaintext ..
        decrypt_parts(envelope, parts, keystore)
        verify_result = verify_envelope(envelope, parts, keystore)

        # .. restore the payloads to what the sender submitted ..
        payloads = _restore_payloads(user_message, parts)

        # .. give the caller a chance to reject the message on business grounds,
        # .. e.g. a receiver that this endpoint does not serve ..
        if validate:
            validate(user_message, payloads)

        # .. and only deliver them if this is not a replay of a message we already have.
        if is_duplicate:
            out.is_duplicate = is_duplicate(user_message.message_id)

        if not out.is_duplicate:
            out.user_message = user_message
            out.payloads = payloads

        # The receipt echoes the verified references - that is the non-repudiation proof.
        receipt_envelope = build_envelope()
        _ = build_receipt(receipt_envelope, user_message.message_id, verify_result.signed_references)

        if pmode.security.sign_receipts:
            _ = sign_envelope(receipt_envelope, [], keystore, pmode.security)

        out.body = _serialize(receipt_envelope)

    except AS4ProtocolException as e:
        out.is_error = True
        out.error_code = e.error_code
        out.body = build_error_response(ref_to_message_id, e.error_code, e.detail, keystore, pmode)

    return out

# ################################################################################################################################
# ################################################################################################################################
