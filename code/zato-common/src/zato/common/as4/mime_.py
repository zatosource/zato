# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from gzip import BadGzipFile, compress as gzip_compress, GzipFile
from io import BytesIO
from zlib import error as ZlibError

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError, Limits
from zato.common.util.xml_.mime_ import build_part_index, build_related, parse_header_parameters, part_list, \
    split_related

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import UserMessageDetails
    from zato.common.util.xml_.mime_ import Part
    from zato.common.typing_ import anytuple
    anytuple = anytuple
    UserMessageDetails = UserMessageDetails

# ################################################################################################################################
# ################################################################################################################################

_soap_content_type = 'application/soap+xml'

# The prefix a reference to a MIME part carries, per RFC 2392.
Cid_Prefix = 'cid:'

# ################################################################################################################################
# ################################################################################################################################

def content_id_from_reference(reference:'str') -> 'str':
    """ Returns the content id that a cid: reference names. AS4 references payloads as MIME parts
    only, so a reference in any other form is EBMS:0001.
    """
    if not reference.startswith(Cid_Prefix):
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, f'Unsupported part reference `{reference}`')

    out = reference[len(Cid_Prefix):]
    return out

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
    """ Reverses AS4 GZIP compression in place, restoring the original content type. A part is
    decompressed up to the size limit and no further, so the cost of the operation is known from
    the limit rather than from what the part declares.
    """
    limit = Limits.Max_Decompressed_Size_Bytes

    # A part that does not decompress cleanly must surface as EBMS:0303 per the AS4 profile -
    # a bad header raises BadGzipFile, truncated data EOFError and a corrupt stream ZlibError.
    try:
        with GzipFile(fileobj=BytesIO(part.data)) as stream:

            # One byte past the limit is enough to tell that the limit was passed, and reading only
            # that much is what keeps the decompression itself bounded.
            data = stream.read(limit + 1)

    except (BadGzipFile, EOFError, ZlibError) as e:
        raise AS4ProtocolException(EbMSError.Decompression_Failure, f'Could not decompress part `{part.content_id}` -> {e}')

    if len(data) > limit:
        raise AS4ProtocolException(
            EbMSError.Decompression_Failure, f'Part `{part.content_id}` decompresses to more than {limit} bytes')

    part.data = data
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
    envelope_content_type = f'{_soap_content_type}; charset=UTF-8'

    # Signals have no payloads, so no multipart is needed for them.
    if not parts:
        out = (envelope, envelope_content_type)
        return out

    out = build_related(envelope, envelope_content_type, parts, _soap_content_type, boundary_prefix='=-as4-')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_part_limits(parts:'part_list') -> 'None':
    """ Holds an incoming multipart to how many parts it may carry and how large each may be.
    """
    part_count = len(parts)

    if part_count > Limits.Max_Part_Count:
        raise AS4ProtocolException(
            EbMSError.Mime_Inconsistency, f'Message carries {part_count} parts, at most {Limits.Max_Part_Count} are accepted')

    for part in parts:
        part_size = len(part.data)

        if part_size > Limits.Max_Part_Size_Bytes:
            raise AS4ProtocolException(
                EbMSError.Mime_Inconsistency,
                f'Part `{part.content_id}` is {part_size} bytes, at most {Limits.Max_Part_Size_Bytes} are accepted')

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

    if not (boundary := parameters.get('boundary')):
        raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Content-Type has no boundary parameter')

    envelope, parts = split_related(body, boundary)

    _check_part_limits(parts)

    # A multipart without an envelope is either empty altogether ..
    if not envelope:
        if not parts:
            raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no parts')

        # .. or it carries attachments while missing its SOAP root part.
        else:
            raise AS4ProtocolException(EbMSError.Mime_Inconsistency, 'Multipart body has no SOAP envelope part')

    out = (envelope, parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

def restore_payloads(user_message:'UserMessageDetails', parts:'part_list') -> 'part_list':
    """ Matches MIME parts with their eb:PartInfo entries and undoes the AS4 compression, returning
    the payloads as the sender originally submitted them. Both the push and the pull side arrive here,
    because a pulled message is processed exactly like a pushed one.
    """

    # Our response to produce
    out:'part_list' = []

    part_index = build_part_index(parts)

    for part_details in user_message.part_details:

        content_id = content_id_from_reference(part_details.href)
        part = part_index.get(content_id)

        if part is None:
            raise AS4ProtocolException(
                EbMSError.Mime_Inconsistency, f'PartInfo `{part_details.href}` has no matching MIME part')

        if mime_type := part_details.properties.get('MimeType'):
            part.mime_type = mime_type

        if character_set := part_details.properties.get('CharacterSet'):
            part.character_set = character_set

        # The CompressionType property is the receiver's only signal that a part is compressed.
        if compression_type := part_details.properties.get('CompressionType'):
            part.content_type = compression_type
            part.compressed = True
            decompress_part(part)

        out.append(part)

    return out

# ################################################################################################################################
# ################################################################################################################################
