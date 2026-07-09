# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from dataclasses import dataclass
from http.client import ACCEPTED, NO_CONTENT, OK

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException, Default
from zato.common.as2.mdn import build_mdn, disposition_from_exception, MDNSigningConfig, new_error_disposition, \
    new_processed_disposition, normalize_message_id, parse_mdn_request
from zato.common.as2.partnership import active_verification_certificates, match_partnership, unquote_as2_identifier
from zato.common.as2.smime import compute_mic, compute_mic_over, decompress, decrypt, select_mic_algorithm, \
    serialize_part, SMIMEPart, verify
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.as2.mdn import Disposition, MDNRequest
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import callable_, strlist, strnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    callable_ = callable_
    Certificate = Certificate
    Disposition = Disposition
    MDNRequest = MDNRequest
    partnership_list = partnership_list
    strlist = strlist
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# The transfer encoding assumed when an incoming request does not declare one.
_default_transfer_encoding = 'binary'

# The smime-type parameter values that mean an application/pkcs7-mime entity is encrypted.
_enveloped_smime_types = ('enveloped-data', 'authenveloped-data')

# The smime-type parameter value of a compressed entity.
_compressed_smime_type = 'compressed-data'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundPayload:
    """ One delivered document - what the inbound topic or service receives.
    """
    data: bytes = b''
    content_type: str = ''
    filename: str = ''

# ################################################################################################################################
# ################################################################################################################################

payload_list = list[InboundPayload]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredMDN:
    """ The MDN response of an earlier delivery, kept by the duplicate store so that a replay
    of the same message gets the exact same bytes back, never a recomputed answer.
    """
    status_code: int = OK
    body: bytes = b''
    headers: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingAsyncMDN:
    """ An MDN the caller is to deliver asynchronously to the URL the sender named.
    """
    url: str = ''
    body: bytes = b''
    headers: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundResult:
    """ What the transport should send back and what the application receives.
    """
    # The HTTP response - an MDN on the body for synchronous receipts,
    # empty for asynchronous ones and when no MDN was requested at all.
    status_code:  int = OK
    content_type: str = ''
    body:         bytes = b''
    headers:      'strstrdict'

    # The identities of the exchange, unquoted, and the Message-ID without its angle brackets.
    as2_from:   str = ''
    as2_to:     str = ''
    message_id: str = ''

    # What the peer advertised in its EDIINT-Features header - logged for onboarding,
    # never driving behavior.
    ediint_features: str = ''

    # The partnership the message matched.
    partnership: 'Partnership | None' = None

    # The MIC computed over the received content, in its wire form.
    mic: str = ''

    # The delivered documents - empty on a duplicate or an error.
    payloads: 'payload_list'

    # The certificate that signed the message, when it arrived signed.
    signer_certificate: 'Certificate | None' = None

    # Whether the message was recognized as a replay - the stored MDN is re-transmitted
    # as it is and the payloads are not delivered a second time.
    is_duplicate: bool = False

    # Whether processing failed and the body carries an MDN with an error disposition.
    is_error: bool = False
    error_modifier: 'strnone' = None

    # The MDN to deliver asynchronously, when the sender asked for one.
    pending_async_mdn: 'PendingAsyncMDN | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _transfer_decode(data:'bytes', transfer_encoding:'str') -> 'bytes':
    """ Undoes the transfer encoding of payload content, returning the document bytes underneath.
    """
    if transfer_encoding.lower() == 'base64':
        out = b64decode(data)
    else:
        out = data

    return out

# ################################################################################################################################

def _read_filename(content_disposition:'str') -> 'str':
    """ Reads the filename out of a Content-Disposition header value, when one travels along.
    """
    parameters = parse_header_parameters(content_disposition)

    if filename := parameters.get('filename'):
        out = filename
    else:
        out = ''

    return out

# ################################################################################################################################

def _payload_from_part(part:'SMIMEPart') -> 'InboundPayload':
    """ Turns one MIME entity into a delivered document.
    """

    # Our response to produce
    out = InboundPayload()

    out.data = _transfer_decode(part.data, part.content_transfer_encoding)

    parameters = parse_header_parameters(part.content_type)
    out.content_type = parameters['']

    if part.content_disposition:
        out.filename = _read_filename(part.content_disposition)

    return out

# ################################################################################################################################

