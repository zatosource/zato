# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The MIME entity every other module in this package works on - what it looks like on the wire,
how its content is canonicalized before anything digests, signs or encrypts it, and how it is
read back once a security layer has been peeled off.
"""

# stdlib
from base64 import b64decode, b64encode
from dataclasses import dataclass

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException
from zato.common.crypto.api import CryptoManager
from zato.common.util.xml_.mime_ import parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import byteslist
    byteslist = byteslist

# ################################################################################################################################
# ################################################################################################################################

CRLF = b'\r\n'

# Transfer encodings whose content is never CRLF-canonicalized (RFC 4130 section 5.2.1).
_no_canonicalization_encodings = ('base64', 'binary')

# The transfer encoding assumed when a parsed entity does not declare one (RFC 2045 section 6.1).
_default_transfer_encoding = '7bit'

# base64 output is wrapped at this many characters per line (RFC 2045 section 6.8).
_base64_line_length = 76

# The printable range of ASCII, which is what a MIME header value may be written from -
# space through tilde, with horizontal tab allowed separately as folding whitespace.
_first_printable_ascii = 0x20
_last_printable_ascii = 0x7E

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SMIMEPart:
    """ One S/MIME entity - MIME headers plus content, in whatever state it currently is
    (plain, compressed, signed or encrypted).
    """
    # The Content-Type header value, with any parameters.
    content_type: str = 'application/octet-stream'

    # The Content-Transfer-Encoding header value.
    content_transfer_encoding: str = 'binary'

    # The optional Content-Disposition header value, carrying the filename when one travels along.
    content_disposition: str = ''

    # The content bytes, already in the transfer encoding declared above.
    data: bytes = b''

# ################################################################################################################################
# ################################################################################################################################

def new_part(data:'bytes', content_type:'str', content_transfer_encoding:'str' = 'binary') -> 'SMIMEPart':
    """ Returns a new S/MIME entity with the given content.
    """

    # Our response to produce
    out = SMIMEPart()

    out.data = data
    out.content_type = content_type
    out.content_transfer_encoding = content_transfer_encoding

    return out

# ################################################################################################################################

def canonicalize_content(part:'SMIMEPart', prevent_canonicalization:'bool') -> 'bytes':
    """ CRLF-canonicalizes the content of a text entity. Binary and base64 content is never touched,
    and the per-partner escape hatch turns canonicalization off entirely.
    """
    if prevent_canonicalization:
        return part.data

    # Only text content is canonicalized ..
    content_type = part.content_type.lower()
    if not content_type.startswith('text/'):
        return part.data

    # .. and only when its transfer encoding leaves the line endings visible.
    transfer_encoding = part.content_transfer_encoding.lower()
    if transfer_encoding in _no_canonicalization_encodings:
        return part.data

    # First bring all line endings to a single form ..
    normalized = part.data.replace(b'\r\n', b'\n')
    normalized = normalized.replace(b'\r', b'\n')

    # .. and then to the canonical CRLF.
    out = normalized.replace(b'\n', CRLF)
    return out

# ################################################################################################################################

def _validate_header(name:'str', value:'str') -> 'None':
    """ Rejects a header value that cannot be written into a header block as it stands.

    On an inner entity - one that came out of decryption or decompression - these values were
    parsed from plaintext the peer controls. Writing a control character back into a header block
    would produce bytes that a downstream parser splits differently from the way this one did,
    which means our idea of what the signature covers and the MIC digests would stop matching the
    partner's. Anything outside printable ASCII plus horizontal tab is refused.
    """
    for character in value:

        if character == '\t':
            continue

        code = ord(character)

        if code < _first_printable_ascii:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error, f'Control character in the {name} header value')

        if code > _last_printable_ascii:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error, f'Non-ASCII character in the {name} header value')

# ################################################################################################################################

def serialize_part(part:'SMIMEPart', prevent_canonicalization:'bool' = False) -> 'bytes':
    """ Serializes an entity into its wire form - MIME headers, an empty line and the content.
    This is what signatures cover, what gets encrypted and what the MIC digests for signed
    and encrypted messages.
    """
    content = canonicalize_content(part, prevent_canonicalization)

    _validate_header('Content-Type', part.content_type)
    _validate_header('Content-Transfer-Encoding', part.content_transfer_encoding)

    headers = f'Content-Type: {part.content_type}\r\nContent-Transfer-Encoding: {part.content_transfer_encoding}\r\n'

    # The disposition header rides along only when a filename actually travels with the entity.
    if part.content_disposition:
        _validate_header('Content-Disposition', part.content_disposition)
        headers += f'Content-Disposition: {part.content_disposition}\r\n'

    headers += '\r\n'

    out = headers.encode('ascii') + content
    return out

# ################################################################################################################################

def parse_part(raw:'bytes') -> 'SMIMEPart':
    """ Parses a serialized MIME entity back into its headers and content.
    """
    headers, body = parse_mime_part(raw)

    # Our response to produce
    out = SMIMEPart()

    out.data = body

    if content_type := headers.get('content-type'):
        out.content_type = content_type

    if transfer_encoding := headers.get('content-transfer-encoding'):
        out.content_transfer_encoding = transfer_encoding
    else:
        out.content_transfer_encoding = _default_transfer_encoding

    if content_disposition := headers.get('content-disposition'):
        out.content_disposition = content_disposition

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_boundary() -> 'str':
    """ Returns a fresh MIME boundary.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'=-zato-{suffix}'
    return out

# ################################################################################################################################

def encode_base64_lines(data:'bytes') -> 'bytes':
    """ base64-encodes data into CRLF-separated lines of the RFC 2045 maximum length.
    """
    encoded = b64encode(data)
    encoded_length = len(encoded)

    lines:'byteslist' = []

    for offset in range(0, encoded_length, _base64_line_length):
        lines.append(encoded[offset:offset + _base64_line_length])

    out = CRLF.join(lines)
    return out

# ################################################################################################################################

def transfer_decode(part:'SMIMEPart') -> 'bytes':
    """ Undoes the transfer encoding of an entity, returning the raw bytes underneath.
    """
    transfer_encoding = part.content_transfer_encoding.lower()

    if transfer_encoding == 'base64':
        out = b64decode(part.data)
    else:
        out = part.data

    return out

# ################################################################################################################################
# ################################################################################################################################
