# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.xml_.core import Id_Size_Bits, new_id

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
strpartdict = dict[str, Part]

# ################################################################################################################################
# ################################################################################################################################

def build_part_index(parts:'part_list') -> 'strpartdict':
    """ Walks a list of MIME parts once and returns them keyed by Content-ID. Everything that resolves
    a cid: reference goes through such an index, so a message with many parts and many references
    costs one walk rather than one per reference.
    """
    out:'strpartdict' = {}

    for part in parts:
        out[part.content_id] = part

    return out

# ################################################################################################################################

def new_content_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh Content-ID for a MIME part.
    """
    out = f'{CryptoManager.generate_hex_string(Id_Size_Bits)}@{suffix}'
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
    """ Splits one raw MIME part into its headers and body. Header names are lowercased
    and folded headers are unfolded - producers wrap long values such as Content-Type
    across lines that continue with leading whitespace (RFC 5322 section 2.2.3).
    """
    headers:'strstrdict' = {}

    # A part may start with a leading CRLF left over from the boundary split.
    if raw.startswith(_crlf):
        raw = raw[2:]

    header_block, _, body = raw.partition(_crlf + _crlf)

    # The name the most recent header line carried - continuation lines extend its value.
    last_name = ''

    for line in header_block.split(_crlf):
        line = line.decode('utf-8')

        # A line starting with whitespace continues the previous header's value ..
        if line[:1] in (' ', '\t'):
            if last_name:
                headers[last_name] = headers[last_name] + ' ' + line.strip()
            continue

        # .. any other line starts a new header.
        name, _, value = line.partition(':')
        last_name = name.strip().lower()
        headers[last_name] = value.strip()

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
    boundary = new_id(boundary_prefix)
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

def _normalize_content_id(value:'str') -> 'str':
    """ Returns a Content-ID without the angle brackets a header wraps it in and without the
    cid: prefix a reference to it carries, so the two forms compare equal.
    """
    out = value.strip()

    if out.startswith('<'):
        out = out[1:-1]

    if out.startswith('cid:'):
        out = out[4:]

    return out

# ################################################################################################################################

def split_related(body:'bytes', boundary:'str', start:'strnone'=None) -> 'anytuple':
    """ Splits a multipart/related body on its boundary. Returns the root document bytes
    and the list of attachment parts, each with its Content-ID and Content-Type filled in.

    The start parameter names the Content-ID of the root part. RFC 2387 lets the root be any part
    of the package, not necessarily the first, so without honouring start a compliant package whose
    root comes second is read with an attachment as the root document. When start is absent the
    first part is the root, which is what the specification says.
    """
    delimiter = b'--' + boundary.encode('ascii')

    # Split the body on the boundary - the first piece is the preamble
    # and the last one is the epilogue after the closing boundary, both are discarded.
    pieces = body.split(delimiter)
    raw_parts = pieces[1:-1]

    if start:
        root_content_id = _normalize_content_id(start)
    else:
        root_content_id = ''

    root_data = b''
    root_index = -1
    parsed_parts = []

    # Everything is read first, because which part is the root is only known once their
    # Content-IDs have been seen.
    for raw in raw_parts:

        # Each part before the closing boundary ends with the CRLF that precedes the next boundary.
        if raw.endswith(_crlf):
            raw = raw[:-2]

        headers, part_body = parse_mime_part(raw)
        parsed_parts.append((headers, part_body))

    for index, entry in enumerate(parsed_parts):
        headers, part_body = entry

        content_id = headers.get('content-id')

        if content_id is None:
            continue

        if _normalize_content_id(content_id) == root_content_id:
            root_index = index
            root_data = part_body
            break

    # No start parameter, or one naming a part that is not in the package - either way the first
    # part is the root, since that is what an unqualified multipart/related means.
    if root_index == -1:
        root_index = 0
        if parsed_parts:
            root_data = parsed_parts[0][1]

    parts:'part_list' = []

    for index, entry in enumerate(parsed_parts):

        if index == root_index:
            continue

        headers, part_body = entry

        part = Part()
        part.data = part_body

        if part_content_type := headers.get('content-type'):
            part_parameters = parse_header_parameters(part_content_type)
            part.content_type = part_parameters['']

        if content_id := headers.get('content-id'):
            part.content_id = _normalize_content_id(content_id)

        parts.append(part)

    out = (root_data, parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
