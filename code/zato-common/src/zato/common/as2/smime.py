# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import zlib
from base64 import b64decode, b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
from os import urandom
from typing import NamedTuple

# cryptography
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES, AES128, AES256
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import Hash, SHA1, SHA256, SHA384, SHA512
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7EnvelopeBuilder, PKCS7Options, PKCS7SignatureBuilder
from cryptography.x509 import load_der_x509_certificate

# Zato
from zato.common.as2.common import AS2Error, AS2Exception, AS2MalformedCMSException, AS2ProtocolException, \
    AS2SecurityException, Default, DigestAlgorithm, EncryptionAlgorithm, Failure
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_, optional
from zato.common.util.xml_.core import XMLSecurityException
from zato.common.util.xml_.keystore import active_decryption_entries
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part
from zato.common.util.xml_.wssec import validate_certificate_chain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7HashTypes
    from cryptography.x509 import Certificate
    from zato.common.typing_ import anytuple, byteslist, dtnone, strlist
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    anytuple = anytuple
    byteslist = byteslist
    certificate_list = certificate_list
    dtnone = dtnone
    strlist = strlist
    PKCS7HashTypes = PKCS7HashTypes
    RSAPrivateKey = RSAPrivateKey
    RSAPublicKey = RSAPublicKey

# ################################################################################################################################
# ################################################################################################################################

der_element_list = list['DERElement']
decryption_candidate_list = list['DecryptionCandidate']

certificatelistnone = optional['certificate_list']
derelementnone      = optional['DERElement']
recipientmatchnone  = optional['RecipientMatch']

# ################################################################################################################################
# ################################################################################################################################

_crlf = b'\r\n'

# Transfer encodings whose content is never CRLF-canonicalized (RFC 4130 section 5.2.1).
_no_canonicalization_encodings = ('base64', 'binary')

# The transfer encoding assumed when a parsed entity does not declare one (RFC 2045 section 6.1).
_default_transfer_encoding = '7bit'

# base64 output is wrapped at this many characters per line (RFC 2045 section 6.8).
_base64_line_length = 76

# The nonce and authentication tag sizes for AES-GCM content encryption (RFC 5084 section 3.2).
_gcm_nonce_size = 12
_gcm_tag_size = 16

# The block sizes of 3DES and AES in CBC mode, which their PKCS#7 padding is based on.
_des_block_size = 8
_aes_block_size = 16

# The key and IV sizes of three-key 3DES in CBC mode.
_des_key_size = 24
_des_iv_size = 8

# The low bit of every 3DES key byte is a parity bit (RFC 5652 section 6.3 key expectations).
_des_parity_bit = 0x01
_des_key_bits_mask = 0xFE

# ################################################################################################################################
# ################################################################################################################################

# DER tags of the ASN.1 constructs that CMS structures are made of.
_tag_integer                  = 0x02
_tag_octet_string             = 0x04
_tag_oid                      = 0x06
_tag_utc_time                 = 0x17
_tag_generalized_time         = 0x18
_tag_octet_string_constructed = 0x24
_tag_sequence                 = 0x30
_tag_set                      = 0x31
_tag_context_0_implicit       = 0x80
_tag_context_0                = 0xA0
_tag_context_1                = 0xA1

# DER length bytes with the high bit set announce a multi-byte length field.
_der_long_form_marker = 0x80

# The constructed bit of a BER tag - set on sequences, sets and chunked string encodings.
_tag_constructed_bit = 0x20

# The BER indefinite-length marker and the end-of-contents octets that conclude such an element.
_ber_indefinite_length = 0x80
_ber_end_of_contents = b'\x00\x00'

# ASN.1 object identifiers use base-128 arcs with a continuation bit,
# and the first two arcs share one byte through this multiplier.
_base128_mask             = 0x7F
_base128_continuation     = 0x80
_oid_first_arc_multiplier = 40

# The DER encoding of an ASN.1 NULL, used as empty algorithm parameters.
_der_null = b'\x05\x00'

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

class DecryptionCandidate(NamedTuple):
    """ One certificate-and-key pair an incoming message may be encrypted to -
    during a rotation window of our own key there is more than one.
    """
    certificate: 'Certificate'
    key: 'RSAPrivateKey'

# ################################################################################################################################
# ################################################################################################################################

class RecipientMatch(NamedTuple):
    """ The certificate-and-key pair a recipient entry named, along with the encrypted
    content key that entry carries.
    """
    certificate: 'Certificate'
    key: 'RSAPrivateKey'
    encrypted_key: bytes

# ################################################################################################################################
# ################################################################################################################################

def _read_der_element(data:'bytes', offset:'int') -> 'DERElement':
    """ Reads the header of one DER element at the given offset.
    """
    tag = data[offset]
    length = data[offset + 1]
    header_size = 2

    # In the long form the first length byte only says how many real length bytes follow.
    if length & _der_long_form_marker:
        count = length & (_der_long_form_marker - 1)
        length = int.from_bytes(data[offset + 2:offset + 2 + count], 'big')
        header_size = 2 + count

    out = DERElement(tag, offset, offset + header_size, length)
    return out

# ################################################################################################################################

def _der_children(data:'bytes', element:'DERElement') -> 'der_element_list':
    """ Returns the immediate children of a constructed DER element.
    """
    out:'der_element_list' = []
    offset = element.content_offset
    end_offset = element.content_offset + element.length

    while offset < end_offset:
        child = _read_der_element(data, offset)
        out.append(child)
        offset = child.content_offset + child.length

    return out

# ################################################################################################################################

