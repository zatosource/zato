# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate, load_der_x509_certificate

# Zato
from zato.common.util.xml_.core import XMLSecurityException
from zato.common.util.xml_.keystore import certificate_list

# ################################################################################################################################
# ################################################################################################################################

# The DER tag of an ASN.1 SEQUENCE - both a PKIPath and each certificate inside it are sequences.
_der_sequence_tag = 0x30

# DER length bytes with the high bit set announce a multi-byte length field.
_der_long_form_marker = 0x80

# ################################################################################################################################
# ################################################################################################################################

def _encode_der_length(length:'int') -> 'bytes':
    """ Encodes a DER length field for the given content length.
    """
    # Short form fits lengths up to 127 in a single byte ..
    if length < _der_long_form_marker:
        out = bytes([length])
        return out

    # .. the long form spells out how many length bytes follow.
    length_bytes = length.to_bytes((length.bit_length() + 7) // 8, 'big')

    out = bytes([_der_long_form_marker | len(length_bytes)]) + length_bytes
    return out

# ################################################################################################################################

def _read_der_element(data:'bytes', offset:'int') -> 'tuple[int, int]':
    """ Reads the header of one DER element at the given offset.
    Returns the offset of its content and the content length.
    """
    length = data[offset + 1]
    header_size = 2

    # In the long form the first length byte only says how many real length bytes follow.
    if length & _der_long_form_marker:
        count = length & (_der_long_form_marker - 1)
        length = int.from_bytes(data[offset + 2:offset + 2 + count], 'big')
        header_size = 2 + count

    out = (offset + header_size, length)
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_pkipath(certificates:'certificate_list') -> 'bytes':
    """ Encodes a certificate chain as an X509PKIPathv1 structure - a DER SEQUENCE
    of certificates ordered from the trust anchor down to the leaf.
    """
    # The PKIPath order is root first, which is the reverse of how the chain is stored.
    content = b''

    for certificate in reversed(certificates):
        content += certificate.public_bytes(Encoding.DER)

    length = _encode_der_length(len(content))

    out = bytes([_der_sequence_tag]) + length + content
    return out

# ################################################################################################################################

def parse_pkipath(data:'bytes') -> 'certificate_list':
    """ Decodes an X509PKIPathv1 structure into its certificates,
    returned leaf first to match how chains are stored in the keystore.
    """
    if not data:
        raise XMLSecurityException('PKIPath token is empty')

    if data[0] != _der_sequence_tag:
        raise XMLSecurityException('PKIPath token is not a DER sequence')

    content_offset, content_length = _read_der_element(data, 0)
    end_offset = content_offset + content_length

    certificates:'certificate_list' = []
    offset = content_offset

    # Walk the sequence one certificate at a time - each one is itself a DER sequence.
    while offset < end_offset:
        certificate_start = offset
        certificate_content_offset, certificate_length = _read_der_element(data, offset)
        offset = certificate_content_offset + certificate_length

        certificate = load_der_x509_certificate(data[certificate_start:offset])
        certificates.append(certificate)

    if not certificates:
        raise XMLSecurityException('PKIPath token contains no certificates')

    # The wire order is root first, the keystore order is leaf first.
    certificates.reverse()

    out = certificates
    return out

# ################################################################################################################################

def parse_x509v3(data:'bytes') -> 'Certificate':
    """ Decodes a single DER certificate from an X509v3 token.
    """
    out = load_der_x509_certificate(data)
    return out

# ################################################################################################################################
# ################################################################################################################################
