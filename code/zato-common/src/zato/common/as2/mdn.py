# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timezone

# Zato
from zato.common.as2.common import AS2Error, AS2Exception, AS2ProtocolException, Default, Failure
from zato.common.as2.smime import new_part, normalize_micalg, select_mic_algorithm, sign, verify
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import optional
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.typing_ import anytuple, strlist, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    anytuple = anytuple
    Certificate = Certificate
    Keystore = Keystore
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

certificatenone   = optional['Certificate']
keystorenone      = optional['Keystore']
signingconfignone = optional['MDNSigningConfig']

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# The disposition mode of an MDN produced without human intervention (RFC 4130 section 7.5.2).
_automatic_mode = 'automatic-action/MDN-sent-automatically'

# What this implementation announces in the Reporting-UA field of every MDN.
_reporting_ua = 'Zato'

# The address type prefix of the recipient fields (RFC 8098 section 3.2.3).
_address_type = 'rfc822'

# The one signed receipt protocol AS2 defines (RFC 4130 section 7.3) - a request
# for any other protocol makes an unsigned MDN the legitimate answer.
_supported_receipt_protocol = 'pkcs7-signature'

# ################################################################################################################################
# ################################################################################################################################

class DispositionType:
    """ The two disposition types AS2 uses (RFC 4130 section 7.5) - "processed" also covers errors
    and warnings through its modifier, while "failed" is reserved for problems with the MDN request itself.
    """
    Processed = 'processed'
    Failed    = 'failed'

# ################################################################################################################################
# ################################################################################################################################

class ModifierKind:
    """ The three disposition modifier kinds of RFC 4130 section 7.5 and RFC 8098 section 3.2.6.
    """
    Error   = 'error'
    Warning = 'warning'
    Failure = 'failure'

# ################################################################################################################################
# ################################################################################################################################

# Failure descriptions accompany the "failed" disposition type - everything else is an error modifier.
_failure_descriptions = {
    Failure.Unsupported_Format,
    Failure.Unsupported_MIC_Algorithms,
}

