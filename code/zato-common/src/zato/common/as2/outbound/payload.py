# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The innermost MIME entity of an outgoing message - one document, or the multipart/related several
of them ride in, in the transfer encoding the partnership travels under.
"""

# Zato
from zato.common.as2.outbound.common import CRLF
from zato.common.as2.smime import encode_base64_lines, new_part
from zato.common.as2.smime.part import new_boundary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound.common import payload_item_list, send_payload
    from zato.common.as2.partnership import Partnership
    from zato.common.as2.smime import SMIMEPart
    from zato.common.typing_ import byteslist, strnone
    byteslist = byteslist
    payload_item_list = payload_item_list
    send_payload = send_payload
    strnone = strnone
    Partnership = Partnership
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

# The transfer encoding that brings arbitrary bytes through implementations
# that only pass 7-bit content along.
_base64_encoding = 'base64'

# ################################################################################################################################
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
    if transfer_encoding == _base64_encoding:
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
        out = _base64_encoding
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
    boundary = new_boundary()

    delimiter = f'--{boundary}'.encode('ascii')
    closing_delimiter = f'--{boundary}--'.encode('ascii')
    encoding_header = f'Content-Transfer-Encoding: {transfer_encoding}'.encode('ascii')

    chunks:'byteslist' = []

    for item in items:
        encoded = _encode_payload_data(item.data, transfer_encoding)
        content_type_header = f'Content-Type: {item.content_type}'.encode('ascii')

        chunks.append(delimiter)
        chunks.append(content_type_header)
        chunks.append(encoding_header)

        if partnership.preserve_filename:
            if item.filename:
                disposition = _attachment_disposition(item.filename)
                disposition_header = f'Content-Disposition: {disposition}'.encode('ascii')
                chunks.append(disposition_header)

        chunks.append(b'')
        chunks.append(encoded)

    chunks.append(closing_delimiter)
    chunks.append(b'')

    body = CRLF.join(chunks)

    # The type parameter of a multipart/related names the media type of its first part.
    first_item = items[0]
    content_type = f'multipart/related; boundary="{boundary}"; type="{first_item.content_type}"'

    out = new_part(body, content_type)
    return out

# ################################################################################################################################

def build_payload_part(partnership:'Partnership', payload:'send_payload', filename:'strnone') -> 'SMIMEPart':
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
