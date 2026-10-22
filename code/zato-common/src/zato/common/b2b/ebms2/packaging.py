# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from binascii import Error as BinasciiError
from dataclasses import dataclass
from quopri import decodestring as decode_quoted_printable_bytes

# Zato
from zato.common.b2b.common.limits import Limits
from zato.common.b2b.ebms2.common import EbMS2Exception, ErrorCode, Multipart_Media_Type, Root_Content_Type, \
    Root_Media_Type, SOAP_Action_Header, SOAP_Action_Value
from zato.common.util.xml_.mime_ import build_related, parse_header_parameters, parse_mime_part, Part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strset, strstrdict
    anylist = anylist
    strset = strset
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# The prefix of the MIME boundaries of outgoing messages.
_boundary_prefix = '=-ebms2-'

# The Content-Transfer-Encoding values whose part bodies are the payload octets as they are.
_identity_encodings:'strset' = {'', '7bit', '8bit', 'binary'}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Payload:
    """ One payload of a message - a MIME part after the SOAP part.
    """
    content_id:   str
    content_type: str
    data:         bytes

payload_list = list[Payload]

# ################################################################################################################################

@dataclass(init=False)
class Package:
    """ A message as it travels over HTTP - the body bytes and the headers that go with them.
    """
    body:    bytes
    headers: 'strstrdict'

# ################################################################################################################################

@dataclass(init=False)
class Unpacked:
    """ A received message split into its SOAP envelope and its payloads.
    """
    envelope: bytes
    payloads: 'payload_list'

# ################################################################################################################################
# ################################################################################################################################

def _mime_problem(detail:'str') -> 'EbMS2Exception':
    out = EbMS2Exception(ErrorCode.MIME_Problem, detail)
    return out

# ################################################################################################################################

def normalize_content_id(value:'str') -> 'str':
    """ Returns a Content-ID without the angle brackets of the header form and without the cid: prefix of
    the reference form, so that both compare equal.
    """
    out = value.strip()

    if out.startswith('<'):
        if out.endswith('>'):
            out = out[1:-1]

    if out.startswith('cid:'):
        out = out[4:]

    return out

# ################################################################################################################################

def lower_case_headers(headers:'strstrdict') -> 'strstrdict':
    """ Returns HTTP headers keyed by their lower-case names, since header names compare case-insensitively.
    """
    out:'strstrdict' = {}

    for name, value in headers.items():
        lower_name = name.lower()
        out[lower_name] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

