# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Generator, NamedTuple

# httpx
import httpx

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.as2.common import AS2Exception, Default, MDNMode, TransferMode
from zato.common.as2.mdn import describe_disposition, DispositionType, ModifierKind, new_message_id, normalize_message_id, \
    parse_mdn
from zato.common.as2.partnership import active_verification_certificates, quote_as2_identifier, select_encryption_certificate
from zato.common.as2.smime import compress, compute_mic, encode_base64_lines, encrypt, new_part, \
    select_mic_algorithm, sign, SMIMEPart
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.mdn import MDNInfo
    from zato.common.as2.partnership import Partnership
    from zato.common.typing_ import anytuple, stranydict, strnone, strstrdict
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    anytuple = anytuple
    certificate_list = certificate_list
    stranydict = stranydict
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class PayloadItem(NamedTuple):
    """ One document of a multi-document payload - its bytes, content type and filename.
    """
    data: bytes
    content_type: str
    filename: str

# ################################################################################################################################
# ################################################################################################################################

payload_item_list = list[PayloadItem]
bytesgen          = Generator[bytes, None, None]

send_payload:TypeAlias = 'bytes | payload_item_list'

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# How many bytes of the body each chunk of a chunked request carries.
_chunk_size = 64 * 1024

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendResult:
    """ The outcome of delivering one AS2 message.
    """
    is_ok: bool = False

    # The Message-ID the message went out with.
    message_id: str = ''

    # The MIC computed at send time, in its wire form - the returned MDN reconciles against it.
    mic: str = ''

    # The parsed and verified MDN, when a synchronous one arrived.
    mdn: 'MDNInfo | None' = None

    # The complete raw MIME body that went over the wire, kept as delivery evidence.
    request_body: bytes = b''

    # The raw HTTP response, kept for audit purposes.
    http_status: int = 0
    response_body: bytes = b''

# ################################################################################################################################
# ################################################################################################################################