def _element_raw(data:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the complete encoding of an element - header and content.
    """
    out = data[element.header_offset:element.content_offset + element.length]
    return out

# ################################################################################################################################

def _element_content(data:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the content of an element, without its header.
    """
    out = data[element.content_offset:element.content_offset + element.length]
    return out

# ################################################################################################################################

def _normalize_ber_element(data:'bytes', offset:'int') -> 'anytuple':
    """ Re-encodes one BER element into its definite-length form, returning the re-encoded
    bytes along with the offset just past the element - end-of-contents octets included.
    """
    tag = data[offset]
    length = data[offset + 1]

    # An indefinite-length element runs until its end-of-contents octets -
    # re-encoding its children makes the actual length explicit ..
    if length == _ber_indefinite_length:
        chunks:'byteslist' = []
        child_offset = offset + 2

        while data[child_offset:child_offset + 2] != _ber_end_of_contents:
            child, child_offset = _normalize_ber_element(data, child_offset)
            chunks.append(child)

        content = b''.join(chunks)
        content_length = len(content)
        length_bytes = _encode_der_length(content_length)

        out = bytes([tag]) + length_bytes + content
        return (out, child_offset + 2)

    element = _read_der_element(data, offset)
    end_offset = element.content_offset + element.length

    # .. a definite-length primitive element stays exactly as it is ..
    if not (tag & _tag_constructed_bit):
        out = data[offset:end_offset]
        return (out, end_offset)

    # .. and a definite-length constructed one may still hide indefinite lengths further down.
    chunks:'byteslist' = []
    child_offset = element.content_offset

    while child_offset < end_offset:
        child, child_offset = _normalize_ber_element(data, child_offset)
        chunks.append(child)

    content = b''.join(chunks)
    content_length = len(content)
    length_bytes = _encode_der_length(content_length)

    out = bytes([tag]) + length_bytes + content
    return (out, child_offset)

# ################################################################################################################################

def _to_definite_der(der:'bytes') -> 'bytes':
    """ Returns the buffer re-encoded with definite lengths when it arrived in the BER
    indefinite-length form that streaming CMS producers emit - RFC 5652 allows it and
    the Java stacks behind most AS2 peers write it. A producer that streams must use
    the indefinite form at the top level, because a definite outer length would require
    buffering the whole structure first - so a definite top level means a definite
    encoding throughout and the buffer is returned as it is.
    """
    if der[1:2] != bytes([_ber_indefinite_length]):
        return der

    out, _ = _normalize_ber_element(der, 0)
    return out

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

def _der(tag:'int', content:'bytes') -> 'bytes':
    """ Encodes one complete DER element from its tag and content.
    """
    content_length = len(content)
    length = _encode_der_length(content_length)

    out = bytes([tag]) + length + content
    return out

# ################################################################################################################################

def _der_integer(value:'int') -> 'bytes':
    """ DER-encodes a non-negative integer, keeping the leading zero byte
    that marks the value as positive when its high bit is set.
    """
    byte_count = (value.bit_length() // 8) + 1
    content = value.to_bytes(byte_count, 'big')

    out = _der(_tag_integer, content)
    return out

# ################################################################################################################################

def _der_octet_string(content:'bytes') -> 'bytes':
    """ DER-encodes an octet string.
    """
    out = _der(_tag_octet_string, content)
    return out

# ################################################################################################################################

def _encode_oid(dotted:'str') -> 'bytes':
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

    out = _der(_tag_oid, content)
    return out

# ################################################################################################################################
# ################################################################################################################################

# Object identifiers of the CMS structures and algorithms this module handles,
# each stored as its complete DER encoding for direct byte comparisons.
_oid_data                = _encode_oid('1.2.840.113549.1.7.1')
_oid_signed_data         = _encode_oid('1.2.840.113549.1.7.2')
_oid_enveloped_data      = _encode_oid('1.2.840.113549.1.7.3')
_oid_content_type_attr   = _encode_oid('1.2.840.113549.1.9.3')
_oid_message_digest      = _encode_oid('1.2.840.113549.1.9.4')
_oid_signing_time        = _encode_oid('1.2.840.113549.1.9.5')
_oid_compressed_data     = _encode_oid('1.2.840.113549.1.9.16.1.9')
_oid_auth_enveloped_data = _encode_oid('1.2.840.113549.1.9.16.1.23')
_oid_zlib                = _encode_oid('1.2.840.113549.1.9.16.3.8')
_oid_rsa_encryption      = _encode_oid('1.2.840.113549.1.1.1')
_oid_des_ede3_cbc        = _encode_oid('1.2.840.113549.3.7')
_oid_aes_128_cbc         = _encode_oid('2.16.840.1.101.3.4.1.2')
_oid_aes_192_cbc         = _encode_oid('2.16.840.1.101.3.4.1.22')
_oid_aes_256_cbc         = _encode_oid('2.16.840.1.101.3.4.1.42')
_oid_aes_128_gcm         = _encode_oid('2.16.840.1.101.3.4.1.6')
_oid_aes_256_gcm         = _encode_oid('2.16.840.1.101.3.4.1.46')
_oid_sha1                = _encode_oid('1.3.14.3.2.26')
_oid_sha256              = _encode_oid('2.16.840.1.101.3.4.2.1')
_oid_sha384              = _encode_oid('2.16.840.1.101.3.4.2.2')
_oid_sha512              = _encode_oid('2.16.840.1.101.3.4.2.3')

# ################################################################################################################################
# ################################################################################################################################

# Maps RFC 5751 digest names to their hash classes.
_digest_by_name = {
    DigestAlgorithm.SHA1:   SHA1,
    DigestAlgorithm.SHA256: SHA256,
    DigestAlgorithm.SHA384: SHA384,
    DigestAlgorithm.SHA512: SHA512,
}

# Maps digest algorithm identifiers from SignerInfo back to RFC 5751 names.
_digest_name_by_oid = {
    _oid_sha1:   DigestAlgorithm.SHA1,
    _oid_sha256: DigestAlgorithm.SHA256,
    _oid_sha384: DigestAlgorithm.SHA384,
    _oid_sha512: DigestAlgorithm.SHA512,
}

# Every micalg spelling accepted on input, mapped to the RFC 5751 spelling always used on output.
_micalg_spelling = {
    'sha1':    DigestAlgorithm.SHA1,
    'sha-1':   DigestAlgorithm.SHA1,
    'sha256':  DigestAlgorithm.SHA256,
    'sha-256': DigestAlgorithm.SHA256,
    'sha384':  DigestAlgorithm.SHA384,
    'sha-384': DigestAlgorithm.SHA384,
    'sha512':  DigestAlgorithm.SHA512,
    'sha-512': DigestAlgorithm.SHA512,
}

# Maps outbound CBC algorithm names to the classes the envelope builder accepts.
_cbc_class_by_name = {
    EncryptionAlgorithm.AES_128_CBC: AES128,
    EncryptionAlgorithm.AES_256_CBC: AES256,
}

# Maps inbound CBC algorithm identifiers to their cipher classes and block sizes -
# AES-192 has no size-specific class, so the size-checking is left to the generic one.
_cbc_class_by_oid = {
    _oid_des_ede3_cbc: TripleDES,
    _oid_aes_128_cbc:  AES128,
    _oid_aes_192_cbc:  AES,
    _oid_aes_256_cbc:  AES256,
}

_cbc_block_size_by_oid = {
    _oid_des_ede3_cbc: _des_block_size,
    _oid_aes_128_cbc:  _aes_block_size,
    _oid_aes_192_cbc:  _aes_block_size,
    _oid_aes_256_cbc:  _aes_block_size,
}

# Key sizes in bytes for the AES-GCM algorithms built in-house through AuthEnvelopedData.
_gcm_key_size_by_name = {
    EncryptionAlgorithm.AES_128_GCM: 16,
    EncryptionAlgorithm.AES_256_GCM: 32,
}

# Maps AES-GCM algorithm names to their object identifiers and back.
_gcm_oid_by_name = {
    EncryptionAlgorithm.AES_128_GCM: _oid_aes_128_gcm,
    EncryptionAlgorithm.AES_256_GCM: _oid_aes_256_gcm,
}

_gcm_key_size_by_oid = {
    _oid_aes_128_gcm: 16,
    _oid_aes_256_gcm: 32,
}

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

@dataclass(init=False)
class VerifyResult:
    """ What verification of a multipart/signed entity yields.
    """
    # The inner entity whose signature was verified.
    part: 'SMIMEPart'

    # The certificate that signed the message, extracted from the signature itself.
    signer_certificate: 'Certificate'

    # The digest algorithm the signature used, in its RFC 5751 spelling.
    digest_algorithm: 'str'

    # The exact bytes the signature covers - the MIC of a signed message is computed over these.
    content: 'bytes'

    # The signing-time attribute, when the signer included one.
    signing_time: 'dtnone' = None

# ################################################################################################################################
# ################################################################################################################################

def new_part(data:'bytes', content_type:'str', content_transfer_encoding:'str'='binary') -> 'SMIMEPart':
    """ Returns a new S/MIME entity with the given content.
    """

    # Our response to produce
    out = SMIMEPart()

    out.data = data
    out.content_type = content_type
    out.content_transfer_encoding = content_transfer_encoding

    return out

# ################################################################################################################################

def _canonicalize_content(part:'SMIMEPart', prevent_canonicalization:'bool') -> 'bytes':
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
    out = normalized.replace(b'\n', _crlf)
    return out

# ################################################################################################################################

def serialize_part(part:'SMIMEPart', prevent_canonicalization:'bool'=False) -> 'bytes':
    """ Serializes an entity into its wire form - MIME headers, an empty line and the content.
    This is what signatures cover, what gets encrypted and what the MIC digests for signed
    and encrypted messages.
    """
    content = _canonicalize_content(part, prevent_canonicalization)

    headers = f'Content-Type: {part.content_type}\r\nContent-Transfer-Encoding: {part.content_transfer_encoding}\r\n'

    # The disposition header rides along only when a filename actually travels with the entity.
    if part.content_disposition:
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

def normalize_micalg(value:'str') -> 'str':
    """ Accepts any known spelling of a MIC algorithm name, case-insensitively,
    and returns the RFC 5751 spelling always used on output.
    """
    stripped = value.strip()
    lowered = stripped.lower()

    if spelling := _micalg_spelling.get(lowered):
        out = spelling
        return out

    # .. anything else is an algorithm this implementation does not support.
    else:
        raise AS2ProtocolException(Failure.Unsupported_MIC_Algorithms, f'Unsupported MIC algorithm `{value}`')

# ################################################################################################################################

def select_mic_algorithm(requested:'strlist') -> 'str':
    """ Picks the first supported algorithm from a signed-receipt-micalg list,
    honoring the sender's order of preference left to right.
    """
    for value in requested:
        stripped = value.strip()
        lowered = stripped.lower()
        if spelling := _micalg_spelling.get(lowered):
            out = spelling
            break
    else:
        joined = ', '.join(requested)
        raise AS2ProtocolException(Failure.Unsupported_MIC_Algorithms, f'No supported MIC algorithm among `{joined}`')

    return out

# ################################################################################################################################

def compute_mic_over(covered:'bytes', algorithm:'str'=Default.Digest_Algorithm) -> 'str':
    """ Digests the exact bytes given and returns the MIC in its wire form -
    the base64 digest with the RFC 5751 algorithm name appended after a comma.
    """
    normalized = normalize_micalg(algorithm)
    hash_class = _digest_by_name[normalized]
    hash_algorithm = hash_class()

    digest = Hash(hash_algorithm)
    digest.update(covered)
    digest_bytes = digest.finalize()

    encoded_bytes = b64encode(digest_bytes)
    encoded = encoded_bytes.decode('ascii')

    out = f'{encoded}, {normalized}'
    return out

# ################################################################################################################################

def compute_mic(
    part:'SMIMEPart',
    algorithm:'str'=Default.Digest_Algorithm,
    *,
    is_signed:'bool',
    is_encrypted:'bool',
    prevent_canonicalization:'bool'=False,
    ) -> 'str':
    """ Computes the Received-Content-MIC per RFC 4130 section 7.3.1. For signed messages the digest
    covers the canonicalized MIME headers plus content of the signed part, for encrypted unsigned
    messages the decrypted canonicalized MIME headers plus content, and for unsigned unencrypted
    messages the content alone, without any headers.
    """
    # Signed and encrypted messages digest the complete MIME entity ..
    include_headers = is_signed
    if is_encrypted:
        include_headers = True

    if include_headers:
        covered = serialize_part(part, prevent_canonicalization)

    # .. plain content travels bare and is digested alone.
    else:
        covered = _canonicalize_content(part, prevent_canonicalization)

    out = compute_mic_over(covered, algorithm)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_boundary() -> 'str':
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

    lines:'byteslist' = []

    for offset in range(0, len(encoded), _base64_line_length):
        lines.append(encoded[offset:offset + _base64_line_length])

    out = _crlf.join(lines)
    return out

# ################################################################################################################################

def _read_content_info(der:'bytes') -> 'anytuple':
    """ Reads the outer CMS ContentInfo, returning its content type identifier
    and the explicit content element underneath.
    """
    content_info = _read_der_element(der, 0)

    if content_info.tag != _tag_sequence:
        raise AS2MalformedCMSException('ContentInfo is not a DER sequence')

    info_children = _der_children(der, content_info)

    first_child = info_children[0]
    content_type_oid = _element_raw(der, first_child)
    explicit_content = info_children[1]

    out = (content_type_oid, explicit_content)
    return out

# ################################################################################################################################

def _transfer_decode(part:'SMIMEPart') -> 'bytes':
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

def _build_sha1_signed_data(content:'bytes', keystore:'Keystore') -> 'bytes':
    """ Builds a detached SHA-1 SignedData structure in-house - the library refuses to create
    new SHA-1 signatures, yet some partners still require them.
    """
    signing_key = cast_('RSAPrivateKey', keystore.signing_key)
    signing_certificate = keystore.signing_certificate

    # The message-digest attribute carries the SHA-1 digest of the content.
    hash_algorithm = SHA1()
    digest = Hash(hash_algorithm)
    digest.update(content)
    content_digest = digest.finalize()

    # The two mandatory signed attributes of RFC 5652 section 5.3, plus the signing time ..
    content_type_attribute = _der(_tag_sequence, _oid_content_type_attr + _der(_tag_set, _oid_data))
    message_digest_attribute = _der(_tag_sequence, _oid_message_digest + _der(_tag_set, _der_octet_string(content_digest)))

    now = datetime.now(timezone.utc)
    time_text = now.strftime('%y%m%d%H%M%SZ').encode('ascii')
    signing_time_attribute = _der(_tag_sequence, _oid_signing_time + _der(_tag_set, _der(_tag_utc_time, time_text)))

    # .. in the ascending encoded order a DER SET OF requires.
    attributes = sorted([content_type_attribute, message_digest_attribute, signing_time_attribute])
    attributes_content = b''.join(attributes)

    # The signature covers the attributes under their SET OF tag,
    # while SignerInfo carries them under IMPLICIT [0].
    signed_bytes = _der(_tag_set, attributes_content)
    signature = signing_key.sign(signed_bytes, PKCS1v15(), SHA1())

    digest_algorithm = _der(_tag_sequence, _oid_sha1 + _der_null)
    signature_algorithm = _der(_tag_sequence, _oid_rsa_encryption + _der_null)

    issuer = signing_certificate.issuer.public_bytes()
    serial = _der_integer(signing_certificate.serial_number)
    issuer_and_serial = _der(_tag_sequence, issuer + serial)

    signer_version = _der_integer(1)
    signer_info = _der(_tag_sequence,
        signer_version
        + issuer_and_serial
        + digest_algorithm
        + _der(_tag_context_0, attributes_content)
        + signature_algorithm
        + _der_octet_string(signature))

    # The whole chain rides along so receivers can build a path to their trust anchors.
    certificates = b''
    for certificate in keystore.signing_certificate_chain:
        certificates += certificate.public_bytes(Encoding.DER)

    # Detached signing leaves the encapsulated content info without any content.
    encapsulated = _der(_tag_sequence, _oid_data)

    version = _der_integer(1)
    signed_data = _der(_tag_sequence,
        version
        + _der(_tag_set, digest_algorithm)
        + encapsulated
        + _der(_tag_context_0, certificates)
        + _der(_tag_set, signer_info))

    out = _der(_tag_sequence, _oid_signed_data + _der(_tag_context_0, signed_data))
    return out

# ################################################################################################################################

def sign(
    part:'SMIMEPart',
    keystore:'Keystore',
    digest_algorithm:'str'=Default.Digest_Algorithm,
    prevent_canonicalization:'bool'=False,
    ) -> 'SMIMEPart':
    """ Wraps an entity in a detached multipart/signed structure per RFC 8551 section 3.5.3,
    with the CMS signature riding in an application/pkcs7-signature part.
    """
    algorithm = normalize_micalg(digest_algorithm)
    hash_class = _digest_by_name[algorithm]

    # The signature covers the complete inner MIME entity - headers and content alike.
    content = serialize_part(part, prevent_canonicalization)

    # SHA-1 for partners that require it is built in-house because the library refuses it ..
    if algorithm == DigestAlgorithm.SHA1:
        signature = _build_sha1_signed_data(content, keystore)

    # .. everything current goes through the library's builder.
    else:
        signing_key = cast_('RSAPrivateKey', keystore.signing_key)
        hash_algorithm = cast_('PKCS7HashTypes', hash_class())

        builder = PKCS7SignatureBuilder()
        builder = builder.set_data(content)
        builder = builder.add_signer(keystore.signing_certificate, signing_key, hash_algorithm)

        # Intermediates ride along so receivers can build a chain up to their trust anchors.
        for certificate in keystore.signing_certificate_chain[1:]:
            builder = builder.add_certificate(certificate)

        signature = builder.sign(Encoding.DER, [PKCS7Options.DetachedSignature, PKCS7Options.Binary])

    encoded_signature = encode_base64_lines(signature)

    # The inner entity goes into the first part exactly as signed,
    # the signature into the second, base64-encoded.
    boundary = _new_boundary()

    chunks:'byteslist' = []
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(content)
    chunks.append(f'--{boundary}'.encode('ascii'))
    chunks.append(b'Content-Type: application/pkcs7-signature; name="smime.p7s"')
    chunks.append(b'Content-Transfer-Encoding: base64')
    chunks.append(b'Content-Disposition: attachment; filename="smime.p7s"')
    chunks.append(b'')
    chunks.append(encoded_signature)
    chunks.append(f'--{boundary}--'.encode('ascii'))
    chunks.append(b'')

    body = _crlf.join(chunks)

    content_type = f'multipart/signed; protocol="application/pkcs7-signature"; micalg={algorithm}; boundary="{boundary}"'

    out = new_part(body, content_type)
    return out

# ################################################################################################################################

def _split_signed(body:'bytes', boundary:'str') -> 'anytuple':
    """ Splits a multipart/signed body into the byte-exact signed content and the decoded signature.
    """
    delimiter = b'--' + boundary.encode('ascii')
    pieces = body.split(delimiter)

    piece_count = len(pieces)
    if piece_count < 4:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'multipart/signed does not have its two parts')

    # The signed content is everything between the first two boundary lines, byte-exact -
    # the delimiter's own leading and trailing CRLF do not belong to it.
    content = pieces[1]
    if content.startswith(_crlf):
        content = content[2:]
    if content.endswith(_crlf):
        content = content[:-2]

    # The second part carries the signature, usually base64-encoded.
    signature_headers, signature = parse_mime_part(pieces[2])

    if signature.endswith(_crlf):
        signature = signature[:-2]

    if transfer_encoding := signature_headers.get('content-transfer-encoding'):
        if transfer_encoding.lower() == 'base64':
            signature = b64decode(signature)

    out = (content, signature)
    return out

# ################################################################################################################################

def _read_attribute_value(der:'bytes', signed_attributes:'DERElement', type_oid:'bytes') -> 'derelementnone':
    """ Finds the first value of the given attribute among the signed attributes, when it is present.
    """
    for attribute in _der_children(der, signed_attributes):
        attribute_children = _der_children(der, attribute)
        attribute_type = _element_raw(der, attribute_children[0])

        if attribute_type == type_oid:
            value_set = attribute_children[1]
            values = _der_children(der, value_set)

            out = values[0]
            break
    else:
        out = None

    return out

# ################################################################################################################################

def _read_message_digest(der:'bytes', signed_attributes:'DERElement') -> 'bytes':
    """ Finds the message-digest attribute (RFC 5652 section 11.2) among the signed attributes.
    """
    digest_value = _read_attribute_value(der, signed_attributes, _oid_message_digest)

    if not digest_value:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Signed attributes do not include a message-digest')

    out = _element_content(der, digest_value)
    return out

# ################################################################################################################################

def _read_signing_time(der:'bytes', signed_attributes:'DERElement') -> 'dtnone':
    """ Finds and parses the optional signing-time attribute (RFC 5652 section 11.3).
    """
    time_value = _read_attribute_value(der, signed_attributes, _oid_signing_time)

    if not time_value:
        return None

    text = _element_content(der, time_value).decode('ascii')

    # UTCTime carries a two-digit year pivoting at 2050, GeneralizedTime a four-digit one.
    if time_value.tag == _tag_utc_time:
        parsed = datetime.strptime(text, '%y%m%d%H%M%SZ')
    elif time_value.tag == _tag_generalized_time:
        parsed = datetime.strptime(text, '%Y%m%d%H%M%SZ')

    # .. any other encoding is not one RFC 5652 allows for this attribute.
    else:
        return None

    out = parsed.replace(tzinfo=timezone.utc)
    return out

# ################################################################################################################################

def _verify_signed_data(
    content:'bytes',
    der:'bytes',
    keystore:'Keystore',
    accepted_certificates:'certificatelistnone'=None,
    ) -> 'anytuple':
    """ Walks a CMS SignedData structure per RFC 5652: extracts the signer's certificate
    and signed attributes, checks the content digest and verifies the signature value.
    Returns the signer's certificate and the digest algorithm name.
    """
    content_type_oid, explicit_content = _read_content_info(der)

    if content_type_oid != _oid_signed_data:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'CMS content type is not SignedData')

    signed_data = _read_der_element(der, explicit_content.content_offset)
    children = _der_children(der, signed_data)

    # Collect the certificates the sender attached ..
    certificates:'certificate_list' = []

    for child in children:
        if child.tag == _tag_context_0:
            for certificate_element in _der_children(der, child):
                raw = _element_raw(der, certificate_element)
                certificate = load_der_x509_certificate(raw)
                certificates.append(certificate)

    # .. and the first signer - AS2 messages have exactly one.
    signer_infos = children[-1]
    signer_list = _der_children(der, signer_infos)
    signer_info = signer_list[0]

    fields = _der_children(der, signer_info)
    signer_id = fields[1]
    digest_algorithm = fields[2]

    # The signed attributes are optional - when present they carry the content digest.
    signed_attributes = None
    next_index = 3

    if fields[next_index].tag == _tag_context_0:
        signed_attributes = fields[next_index]
        next_index += 1

    signature_element = fields[next_index + 1]
    signature = _element_content(der, signature_element)

    # Resolve the digest algorithm the signature used.
    algorithm_children = _der_children(der, digest_algorithm)
    digest_oid = _element_raw(der, algorithm_children[0])

    if not (digest_name := _digest_name_by_oid.get(digest_oid)):
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Unsupported digest algorithm in SignerInfo')

    hash_class = _digest_by_name[digest_name]

    # The signer identifier names the certificate by issuer and serial number.
    sid_children = _der_children(der, signer_id)
    issuer_raw = _element_raw(der, sid_children[0])
    serial_content = _element_content(der, sid_children[1])
    serial_number = int.from_bytes(serial_content, 'big')

    # The certificates field is optional (RFC 5652 section 5.1) - some peers attach nothing
    # and count on the verifier holding their certificate already, so the attached ones
    # are searched first and the configured trust material after them.
    candidates:'certificate_list' = list(certificates)

    if accepted_certificates:
        candidates.extend(accepted_certificates)

    if keystore.peer_signing_certificate:
        candidates.append(keystore.peer_signing_certificate)

    for certificate in candidates:
        issuer_bytes = certificate.issuer.public_bytes()
        if issuer_bytes == issuer_raw:
            if certificate.serial_number == serial_number:
                signer_certificate = certificate
                break
    else:
        raise AS2SecurityException(
            AS2Error.Authentication_Failed, 'Signer certificate is neither attached to the signature nor configured')

    # The digest of the content as it actually arrived.
    hash_algorithm = hash_class()
    digest = Hash(hash_algorithm)
    digest.update(content)
    content_digest = digest.finalize()

    # With signed attributes present, the content digest must match the message-digest attribute
    # and the signature covers the attributes themselves ..
    signing_time = None

    if signed_attributes:
        message_digest = _read_message_digest(der, signed_attributes)
        signing_time = _read_signing_time(der, signed_attributes)

        if message_digest != content_digest:
            raise AS2SecurityException(
                AS2Error.Integrity_Check_Failed, 'Content digest does not match the message-digest attribute')

        # For the signature check the IMPLICIT [0] tag reverts to the SET OF it replaced (RFC 5652 section 5.4).
        attributes_raw = _element_raw(der, signed_attributes)
        signed_bytes = bytes([_tag_set]) + attributes_raw[1:]

    # .. without them the signature covers the content directly.
    else:
        signed_bytes = content

    public_key = cast_('RSAPublicKey', signer_certificate.public_key())

    try:
        public_key.verify(signature, signed_bytes, PKCS1v15(), hash_class())
    except InvalidSignature:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Signature verification failed') from None

    # A cryptographically valid signature still needs a trusted signer. With a rotation list
    # given, the list itself is the trust decision - the signer must be one of its entries,
    # which during an overlap window means either the old or the new certificate ..
    if accepted_certificates:

        if signer_certificate not in accepted_certificates:
            raise AS2SecurityException(
                AS2Error.Authentication_Failed, 'Signer certificate is not among the accepted ones')

    # .. without one, the keystore decides - the chain starts at the signer's certificate
    # and any other attached certificates are potential intermediates.
    else:
        chain:'certificate_list' = [signer_certificate]

        for certificate in certificates:
            if certificate != signer_certificate:
                chain.append(certificate)

        try:
            validate_certificate_chain(chain, keystore)
        except XMLSecurityException as e:
            raise AS2SecurityException(AS2Error.Authentication_Failed, str(e)) from None

    out = (signer_certificate, digest_name, signing_time)
    return out

