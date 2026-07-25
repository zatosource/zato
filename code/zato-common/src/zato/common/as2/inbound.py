# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64decode
from dataclasses import dataclass
from http.client import ACCEPTED, NO_CONTENT, OK
from urllib.parse import urlsplit

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException, Default
from zato.common.as2.mdn import build_mdn, disposition_from_exception, MDNSigningConfig, new_error_disposition, \
    new_processed_disposition, normalize_message_id, parse_mdn_request
from zato.common.as2.partnership import active_verification_certificates, match_partnership, unquote_as2_identifier
from zato.common.as2.smime import compute_mic, compute_mic_over, decompress, decrypt, select_mic_algorithm, \
    serialize_part, SMIMEPart, verify
from zato.common.typing_ import cast_, optional
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.as2.mdn import Disposition, MDNRequest
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import callnone, strlist, strnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    callnone = callnone
    Certificate = Certificate
    Disposition = Disposition
    MDNRequest = MDNRequest
    partnership_list = partnership_list
    strlist = strlist
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
certificatenone     = optional['Certificate']
dispositionnone     = optional['Disposition']
keystorenone        = optional['Keystore']
partnershipnone     = optional['Partnership']
pendingasyncmdnnone = optional['PendingAsyncMDN']

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# The transfer encoding assumed when an incoming request does not declare one.
_default_transfer_encoding = 'binary'

# The smime-type parameter values that mean an application/pkcs7-mime entity is encrypted.
_enveloped_smime_types = ('enveloped-data', 'authenveloped-data')

# The smime-type parameter value of a compressed entity.
_compressed_smime_type = 'compressed-data'

# How many security layers one message may be wrapped in. Real messages use at most
# compression, signing and encryption together, so this leaves generous room while still
# denying a peer the ability to stack layers without limit.
_max_layer_depth = 8

# How large an incoming request body may be. Processing one message holds the body, its base64
# form and the decoded payload at once, so peak memory is a multiple of this rather than equal
# to it, which is why the ceiling sits well below what a single process can hold.
_max_inbound_bytes = 256 * 1024 * 1024

# The URL schemes an asynchronous MDN may be delivered over - the two AS2 itself travels on,
# so that a destination naming any other scheme reaches no handler for it.
_allowed_async_mdn_schemes = ('http', 'https')

# What a peer-supplied filename is reduced to a plain name by - both separators, because the
# name may have been produced on either kind of system, and the characters that no filesystem
# accepts anyway.
_path_separators = ('/', '\\')
_forbidden_filename_characters = frozenset('\x00\r\n\t')

# How long a filename may be. Filesystems commonly stop at 255 bytes for one name.
_max_filename_length = 255

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
    """ An MDN the caller is to deliver asynchronously to the URL the sender named -
    already checked against the partnership, so the caller delivers it as it stands.
    """
    url: str = ''
    body: bytes = b''
    headers: 'strstrdict'

    # How the delivery is to be made, carried here so that the transport does not need
    # the partnership - an outgoing request with no ceiling on it would hold a worker
    # for as long as the destination cared to keep the connection open.
    verify_tls: bool = True
    timeout_seconds: int = Default.HTTP_Timeout_Seconds

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
    partnership: 'partnershipnone' = None

    # The MIC computed over the received content, in its wire form.
    mic: str = ''

    # The delivered documents - empty on a duplicate or an error.
    payloads: 'payload_list'

    # The certificate that signed the message, when it arrived signed.
    signer_certificate: 'certificatenone' = None

    # Whether the message was recognized as a replay - the stored MDN is re-transmitted
    # as it is and the payloads are not delivered a second time.
    is_duplicate: bool = False

    # Whether processing failed and the body carries an MDN with an error disposition.
    is_error: bool = False
    error_modifier: 'strnone' = None

    # The disposition the MDN was built with - clean processing or the matching error,
    # kept on the result so the caller can record it as delivery evidence.
    disposition: 'dispositionnone' = None

    # The MDN to deliver asynchronously, when the sender asked for one.
    pending_async_mdn: 'pendingasyncmdnnone' = None

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

