# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Turning the innermost MIME entity, the one left once every security layer has been peeled off,
into the documents that are handed on - one for a plain payload, several for a multipart/related.
"""

# stdlib
from base64 import b64decode

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException
from zato.common.as2.inbound.common import CRLF, InboundPayload, payload_list
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.smime import SMIMEPart
    from zato.common.typing_ import strlist
    strlist = strlist
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

# What a peer-supplied filename is reduced to a plain name by - both separators, because the
# name may have been produced on either kind of system, and the characters that no filesystem
# accepts anyway.
_path_separators = ('/', '\\')
_forbidden_filename_characters = frozenset('\x00\r\n\t')

# How long a filename may be. Filesystems commonly stop at 255 bytes for one name.
_max_filename_length = 255

# ################################################################################################################################
# ################################################################################################################################

def _transfer_decode(data:'bytes', transfer_encoding:'str') -> 'bytes':
    """ Undoes the transfer encoding of payload content, returning the document bytes underneath.
    """
    if transfer_encoding.lower() == 'base64':
        out = b64decode(data)
    else:
        out = data

    return out

# ################################################################################################################################

def _sanitize_filename(filename:'str') -> 'str':
    """ Reduces a peer-supplied filename to a plain name safe to hand on.

    Nothing in the AS2 code writes a file under this name, but it travels into the routed message
    and the stored audit data, and a service or a subscriber that does write it would be the one
    exposed. Sanitizing here means every consumer gets a name that cannot escape a directory,
    rather than each of them having to remember to check.
    """
    out = filename.strip()

    # Any directory part is dropped, both separators, so that neither a path nor a parent
    # reference survives - and a name that was nothing but a path leaves nothing behind.
    for separator in _path_separators:
        _, _, out = out.rpartition(separator)

    # A name made only of dots would still be a parent reference.
    if out.strip('.') == '':
        return ''

    # Control characters have no place in a filename and are what turns one into an injection
    # into whatever format a consumer writes it to.
    kept:'strlist' = []

    for character in out:
        if character not in _forbidden_filename_characters:
            if character.isprintable():
                kept.append(character)

    out = ''.join(kept)

    # A name longer than a filesystem accepts is truncated rather than refused, since the
    # document itself is what matters and the name is metadata travelling with it.
    out = out[:_max_filename_length]

    return out

# ################################################################################################################################

def _read_filename(content_disposition:'str') -> 'str':
    """ Reads the filename out of a Content-Disposition header value, when one travels along.
    """
    parameters = parse_header_parameters(content_disposition)

    if filename := parameters.get('filename'):
        out = _sanitize_filename(filename)
    else:
        out = ''

    return out

# ################################################################################################################################

def _payload_from_part(part:'SMIMEPart') -> 'InboundPayload':
    """ Turns one MIME entity into a delivered document.
    """

    # Our response to produce
    out = InboundPayload()

    out.data = _transfer_decode(part.data, part.content_transfer_encoding)

    parameters = parse_header_parameters(part.content_type)
    out.content_type = parameters['']

    if part.content_disposition:
        out.filename = _read_filename(part.content_disposition)

    return out

# ################################################################################################################################

def _split_related_payloads(part:'SMIMEPart') -> 'payload_list':
    """ Splits a multipart/related entity into its documents - the multiple-attachments shape.
    """
    parameters = parse_header_parameters(part.content_type)

    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(
            AS2Error.Unexpected_Processing_Error, 'multipart/related without a boundary parameter')

    delimiter = b'--' + boundary.encode('ascii')

    # The first piece is the preamble and the last one the epilogue - both are discarded.
    pieces = part.data.split(delimiter)

    out:'payload_list' = []

    for piece in pieces[1:-1]:

        if piece.endswith(CRLF):
            piece = piece[:-2]

        headers, body = parse_mime_part(piece)

        payload = InboundPayload()

        if content_type := headers.get('content-type'):
            piece_parameters = parse_header_parameters(content_type)
            payload.content_type = piece_parameters['']

        if transfer_encoding := headers.get('content-transfer-encoding'):
            payload.data = _transfer_decode(body, transfer_encoding)
        else:
            payload.data = body

        if content_disposition := headers.get('content-disposition'):
            payload.filename = _read_filename(content_disposition)

        out.append(payload)

    return out

# ################################################################################################################################

def extract_payloads(part:'SMIMEPart') -> 'payload_list':
    """ Turns the innermost entity into the list of delivered documents -
    one for a plain payload, several for a multipart/related.
    """
    parameters = parse_header_parameters(part.content_type)
    media_type = parameters['']

    if media_type == 'multipart/related':
        out = _split_related_payloads(part)
    else:
        payload = _payload_from_part(part)
        out = [payload]

    return out

# ################################################################################################################################
# ################################################################################################################################
