# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The byte layer every CMS structure in this package is built out of and read back through - DER tags
and lengths, the encoders the in-house structures are assembled with, and the re-encoding that turns
the BER indefinite-length form streaming producers emit into the definite-length form readers expect.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.as2.common import AS2MalformedCMSException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple, byteslist
    anytuple = anytuple
    byteslist = byteslist

# ################################################################################################################################
# ################################################################################################################################

der_element_list = list['DERElement']

# ################################################################################################################################
# ################################################################################################################################

class Tag:
    """ DER tags of the ASN.1 constructs that CMS structures are made of.
    """
    Integer                  = 0x02
    Octet_String             = 0x04
    OID                      = 0x06
    UTC_Time                 = 0x17
    Generalized_Time         = 0x18
    Octet_String_Constructed = 0x24
    Sequence                 = 0x30
    Set                      = 0x31
    Context_0_Implicit       = 0x80
    Context_0                = 0xA0
    Context_1                = 0xA1

    # The constructed bit of a BER tag - set on sequences, sets and chunked string encodings.
    Constructed_Bit = 0x20

# ################################################################################################################################
# ################################################################################################################################

# DER length bytes with the high bit set announce a multi-byte length field.
Long_Form_Marker = 0x80

# The BER indefinite-length marker and the end-of-contents octets that conclude such an element.
Indefinite_Length = 0x80
End_Of_Contents = b'\x00\x00'

# The DER encoding of an ASN.1 NULL, used as empty algorithm parameters.
Der_Null = b'\x05\x00'

# How deep a BER structure may nest before it is rejected as malformed. A real CMS structure
# nests around a dozen levels, so this leaves ample room while staying far below the point
# where the re-encoding recursion would exhaust the interpreter stack.
Max_BER_Depth = 64

# ASN.1 object identifiers use base-128 arcs with a continuation bit,
# and the first two arcs share one byte through this multiplier.
_base128_mask             = 0x7F
_base128_continuation     = 0x80
_oid_first_arc_multiplier = 40

# ################################################################################################################################
# ################################################################################################################################

class DERElement(NamedTuple):
    """ One parsed DER element - its tag, where its complete encoding starts,
    where its content starts and how long the content is.
    """
    tag: int
    header_offset: int
    content_offset: int
    length: int

# ################################################################################################################################
# ################################################################################################################################

def read_der_element(data:'bytes', offset:'int') -> 'DERElement':
    """ Reads the header of one DER element at the given offset.
    """
    tag = data[offset]
    length = data[offset + 1]
    header_size = 2

    # In the long form the first length byte only says how many real length bytes follow.
    if length & Long_Form_Marker:
        count = length & (Long_Form_Marker - 1)
        length = int.from_bytes(data[offset + 2:offset + 2 + count], 'big')
        header_size = 2 + count

    out = DERElement(tag, offset, offset + header_size, length)
    return out

# ################################################################################################################################

def der_children(data:'bytes', element:'DERElement') -> 'der_element_list':
    """ Returns the immediate children of a constructed DER element.
    """
    out:'der_element_list' = []
    offset = element.content_offset
    end_offset = element.content_offset + element.length

    while offset < end_offset:
        child = read_der_element(data, offset)
        out.append(child)
        offset = child.content_offset + child.length

    return out

# ################################################################################################################################