def _sanitize_filename(filename:'str') -> 'str':
    """ Reduces a peer-supplied filename to a plain name safe to hand on.

    Nothing in the AS2 code writes a file under this name, but it travels into the routed message
    and the stored audit data, and a service or a subscriber that does write it would be the one
    exposed. Sanitizing here means every consumer gets a name that cannot escape a directory,
    rather than each of them having to remember to check.
    """
    out = filename.strip()

    # Any directory part is dropped, both separators, so that neither a path nor a parent
    # reference survives - and a name that was nothing but a path leaves nothing behind.
    for separator in _path_separators:
        _, _, out = out.rpartition(separator)

    # A name made only of dots would still be a parent reference.
    if out.strip('.') == '':
        return ''

    # Control characters have no place in a filename and are what turns one into an injection
    # into whatever format a consumer writes it to.
    kept:'strlist' = []

    for character in out:
        if character not in _forbidden_filename_characters:
            if character.isprintable():
                kept.append(character)

    out = ''.join(kept)

    # A name longer than a filesystem accepts is truncated rather than refused, since the
    # document itself is what matters and the name is metadata travelling with it.
    out = out[:_max_filename_length]

    return out

# ################################################################################################################################

def _read_filename(content_disposition:'str') -> 'str':
    """ Reads the filename out of a Content-Disposition header value, when one travels along.
    """
    parameters = parse_header_parameters(content_disposition)

    if filename := parameters.get('filename'):
        out = _sanitize_filename(filename)
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

def _is_async_mdn_url_allowed(partnership:'partnershipnone', url:'str') -> 'bool':
    """ Tells whether an asynchronous MDN may be delivered to the URL the sender named.

    The destination arrives in the sender's Receipt-Delivery-Option header, which means an
    unauthenticated caller would otherwise choose where the server makes an outgoing request to -
    and the header is read on the error paths too, before the message has proven to come from
    the partner at all. An asynchronous receipt goes back to the party we exchange messages with,
    so the destination has to sit on the same host as that party's own AS2 endpoint.
    """
    # Without a partnership there is nothing to hold the destination against, which is the
    # unknown-trading-relationship case - a stranger does not get to name a destination.
    if not partnership:
        return False

    if not partnership.endpoint_url:
        return False

    named = urlsplit(url)
    endpoint = urlsplit(partnership.endpoint_url)

    # Only the two schemes AS2 travels over, so that no other URL handler is ever reached ..
    if named.scheme not in _allowed_async_mdn_schemes:
        return False

    # .. and only the partner's own host, port included, since a different port on the same
    # host is a different service.
    if named.netloc.lower() != endpoint.netloc.lower():
        return False

    return True

# ################################################################################################################################