def _split_related_payloads(part:'SMIMEPart') -> 'payload_list':
    """ Splits a multipart/related entity into its documents - the multiple-attachments shape.
    """
    parameters = parse_header_parameters(part.content_type)

    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(AS2Error.Unexpected_Processing_Error, 'multipart/related without a boundary parameter')

    delimiter = b'--' + boundary.encode('ascii')

    # The first piece is the preamble and the last one the epilogue - both are discarded.
    pieces = part.data.split(delimiter)

    out:'payload_list' = []

    for piece in pieces[1:-1]:

        if piece.endswith(_crlf):
            piece = piece[:-2]

        headers, body = parse_mime_part(piece)

        payload = InboundPayload()

        if content_type := headers.get('content-type'):
            piece_parameters = parse_header_parameters(content_type)
            payload.content_type = piece_parameters['']

        if transfer_encoding := headers.get('content-transfer-encoding'):
            payload.data = _transfer_decode(body, transfer_encoding)
        else:
            payload.data = body

        if content_disposition := headers.get('content-disposition'):
            payload.filename = _read_filename(content_disposition)

        out.append(payload)

    return out

# ################################################################################################################################

def _extract_payloads(part:'SMIMEPart') -> 'payload_list':
    """ Turns the innermost entity into the list of delivered documents -
    one for a plain payload, several for a multipart/related.
    """
    parameters = parse_header_parameters(part.content_type)
    media_type = parameters['']

    if media_type == 'multipart/related':
        out = _split_related_payloads(part)
    else:
        payload = _payload_from_part(part)
        out = [payload]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _attach_mdn(
    result:'InboundResult',
    request:'MDNRequest',
    disposition:'Disposition',
    mic:'str',
    keystore:'Keystore | None',
    ) -> 'None':
    """ Builds the MDN a message calls for and places it on the result - on the HTTP response
    for a synchronous one, as a pending delivery for an asynchronous one. Positive and negative
    MDNs alike ride on HTTP 200 - the disposition carries the outcome, not the status code.
    """
    # No MDN was requested at all - the response stays empty.
    if not request.requests_mdn:
        result.status_code = NO_CONTENT
        return

    # A signed receipt request is honored whenever signing material is available,
    # even when processing failed - build_mdn itself checks the requested protocol.
    signing_config = None

    if keystore:
        if keystore.signing_key:
            signing_config = MDNSigningConfig()
            signing_config.keystore = keystore

    body, headers = build_mdn(request, disposition, mic, signing_config)

    # An asynchronous MDN is the caller's to deliver - the inbound POST itself is merely accepted ..
    if request.async_mdn_url:
        pending = PendingAsyncMDN()
        pending.url = request.async_mdn_url
        pending.body = body
        pending.headers = headers

        result.pending_async_mdn = pending
        result.status_code = ACCEPTED

    # .. a synchronous one rides back on the HTTP response.
    else:
        result.status_code = OK
        result.body = body
        result.headers = headers
        result.content_type = headers['Content-Type']

# ################################################################################################################################

def _process_layers(
    result:'InboundResult',
    part:'SMIMEPart',
    partnership:'Partnership',
    keystore:'Keystore',
    mic_request_algorithms:'strlist',
    ) -> 'SMIMEPart':
    """ Reverses the security layers in whichever order they actually arrived, detected from
    the content types, and captures what the MIC is to cover per RFC 4130 section 7.3.1 -
    the signed entity for signed messages, the decrypted entity for encrypted unsigned ones,
    the content alone for everything else.
    """
    signed_content = b''
    decrypted_content = b''
    compressed_content = b''

    # The partner's rotation list - during an overlap window it holds more than one
    # certificate and a signature from any of them is accepted.
    accepted_certificates = active_verification_certificates(partnership)

    while True:
        parameters = parse_header_parameters(part.content_type)
        media_type = parameters['']

        # An encrypted or compressed entity - both ride in application/pkcs7-mime ..
        if media_type == 'application/pkcs7-mime':

            smime_type = parameters.get('smime-type', '')

            if smime_type == _compressed_smime_type:
                if not compressed_content:
                    compressed_content = part.data
                part = decompress(part)

            # .. an absent smime-type parameter means an encrypted entity,
            # the one shape peers ship without the parameter.
            elif smime_type in _enveloped_smime_types or not smime_type:
                part = decrypt(part, keystore)
                if not decrypted_content:
                    decrypted_content = serialize_part(part, partnership.prevent_canonicalization)

            # .. any other smime-type is not something this pipeline handles.
            else:
                raise AS2ProtocolException(
                    AS2Error.Unexpected_Processing_Error, f'Unsupported smime-type `{smime_type}`')

        # .. a signed entity is verified and unwrapped ..
        elif media_type == 'multipart/signed':
            verify_result = verify(part, keystore, accepted_certificates)

            if not signed_content:
                signed_content = verify_result.content

            result.signer_certificate = verify_result.signer_certificate
            part = verify_result.part

        # .. anything else is the payload itself.
        else:
            break

    # The MIC algorithm honors the request's preference list when there is one.
    if mic_request_algorithms:
        algorithm = select_mic_algorithm(mic_request_algorithms)
    else:
        algorithm = Default.Digest_Algorithm

    # The 7.3.1 selection - signed wins over encrypted, encrypted over compressed,
    # and a bare payload digests its content alone, without any headers.
    if signed_content:
        result.mic = compute_mic_over(signed_content, algorithm)
    elif decrypted_content:
        result.mic = compute_mic_over(decrypted_content, algorithm)
    elif compressed_content:
        result.mic = compute_mic_over(compressed_content, algorithm)
    else:
        result.mic = compute_mic(
            part,
            algorithm,
            is_signed=False,
            is_encrypted=False,
            prevent_canonicalization=partnership.prevent_canonicalization,
        )

    return part