# ################################################################################################################################

def verify(
    part:'SMIMEPart',
    keystore:'Keystore',
    accepted_certificates:'certificatelistnone'=None,
    ) -> 'VerifyResult':
    """ Verifies a detached multipart/signed entity and returns what was signed, by whom
    and with which digest algorithm. Raises AS2SecurityException with integrity-check-failed
    for a cryptographically bad signature and authentication-failed for an untrusted signer.
    A non-empty accepted_certificates list is the trust decision - the signer must be one
    of its entries - while an absent one leaves trust to the keystore.
    """
    parameters = parse_header_parameters(part.content_type)
    media_type = parameters['']

    if media_type != 'multipart/signed':
        raise AS2ProtocolException(AS2Error.Insufficient_Message_Security, f'Expected multipart/signed, received `{media_type}`')

    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(AS2Error.Unexpected_Processing_Error, 'multipart/signed without a boundary parameter')

    content, signature_der = _split_signed(part.data, boundary)

    try:
        # Streaming producers encode the signature with BER indefinite lengths.
        signature_der = _to_definite_der(signature_der)

        signer_certificate, digest_name, signing_time = _verify_signed_data(
            content, signature_der, keystore, accepted_certificates)
    except (AS2MalformedCMSException, IndexError, ValueError) as e:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, f'Malformed signature structure ({e})') from None

    inner = parse_part(content)

    # Our response to produce
    out = VerifyResult()

    out.part = inner
    out.signer_certificate = signer_certificate
    out.digest_algorithm = digest_name
    out.content = content
    out.signing_time = signing_time

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_key_transport_recipient(content_key:'bytes', certificate:'Certificate') -> 'bytes':
    """ Builds a KeyTransRecipientInfo per RFC 5652 section 6.2.1 - the content encryption key,
    RSA-encrypted to the recipient's certificate, named by issuer and serial number.
    """
    public_key = cast_('RSAPublicKey', certificate.public_key())
    encrypted_key = public_key.encrypt(content_key, PKCS1v15())

    issuer = certificate.issuer.public_bytes()
    serial = _der_integer(certificate.serial_number)
    issuer_and_serial = _der(_tag_sequence, issuer + serial)

    key_algorithm = _der(_tag_sequence, _oid_rsa_encryption + _der_null)
    version = _der_integer(0)

    out = _der(_tag_sequence, version + issuer_and_serial + key_algorithm + _der_octet_string(encrypted_key))
    return out