def element_bytes(data:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the complete encoding of an element - header and content.
    """
    out = data[element.header_offset:element.content_offset + element.length]
    return out

# ################################################################################################################################

def element_content(data:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the content of an element, without its header.
    """
    out = data[element.content_offset:element.content_offset + element.length]
    return out

# ################################################################################################################################
# ################################################################################################################################

def encode_der_length(length:'int') -> 'bytes':
    """ Encodes a DER length field for the given content length.
    """
    # Short form fits lengths up to 127 in a single byte ..
    if length < Long_Form_Marker:
        out = bytes([length])
        return out

    # .. the long form spells out how many length bytes follow.
    length_bytes = length.to_bytes((length.bit_length() + 7) // 8, 'big')

    out = bytes([Long_Form_Marker | len(length_bytes)]) + length_bytes
    return out

# ################################################################################################################################

def encode_der(tag:'int', content:'bytes') -> 'bytes':
    """ Encodes one complete DER element from its tag and content.
    """
    content_length = len(content)
    length = encode_der_length(content_length)

    out = bytes([tag]) + length + content
    return out

# ################################################################################################################################

def encode_der_integer(value:'int') -> 'bytes':
    """ DER-encodes a non-negative integer, keeping the leading zero byte
    that marks the value as positive when its high bit is set.
    """
    byte_count = (value.bit_length() // 8) + 1
    content = value.to_bytes(byte_count, 'big')

    out = encode_der(Tag.Integer, content)
    return out

# ################################################################################################################################

def encode_der_octet_string(content:'bytes') -> 'bytes':
    """ DER-encodes an octet string.
    """
    out = encode_der(Tag.Octet_String, content)
    return out

# ################################################################################################################################

def encode_oid(dotted:'str') -> 'bytes':
    """ DER-encodes a dotted object identifier, returning its complete tag-length-value bytes.
    """
    pieces = dotted.split('.')

    # The first two arcs share a single byte ..
    first_arc = int(pieces[0])
    second_arc = int(pieces[1])
    content = bytes([first_arc * _oid_first_arc_multiplier + second_arc])

    # .. every following arc is base-128 with a continuation bit on all bytes but the last.
    for piece in pieces[2:]:
        value = int(piece)
        encoded = bytes([value & _base128_mask])
        value >>= 7

        while value:
            encoded = bytes([(value & _base128_mask) | _base128_continuation]) + encoded
            value >>= 7

        content += encoded

    out = encode_der(Tag.OID, content)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _normalize_ber_element(data:'bytes', offset:'int', depth:'int' = 0) -> 'anytuple':
    """ Re-encodes one BER element into its definite-length form, returning the re-encoded
    bytes along with the offset just past the element - end-of-contents octets included.

    The depth is carried down because this runs on unauthenticated input, before any trust
    decision is made - a structure nested deeply enough would otherwise exhaust the Python
    stack rather than being rejected as malformed.
    """
    if depth >= Max_BER_Depth:
        raise AS2MalformedCMSException(f'BER nesting is deeper than the maximum of {Max_BER_Depth}')

    child_depth = depth + 1

    tag = data[offset]
    length = data[offset + 1]

    # An indefinite-length element runs until its end-of-contents octets -
    # re-encoding its children makes the actual length explicit ..
    if length == Indefinite_Length:
        chunks:'byteslist' = []
        child_offset = offset + 2

        while data[child_offset:child_offset + 2] != End_Of_Contents:
            child, child_offset = _normalize_ber_element(data, child_offset, child_depth)
            chunks.append(child)

        content = b''.join(chunks)
        content_length = len(content)
        length_bytes = encode_der_length(content_length)

        out = bytes([tag]) + length_bytes + content
        return (out, child_offset + 2)

    element = read_der_element(data, offset)
    end_offset = element.content_offset + element.length

    # .. a definite-length primitive element stays exactly as it is ..
    if not (tag & Tag.Constructed_Bit):
        out = data[offset:end_offset]
        return (out, end_offset)

    # .. and a definite-length constructed one may still hide indefinite lengths further down.
    chunks:'byteslist' = []
    child_offset = element.content_offset

    while child_offset < end_offset:
        child, child_offset = _normalize_ber_element(data, child_offset, child_depth)
        chunks.append(child)

    content = b''.join(chunks)
    content_length = len(content)
    length_bytes = encode_der_length(content_length)

    out = bytes([tag]) + length_bytes + content
    return (out, child_offset)

# ################################################################################################################################

def to_definite_der(der:'bytes') -> 'bytes':
    """ Returns the buffer re-encoded with definite lengths when it arrived in the BER
    indefinite-length form that streaming CMS producers emit - RFC 5652 allows it and
    the Java stacks behind most AS2 peers write it. A producer that streams must use
    the indefinite form at the top level, because a definite outer length would require
    buffering the whole structure first - so a definite top level means a definite
    encoding throughout and the buffer is returned as it is.
    """
    if der[1:2] != bytes([Indefinite_Length]):
        return der

    out, _ = _normalize_ber_element(der, 0)

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_content_info(der:'bytes') -> 'anytuple':
    """ Reads the outer CMS ContentInfo, returning its content type identifier
    and the explicit content element underneath.
    """
    content_info = read_der_element(der, 0)

    if content_info.tag != Tag.Sequence:
        raise AS2MalformedCMSException('ContentInfo is not a DER sequence')

    info_children = der_children(der, content_info)

    first_child = info_children[0]
    content_type_oid = element_bytes(der, first_child)
    explicit_content = info_children[1]

    out = (content_type_oid, explicit_content)
    return out

# ################################################################################################################################
# ################################################################################################################################
