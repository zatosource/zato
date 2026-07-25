# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Building the receipt a received message calls for - the multipart/report of RFC 8098, signed when
the sender asked for a signed one and signing material is at hand.
"""

# stdlib
from datetime import datetime, timezone

# Zato
from zato.common.as2.common import AS2ProtocolException
from zato.common.as2.mdn.common import Address_Type, CRLF, new_message_id, Reporting_UA, Supported_Receipt_Protocol
from zato.common.as2.mdn.disposition import format_disposition
from zato.common.as2.smime import new_part, select_mic_algorithm, sign
from zato.common.as2.smime.part import new_boundary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.mdn.common import Disposition, MDNRequest, MDNSigningConfig
    from zato.common.typing_ import anytuple, byteslist, strlist, strstrdict
    anytuple = anytuple
    byteslist = byteslist
    strlist = strlist
    strstrdict = strstrdict
    Disposition = Disposition
    MDNRequest = MDNRequest
    MDNSigningConfig = MDNSigningConfig

# ################################################################################################################################
# ################################################################################################################################

def _build_report(request:'MDNRequest', disposition:'Disposition', mic:'str') -> 'anytuple':
    """ Builds the multipart/report body of an MDN - the human-readable text part
    and the message/disposition-notification part. Returns the body bytes
    and the Content-Type header value that describes them.
    """
    formatted = format_disposition(disposition)
    now = datetime.now(timezone.utc)
    received_on = now.isoformat()

    # The human-readable part explains the outcome to whoever ends up reading the raw MDN ..
    text_lines:'strlist' = []
    text_lines.append('MDN for -')
    text_lines.append(f' Message-ID: {request.message_id}')
    text_lines.append(f' From: {request.as2_from}')
    text_lines.append(f' To: {request.as2_to}')
    text_lines.append(f' Received on: {received_on}')
    text_lines.append(f' Disposition: {formatted}')

    text = '\r\n'.join(text_lines)

    # .. the machine-readable part carries the fields of RFC 8098 section 3.2 that AS2 uses.
    fields:'strlist' = []
    fields.append(f'Reporting-UA: {Reporting_UA}')
    fields.append(f'Original-Recipient: {Address_Type}; {request.as2_to}')
    fields.append(f'Final-Recipient: {Address_Type}; {request.as2_to}')
    fields.append(f'Original-Message-ID: {request.message_id}')

    if mic:
        fields.append(f'Received-Content-MIC: {mic}')

    fields.append(f'Disposition: {formatted}')

    notification = '\r\n'.join(fields)

    # Both parts ride in a multipart/report with the disposition-notification report type.
    boundary = new_boundary()

    delimiter = f'--{boundary}'.encode('ascii')
    closing_delimiter = f'--{boundary}--'.encode('ascii')

    text_bytes = text.encode('utf-8')
    notification_bytes = notification.encode('utf-8')

    chunks:'byteslist' = []
    chunks.append(delimiter)
    chunks.append(b'Content-Type: text/plain')
    chunks.append(b'Content-Transfer-Encoding: 7bit')
    chunks.append(b'')
    chunks.append(text_bytes)
    chunks.append(delimiter)
    chunks.append(b'Content-Type: message/disposition-notification')
    chunks.append(b'Content-Transfer-Encoding: 7bit')
    chunks.append(b'')
    chunks.append(notification_bytes)
    chunks.append(closing_delimiter)
    chunks.append(b'')

    body = CRLF.join(chunks)
    content_type = f'multipart/report; report-type=disposition-notification; boundary="{boundary}"'

    out = (body, content_type)
    return out

# ################################################################################################################################

def build_mdn(
    request:'MDNRequest',
    disposition:'Disposition',
    mic:'str' = '',
    signing_config:'MDNSigningConfig | None' = None,
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
            if request.signed_receipt_protocol == Supported_Receipt_Protocol:

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
