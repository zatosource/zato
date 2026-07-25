# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Compressing and decompressing an entity - the CompressedData structure of RFC 5402 and RFC 3274,
with a ceiling on what one compressed entity may expand to.
"""

# stdlib
import zlib

# Zato
from zato.common.as2.common import AS2Error, AS2MalformedCMSException, AS2ProtocolException
from zato.common.as2.smime.algorithms import OID
from zato.common.as2.smime.der import der_children, element_bytes, element_content, encode_der, encode_der_integer, \
    encode_der_octet_string, read_content_info, read_der_element, Tag, to_definite_der
from zato.common.as2.smime.part import parse_part, serialize_part, SMIMEPart, transfer_decode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.smime.der import DERElement
    from zato.common.typing_ import byteslist
    byteslist = byteslist
    DERElement = DERElement

# ################################################################################################################################
# ################################################################################################################################

# How many bytes one compressed entity may expand to. Compression ratios above a thousand to one
# are the signature of a decompression bomb rather than of an EDI document, and the whole point
# of the ceiling is that the expansion stops before the process runs out of memory.
Max_Decompressed_Bytes = 512 * 1024 * 1024

# How many bytes to inflate per step while the ceiling above is being watched.
_decompression_chunk_size = 256 * 1024

# ################################################################################################################################
# ################################################################################################################################

def compress(part:'SMIMEPart', prevent_canonicalization:'bool' = False) -> 'SMIMEPart':
    """ Wraps an entity in a CMS CompressedData structure per RFC 5402 and RFC 3274,
    producing an application/pkcs7-mime entity with smime-type=compressed-data.
    Compression may run before or after signing - both orders exist in the wild.
    """
    content = serialize_part(part, prevent_canonicalization)
    compressed = zlib.compress(content)

    # CompressedData per RFC 3274 - the zlib stream rides in an id-data encapsulated content.
    algorithm_identifier = encode_der(Tag.Sequence, OID.Zlib)
    octets = encode_der_octet_string(compressed)
    explicit_octets = encode_der(Tag.Context_0, octets)
    encapsulated = encode_der(Tag.Sequence, OID.Data + explicit_octets)

    version = encode_der_integer(0)
    compressed_data = encode_der(Tag.Sequence, version + algorithm_identifier + encapsulated)
    explicit_content = encode_der(Tag.Context_0, compressed_data)
    envelope = encode_der(Tag.Sequence, OID.Compressed_Data + explicit_content)

    # Our response to produce
    out = SMIMEPart()

    out.content_type = 'application/pkcs7-mime; smime-type=compressed-data; name="smime.p7z"'
    out.content_transfer_encoding = 'binary'
    out.data = envelope

    return out

# ################################################################################################################################

def _collect_compressed_content(der:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the compressed content octets, joining the chunks of a constructed encoding if needed.
    """
    # The primitive form carries the octets directly ..
    if element.tag == Tag.Octet_String:
        out = element_content(der, element)
        return out

    # .. the constructed BER form some producers emit splits them into octet string chunks ..
    elif element.tag == Tag.Octet_String_Constructed:
        chunks:'byteslist' = []

        for chunk in der_children(der, element):
            chunk_content = element_content(der, chunk)
            chunks.append(chunk_content)

        out = b''.join(chunks)
        return out

    # .. and any other tag means the structure is not what CMS says it should be.
    else:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, 'Unexpected encoding of the compressed content')

# ################################################################################################################################

def _inflate_bounded(compressed:'bytes') -> 'bytes':
    """ Inflates a zlib stream a chunk at a time, giving up once the output crosses the ceiling.
    A single decompress call would expand a small hostile input until the process ran out of
    memory, and this runs on unauthenticated input, so the expansion has to be watched
    as it happens rather than measured afterwards.
    """
    decompressor = zlib.decompressobj()
    chunks:'byteslist' = []
    total = 0

    try:
        # An empty result means the stream is exhausted, which is the normal way out ..
        while chunk := decompressor.decompress(compressed, _decompression_chunk_size):

            total += len(chunk)

            # .. while crossing the ceiling means the input was built to expand without limit.
            if total > Max_Decompressed_Bytes:
                raise AS2ProtocolException(
                    AS2Error.Decompression_Failed,
                    f'Decompressed content is larger than the maximum of {Max_Decompressed_Bytes} bytes')

            chunks.append(chunk)

            # Whatever the decompressor did not consume is the input of the next round,
            # and an empty buffer keeps it draining what it already holds.
            compressed = decompressor.unconsumed_tail

    except zlib.error as e:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, f'Decompression failed ({e})') from None

    # A chunked decompressor reports a truncated stream by never reaching its end, rather than
    # by raising the way a single-call decompression would.
    if not decompressor.eof:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, 'Compressed stream is incomplete or truncated')

    out = b''.join(chunks)
    return out

# ################################################################################################################################

def decompress(part:'SMIMEPart') -> 'SMIMEPart':
    """ Unwraps a CMS CompressedData entity back into the MIME entity underneath.
    """
    der = transfer_decode(part)

    try:
        # Streaming producers encode their compressed structures with BER indefinite lengths.
        der = to_definite_der(der)

        content_type_oid, explicit_content = read_content_info(der)

        if content_type_oid != OID.Compressed_Data:
            raise AS2ProtocolException(AS2Error.Decompression_Failed, 'CMS content type is not CompressedData')

        compressed_data = read_der_element(der, explicit_content.content_offset)
        children = der_children(der, compressed_data)

        # The only compression algorithm RFC 5402 defines is zlib.
        algorithm_identifier = children[1]
        algorithm_children = der_children(der, algorithm_identifier)
        algorithm_oid = element_bytes(der, algorithm_children[0])

        if algorithm_oid != OID.Zlib:
            raise AS2ProtocolException(AS2Error.Decompression_Failed, 'Unsupported compression algorithm')

        # The compressed octets live inside the encapsulated content info.
        encapsulated = children[2]
        encapsulated_children = der_children(der, encapsulated)
        explicit_octets = encapsulated_children[1]
        octets = read_der_element(der, explicit_octets.content_offset)
        compressed = _collect_compressed_content(der, octets)

    except (AS2MalformedCMSException, IndexError, ValueError, RecursionError) as e:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, f'Malformed compressed structure ({e})') from None

    plaintext = _inflate_bounded(compressed)

    out = parse_part(plaintext)
    return out

# ################################################################################################################################
# ################################################################################################################################