# ################################################################################################################################

def handle(
    body:'bytes',
    headers:'strstrdict',
    partnerships:'partnership_list',
    keystore:'Keystore',
    is_duplicate:'callable_ | None'=None,
    ) -> 'InboundResult':
    """ The transport-neutral inbound pipeline. Takes the raw HTTP body and headers of an incoming
    AS2 request and returns what to send back plus the delivered documents.

    The is_duplicate callable, when given, receives the unquoted AS2-From and AS2-To identifiers
    and the Message-ID without its angle brackets, and returns the StoredMDN of an earlier delivery
    of the same message or None - on a duplicate the stored bytes are re-transmitted as they are
    and the payloads are not delivered a second time.
    """

    # Our response to produce
    out = InboundResult()
    out.payloads = []
    out.headers = {}

    # Header names arrive in whatever case the peer chose.
    lowered:'strstrdict' = {}

    for name, value in headers.items():
        lowered[name.lower()] = value

    # What kind of MDN the sender asked for, straight from the headers.
    request = parse_mdn_request(lowered)

    out.as2_from = unquote_as2_identifier(request.as2_from)
    out.as2_to = unquote_as2_identifier(request.as2_to)
    out.message_id = normalize_message_id(request.message_id)

    if features := lowered.get('ediint-features'):
        out.ediint_features = features

    # An unknown AS2-From/AS2-To pair gets an unsigned explanatory MDN - there is no partnership
    # to say how to sign one, and the disposition explains what went wrong.
    partnership = match_partnership(partnerships, out.as2_from, out.as2_to)

    if not partnership:
        out.is_error = True
        out.error_modifier = AS2Error.Unknown_Trading_Relationship

        disposition = new_error_disposition(AS2Error.Unknown_Trading_Relationship)
        _attach_mdn(out, request, disposition, '', None)

        return out

    out.partnership = partnership

    # A replay of a message already processed gets the stored MDN back, byte for byte,
    # and its payload is never delivered a second time.
    if is_duplicate:
        if out.message_id:
            if stored := is_duplicate(out.as2_from, out.as2_to, out.message_id):
                out.is_duplicate = True
                out.status_code = stored.status_code
                out.body = stored.body
                out.headers = stored.headers

                if content_type := stored.headers.get('Content-Type'):
                    out.content_type = content_type

                return out

    # The top-level entity as it arrived - its MIME headers travel as HTTP headers.
    part = SMIMEPart()
    part.data = body

    if content_type := lowered.get('content-type'):
        part.content_type = content_type

    if transfer_encoding := lowered.get('content-transfer-encoding'):
        part.content_transfer_encoding = transfer_encoding
    else:
        part.content_transfer_encoding = _default_transfer_encoding

    # An unwrapped payload carries its filename directly on the HTTP headers.
    if content_disposition := lowered.get('content-disposition'):
        part.content_disposition = content_disposition

    try:
        # Reverse the security layers and compute the MIC on the way ..
        part = _process_layers(out, part, partnership, keystore, request.mic_algorithms)

        # .. hand the documents over ..
        out.payloads = _extract_payloads(part)

        # .. and answer with the MDN the sender asked for.
        disposition = new_processed_disposition()
        _attach_mdn(out, request, disposition, out.mic, keystore)

    # Failures still produce an MDN with the matching disposition modifier -
    # signed when a signed receipt was requested, because the partner is identifiable.
    except AS2ProtocolException as e:
        out.is_error = True
        out.error_modifier = e.modifier
        out.payloads = []

        disposition = disposition_from_exception(e)
        _attach_mdn(out, request, disposition, out.mic, keystore)

    return out

# ################################################################################################################################
# ################################################################################################################################