# ################################################################################################################################

def _encrypt_gcm(content:'bytes', certificate:'Certificate', algorithm:'str', key_size:'int') -> 'bytes':
    """ Builds a CMS AuthEnvelopedData structure per RFC 5083 with AES-GCM content encryption
    per RFC 5084 - the opt-in outbound path for partners that ask for it.
    """
    # A fresh content encryption key and nonce for every message.
    content_key = urandom(key_size)
    nonce = urandom(_gcm_nonce_size)

    cipher = AESGCM(content_key)
    sealed = cipher.encrypt(nonce, content, None)

    # AESGCM appends the authentication tag - CMS carries it in a separate field.
    ciphertext = sealed[:-_gcm_tag_size]
    tag = sealed[-_gcm_tag_size:]

    recipient_info = _build_key_transport_recipient(content_key, certificate)
    recipient_infos = _der(_tag_set, recipient_info)

    # GCMParameters per RFC 5084 - the nonce and the explicit tag length.
    parameters = _der(_tag_sequence, _der_octet_string(nonce) + _der_integer(_gcm_tag_size))
    algorithm_identifier = _der(_tag_sequence, _gcm_oid_by_name[algorithm] + parameters)

    encrypted_content = _der(_tag_context_0_implicit, ciphertext)
    encrypted_content_info = _der(_tag_sequence, _oid_data + algorithm_identifier + encrypted_content)

    version = _der_integer(0)
    auth_enveloped = _der(_tag_sequence, version + recipient_infos + encrypted_content_info + _der_octet_string(tag))

    out = _der(_tag_sequence, _oid_auth_enveloped_data + _der(_tag_context_0, auth_enveloped))
    return out

