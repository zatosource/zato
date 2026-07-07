# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple, strnone, strstrdict
    anytuple = anytuple
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Part:
    """ One MIME attachment of a multipart message - a payload in whatever state
    it currently is (plain, compressed or encrypted).
    """
    # The Content-ID, stored without the cid: prefix and without angle brackets.
    content_id: str = ''

    # The Content-Type of the MIME part as it appears on the wire.
    content_type: str = 'application/octet-stream'

    # The bytes as they currently are - build steps mutate this in place
    # (compression, then encryption) and parse steps reverse it.
    data: bytes = b''

    # The MIME type of the original, unprocessed payload - protocols such as AS4
    # carry it in a part property so the receiver can restore it.
    mime_type: str = 'application/xml'

    # Optional character set of the original payload.
    character_set: 'strnone' = None

    # Whether this part is compressed.
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
# ################################################################################################################################

def parse_header_parameters(value:'str') -> 'strstrdict':
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

def parse_mime_part(raw:'bytes') -> 'anytuple':
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
# ################################################################################################################################

def build_related(
    root_data:'bytes',
    root_content_type:'str',
    parts:'part_list',
    type_parameter:'str',
    boundary_prefix:'str'='=-zato',
    start_info:'strnone'=None,
    ) -> 'anytuple':
    """ Serializes a root document and its attachments into a multipart/related body.
    Returns the body bytes and the Content-Type header value to send with them.
    """
    boundary = f'{boundary_prefix}{uuid4().hex}'
    root_content_id = new_content_id()

    # The root document always goes into the first MIME part ..
    chunks:'list[bytes]' = []
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(f'Content-Type: {root_content_type}'.encode('ascii'))
    chunks.append(f'Content-ID: <{root_content_id}>'.encode('ascii'))
    chunks.append(b'')
    chunks.append(root_data)

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
    content_type = f'multipart/related; boundary="{boundary}"; type="{type_parameter}"; start="<{root_content_id}>"'

    # MTOM additionally declares the content type of the root document inside the XOP package.
    if start_info:
        content_type = f'{content_type}; start-info="{start_info}"'

    out = (body, content_type)
    return out

# ################################################################################################################################

def split_related(body:'bytes', boundary:'str') -> 'anytuple':
    """ Splits a multipart/related body on its boundary. Returns the root document bytes
    and the list of attachment parts, each with its Content-ID and Content-Type filled in.
    """
    delimiter = b'--' + boundary.encode('ascii')

    # Split the body on the boundary - the first piece is the preamble
    # and the last one is the epilogue after the closing boundary, both are discarded.
    pieces = body.split(delimiter)
    raw_parts = pieces[1:-1]

    root_data = b''
    parts:'part_list' = []

    for index, raw in enumerate(raw_parts):

        # Each part before the closing boundary ends with the CRLF that precedes the next boundary.
        if raw.endswith(_crlf):
            raw = raw[:-2]

        headers, part_body = parse_mime_part(raw)

        # The first part carries the root document, all the others are attachments.
        if index == 0:
            root_data = part_body
            continue

        part = Part()
        part.data = part_body

        if part_content_type := headers.get('content-type'):
            part_parameters = parse_header_parameters(part_content_type)
            part.content_type = part_parameters['']

        if content_id := headers.get('content-id'):
            content_id = content_id.strip()
            if content_id.startswith('<'):
                content_id = content_id[1:-1]
            part.content_id = content_id

        parts.append(part)

    out = (root_data, parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
