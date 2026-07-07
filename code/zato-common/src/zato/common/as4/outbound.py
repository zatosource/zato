# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# httpx
import httpx

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import AS4Exception, NS
from zato.common.as4.ebms import build_envelope, build_pull_request, build_receipt, build_user_message, new_message_id, \
    parse_messaging
from zato.common.as4.mime_ import build_multipart, compress_part, decompress_part, parse_multipart
from zato.common.as4.security.encrypt import encrypt_parts
from zato.common.as4.security.sign import sign_envelope
from zato.common.as4.security.verify import decrypt_parts, verify_envelope
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.mime_ import new_content_id, Part, part_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import error_info_list, SignalInfo, UserMessageInfo
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, anytuple, strnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anytuple = anytuple
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendResult:
    """ The outcome of pushing one AS4 user message.
    """
    is_ok: bool = False
    message_id: str = ''
    http_status: int = 0

    # The receipt signal parsed from the response, when one arrived synchronously.
    receipt: 'SignalInfo | None' = None

    # Any error signals the responder returned instead of, or next to, a receipt.
    errors: 'error_info_list'

    # The raw response body, kept for audit purposes.
    response_body: bytes = b''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PullResult:
    """ The outcome of one pull request - either a user message with its payloads or nothing to pull.
    """
    is_ok: bool = False
    has_message: bool = False
    http_status: int = 0

    user_message: 'UserMessageInfo | None' = None
    payloads: 'part_list'
    errors: 'error_info_list'

    # Whether the receipt for the pulled message was delivered back successfully.
    receipt_sent: bool = False

# ################################################################################################################################
# ################################################################################################################################

def new_part(data:'bytes', mime_type:'str'='application/xml', character_set:'strnone'=None) -> 'Part':
    """ Wraps payload bytes in a MIME part with a fresh Content-ID.
    """
    out = Part()
    out.data = data
    out.mime_type = mime_type
    out.content_type = mime_type
    out.character_set = character_set
    out.content_id = new_content_id()

    return out

# ################################################################################################################################

def _serialize(envelope:'any_') -> 'bytes':
    """ Serializes an envelope for the wire.
    """
    out = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def _collect_sent_digests(signature:'any_') -> 'strstrdict':
    """ Maps each signed reference URI to its digest value - the receipt must echo these back.
    """
    out:'strstrdict' = {}

    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    for reference in signed_info.findall(qname(NS.DS, 'Reference')):
        digest_value = reference.find(qname(NS.DS, 'DigestValue'))
        out[reference.get('URI') or ''] = digest_value.text or ''

    return out

# ################################################################################################################################

def _check_receipt_digests(receipt:'SignalInfo', sent_digests:'strstrdict') -> 'None':
    """ Compares the digests echoed in a receipt's non-repudiation information
    with what was actually sent - a mismatch means the responder received something else.
    """
    for reference in receipt.receipt_references:
        uri = reference.get('URI') or ''
        digest_value = reference.find(qname(NS.DS, 'DigestValue'))
        echoed = ''.join((digest_value.text or '').split())

        if sent := sent_digests.get(uri):
            if echoed != sent:
                raise AS4Exception(f'Receipt digest mismatch for `{uri}` - sent `{sent}`, receipt has `{echoed}`')

# ################################################################################################################################

def build_push_message(
    pmode:'PMode',
    keystore:'Keystore',
    parts:'part_list',
    conversation_id:'strnone'=None,
    ) -> 'anytuple':
    """ Builds a complete, signed and optionally encrypted AS4 push message.
    Returns the wire body, its content type, the message id and the sent digests.
    """
    message_id = new_message_id()

    if not conversation_id:
        conversation_id = message_id

    # Compression comes first so that the signature covers the compressed bytes ..
    if pmode.compress:
        for part in parts:
            compress_part(part)

    # .. then the header block is built around the parts ..
    envelope = build_envelope()
    _ = build_user_message(envelope, pmode, parts, message_id, conversation_id)

    # .. the whole of it is signed ..
    signature = sign_envelope(envelope, parts, keystore, pmode.security)
    sent_digests = _collect_sent_digests(signature)

    # .. and encrypted last, so that only ciphertext travels over the wire.
    if pmode.security.encrypt:
        if keystore.peer_encryption_certificate:
            encrypt_parts(envelope, parts, keystore, pmode.security)

    body, content_type = build_multipart(_serialize(envelope), parts)

    out = (body, content_type, message_id, sent_digests)
    return out

# ################################################################################################################################