# ################################################################################################################################

def _new_3des_key() -> 'bytes':
    """ Returns a fresh three-key 3DES key with the parity bit of every byte set,
    as DES key material is defined to carry odd parity.
    """
    raw = urandom(_des_key_size)

    key_bytes = bytearray()

    for byte in raw:

        # Keep the seven key bits and count how many of them are set ..
        key_bits = byte & _des_key_bits_mask
        ones_count = bin(key_bits).count('1')

        # .. the parity bit makes the total number of set bits odd.
        if ones_count % 2 == 0:
            key_bits |= _des_parity_bit

        key_bytes.append(key_bits)

    out = bytes(key_bytes)
    return out

# ################################################################################################################################

def _add_cbc_padding(content:'bytes') -> 'bytes':
    """ Appends the PKCS#7 block padding of a CBC plaintext - the counterpart of _strip_cbc_padding.
    """
    pad_length = _des_block_size - (len(content) % _des_block_size)

    out = content + bytes([pad_length]) * pad_length
    return out

# ################################################################################################################################

def _encrypt_3des(content:'bytes', certificate:'Certificate') -> 'bytes':
    """ Builds a CMS EnvelopedData structure with 3DES-CBC content encryption per RFC 5652 -
    the outbound path for partners that cannot decrypt AES, the exact structure
    _decrypt_enveloped parses on the way in.
    """
    # A fresh content encryption key and IV for every message.
    content_key = _new_3des_key()
    initialization_vector = urandom(_des_iv_size)

    # CBC needs the plaintext padded to whole blocks before encryption.
    padded = _add_cbc_padding(content)

    cipher_algorithm = TripleDES(content_key)
    cipher_mode = CBC(initialization_vector)

    cipher = Cipher(cipher_algorithm, cipher_mode)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    recipient_info = _build_key_transport_recipient(content_key, certificate)
    recipient_infos = _der(_tag_set, recipient_info)

    # The algorithm identifier carries the IV as its parameter.
    algorithm_identifier = _der(_tag_sequence, _oid_des_ede3_cbc + _der_octet_string(initialization_vector))

    encrypted_content = _der(_tag_context_0_implicit, ciphertext)
    encrypted_content_info = _der(_tag_sequence, _oid_data + algorithm_identifier + encrypted_content)

    version = _der_integer(0)
    enveloped = _der(_tag_sequence, version + recipient_infos + encrypted_content_info)

    out = _der(_tag_sequence, _oid_enveloped_data + _der(_tag_context_0, enveloped))
    return out

