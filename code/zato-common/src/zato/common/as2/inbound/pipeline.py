# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The transport-neutral inbound pipeline - what an arriving AS2 request goes through, from the raw
body and headers to the documents delivered and the receipt sent back.
"""

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException
from zato.common.as2.inbound.common import Default_Transfer_Encoding, InboundResult, Max_Inbound_Bytes
from zato.common.as2.inbound.layers import process_layers
from zato.common.as2.inbound.payloads import extract_payloads
from zato.common.as2.inbound.receipt import attach_mdn
from zato.common.as2.mdn import disposition_from_exception, new_error_disposition, new_processed_disposition, \
    normalize_message_id, parse_mdn_request
from zato.common.as2.partnership import match_partnership, unquote_as2_identifier
from zato.common.as2.smime import SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.partnership import partnership_list
    from zato.common.typing_ import callnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    callnone = callnone
    partnership_list = partnership_list
    strstrdict = strstrdict
    Keystore = Keystore

# ################################################################################################################################
# ################################################################################################################################

def handle(
    body:'bytes',
    headers:'strstrdict',
    partnerships:'partnership_list',
    keystore:'Keystore',
    is_duplicate:'callnone' = None,
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
        attach_mdn(out, request, disposition, '', None)

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
        part.content_transfer_encoding = Default_Transfer_Encoding

    # An unwrapped payload carries its filename directly on the HTTP headers.
    if content_disposition := lowered.get('content-disposition'):
        part.content_disposition = content_disposition

    try:
        # An oversized body is turned down before any of it is unwrapped, stored or routed ..
        body_size = len(body)

        if body_size > Max_Inbound_Bytes:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error,
                f'Request body of {body_size} bytes is larger than the maximum of {Max_Inbound_Bytes}')

        # .. reverse the security layers and compute the MIC on the way ..
        part = process_layers(out, part, partnership, keystore, request.mic_algorithms)

        # .. hand the documents over ..
        out.payloads = extract_payloads(part)

        # .. and answer with the MDN the sender asked for.
        disposition = new_processed_disposition()
        out.disposition = disposition
        attach_mdn(out, request, disposition, out.mic, keystore, partnership)

    # Failures still produce an MDN with the matching disposition modifier -
    # signed when a signed receipt was requested, because the partner is identifiable.
    except AS2ProtocolException as e:
        out.is_error = True
        out.error_modifier = e.modifier
        out.payloads = []

        disposition = disposition_from_exception(e)
        out.disposition = disposition
        attach_mdn(out, request, disposition, out.mic, keystore, partnership)

    return out

# ################################################################################################################################
# ################################################################################################################################
