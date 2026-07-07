# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from gzip import compress as gzip_compress, decompress as gzip_decompress
from uuid import uuid4

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple, strnone, strstrdict
    anytuple = anytuple
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_soap_content_type = 'application/soap+xml'
_crlf = b'\r\n'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Part:
    """ One MIME attachment of an AS4 message - a business payload in whatever state
    it currently is (plain, compressed or encrypted).
    """
    # The Content-ID, stored without the cid: prefix and without angle brackets.
    content_id: str = ''

    # The Content-Type of the MIME part as it appears on the wire.
    content_type: str = 'application/octet-stream'

    # The bytes as they currently are - build steps mutate this in place
    # (compression, then encryption) and parse steps reverse it.
    data: bytes = b''

    # The MIME type of the original, uncompressed payload - carried
    # in the MimeType part property so the receiver can restore it.
    mime_type: str = 'application/xml'

    # Optional character set of the original payload, carried in the CharacterSet part property.
    character_set: 'strnone' = None

    # Whether this part is compressed - reflected in the CompressionType part property.
    compressed: bool = False

# ################################################################################################################################
# ################################################################################################################################

part_list = list[Part]

# ################################################################################################################################
# ################################################################################################################################

def new_content_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh Content-ID for a MIME part.
    """
    out = f'{uuid4().hex}@{suffix}'
    return out

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

    boundary = f'=-as4-{uuid4().hex}'
    root_content_id = new_content_id()

    # The envelope always goes into the first MIME part ..
    chunks:'list[bytes]' = []
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(f'Content-Type: {_soap_content_type}; charset=UTF-8'.encode('ascii'))
    chunks.append(f'Content-ID: <{root_content_id}>'.encode('ascii'))
    chunks.append(b'')
    chunks.append(envelope)

    # .. each payload follows in its own part, in binary transfer encoding
    # because HTTP is 8-bit clean and base64 would only inflate the message ..
    for part in parts:
        chunks.append(f'--{boundary}'.encode('ascii'))
        chunks.append(f'Content-Type: {part.content_type}'.encode('ascii'))
        chunks.append(b'Content-Transfer-Encoding: binary')
        chunks.append(f'Content-ID: <{part.content_id}>'.encode('ascii'))
        chunks.append(b'')
        chunks.append(part.data)

    # .. and the closing boundary ends the message.
    chunks.append(f'--{boundary}--'.encode('ascii'))
    chunks.append(b'')

    body = _crlf.join(chunks)
    content_type = f'multipart/related; boundary="{boundary}"; type="{_soap_content_type}"; start="<{root_content_id}>"'

    out = (body, content_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_header_parameters(value:'str') -> 'strstrdict':
    """ Splits a structured header value such as Content-Type into its parameters,
    lowercasing parameter names and stripping optional quotes from values.
    """
    out:'strstrdict' = {}

    pieces = value.split(';')

    # The base value (e.g. multipart/related) is kept under an empty key.
    out[''] = pieces[0].strip().lower()

    for piece in pieces[1:]:
        piece = piece.strip()
        if '=' not in piece:
            continue
        name, _, parameter = piece.partition('=')
        parameter = parameter.strip()
        if parameter.startswith('"'):
            parameter = parameter[1:-1]
        out[name.strip().lower()] = parameter

    return out

# ################################################################################################################################

def _parse_mime_part(raw:'bytes') -> 'anytuple':
    """ Splits one raw MIME part into its headers and body. Header names are lowercased.
    """
    headers:'strstrdict' = {}

    # A part may start with a leading CRLF left over from the boundary split.
    if raw.startswith(_crlf):
        raw = raw[2:]

    header_block, _, body = raw.partition(_crlf + _crlf)

    for line in header_block.split(_crlf):
        name, _, value = line.decode('utf-8').partition(':')
        headers[name.strip().lower()] = value.strip()

    out = (headers, body)
    return out

# ################################################################################################################################

def parse_multipart(body:'bytes', content_type:'str') -> 'anytuple':
    """ Parses an incoming AS4 HTTP body. Returns the SOAP envelope bytes and the list
    of attachment parts. A bare application/soap+xml body yields an empty part list.
    """
    parameters = _parse_header_parameters(content_type)
    base_type = parameters['']

    # Signals arrive as a bare envelope without MIME wrapping.
    if base_type == _soap_content_type:
        out = (body, [])
        return out

    if base_type != 'multipart/related':
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, f'Unexpected content type `{base_type}`')

    if 'boundary' not in parameters:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Content-Type has no boundary parameter')

    boundary = parameters['boundary'].encode('ascii')
    delimiter = b'--' + boundary

    # Split the body on the boundary - the first piece is the preamble
    # and the last one is the epilogue after the closing boundary, both are discarded.
    pieces = body.split(delimiter)
    raw_parts = pieces[1:-1]

    if not raw_parts:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no parts')

    envelope = b''
    parts:'part_list' = []

    for index, raw in enumerate(raw_parts):

        # Each part before the closing boundary ends with the CRLF that precedes the next boundary.
        if raw.endswith(_crlf):
            raw = raw[:-2]

        headers, part_body = _parse_mime_part(raw)

        # The first part carries the envelope, all the others are attachments.
        if index == 0:
            envelope = part_body
            continue

        part = Part()
        part.data = part_body

        if part_content_type := headers.get('content-type'):
            part_parameters = _parse_header_parameters(part_content_type)
            part.content_type = part_parameters['']

        if content_id := headers.get('content-id'):
            content_id = content_id.strip()
            if content_id.startswith('<'):
                content_id = content_id[1:-1]
            part.content_id = content_id

        parts.append(part)

    if not envelope:
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no SOAP envelope part')

    out = (envelope, parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