# ################################################################################################################################

def encrypt(
    part:'SMIMEPart',
    certificate:'Certificate',
    algorithm:'str'=Default.Encryption_Algorithm,
    force_base64:'bool'=False,
    prevent_canonicalization:'bool'=False,
    ) -> 'SMIMEPart':
    """ Encrypts an entity to the recipient's certificate, producing an application/pkcs7-mime
    entity with smime-type=enveloped-data (CBC) or its AuthEnvelopedData sibling (GCM).
    """
    content = serialize_part(part, prevent_canonicalization)

    # The CBC baseline goes through the library's envelope builder ..
    if cbc_class := _cbc_class_by_name.get(algorithm):
        builder = PKCS7EnvelopeBuilder()
        builder = builder.set_data(content)
        builder = builder.add_recipient(certificate)
        builder = builder.set_content_encryption_algorithm(cbc_class)
        envelope = builder.encrypt(Encoding.DER, [PKCS7Options.Binary])

    # .. the GCM opt-in is built in-house because the library has no AuthEnvelopedData support ..
    elif key_size := _gcm_key_size_by_name.get(algorithm):
        envelope = _encrypt_gcm(content, certificate, algorithm, key_size)

    # .. 3DES for partners that cannot decrypt AES is built in-house
    # because the library refuses to produce it ..
    elif algorithm == EncryptionAlgorithm.DES_EDE3_CBC:
        envelope = _encrypt_3des(content, certificate)

    # .. and anything else is not an algorithm outgoing messages may use.
    else:
        raise AS2Exception(f'Unsupported encryption algorithm `{algorithm}`')

    # Our response to produce
    out = SMIMEPart()

    out.content_type = 'application/pkcs7-mime; smime-type=enveloped-data; name="smime.p7m"'

    if force_base64:
        out.data = encode_base64_lines(envelope)
        out.content_transfer_encoding = 'base64'
    else:
        out.data = envelope
        out.content_transfer_encoding = 'binary'

    return out