# Every disposition modifier this implementation recognizes as a known value on input,
# including the registry values of the AS2 specification modernization draft.
_known_modifiers = {
    AS2Error.Authentication_Failed,
    AS2Error.Decompression_Failed,
    AS2Error.Decryption_Failed,
    AS2Error.Duplicate_Filename,
    AS2Error.Illegal_Filename,
    AS2Error.Insufficient_Message_Security,
    AS2Error.Integrity_Check_Failed,
    AS2Error.Invalid_Message_ID,
    AS2Error.Unexpected_Processing_Error,
    AS2Error.Unknown_Trading_Partner,
    AS2Error.Unknown_Trading_Relationship,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Disposition:
    """ One parsed or to-be-emitted Disposition field of an MDN.
    """
    # The action mode pair before the semicolon, e.g. automatic-action/MDN-sent-automatically.
    mode: str = _automatic_mode

    # The disposition type - processed or failed.
    disposition_type: str = DispositionType.Processed

    # The modifier kind - error, warning or failure - or an empty string for a clean disposition.
    modifier_kind: str = ''

    # The modifier text after the kind, e.g. decryption-failed - never split on a comma,
    # so a value like "authentication-failed, processing continued" stays whole.
    modifier: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNRequest:
    """ What the sender of a message asked for in terms of its MDN - parsed out of the AS2 headers.
    """
    # The Message-ID of the message the MDN will answer, exactly as received.
    message_id: str = ''

    # The AS2 identities of the exchange - as2_from is the message's sender, who receives the MDN.
    as2_from: str = ''
    as2_to: str = ''

    # Whether an MDN was requested at all - the Disposition-Notification-To field indicates it
    # by its mere presence, its value is never used for routing.
    requests_mdn: bool = False

    # Whether a signed receipt was requested, and with which protocol.
    requests_signed_mdn: bool = False
    signed_receipt_protocol: str = ''

    # The signed-receipt-micalg preference list, in the sender's order -
    # assigned by parse_mdn_request.
    mic_algorithms: 'strlist'

    # The Receipt-Delivery-Option URL for an asynchronous MDN - empty means a synchronous one.
    async_mdn_url: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNSigningConfig:
    """ What signing an MDN requires - our keystore and the digest algorithm to prefer
    when the request does not name any.
    """
    keystore: 'Keystore'
    digest_algorithm: str = Default.Digest_Algorithm

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNInfo:
    """ What parsing an MDN yields.
    """
    # The Original-Message-ID field - which message this MDN answers.
    original_message_id: str = ''

    # The parsed pieces of the Disposition field.
    mode: str = ''
    disposition: str = ''
    modifier_kind: str = ''
    modifier: str = ''

    # The Received-Content-MIC - the base64 digest and the algorithm name.
    mic: str = ''
    mic_algorithm: str = ''

    # Whether the MDN arrived signed and, if so, who signed it.
    is_signed: bool = False
    signer_certificate: 'certificatenone' = None

    # The human-readable first part of the report.
    text: str = ''

# ################################################################################################################################
# ################################################################################################################################

def new_message_id() -> 'str':
    """ Returns a fresh Message-ID for an outgoing message or MDN.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'<{suffix}@zato>'
    return out

# ################################################################################################################################

def normalize_message_id(value:'str') -> 'str':
    """ Strips the angle brackets off a Message-ID - the comparison stays case-sensitive
    on the full addr-spec underneath, so nothing else is touched.
    """
    out = value.strip()

    if out.startswith('<'):
        out = out[1:]

    if out.endswith('>'):
        out = out[:-1]

    return out

# ################################################################################################################################

def _new_boundary() -> 'str':
    """ Returns a fresh MIME boundary.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'=-zato-{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_processed_disposition() -> 'Disposition':
    """ Returns the disposition of a message that was processed cleanly.
    """

    # Our response to produce
    out = Disposition()

    return out

# ################################################################################################################################

def new_error_disposition(modifier:'str') -> 'Disposition':
    """ Returns a processed/error disposition with the given modifier.
    """

    # Our response to produce
    out = Disposition()

    out.modifier_kind = ModifierKind.Error
    out.modifier = modifier

    return out

# ################################################################################################################################

def new_warning_disposition(modifier:'str') -> 'Disposition':
    """ Returns a processed/warning disposition with the given modifier.
    """

    # Our response to produce
    out = Disposition()

    out.modifier_kind = ModifierKind.Warning
    out.modifier = modifier

    return out

# ################################################################################################################################

def new_failure_disposition(description:'str') -> 'Disposition':
    """ Returns a failed/Failure disposition - reserved for problems with the MDN request itself,
    such as an unsupported format or unsupported MIC algorithms, never for content processing.
    """

    # Our response to produce
    out = Disposition()

    out.disposition_type = DispositionType.Failed
    out.modifier_kind = ModifierKind.Failure
    out.modifier = description

    return out

# ################################################################################################################################

def disposition_from_exception(exception:'AS2ProtocolException') -> 'Disposition':
    """ Maps a protocol exception to its disposition - failure descriptions become failed/Failure,
    everything else is a processed/error with the exception's modifier.
    """
    if exception.modifier in _failure_descriptions:
        out = new_failure_disposition(exception.modifier)
    else:
        out = new_error_disposition(exception.modifier)

    return out

# ################################################################################################################################
# ################################################################################################################################

def format_disposition(disposition:'Disposition') -> 'str':
    """ Emits a Disposition field value in the historic RFC 4130 construction -
    the form every AS2 implementation accepts.
    """
    base = f'{disposition.mode}; {disposition.disposition_type}'

    # A clean disposition has no modifier at all ..
    if not disposition.modifier_kind:
        out = base

    # .. failure descriptions keep the capitalized spelling of the RFC 4130 examples ..
    elif disposition.modifier_kind == ModifierKind.Failure:
        out = f'{base}/Failure: {disposition.modifier}'

    # .. errors and warnings ride lowercase after the disposition type.
    else:
        out = f'{base}/{disposition.modifier_kind}: {disposition.modifier}'

    return out

# ################################################################################################################################

def parse_disposition(value:'str') -> 'Disposition':
    """ Parses a Disposition field value, accepting the historic RFC 4130 constructions
    and the RFC 3798 and RFC 8098 forms alike. The modifier is never split on a comma.
    """

    # Our response to produce
    out = Disposition()

    # The mode rides before the semicolon - lenient parsing accepts its absence.
    if ';' in value:
        mode, _, rest = value.partition(';')
        out.mode = mode.strip()
    else:
        rest = value

    rest = rest.strip()

    # The modifier follows the disposition type after a slash, when there is one.
    disposition_type, _, modifier_part = rest.partition('/')
    out.disposition_type = disposition_type.strip().lower()

    modifier_part = modifier_part.strip()

    if modifier_part:

        # The historic construction spells out the kind and its text, e.g. error: decryption-failed ..
        if ':' in modifier_part:
            kind, _, text = modifier_part.partition(':')
            out.modifier_kind = kind.strip().lower()
            out.modifier = text.strip()

        # .. the RFC 8098 form may carry the bare kind alone, with the details in separate fields.
        else:
            out.modifier_kind = modifier_part.lower()

    return out

# ################################################################################################################################

def is_known_modifier(value:'str') -> 'bool':
    """ Tells whether a modifier value is one of the registry values this implementation recognizes.
    """
    out = value in _known_modifiers
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_mdn_request(headers:'strstrdict') -> 'MDNRequest':
    """ Reads what kind of MDN the sender of a message asked for out of its AS2 headers.
    Header names are expected in lowercase. Implementations must never reject a message
    based on the syntax of these fields, so everything here is lenient.
    """

    # Our response to produce
    out = MDNRequest()
    out.mic_algorithms = []

    if message_id := headers.get('message-id'):
        out.message_id = message_id

    if as2_from := headers.get('as2-from'):
        out.as2_from = as2_from

    if as2_to := headers.get('as2-to'):
        out.as2_to = as2_to

    # The mere presence of this field requests an MDN - its value is never used for routing.
    out.requests_mdn = 'disposition-notification-to' in headers

    # A synchronous MDN rides on the HTTP response, an asynchronous one is delivered to this URL.
    if async_mdn_url := headers.get('receipt-delivery-option'):
        out.async_mdn_url = async_mdn_url.strip()

    # The options field carries the signed receipt request - each option names its importance
    # first (required or optional) and its values after it.
    if options := headers.get('disposition-notification-options'):

        for option in options.split(';'):
            name, _, values_part = option.partition('=')
            name = name.strip().lower()

            values:'strlist' = []

            # The first comma-separated piece is the importance token, the rest are the values.
            for piece in values_part.split(',')[1:]:
                piece = piece.strip()
                if piece:
                    values.append(piece)

            if name == 'signed-receipt-protocol':
                if values:
                    out.signed_receipt_protocol = values[0].lower()
                    out.requests_signed_mdn = True

            elif name == 'signed-receipt-micalg':
                out.mic_algorithms = values

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_report(request:'MDNRequest', disposition:'Disposition', mic:'str') -> 'anytuple':
    """ Builds the multipart/report body of an MDN - the human-readable text part
    and the message/disposition-notification part. Returns the body bytes
    and the Content-Type header value that describes them.
    """
    formatted = format_disposition(disposition)
    now = datetime.now(timezone.utc)

    # The human-readable part explains the outcome to whoever ends up reading the raw MDN ..
    text_lines:'strlist' = []
    text_lines.append('MDN for -')
    text_lines.append(f' Message-ID: {request.message_id}')
    text_lines.append(f' From: {request.as2_from}')
    text_lines.append(f' To: {request.as2_to}')
    text_lines.append(f' Received on: {now.isoformat()}')
    text_lines.append(f' Disposition: {formatted}')

    text = '\r\n'.join(text_lines)

    # .. the machine-readable part carries the fields of RFC 8098 section 3.2 that AS2 uses.
    fields:'strlist' = []
    fields.append(f'Reporting-UA: {_reporting_ua}')
    fields.append(f'Original-Recipient: {_address_type}; {request.as2_to}')
    fields.append(f'Final-Recipient: {_address_type}; {request.as2_to}')
    fields.append(f'Original-Message-ID: {request.message_id}')

    if mic:
        fields.append(f'Received-Content-MIC: {mic}')

    fields.append(f'Disposition: {formatted}')

    notification = '\r\n'.join(fields)

    # Both parts ride in a multipart/report with the disposition-notification report type.
    boundary = _new_boundary()

    chunks:'list[bytes]' = []
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(b'Content-Type: text/plain')
    chunks.append(b'Content-Transfer-Encoding: 7bit')
    chunks.append(b'')
    chunks.append(text.encode('utf-8'))
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(b'Content-Type: message/disposition-notification')
    chunks.append(b'Content-Transfer-Encoding: 7bit')
    chunks.append(b'')
    chunks.append(notification.encode('utf-8'))
    chunks.append(f'--{boundary}--'.encode('ascii'))
    chunks.append(b'')

    body = _crlf.join(chunks)
    content_type = f'multipart/report; report-type=disposition-notification; boundary="{boundary}"'

    out = (body, content_type)
    return out

# ################################################################################################################################

def build_mdn(
    request:'MDNRequest',
    disposition:'Disposition',
    mic:'str'='',
    signing_config:'signingconfignone'=None,
    ) -> 'anytuple':
    """ Builds a complete MDN for a received message - the multipart/report body and the headers
    to send it with. A signed receipt request is honored whenever signing material is available,
    even when processing failed - while an unsigned MDN is the legitimate answer when the requested
    receipt protocol is not the one AS2 defines or when no signing material was given, e.g. because
    the AS2-From/AS2-To pair is unknown and the MDN is only an unsigned explanation.
    """
    body, content_type = _build_report(request, disposition, mic)

    # A signed receipt request is honored only for the one protocol AS2 defines.
    if signing_config:
        if request.requests_signed_mdn:
            if request.signed_receipt_protocol == _supported_receipt_protocol:

                # The signature algorithm honors the request's preference list when it names
                # anything supported - otherwise our own default carries the signature,
                # because even the MDN reporting unsupported MIC algorithms rides signed.
                if request.mic_algorithms:
                    try:
                        algorithm = select_mic_algorithm(request.mic_algorithms)
                    except AS2ProtocolException:
                        algorithm = signing_config.digest_algorithm
                else:
                    algorithm = signing_config.digest_algorithm

                report = new_part(body, content_type, '7bit')
                signed = sign(report, signing_config.keystore, algorithm)

                body = signed.data
                content_type = signed.content_type

    # The MDN flows back to the message's sender, so the identities swap places.
    headers:'strstrdict' = {}
    headers['Content-Type'] = content_type
    headers['Message-ID'] = new_message_id()
    headers['AS2-From'] = request.as2_to
    headers['AS2-To'] = request.as2_from
    headers['MIME-Version'] = '1.0'

    out = (body, headers)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_notification_fields(info:'MDNInfo', notification:'bytes') -> 'None':
    """ Reads the fields of a message/disposition-notification part into the result.
    """
    for line in notification.split(_crlf):

        name, _, value = line.decode('utf-8').partition(':')
        name = name.strip().lower()
        value = value.strip()

        if name == 'original-message-id':
            info.original_message_id = value

        elif name == 'disposition':
            disposition = parse_disposition(value)
            info.mode = disposition.mode
            info.disposition = disposition.disposition_type
            info.modifier_kind = disposition.modifier_kind
            info.modifier = disposition.modifier

        elif name == 'received-content-mic':

            # The MIC value is the base64 digest with the algorithm name appended after a comma -
            # base64 contains no commas, so the split from the right is unambiguous.
            digest, _, algorithm = value.rpartition(',')
            info.mic = digest.strip()

            # Any known spelling of the algorithm name is normalized on the way in,
            # an unknown one is kept as it arrived for the caller to reconcile against.
            algorithm = algorithm.strip().lower()

            try:
                info.mic_algorithm = normalize_micalg(algorithm)
            except AS2ProtocolException:
                info.mic_algorithm = algorithm

# ################################################################################################################################

def _parse_report(info:'MDNInfo', body:'bytes', parameters:'strstrdict') -> 'None':
    """ Splits a multipart/report body into its parts and reads the disposition notification
    and the human-readable text out of them.
    """
    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(AS2Error.Unexpected_Processing_Error, 'multipart/report without a boundary parameter')

    delimiter = b'--' + boundary.encode('ascii')

    # The first piece is the preamble and the last one the epilogue - both are discarded.
    pieces = body.split(delimiter)

    for piece in pieces[1:-1]:

        if piece.endswith(_crlf):
            piece = piece[:-2]

        part_headers, part_body = parse_mime_part(piece)

        if not (part_content_type := part_headers.get('content-type')):
            continue

        part_parameters = parse_header_parameters(part_content_type)
        media_type = part_parameters['']

        # The machine-readable part carries the disposition fields ..
        if media_type == 'message/disposition-notification':
            _parse_notification_fields(info, part_body)

        # .. and the text part carries the human-readable explanation.
        elif media_type == 'text/plain':
            info.text = part_body.decode('utf-8')

# ################################################################################################################################

def parse_mdn(body:'bytes', content_type:'str', keystore:'keystorenone'=None) -> 'MDNInfo':
    """ Parses an MDN - signed or unsigned, synchronous or delivered asynchronously - into its pieces.
    A signed MDN is verified against the keystore, so its signer certificate comes out along
    with the disposition and the Received-Content-MIC.
    """

    # Our response to produce
    out = MDNInfo()

    parameters = parse_header_parameters(content_type)
    media_type = parameters['']

    # A signed MDN wraps the report in a multipart/signed whose signature is verified first ..
    if media_type == 'multipart/signed':

        if not keystore:
            raise AS2Exception('A signed MDN requires a keystore to verify its signature')

        part = new_part(body, content_type)
        result = verify(part, keystore)

        out.is_signed = True
        out.signer_certificate = result.signer_certificate

        report_body = result.part.data
        report_parameters = parse_header_parameters(result.part.content_type)

    # .. an unsigned MDN is the report itself.
    elif media_type == 'multipart/report':
        report_body = body
        report_parameters = parameters

    # .. anything else is not an MDN at all.
    else:
        raise AS2ProtocolException(AS2Error.Unexpected_Processing_Error, f'Not an MDN content type `{media_type}`')

    _parse_report(out, report_body, report_parameters)

    return out

# ################################################################################################################################
# ################################################################################################################################