def _attach_mdn(
    result:'InboundResult',
    request:'MDNRequest',
    disposition:'Disposition',
    mic:'str',
    keystore:'keystorenone',
    partnership:'partnershipnone'=None,
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

    # A destination we will not deliver to falls back to the response body. The receipt still
    # reaches whoever made the request, which is more use to a genuine partner that named a
    # destination we do not recognize than a refusal would be.
    is_async = False

    if request.async_mdn_url:
        is_async = _is_async_mdn_url_allowed(partnership, request.async_mdn_url)

        if not is_async:
            logger.warning(
                'Refusing to deliver an AS2 async MDN to `%s`, which is not the endpoint of partner `%s`',
                request.async_mdn_url, result.as2_from)

    # An asynchronous MDN is the caller's to deliver - the inbound POST itself is merely accepted ..
    if is_async:
        partnership = cast_('Partnership', partnership)

        pending = PendingAsyncMDN()
        pending.url = request.async_mdn_url
        pending.body = body
        pending.headers = headers
        pending.verify_tls = partnership.verify_tls
        pending.timeout_seconds = partnership.http_timeout_seconds

        result.pending_async_mdn = pending
        result.status_code = ACCEPTED

    # .. a synchronous one rides back on the HTTP response.
    else:
        result.status_code = OK
        result.body = body
        result.headers = headers
        result.content_type = headers['Content-Type']

# ################################################################################################################################

def _enforce_security_policy(partnership:'Partnership', is_signed:'bool', is_encrypted:'bool') -> 'None':
    """ Rejects a message that arrived with fewer security layers than the partnership requires.
    Without this check the layers that happened to arrive would be the only ones enforced, so a
    partnership configured for signing and encryption would accept an unsigned plaintext POST from
    anyone able to reach the channel URL and guess the AS2-From/AS2-To pair - and that pair is in
    every message the partner sends, so it is not a secret.
    """
    # The partnership's own signing and encryption settings describe the relationship,
    # not just what we send, so inbound holds the peer to the same terms.
    if partnership.sign:
        if not is_signed:
            raise AS2ProtocolException(
                AS2Error.Insufficient_Message_Security, 'The partnership requires a signed message')

    if partnership.encrypt:
        if not is_encrypted:
            raise AS2ProtocolException(
                AS2Error.Insufficient_Message_Security, 'The partnership requires an encrypted message')

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

    # Which layers actually arrived, tracked apart from the captured bytes above because
    # a layer wrapping empty content is still a layer that arrived.
    is_signed = False
    is_encrypted = False

    # How many layers have been unwrapped so far - each iteration below removes one layer
    # and may reveal another, so without a ceiling a peer could stack them without limit
    # and multiply the work of every unwrapping step, all before any trust decision is made.
    depth = 0

    # The partner's rotation list - during an overlap window it holds more than one
    # certificate and a signature from any of them is accepted.
    accepted_certificates = active_verification_certificates(partnership)

    while True:

        # A well-formed message has at most a handful of layers, so crossing the ceiling
        # means the structure is hostile rather than merely unusual.
        if depth >= _max_layer_depth:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error, f'Too many security layers, the maximum is {_max_layer_depth}')

        parameters = parse_header_parameters(part.content_type)
        media_type = parameters['']

        # An encrypted or compressed entity - both ride in application/pkcs7-mime ..
        if media_type == 'application/pkcs7-mime':

            smime_type = parameters.get('smime-type')

            if smime_type is None:
                smime_type = ''

            # An absent smime-type parameter means an encrypted entity,
            # the one shape peers ship without the parameter.
            is_enveloped = smime_type in _enveloped_smime_types
            if not smime_type:
                is_enveloped = True

            if smime_type == _compressed_smime_type:
                if not compressed_content:
                    compressed_content = part.data
                part = decompress(part)

            # .. the encrypted entity is decrypted with our own key ..
            elif is_enveloped:
                part = decrypt(part, keystore)
                is_encrypted = True
                if not decrypted_content:
                    decrypted_content = serialize_part(part, partnership.prevent_canonicalization)

            # .. any other smime-type is not something this pipeline handles.
            else:
                raise AS2ProtocolException(
                    AS2Error.Unexpected_Processing_Error, f'Unsupported smime-type `{smime_type}`')

        # .. a signed entity is verified and unwrapped ..
        elif media_type == 'multipart/signed':
            verify_result = verify(part, keystore, accepted_certificates)
            is_signed = True

            if not signed_content:
                signed_content = verify_result.content

            result.signer_certificate = verify_result.signer_certificate
            part = verify_result.part

        # .. anything else is the payload itself.
        else:
            break

        depth += 1

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

    # The MIC is computed before the policy check so that a rejected message still reports
    # what arrived - the partner needs that value to tell which message we turned down.
    _enforce_security_policy(partnership, is_signed, is_encrypted)

    return part

# ################################################################################################################################

def handle(
    body:'bytes',
    headers:'strstrdict',
    partnerships:'partnership_list',
    keystore:'Keystore',
    is_duplicate:'callnone'=None,
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
        name = name.lower()
        lowered[name] = value

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
        out.disposition = disposition
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
        # An oversized body is turned down before any of it is unwrapped, stored or routed ..
        body_size = len(body)

        if body_size > _max_inbound_bytes:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error,
                f'Request body of {body_size} bytes is larger than the maximum of {_max_inbound_bytes}')

        # .. reverse the security layers and compute the MIC on the way ..
        part = _process_layers(out, part, partnership, keystore, request.mic_algorithms)

        # .. hand the documents over ..
        out.payloads = _extract_payloads(part)

        # .. and answer with the MDN the sender asked for.
        disposition = new_processed_disposition()
        out.disposition = disposition
        _attach_mdn(out, request, disposition, out.mic, keystore, partnership)

    # Failures still produce an MDN with the matching disposition modifier -
    # signed when a signed receipt was requested, because the partner is identifiable.
    except AS2ProtocolException as e:
        out.is_error = True
        out.error_modifier = e.modifier
        out.payloads = []

        disposition = disposition_from_exception(e)
        out.disposition = disposition
        _attach_mdn(out, request, disposition, out.mic, keystore, partnership)

    return out

# ################################################################################################################################
# ################################################################################################################################