# ################################################################################################################################

def _collect_encrypted_content(der:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the encrypted content octets, joining the chunks of a constructed encoding if needed.
    """
    # The primitive form carries the octets directly ..
    if element.tag == _tag_context_0_implicit:
        out = _element_content(der, element)
        return out

    # .. the constructed BER form some producers emit splits them into octet string chunks.
    if element.tag == _tag_context_0:
        chunks:'byteslist' = []

        for chunk in _der_children(der, element):
            chunk_content = _element_content(der, chunk)
            chunks.append(chunk_content)

        out = b''.join(chunks)
        return out

    # .. any other tag means the structure is not what CMS says it should be.
    raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unexpected encoding of the encrypted content')

# ################################################################################################################################

def _collect_compressed_content(der:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the compressed content octets, joining the chunks of a constructed encoding if needed.
    """
    # The primitive form carries the octets directly ..
    if element.tag == _tag_octet_string:
        out = _element_content(der, element)
        return out

    # .. the constructed BER form some producers emit splits them into octet string chunks.
    if element.tag == _tag_octet_string_constructed:
        chunks:'byteslist' = []

        for chunk in _der_children(der, element):
            chunk_content = _element_content(der, chunk)
            chunks.append(chunk_content)

        out = b''.join(chunks)
        return out

    # .. any other tag means the structure is not what CMS says it should be.
    raise AS2ProtocolException(AS2Error.Decompression_Failed, 'Unexpected encoding of the compressed content')

# ################################################################################################################################

def _decryption_candidates(keystore:'Keystore') -> 'decryption_candidate_list':
    """ Returns every certificate-and-key pair an incoming message may be encrypted to -
    the primary pair plus each currently active rotation entry.
    """

    # Our response to produce
    out:'decryption_candidate_list' = []

    # The primary pair - our signing certificate with the configured decryption key ..
    if keystore.decryption_key:
        key = cast_('RSAPrivateKey', keystore.decryption_key)
        candidate = DecryptionCandidate(keystore.signing_certificate, key)
        out.append(candidate)

    # .. and the rotation entries, each with its own certificate.
    for entry in active_decryption_entries(keystore):
        key = cast_('RSAPrivateKey', entry.key)
        certificate = cast_('Certificate', entry.certificate)
        candidate = DecryptionCandidate(certificate, key)
        out.append(candidate)

    return out

# ################################################################################################################################

def _match_recipient(der:'bytes', recipient_infos:'DERElement', keystore:'Keystore') -> 'RecipientMatch':
    """ Walks the recipient set looking for an entry that names any of our certificate-and-key
    pairs by issuer and serial number, returning the pair and the encrypted content key.
    """
    candidates = _decryption_candidates(keystore)

    # Our response to produce
    out:'recipientmatchnone' = None

    for recipient in _der_children(der, recipient_infos):
        fields = _der_children(der, recipient)
        recipient_id = fields[1]

        # Only the issuerAndSerialNumber form of recipient identification is used by AS2 peers.
        if recipient_id.tag != _tag_sequence:
            continue

        rid_children = _der_children(der, recipient_id)
        issuer_raw = _element_raw(der, rid_children[0])
        serial_content = _element_content(der, rid_children[1])
        serial_number = int.from_bytes(serial_content, 'big')

        # The first of our pairs this recipient entry names is the one to decrypt with ..
        for candidate in candidates:

            issuer = candidate.certificate.issuer.public_bytes()
            if issuer_raw != issuer:
                continue

            if serial_number != candidate.certificate.serial_number:
                continue

            encrypted_key = _element_content(der, fields[3])
            out = RecipientMatch(candidate.certificate, candidate.key, encrypted_key)
            break

        # .. and a matched pair concludes the search.
        if out:
            break

    # No recipient entry names any of our certificates.
    if not out:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'No recipient entry matches our certificate')

    return out

# ################################################################################################################################

def _recover_content_key(der:'bytes', recipient_infos:'DERElement', keystore:'Keystore') -> 'bytes':
    """ Finds our recipient entry and RSA-decrypts the content encryption key it carries.
    """
    match = _match_recipient(der, recipient_infos, keystore)

    try:
        out = match.key.decrypt(match.encrypted_key, PKCS1v15())
    except ValueError:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Content encryption key decryption failed') from None

    return out

# ################################################################################################################################

def _strip_cbc_padding(padded:'bytes', block_size:'int') -> 'bytes':
    """ Removes the PKCS#7 block padding of a CBC plaintext, verifying that it is well-formed.
    """
    if not padded:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Decrypted content is empty')

    pad_length = padded[-1]

    if pad_length == 0:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Invalid block padding')

    if pad_length > block_size:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Invalid block padding')

    expected = bytes([pad_length]) * pad_length
    padding = padded[-pad_length:]

    if padding != expected:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Invalid block padding')

    out = padded[:-pad_length]
    return out

# ################################################################################################################################

def _decrypt_enveloped(der:'bytes', explicit_content:'DERElement', keystore:'Keystore') -> 'bytes':
    """ Decrypts a CBC EnvelopedData structure per RFC 5652 - AES or 3DES, whichever
    the algorithm identifier names.
    """
    enveloped = _read_der_element(der, explicit_content.content_offset)
    children = _der_children(der, enveloped)

    # Skip past the version and the optional originator info to the recipient set,
    # so that whichever of our certificate-and-key pairs the message was encrypted to
    # is the one that decrypts it.
    next_index = 1
    if children[next_index].tag == _tag_context_0:
        next_index += 1

    recipient_infos = children[next_index]
    encrypted_content_info = children[next_index + 1]

    content_key = _recover_content_key(der, recipient_infos, keystore)

    # The algorithm identifier carries the IV as its parameter.
    info_children = _der_children(der, encrypted_content_info)
    algorithm_identifier = info_children[1]
    encrypted_content = info_children[2]

    algorithm_children = _der_children(der, algorithm_identifier)
    algorithm_oid = _element_raw(der, algorithm_children[0])

    if not (cipher_class := _cbc_class_by_oid.get(algorithm_oid)):
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unsupported content encryption algorithm')

    block_size = _cbc_block_size_by_oid[algorithm_oid]

    initialization_vector = _element_content(der, algorithm_children[1])
    ciphertext = _collect_encrypted_content(der, encrypted_content)

    cipher = Cipher(cipher_class(content_key), CBC(initialization_vector))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    out = _strip_cbc_padding(padded, block_size)
    return out