def _post(
    pmode:'PMode',
    body:'bytes',
    content_type:'str',
    client:'httpx.Client | None',
    ) -> 'httpx.Response':
    """ Delivers one AS4 request over HTTP, with a per-call client unless one was supplied.
    """
    headers = {'Content-Type': content_type}

    if client:
        out = client.post(pmode.endpoint_url, content=body, headers=headers)
    else:
        with httpx.Client(verify=pmode.verify_tls, timeout=pmode.http_timeout_seconds) as own_client:
            out = own_client.post(pmode.endpoint_url, content=body, headers=headers)

    return out

# ################################################################################################################################

def send(
    pmode:'PMode',
    keystore:'Keystore',
    parts:'part_list',
    conversation_id:'strnone'=None,
    client:'httpx.Client | None'=None,
    ) -> 'SendResult':
    """ Pushes one AS4 user message with the given payload parts and verifies
    the synchronous receipt when one comes back.
    """

    # Our response to produce
    out = SendResult()
    out.errors = []

    body, content_type, message_id, sent_digests = build_push_message(pmode, keystore, parts, conversation_id)
    out.message_id = message_id

    response = _post(pmode, body, content_type, client)
    out.http_status = response.status_code
    out.response_body = response.content

    # An empty body with a success status means the receipt will arrive asynchronously.
    if not response.content:
        out.is_ok = response.is_success
        return out

    response_envelope, response_parts = parse_multipart(response.content, response.headers['content-type'])
    messaging = parse_messaging(etree.fromstring(response_envelope))

    for signal in messaging.signals:

        # A receipt for our message proves delivery - but only if it echoes our digests.
        if signal.is_receipt:
            if signal.ref_to_message_id == message_id:
                _check_receipt_digests(signal, sent_digests)
                out.receipt = signal

        for error in signal.errors:
            out.errors.append(error)

    _ = response_parts
    out.is_ok = bool(out.receipt) and not out.errors

    return out

# ################################################################################################################################

def _send_pull_receipt(
    pmode:'PMode',
    keystore:'Keystore',
    pulled_message_id:'str',
    signed_references:'any_',
    client:'httpx.Client | None',
    ) -> 'bool':
    """ Acknowledges a pulled user message - per the pull pattern, signals for pulled
    messages are posted asynchronously to the same URL the message was pulled from.
    """
    envelope = build_envelope()
    _ = build_receipt(envelope, pulled_message_id, signed_references)

    if pmode.security.sign_receipts:
        _ = sign_envelope(envelope, [], keystore, pmode.security)

    body, content_type = build_multipart(_serialize(envelope), [])
    response = _post(pmode, body, content_type, client)

    out = response.is_success
    return out

# ################################################################################################################################

def pull(
    pmode:'PMode',
    keystore:'Keystore',
    mpc:'strnone'=None,
    client:'httpx.Client | None'=None,
    ) -> 'PullResult':
    """ Sends a pull request for the given message partition channel and processes
    whatever user message the responder returns: decrypt, verify, decompress, acknowledge.
    """

    # Our response to produce
    out = PullResult()
    out.payloads = []
    out.errors = []

    if not mpc:
        mpc = pmode.mpc

    # A pull request is a signed signal without payloads ..
    envelope = build_envelope()
    _ = build_pull_request(envelope, mpc)
    _ = sign_envelope(envelope, [], keystore, pmode.security)

    body, content_type = build_multipart(_serialize(envelope), [])

    # .. the response carries either a user message or an error signal such as an empty channel warning.
    response = _post(pmode, body, content_type, client)
    out.http_status = response.status_code

    if not response.content:
        out.is_ok = response.is_success
        return out

    response_envelope_bytes, response_parts = parse_multipart(response.content, response.headers['content-type'])
    response_envelope = etree.fromstring(response_envelope_bytes)
    messaging = parse_messaging(response_envelope)

    for signal in messaging.signals:
        for error in signal.errors:
            out.errors.append(error)

    # No user message means there was nothing to pull.
    if not messaging.user_messages:
        out.is_ok = not out.errors
        return out

    user_message = messaging.user_messages[0]
    out.user_message = user_message
    out.has_message = True

    # The pulled message is processed exactly like a pushed one -
    # decrypt first, verify the plaintext signature, then decompress.
    decrypt_parts(response_envelope, response_parts, keystore)
    verify_result = verify_envelope(response_envelope, response_parts, keystore)

    for part_info in user_message.part_infos:
        content_id = part_info.href[4:]

        for part in response_parts:
            if part.content_id == content_id:
                if compression_type := part_info.properties.get('CompressionType'):
                    part.compressed = True
                    part.content_type = compression_type
                    if mime_type := part_info.properties.get('MimeType'):
                        part.mime_type = mime_type
                    decompress_part(part)
                out.payloads.append(part)
                break

    out.receipt_sent = _send_pull_receipt(pmode, keystore, user_message.message_id, verify_result.signed_references, client)
    out.is_ok = not out.errors

    return out

# ################################################################################################################################
# ################################################################################################################################
