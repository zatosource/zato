# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reading a receipt that arrived - signed or unsigned, on the response or delivered asynchronously -
into the disposition, the MIC and the signer it reports.
"""

# Zato
from zato.common.as2.common import AS2Error, AS2Exception, AS2ProtocolException
from zato.common.as2.mdn.common import CRLF, MDNDetails
from zato.common.as2.mdn.disposition import parse_disposition
from zato.common.as2.smime import new_part, normalize_micalg, verify
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    strstrdict = strstrdict
    certificate_list = certificate_list
    Keystore = Keystore

# ################################################################################################################################
# ################################################################################################################################

def _read_original_message_id(details:'MDNDetails', value:'str') -> 'None':
    """ Reads the Original-Message-ID field - which message the receipt answers.
    """
    details.original_message_id = value

# ################################################################################################################################

def _read_disposition(details:'MDNDetails', value:'str') -> 'None':
    """ Reads the Disposition field into its parsed pieces.
    """
    disposition = parse_disposition(value)

    details.mode = disposition.mode
    details.disposition = disposition.disposition_type
    details.modifier_kind = disposition.modifier_kind
    details.modifier = disposition.modifier

# ################################################################################################################################

def _read_content_mic(details:'MDNDetails', value:'str') -> 'None':
    """ Reads the Received-Content-MIC field - the digest the partner computed and the algorithm
    it used, which is what the reconciliation of a sent message rests on.
    """
    # The MIC value is the base64 digest with the algorithm name appended after a comma -
    # base64 contains no commas, so the split from the right is unambiguous.
    digest, _, algorithm = value.rpartition(',')
    details.mic = digest.strip()

    # Any known spelling of the algorithm name is normalized on the way in,
    # an unknown one is kept as it arrived for the caller to reconcile against.
    algorithm = algorithm.strip()
    algorithm = algorithm.lower()

    try:
        details.mic_algorithm = normalize_micalg(algorithm)
    except AS2ProtocolException:
        details.mic_algorithm = algorithm

# ################################################################################################################################

# The disposition-notification fields this implementation reads, each with the reader that takes it.
# Every other field of RFC 8098 section 3.2 is accepted and ignored.
_field_readers = {
    'original-message-id':  _read_original_message_id,
    'disposition':          _read_disposition,
    'received-content-mic': _read_content_mic,
}

# ################################################################################################################################

def _parse_notification_fields(details:'MDNDetails', notification:'bytes') -> 'None':
    """ Reads the fields of a message/disposition-notification part into the result.
    """
    for line in notification.split(CRLF):

        decoded = line.decode('utf-8')
        name, _, value = decoded.partition(':')
        name = name.strip()
        name = name.lower()
        value = value.strip()

        if reader := _field_readers.get(name):
            reader(details, value)

# ################################################################################################################################

def _parse_report(details:'MDNDetails', body:'bytes', parameters:'strstrdict') -> 'None':
    """ Splits a multipart/report body into its parts and reads the disposition notification
    and the human-readable text out of them.
    """
    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(
            AS2Error.Unexpected_Processing_Error, 'multipart/report without a boundary parameter')

    delimiter = b'--' + boundary.encode('ascii')

    # The first piece is the preamble and the last one the epilogue - both are discarded.
    pieces = body.split(delimiter)

    for piece in pieces[1:-1]:

        if piece.endswith(CRLF):
            piece = piece[:-2]

        part_headers, part_body = parse_mime_part(piece)

        if not (part_content_type := part_headers.get('content-type')):
            continue

        part_parameters = parse_header_parameters(part_content_type)
        media_type = part_parameters['']

        # The machine-readable part carries the disposition fields ..
        if media_type == 'message/disposition-notification':
            _parse_notification_fields(details, part_body)

        # .. and the text part carries the human-readable explanation.
        elif media_type == 'text/plain':
            details.text = part_body.decode('utf-8')

# ################################################################################################################################

def parse_mdn(
    body:'bytes',
    content_type:'str',
    keystore:'Keystore | None' = None,
    accepted_certificates:'certificate_list | None' = None,
    ) -> 'MDNDetails':
    """ Parses an MDN - signed or unsigned, synchronous or delivered asynchronously - into its pieces.
    A signed MDN is verified against the keystore, so its signer certificate comes out along
    with the disposition and the Received-Content-MIC. A non-empty accepted_certificates list
    is the trust decision for the signer - during a rotation window it holds both the partner's
    old and new certificate.
    """

    # Our response to produce
    out = MDNDetails()

    parameters = parse_header_parameters(content_type)
    media_type = parameters['']

    # A signed MDN wraps the report in a multipart/signed whose signature is verified first ..
    if media_type == 'multipart/signed':

        if not keystore:
            raise AS2Exception('A signed MDN requires a keystore to verify its signature')

        part = new_part(body, content_type)
        result = verify(part, keystore, accepted_certificates)

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