# ################################################################################################################################

def _decrypt_auth_enveloped(der:'bytes', explicit_content:'DERElement', keystore:'Keystore') -> 'bytes':
    """ Decrypts an AES-GCM AuthEnvelopedData structure per RFC 5083 and RFC 5084.
    """
    auth_enveloped = _read_der_element(der, explicit_content.content_offset)
    children = _der_children(der, auth_enveloped)

    # Skip past the version and the optional originator info to the recipient set.
    next_index = 1
    if children[next_index].tag == _tag_context_0:
        next_index += 1

    recipient_infos = children[next_index]
    encrypted_content_info = children[next_index + 1]
    next_index += 2

    # The optional authenticated attributes become additional authenticated data,
    # re-tagged as the SET OF their IMPLICIT [1] tag replaced.
    associated_data = None

    if children[next_index].tag == _tag_context_1:
        attributes_raw = _element_raw(der, children[next_index])
        associated_data = bytes([_tag_set]) + attributes_raw[1:]
        next_index += 1

    mac = children[next_index]

    content_key = _recover_content_key(der, recipient_infos, keystore)

    info_children = _der_children(der, encrypted_content_info)
    algorithm_identifier = info_children[1]
    encrypted_content = info_children[2]

    algorithm_children = _der_children(der, algorithm_identifier)
    algorithm_oid = _element_raw(der, algorithm_children[0])

    if not (key_size := _gcm_key_size_by_oid.get(algorithm_oid)):
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unsupported content encryption algorithm')

    if len(content_key) != key_size:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Content encryption key size does not match the algorithm')

    # GCMParameters - the nonce and, optionally, an explicit tag length which is not needed
    # because the tag travels in the mac field with its own length.
    parameter_children = _der_children(der, algorithm_children[1])
    nonce = _element_content(der, parameter_children[0])

    ciphertext = _collect_encrypted_content(der, encrypted_content)
    tag = _element_content(der, mac)

    cipher = AESGCM(content_key)

    try:
        out = cipher.decrypt(nonce, ciphertext + tag, associated_data)
    except InvalidTag:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Authentication tag verification failed') from None

    return out

# ################################################################################################################################

def decrypt(part:'SMIMEPart', keystore:'Keystore') -> 'SMIMEPart':
    """ Decrypts an application/pkcs7-mime entity back into the MIME entity underneath.
    Handles EnvelopedData with AES-CBC or 3DES, and AES-GCM AuthEnvelopedData.
    """
    der = _transfer_decode(part)

    try:
        # Streaming producers encode their envelopes with BER indefinite lengths.
        der = _to_definite_der(der)

        content_type_oid, explicit_content = _read_content_info(der)

        if content_type_oid == _oid_enveloped_data:
            plaintext = _decrypt_enveloped(der, explicit_content, keystore)
        elif content_type_oid == _oid_auth_enveloped_data:
            plaintext = _decrypt_auth_enveloped(der, explicit_content, keystore)

        # .. any other content type is not something decryption can handle.
        else:
            raise AS2SecurityException(AS2Error.Decryption_Failed, 'CMS content type is not an enveloped structure')

    except (AS2MalformedCMSException, IndexError, ValueError) as e:
        raise AS2SecurityException(AS2Error.Decryption_Failed, f'Malformed encrypted structure ({e})') from None

    out = parse_part(plaintext)
    return out

# ################################################################################################################################
# ################################################################################################################################

def compress(part:'SMIMEPart', prevent_canonicalization:'bool'=False) -> 'SMIMEPart':
    """ Wraps an entity in a CMS CompressedData structure per RFC 5402 and RFC 3274,
    producing an application/pkcs7-mime entity with smime-type=compressed-data.
    Compression may run before or after signing - both orders exist in the wild.
    """
    content = serialize_part(part, prevent_canonicalization)
    compressed = zlib.compress(content)

    # CompressedData per RFC 3274 - the zlib stream rides in an id-data encapsulated content.
    algorithm_identifier = _der(_tag_sequence, _oid_zlib)
    octets = _der_octet_string(compressed)
    encapsulated = _der(_tag_sequence, _oid_data + _der(_tag_context_0, octets))

    version = _der_integer(0)
    compressed_data = _der(_tag_sequence, version + algorithm_identifier + encapsulated)
    envelope = _der(_tag_sequence, _oid_compressed_data + _der(_tag_context_0, compressed_data))

    # Our response to produce
    out = SMIMEPart()

    out.content_type = 'application/pkcs7-mime; smime-type=compressed-data; name="smime.p7z"'
    out.content_transfer_encoding = 'binary'
    out.data = envelope

    return out

# ################################################################################################################################

def decompress(part:'SMIMEPart') -> 'SMIMEPart':
    """ Unwraps a CMS CompressedData entity back into the MIME entity underneath.
    """
    der = _transfer_decode(part)

    try:
        # Streaming producers encode their compressed structures with BER indefinite lengths.
        der = _to_definite_der(der)

        content_type_oid, explicit_content = _read_content_info(der)

        if content_type_oid != _oid_compressed_data:
            raise AS2ProtocolException(AS2Error.Decompression_Failed, 'CMS content type is not CompressedData')

        compressed_data = _read_der_element(der, explicit_content.content_offset)
        children = _der_children(der, compressed_data)

        # The only compression algorithm RFC 5402 defines is zlib.
        algorithm_identifier = children[1]
        algorithm_children = _der_children(der, algorithm_identifier)
        algorithm_oid = _element_raw(der, algorithm_children[0])

        if algorithm_oid != _oid_zlib:
            raise AS2ProtocolException(AS2Error.Decompression_Failed, 'Unsupported compression algorithm')

        # The compressed octets live inside the encapsulated content info.
        encapsulated = children[2]
        encapsulated_children = _der_children(der, encapsulated)
        explicit_octets = encapsulated_children[1]
        octets = _read_der_element(der, explicit_octets.content_offset)
        compressed = _collect_compressed_content(der, octets)

    except (AS2MalformedCMSException, IndexError, ValueError) as e:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, f'Malformed compressed structure ({e})') from None

    try:
        plaintext = zlib.decompress(compressed)
    except zlib.error as e:
        raise AS2ProtocolException(AS2Error.Decompression_Failed, f'Decompression failed ({e})') from None

    out = parse_part(plaintext)
    return out

# ################################################################################################################################
# ################################################################################################################################
