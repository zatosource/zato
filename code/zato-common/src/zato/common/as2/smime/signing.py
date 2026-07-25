# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Signing an outgoing entity - the detached multipart/signed structure of RFC 8551 section 3.5.3,
with the CMS SignedData of RFC 5652 riding in its second part.
"""

# stdlib
from datetime import datetime, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import Hash, SHA1
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7Options, PKCS7SignatureBuilder

# Zato
from zato.common.as2.common import Default, DigestAlgorithm
from zato.common.as2.smime.algorithms import Digest_By_Name, OID
from zato.common.as2.smime.der import Der_Null, encode_der, encode_der_integer, encode_der_octet_string, Tag
from zato.common.as2.smime.mic import normalize_micalg
from zato.common.as2.smime.part import CRLF, encode_base64_lines, new_boundary, new_part, serialize_part
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7HashTypes
    from zato.common.as2.smime.part import SMIMEPart
    from zato.common.typing_ import byteslist
    from zato.common.util.xml_.keystore import Keystore
    byteslist = byteslist
    Keystore = Keystore
    PKCS7HashTypes = PKCS7HashTypes
    RSAPrivateKey = RSAPrivateKey
    SMIMEPart = SMIMEPart

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
    content_type_set = encode_der(Tag.Set, OID.Data)
    content_type_attribute = encode_der(Tag.Sequence, OID.Content_Type_Attr + content_type_set)

    digest_octets = encode_der_octet_string(content_digest)
    digest_set = encode_der(Tag.Set, digest_octets)
    message_digest_attribute = encode_der(Tag.Sequence, OID.Message_Digest + digest_set)

    now = datetime.now(timezone.utc)
    time_text = now.strftime('%y%m%d%H%M%SZ').encode('ascii')
    time_element = encode_der(Tag.UTC_Time, time_text)
    time_set = encode_der(Tag.Set, time_element)
    signing_time_attribute = encode_der(Tag.Sequence, OID.Signing_Time + time_set)

    # .. in the ascending encoded order a DER SET OF requires.
    attributes = sorted([content_type_attribute, message_digest_attribute, signing_time_attribute])
    attributes_content = b''.join(attributes)

    # The signature covers the attributes under their SET OF tag,
    # while SignerInfo carries them under IMPLICIT [0].
    signed_bytes = encode_der(Tag.Set, attributes_content)
    padding = PKCS1v15()
    signature_hash = SHA1()
    signature = signing_key.sign(signed_bytes, padding, signature_hash)

    digest_algorithm = encode_der(Tag.Sequence, OID.SHA1 + Der_Null)
    signature_algorithm = encode_der(Tag.Sequence, OID.RSA_Encryption + Der_Null)

    issuer = signing_certificate.issuer.public_bytes()
    serial = encode_der_integer(signing_certificate.serial_number)
    issuer_and_serial = encode_der(Tag.Sequence, issuer + serial)

    signer_version = encode_der_integer(1)
    implicit_attributes = encode_der(Tag.Context_0, attributes_content)
    signature_octets = encode_der_octet_string(signature)

    signer_info = encode_der(Tag.Sequence,
        signer_version
        + issuer_and_serial
        + digest_algorithm
        + implicit_attributes
        + signature_algorithm
        + signature_octets)

    # The whole chain rides along so receivers can build a path to their trust anchors.
    certificates = b''

    for certificate in keystore.signing_certificate_chain:
        certificates += certificate.public_bytes(Encoding.DER)

    # Detached signing leaves the encapsulated content info without any content.
    encapsulated = encode_der(Tag.Sequence, OID.Data)

    version = encode_der_integer(1)
    digest_algorithms = encode_der(Tag.Set, digest_algorithm)
    implicit_certificates = encode_der(Tag.Context_0, certificates)
    signer_infos = encode_der(Tag.Set, signer_info)

    signed_data = encode_der(Tag.Sequence,
        version
        + digest_algorithms
        + encapsulated
        + implicit_certificates
        + signer_infos)

    explicit_content = encode_der(Tag.Context_0, signed_data)

    out = encode_der(Tag.Sequence, OID.Signed_Data + explicit_content)
    return out

# ################################################################################################################################

def sign(
    part:'SMIMEPart',
    keystore:'Keystore',
    digest_algorithm:'str' = Default.Digest_Algorithm,
    prevent_canonicalization:'bool' = False,
    ) -> 'SMIMEPart':
    """ Wraps an entity in a detached multipart/signed structure per RFC 8551 section 3.5.3,
    with the CMS signature riding in an application/pkcs7-signature part.
    """
    algorithm = normalize_micalg(digest_algorithm)
    hash_class = Digest_By_Name[algorithm]

    # The signature covers the complete inner MIME entity - headers and content alike.
    content = serialize_part(part, prevent_canonicalization)

    # SHA-1 for partners that require it is built in-house because the library refuses it ..
    if algorithm == DigestAlgorithm.SHA1:
        signature = _build_sha1_signed_data(content, keystore)

    # .. everything current goes through the library's builder.
    else:
        signing_key = cast_('RSAPrivateKey', keystore.signing_key)
        hash_instance = hash_class()
        hash_algorithm = cast_('PKCS7HashTypes', hash_instance)

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
    boundary = new_boundary()

    delimiter = f'--{boundary}'.encode('ascii')
    closing_delimiter = f'--{boundary}--'.encode('ascii')

    chunks:'byteslist' = []
    chunks.append(delimiter)
    chunks.append(content)
    chunks.append(delimiter)
    chunks.append(b'Content-Type: application/pkcs7-signature; name="smime.p7s"')
    chunks.append(b'Content-Transfer-Encoding: base64')
    chunks.append(b'Content-Disposition: attachment; filename="smime.p7s"')
    chunks.append(b'')
    chunks.append(encoded_signature)
    chunks.append(closing_delimiter)
    chunks.append(b'')

    body = CRLF.join(chunks)

    protocol = 'protocol="application/pkcs7-signature"'
    content_type = f'multipart/signed; {protocol}; micalg={algorithm}; boundary="{boundary}"'

    out = new_part(body, content_type)
    return out

# ################################################################################################################################
# ################################################################################################################################
