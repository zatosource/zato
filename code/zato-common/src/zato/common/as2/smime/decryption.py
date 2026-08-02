# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Decrypting an incoming entity - finding which of our certificate-and-key pairs a message was
encrypted to, recovering the content encryption key and undoing the content encryption itself,
be it CBC per RFC 5652 or AES-GCM per RFC 5083.

Every failure on this path reports the same decryption-failed modifier, with no detail reaching
the wire, because RSA key transport here is PKCS #1 v1.5 and a distinguishable failure is what
a Bleichenbacher-style attack needs.
"""

# stdlib
from typing import NamedTuple

# cryptography
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.modes import CBC

# Zato
from zato.common.as2.common import AS2Error, AS2MalformedCMSException, AS2SecurityException
from zato.common.as2.smime.algorithms import CBC_Block_Size_By_OID, CBC_Class_By_OID, GCM_Key_Size_By_OID, OID
from zato.common.as2.smime.der import der_children, element_bytes, element_content, read_content_info, \
    read_der_element, Tag, to_definite_der
from zato.common.as2.smime.part import parse_part, transfer_decode
from zato.common.typing_ import cast_
from zato.common.util.xml_.keystore import active_decryption_entries

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.x509 import Certificate
    from zato.common.as2.smime.der import DERElement
    from zato.common.as2.smime.part import SMIMEPart
    from zato.common.typing_ import byteslist
    from zato.common.util.xml_.keystore import Keystore
    byteslist = byteslist
    Certificate = Certificate
    DERElement = DERElement
    Keystore = Keystore
    RSAPrivateKey = RSAPrivateKey
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

decryption_candidate_list = list['DecryptionCandidate']


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

def _collect_encrypted_content(der:'bytes', element:'DERElement') -> 'bytes':
    """ Returns the encrypted content octets, joining the chunks of a constructed encoding if needed.
    """
    # The primitive form carries the octets directly ..
    if element.tag == Tag.Context_0_Implicit:
        out = element_content(der, element)
        return out

    # .. the constructed BER form some producers emit splits them into octet string chunks ..
    elif element.tag == Tag.Context_0:
        chunks:'byteslist' = []

        for chunk in der_children(der, element):
            chunk_content = element_content(der, chunk)
            chunks.append(chunk_content)

        out = b''.join(chunks)
        return out

    # .. and any other tag means the structure is not what CMS says it should be.
    else:
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unexpected encoding of the encrypted content')

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
    out:'RecipientMatch | None' = None

    for recipient in der_children(der, recipient_infos):
        fields = der_children(der, recipient)
        recipient_id = fields[1]

        # Only the issuerAndSerialNumber form of recipient identification is used by AS2 peers.
        if recipient_id.tag != Tag.Sequence:
            continue

        rid_children = der_children(der, recipient_id)
        recipient_issuer = element_bytes(der, rid_children[0])
        serial_content = element_content(der, rid_children[1])
        serial_number = int.from_bytes(serial_content, 'big')

        # The first of our pairs this recipient entry names is the one to decrypt with ..
        for candidate in candidates:

            issuer = candidate.certificate.issuer.public_bytes()
            if recipient_issuer != issuer:
                continue

            if serial_number != candidate.certificate.serial_number:
                continue

            encrypted_key = element_content(der, fields[3])
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

    padding = PKCS1v15()

    try:
        out = match.key.decrypt(match.encrypted_key, padding)
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
    enveloped = read_der_element(der, explicit_content.content_offset)
    children = der_children(der, enveloped)

    # Skip past the version and the optional originator info to the recipient set,
    # so that whichever of our certificate-and-key pairs the message was encrypted to
    # is the one that decrypts it.
    next_index = 1
    if children[next_index].tag == Tag.Context_0:
        next_index += 1

    recipient_infos = children[next_index]
    encrypted_content_info = children[next_index + 1]

    content_key = _recover_content_key(der, recipient_infos, keystore)

    # The algorithm identifier carries the IV as its parameter.
    info_children = der_children(der, encrypted_content_info)
    algorithm_identifier = info_children[1]
    encrypted_content = info_children[2]

    algorithm_children = der_children(der, algorithm_identifier)
    algorithm_oid = element_bytes(der, algorithm_children[0])

    if not (cipher_class := CBC_Class_By_OID.get(algorithm_oid)):
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unsupported content encryption algorithm')

    block_size = CBC_Block_Size_By_OID[algorithm_oid]

    initialization_vector = element_content(der, algorithm_children[1])
    ciphertext = _collect_encrypted_content(der, encrypted_content)

    cipher_algorithm = cipher_class(content_key)
    cipher_mode = CBC(initialization_vector)

    cipher = Cipher(cipher_algorithm, cipher_mode)
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    out = _strip_cbc_padding(padded, block_size)
    return out

# ################################################################################################################################

def _decrypt_auth_enveloped(der:'bytes', explicit_content:'DERElement', keystore:'Keystore') -> 'bytes':
    """ Decrypts an AES-GCM AuthEnvelopedData structure per RFC 5083 and RFC 5084.
    """
    auth_enveloped = read_der_element(der, explicit_content.content_offset)
    children = der_children(der, auth_enveloped)

    # Skip past the version and the optional originator info to the recipient set.
    next_index = 1
    if children[next_index].tag == Tag.Context_0:
        next_index += 1

    recipient_infos = children[next_index]
    encrypted_content_info = children[next_index + 1]
    next_index += 2

    # The optional authenticated attributes become additional authenticated data,
    # re-tagged as the SET OF their IMPLICIT [1] tag replaced.
    associated_data = None

    if children[next_index].tag == Tag.Context_1:
        attributes_encoded = element_bytes(der, children[next_index])
        associated_data = bytes([Tag.Set]) + attributes_encoded[1:]
        next_index += 1

    mac = children[next_index]

    content_key = _recover_content_key(der, recipient_infos, keystore)

    info_children = der_children(der, encrypted_content_info)
    algorithm_identifier = info_children[1]
    encrypted_content = info_children[2]

    algorithm_children = der_children(der, algorithm_identifier)
    algorithm_oid = element_bytes(der, algorithm_children[0])

    if not (key_size := GCM_Key_Size_By_OID.get(algorithm_oid)):
        raise AS2SecurityException(AS2Error.Decryption_Failed, 'Unsupported content encryption algorithm')

    content_key_size = len(content_key)

    if content_key_size != key_size:
        raise AS2SecurityException(
            AS2Error.Decryption_Failed, 'Content encryption key size does not match the algorithm')

    # GCMParameters - the nonce and, optionally, an explicit tag length which is not needed
    # because the tag travels in the mac field with its own length.
    parameter_children = der_children(der, algorithm_children[1])
    nonce = element_content(der, parameter_children[0])

    ciphertext = _collect_encrypted_content(der, encrypted_content)
    tag = element_content(der, mac)

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
    der = transfer_decode(part)

    try:
        # Streaming producers encode their envelopes with BER indefinite lengths.
        der = to_definite_der(der)

        content_type_oid, explicit_content = read_content_info(der)

        if content_type_oid == OID.Enveloped_Data:
            plaintext = _decrypt_enveloped(der, explicit_content, keystore)
        elif content_type_oid == OID.Auth_Enveloped_Data:
            plaintext = _decrypt_auth_enveloped(der, explicit_content, keystore)

        # .. any other content type is not something decryption can handle.
        else:
            raise AS2SecurityException(AS2Error.Decryption_Failed, 'CMS content type is not an enveloped structure')

    except (AS2MalformedCMSException, IndexError, ValueError, RecursionError) as e:
        raise AS2SecurityException(AS2Error.Decryption_Failed, f'Malformed encrypted structure ({e})') from None

    out = parse_part(plaintext)
    return out

# ################################################################################################################################
# ################################################################################################################################