def package(envelope:'bytes', payloads:'payload_list') -> 'Package':
    """ Returns a SOAP envelope and its payloads as a multipart/related message with the headers ebMS 2.0 requires.
    """
    parts = []

    for payload in payloads:
        part = Part()
        part.content_id = payload.content_id
        part.content_type = payload.content_type
        part.data = payload.data
        parts.append(part)

    body, content_type = build_related(envelope, Root_Content_Type, parts, Root_Media_Type, _boundary_prefix)

    out = Package()
    out.body = body
    out.headers = {
        'Content-Type': content_type,
        SOAP_Action_Header: SOAP_Action_Value,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _decode_base64(body:'bytes', content_id:'str') -> 'bytes':
    try:
        out = b64decode(body)
    except (BinasciiError, ValueError) as e:
        raise _mime_problem(f'Part `{content_id}` is not valid base64 -> {e}')

    return out

# ################################################################################################################################

def _decode_quoted_printable(body:'bytes', content_id:'str') -> 'bytes':
    out = decode_quoted_printable_bytes(body)
    return out

# ################################################################################################################################

# The decoders of the transfer encodings that change the payload octets.
_decoders = {
    'base64':           _decode_base64,
    'quoted-printable': _decode_quoted_printable,
}

# ################################################################################################################################

def _decode_part(headers:'strstrdict', body:'bytes', content_id:'str') -> 'bytes':
    """ Returns the octets of a MIME part with its transfer encoding removed.
    """
    if (encoding := headers.get('content-transfer-encoding')) is None:
        encoding = ''

    encoding = encoding.strip().lower()

    if encoding in _identity_encodings:
        out = body

    elif decoder := _decoders.get(encoding):
        out = decoder(body, content_id)

    else:
        raise _mime_problem(f'Part `{content_id}` has an unsupported transfer encoding `{encoding}`')

    return out

# ################################################################################################################################

def _split_parts(body:'bytes', boundary:'str') -> 'anylist':
    """ Returns the raw MIME parts between the boundaries of a multipart body.
    """
    delimiter = b'--' + boundary.encode('ascii')
    closing_delimiter = delimiter + b'--'

    if closing_delimiter not in body:
        raise _mime_problem('The closing MIME boundary is missing')

    pieces = body.split(delimiter)

    # The first piece is the preamble and the last one is the epilogue after the closing boundary.
    out:'anylist' = []

    for raw in pieces[1:-1]:

        # Each part ends with the CRLF that precedes the next boundary.
        if raw.endswith(_crlf):
            raw = raw[:-2]

        try:
            entry = parse_mime_part(raw)
        except UnicodeDecodeError as e:
            raise _mime_problem(f'MIME part headers are not valid UTF-8 -> {e}')

        out.append(entry)

    return out

# ################################################################################################################################

def _unpack_multipart(body:'bytes', parameters:'strstrdict') -> 'Unpacked':

    if not (boundary := parameters.get('boundary')):
        raise _mime_problem('The multipart/related Content-Type has no boundary')

    if (type_parameter := parameters.get('type')) is None:
        raise _mime_problem('The multipart/related Content-Type has no type parameter')

    if type_parameter.lower() != Root_Media_Type:
        raise _mime_problem(f'The multipart/related type parameter is `{type_parameter}`')

    raw_parts = _split_parts(body, boundary)

    if not raw_parts:
        raise _mime_problem('The message has no MIME parts')

    payload_count = len(raw_parts) - 1

    if payload_count > Limits.Max_Part_Count:
        raise _mime_problem(f'The message has {payload_count} payloads, more than {Limits.Max_Part_Count}')

    # The SOAP part is the one the start parameter names, or the first one if there is no start parameter.
    if start := parameters.get('start'):
        root_content_id = normalize_content_id(start)
    else:
        root_content_id = ''

    root_index = 0
    content_ids:'strset' = set()

    for index, entry in enumerate(raw_parts):
        headers, _ = entry

        if content_id := headers.get('content-id'):
            normalized = normalize_content_id(content_id)
            if normalized == root_content_id:
                root_index = index
                break
    else:
        if root_content_id:
            raise _mime_problem(f'The start parameter names no MIME part -> `{start}`')

    out = Unpacked()
    out.payloads = []

    for index, entry in enumerate(raw_parts):
        headers, part_body = entry

        if (content_type := headers.get('content-type')) is None:
            content_type = ''

        if index == root_index:

            root_parameters = parse_header_parameters(content_type)

            if root_parameters[''] != Root_Media_Type:
                raise _mime_problem(f'The SOAP part has the Content-Type `{content_type}`')

            out.envelope = _decode_part(headers, part_body, root_content_id)
            continue

        if not (content_id := headers.get('content-id')):
            raise _mime_problem(f'Payload {index} has no Content-ID')

        normalized = normalize_content_id(content_id)

        if normalized in content_ids:
            raise _mime_problem(f'Content-ID `{normalized}` is used by more than one payload')

        content_ids.add(normalized)

        if not content_type:
            raise _mime_problem(f'Payload `{normalized}` has no Content-Type')

        payload = Payload()
        payload.content_id = normalized
        payload.content_type = content_type
        payload.data = _decode_part(headers, part_body, normalized)

        out.payloads.append(payload)

    return out

# ################################################################################################################################

def unpack(headers:'strstrdict', body:'bytes') -> 'Unpacked':
    """ Splits a received message into its SOAP envelope and its payloads. A message without payloads
    may also arrive as a SOAP envelope on its own.
    """
    body_size = len(body)

    if body_size > Limits.Max_Message_Size_Bytes:
        raise _mime_problem(f'The message has {body_size} bytes, more than {Limits.Max_Message_Size_Bytes}')

    lower_headers = lower_case_headers(headers)

    if not (content_type := lower_headers.get('content-type')):
        raise _mime_problem('The message has no Content-Type')

    parameters = parse_header_parameters(content_type)
    media_type = parameters['']

    if media_type == Multipart_Media_Type:
        out = _unpack_multipart(body, parameters)

    elif media_type == Root_Media_Type:
        out = Unpacked()
        out.envelope = body
        out.payloads = []

    else:
        raise _mime_problem(f'The message has the Content-Type `{content_type}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
