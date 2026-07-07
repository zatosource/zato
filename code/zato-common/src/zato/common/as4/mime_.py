# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from gzip import compress as gzip_compress, decompress as gzip_decompress

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError
from zato.common.util.xml_.mime_ import build_related, parse_header_parameters, part_list, split_related

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.util.xml_.mime_ import Part
    from zato.common.typing_ import anytuple
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

_soap_content_type = 'application/soap+xml'

# ################################################################################################################################
# ################################################################################################################################

def compress_part(part:'Part') -> 'None':
    """ Applies AS4 GZIP compression to a part in place. The mtime is pinned to zero
    so that compressing the same bytes always produces the same output.
    """
    part.data = gzip_compress(part.data, mtime=0)
    part.content_type = 'application/gzip'
    part.compressed = True

# ################################################################################################################################

def decompress_part(part:'Part') -> 'None':
    """ Reverses AS4 GZIP compression in place, restoring the original content type.
    """
    # A part that does not decompress cleanly must surface as EBMS:0303 per the AS4 profile.
    try:
        part.data = gzip_decompress(part.data)
    except Exception as e:
        raise AS4ProtocolException(EbMSError.Decompression_Failure, f'Could not decompress part `{part.content_id}` -> {e}')

    part.content_type = part.mime_type
    part.compressed = False

# ################################################################################################################################
# ################################################################################################################################

def build_multipart(envelope:'bytes', parts:'part_list') -> 'anytuple':
    """ Serializes a SOAP envelope and its attachments into a multipart/related body.
    Returns the body bytes and the Content-Type header value to send with them.

    Messages without attachments (signals such as receipts and errors) are serialized
    as a bare SOAP envelope without any MIME wrapping.
    """
    # Signals have no payloads, so no multipart is needed for them.
    if not parts:
        out = (envelope, f'{_soap_content_type}; charset=UTF-8')
        return out

    out = build_related(envelope, f'{_soap_content_type}; charset=UTF-8', parts, _soap_content_type, boundary_prefix='=-as4-')
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_multipart(body:'bytes', content_type:'str') -> 'anytuple':
    """ Parses an incoming AS4 HTTP body. Returns the SOAP envelope bytes and the list
    of attachment parts. A bare application/soap+xml body yields an empty part list.
    """
    parameters = parse_header_parameters(content_type)
    base_type = parameters['']

    # Signals arrive as a bare envelope without MIME wrapping.
    if base_type == _soap_content_type:
        out = (body, [])
        return out

    if base_type != 'multipart/related':
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, f'Unexpected content type `{base_type}`')

    if 'boundary' not in parameters:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Content-Type has no boundary parameter')

    envelope, parts = split_related(body, parameters['boundary'])

    if not envelope and not parts:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no parts')

    if not envelope:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no SOAP envelope part')

    out = (envelope, parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