def _new_boundary() -> 'str':
    """ Returns a fresh MIME boundary.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'=-zato-{suffix}'
    return out

# ################################################################################################################################

def _attachment_disposition(filename:'str') -> 'str':
    """ Returns a Content-Disposition header value carrying the given filename.
    """
    out = f'attachment; filename="{filename}"'
    return out

# ################################################################################################################################

def _encode_payload_data(data:'bytes', transfer_encoding:'str') -> 'bytes':
    """ Brings payload bytes into the configured transfer encoding.
    """
    if transfer_encoding == 'base64':
        out = encode_base64_lines(data)
    else:
        out = data

    return out

# ################################################################################################################################

def _resolve_transfer_encoding(partnership:'Partnership') -> 'str':
    """ Returns the transfer encoding outgoing payloads travel in - the partnership's own choice
    unless the force-base64 escape hatch overrides it.
    """
    if partnership.force_base64:
        out = 'base64'
    else:
        out = partnership.content_transfer_encoding

    return out

# ################################################################################################################################

def _build_single_payload_part(partnership:'Partnership', data:'bytes', filename:'strnone') -> 'SMIMEPart':
    """ Builds the MIME entity of a single-document payload.
    """
    transfer_encoding = _resolve_transfer_encoding(partnership)
    encoded = _encode_payload_data(data, transfer_encoding)

    # Our response to produce
    out = new_part(encoded, partnership.content_type, transfer_encoding)

    # The filename travels along only when the partnership preserves filenames.
    if partnership.preserve_filename:
        if filename:
            out.content_disposition = _attachment_disposition(filename)

    return out

# ################################################################################################################################

def _build_related_payload_part(partnership:'Partnership', items:'payload_item_list') -> 'SMIMEPart':
    """ Builds a multipart/related entity out of several documents - the shape logistics partners
    use to send an EDI document together with, say, the PDF of the bill of lading.
    """
    transfer_encoding = _resolve_transfer_encoding(partnership)
    boundary = _new_boundary()

    chunks:'list[bytes]' = []

    for item in items:
        encoded = _encode_payload_data(item.data, transfer_encoding)

        chunks.append(f'--{boundary}'.encode('ascii'))
        chunks.append(f'Content-Type: {item.content_type}'.encode('ascii'))
        chunks.append(f'Content-Transfer-Encoding: {transfer_encoding}'.encode('ascii'))

        if partnership.preserve_filename:
            if item.filename:
                disposition = _attachment_disposition(item.filename)
                chunks.append(f'Content-Disposition: {disposition}'.encode('ascii'))

        chunks.append(b'')
        chunks.append(encoded)

    chunks.append(f'--{boundary}--'.encode('ascii'))
    chunks.append(b'')

    body = _crlf.join(chunks)

    # The type parameter of a multipart/related names the media type of its first part.
    first_item = items[0]
    content_type = f'multipart/related; boundary="{boundary}"; type="{first_item.content_type}"'

    out = new_part(body, content_type)
    return out

# ################################################################################################################################

def _build_payload_part(partnership:'Partnership', payload:'send_payload', filename:'strnone') -> 'SMIMEPart':
    """ Builds the innermost MIME entity - one document or a multipart/related of several.
    """
    # A single document travels as one entity ..
    if isinstance(payload, bytes):
        out = _build_single_payload_part(partnership, payload, filename)

    # .. several documents ride together in a multipart/related.
    else:
        out = _build_related_payload_part(partnership, payload)

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_message(
    partnership:'Partnership',
    keystore:'Keystore',
    payload:'send_payload',
    filename:'strnone'=None,
    message_id:'strnone'=None,
    ) -> 'anytuple':
    """ Builds one complete AS2 message - compress, sign and encrypt in the configured order,
    then the AS2 headers around the result. Returns the body bytes, the HTTP headers,
    the Message-ID and the MIC computed at send time.
    """
    # A fresh Message-ID unless the caller resends earlier content under the original one.
    if not message_id:
        message_id = new_message_id()

    prevent_canonicalization = partnership.prevent_canonicalization
    current = _build_payload_part(partnership, payload, filename)

    # Compression before signing makes the signature cover the compressed bytes ..
    if partnership.compress:
        if partnership.compress_before_signing:
            current = compress(current, prevent_canonicalization)

    # .. the MIC of a signed message covers exactly what gets signed,
    # while an unsigned one is digested only once all its wrapping is done ..
    if partnership.sign:
        mic = compute_mic(
            current,
            partnership.sign_algorithm,
            is_signed=True,
            is_encrypted=partnership.encrypt,
            prevent_canonicalization=prevent_canonicalization,
        )
        current = sign(current, keystore, partnership.sign_algorithm, prevent_canonicalization)
    else:
        mic = ''

    # .. compression after signing wraps the signed structure whole ..
    if partnership.compress:
        if not partnership.compress_before_signing:
            current = compress(current, prevent_canonicalization)

    # .. an unsigned message digests whatever is about to hit the wire or get encrypted,
    # with the MIC algorithm taken from the partnership's own preference list.
    if not mic:
        mic_algorithm = select_mic_algorithm(partnership.mdn_mic_algorithms)
        mic = compute_mic(
            current,
            mic_algorithm,
            is_signed=False,
            is_encrypted=partnership.encrypt,
            prevent_canonicalization=prevent_canonicalization,
        )

    # .. and encryption comes last, so that only ciphertext travels over the wire.
    # The partner's rotation list decides what to encrypt to - during a migration window
    # the most recently activated certificate wins - while a partnership without one
    # uses the certificate pinned in the keystore.
    if partnership.encrypt:
        encryption_certificate = select_encryption_certificate(partnership)

        if not encryption_certificate:
            encryption_certificate = keystore.peer_encryption_certificate

        if not encryption_certificate:
            raise AS2Exception(f'No encryption certificate for partner `{partnership.as2_to}`')

        current = encrypt(
            current,
            encryption_certificate,
            partnership.encryption_algorithm,
            partnership.force_base64,
            prevent_canonicalization,
        )

    # The outermost entity's MIME headers become HTTP headers.
    headers:'strstrdict' = {}

    headers['Content-Type'] = current.content_type
    headers['Content-Transfer-Encoding'] = current.content_transfer_encoding

    if current.content_disposition:
        headers['Content-Disposition'] = current.content_disposition

    headers['MIME-Version'] = '1.0'
    headers['Message-ID'] = message_id
    headers['Subject'] = partnership.subject
    headers['AS2-Version'] = partnership.as2_version
    headers['AS2-From'] = quote_as2_identifier(partnership.as2_from)
    headers['AS2-To'] = quote_as2_identifier(partnership.as2_to)
    headers['EDIINT-Features'] = Default.EDIINT_Features

    # The MDN request headers - the notification address is informational
    # and never used for routing, so our own identifier serves as one.
    if partnership.mdn_mode != MDNMode.None_:

        headers['Disposition-Notification-To'] = partnership.as2_from

        if partnership.mdn_signed:
            algorithms = ', '.join(partnership.mdn_mic_algorithms)
            headers['Disposition-Notification-Options'] = \
                f'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, {algorithms}'

        if partnership.mdn_mode == MDNMode.Async:
            headers['Receipt-Delivery-Option'] = partnership.async_mdn_url

    out = (current.data, headers, message_id, mic)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _iterate_chunks(body:'bytes') -> 'bytesgen':
    """ Yields the body in chunks, which makes the HTTP client frame the request
    with chunked transfer encoding instead of a Content-Length header.
    """
    for offset in range(0, len(body), _chunk_size):
        yield body[offset:offset + _chunk_size]

# ################################################################################################################################

def _should_chunk(partnership:'Partnership', body:'bytes') -> 'bool':
    """ Tells whether the request body is to be framed with chunked transfer encoding.
    """
    if partnership.http_transfer_mode == TransferMode.Chunked:
        out = True

    elif partnership.http_transfer_mode == TransferMode.Threshold:
        body_size = len(body)
        out = body_size > partnership.chunked_threshold_bytes

    # .. anything else is the Content-Length default.
    else:
        out = False

    return out

# ################################################################################################################################

def _post(
    partnership:'Partnership',
    body:'bytes',
    headers:'strstrdict',
    client:'httpx.Client | None',
    ) -> 'httpx.Response':
    """ Delivers one AS2 request over HTTP, with a per-call client unless one was supplied.
    """
    # Chunked framing rides on an iterable body - a plain bytes body gets a Content-Length.
    if _should_chunk(partnership, body):
        content = _iterate_chunks(body)
    else:
        content = body

    # Basic authentication is a per-partner option, meaningful only over TLS.
    if auth_config := partnership.http_auth:
        auth = (auth_config.username, auth_config.password)
    else:
        auth = httpx.USE_CLIENT_DEFAULT

    if client:
        out = client.post(partnership.endpoint_url, content=content, headers=headers, auth=auth)
    else:
        with httpx.Client(verify=partnership.verify_tls, timeout=partnership.http_timeout_seconds) as own_client:
            out = own_client.post(partnership.endpoint_url, content=content, headers=headers, auth=auth)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _reconcile_sync_mdn(
    result:'SendResult',
    keystore:'Keystore',
    response:'httpx.Response',
    accepted_certificates:'certificate_list | None'=None,
    ) -> 'None':
    """ Parses and verifies the synchronous MDN riding on the HTTP response. A response whose body
    fails MDN parsing or signature verification counts as no MDN received, an Original-Message-ID
    or Received-Content-MIC mismatch is a delivery failure. A non-empty accepted_certificates list
    is the trust decision for the MDN's signer - during a rotation window it holds both
    the partner's old and new certificate.
    """
    if not (content_type := response.headers.get('content-type')):
        return

    # A body that does not parse and verify as an MDN counts as no MDN received ..
    try:
        mdn = parse_mdn(response.content, content_type, keystore, accepted_certificates)
    except AS2Exception:
        return

    result.mdn = mdn

    # .. the MDN must answer the message that was actually sent ..
    answered_id = normalize_message_id(mdn.original_message_id)
    sent_id = normalize_message_id(result.message_id)

    if answered_id != sent_id:
        return

    # .. its disposition must report clean processing - a warning still counts as processed ..
    if mdn.disposition != DispositionType.Processed:
        return

    if mdn.modifier_kind == ModifierKind.Error:
        return

    if mdn.modifier_kind == ModifierKind.Failure:
        return

    # .. and the Received-Content-MIC must match what was computed at send time.
    if mdn.mic:
        sent_digest, _, sent_algorithm = result.mic.partition(', ')

        if mdn.mic != sent_digest:
            return

        if mdn.mic_algorithm != sent_algorithm:
            return

    result.is_ok = True

# ################################################################################################################################

def send(
    partnership:'Partnership',
    keystore:'Keystore',
    payload:'send_payload',
    filename:'strnone'=None,
    client:'httpx.Client | None'=None,
    *,
    message_id:'strnone'=None,
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

    response = _post(partnership, body, headers, client)

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

def new_send_report() -> 'stranydict':
    """ Returns an empty delivery report - the JSON-friendly shape a completed delivery
    and a failed attempt share, so callers always read the same keys.
    """
    out:'stranydict' = {
        'is_ok': False,
        'message_id': '',
        'http_status': 0,
        'has_mdn': False,
        'mdn_signed': False,
        'disposition': '',
        'mic_matched': None,
        'error': '',
    }

    return out

# ################################################################################################################################

def describe_send_result(result:'SendResult') -> 'stranydict':
    """ Turns one delivery result into a JSON-friendly report of the MDN outcome -
    whether the receipt arrived signed, what its disposition says and whether
    its Received-Content-MIC agrees with the one computed at send time.
    """

    # Our response to produce
    out = new_send_report()

    out['is_ok'] = result.is_ok
    out['message_id'] = result.message_id
    out['http_status'] = result.http_status

    mdn = result.mdn

    # With no MDN on the response, the transport details are everything there is to report.
    if not mdn:
        return out

    out['has_mdn'] = True
    out['mdn_signed'] = mdn.is_signed
    out['disposition'] = describe_disposition(mdn.disposition, mdn.modifier_kind, mdn.modifier)

    # The Received-Content-MIC is compared with the one computed at send time,
    # both the digest and the algorithm - an MDN without one leaves the comparison undecided.
    if mdn.mic:
        sent_digest, _, sent_algorithm = result.mic.partition(', ')

        if mdn.mic != sent_digest:
            out['mic_matched'] = False
        elif mdn.mic_algorithm != sent_algorithm:
            out['mic_matched'] = False
        else:
            out['mic_matched'] = True

    return out

# ################################################################################################################################
# ################################################################################################################################
