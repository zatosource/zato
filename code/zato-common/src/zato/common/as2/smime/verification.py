# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Verifying an incoming signature - splitting a multipart/signed entity into the bytes the signature
covers, walking the CMS SignedData of RFC 5652 that carries it, and deciding whether the signer
is one we trust.
"""

# stdlib
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime, timezone
from hmac import compare_digest

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import Hash
from cryptography.x509 import load_der_x509_certificate

# Zato
from zato.common.as2.common import AS2Error, AS2MalformedCMSException, AS2ProtocolException, AS2SecurityException
from zato.common.as2.smime.algorithms import Digest_By_Name, Digest_Name_By_OID, OID
from zato.common.as2.smime.der import der_children, der_element_list, element_bytes, element_content, \
    read_content_info, read_der_element, Tag, to_definite_der
from zato.common.as2.smime.part import CRLF, parse_part
from zato.common.typing_ import cast_
from zato.common.util.xml_.core import XMLSecurityException
from zato.common.util.xml_.mime_ import parse_header_parameters, parse_mime_part
from zato.common.util.xml_.trust import validate_certificate_chain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.x509 import Certificate
    from zato.common.as2.smime.der import DERElement
    from zato.common.as2.smime.part import SMIMEPart
    from zato.common.typing_ import anytuple, dtnone
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    anytuple = anytuple
    certificate_list = certificate_list
    dtnone = dtnone
    DERElement = DERElement
    Keystore = Keystore
    RSAPublicKey = RSAPublicKey
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################


# How many parts a multipart/signed body splits into at its boundary - the preamble,
# the signed entity, the signature and the epilogue after the closing delimiter.
_signed_piece_count = 4

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

def _split_signed(body:'bytes', boundary:'str') -> 'anytuple':
    """ Splits a multipart/signed body into the byte-exact signed content and the decoded signature.
    """
    delimiter = b'--' + boundary.encode('ascii')
    pieces = body.split(delimiter)

    piece_count = len(pieces)
    if piece_count < _signed_piece_count:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'multipart/signed does not have its two parts')

    # The signed content is everything between the first two boundary lines, byte-exact -
    # the delimiter's own leading and trailing CRLF do not belong to it.
    content = pieces[1]
    if content.startswith(CRLF):
        content = content[2:]
    if content.endswith(CRLF):
        content = content[:-2]

    # The second part carries the signature, usually base64-encoded.
    signature_headers, signature = parse_mime_part(pieces[2])

    if signature.endswith(CRLF):
        signature = signature[:-2]

    if transfer_encoding := signature_headers.get('content-transfer-encoding'):
        if transfer_encoding.lower() == 'base64':
            signature = b64decode(signature)

    out = (content, signature)
    return out

# ################################################################################################################################

def _read_attribute(der:'bytes', signed_attributes:'DERElement', type_oid:'bytes') -> 'DERElement | None':
    """ Finds the first value of the given attribute among the signed attributes, when it is present.
    """
    for attribute in der_children(der, signed_attributes):
        attribute_children = der_children(der, attribute)
        attribute_type = element_bytes(der, attribute_children[0])

        if attribute_type == type_oid:
            value_set = attribute_children[1]
            values = der_children(der, value_set)

            out = values[0]
            break
    else:
        out = None

    return out

# ################################################################################################################################

def _read_message_digest(der:'bytes', signed_attributes:'DERElement') -> 'bytes':
    """ Finds the message-digest attribute (RFC 5652 section 11.2) among the signed attributes.
    """
    digest_element = _read_attribute(der, signed_attributes, OID.Message_Digest)

    if not digest_element:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Signed attributes do not include a message-digest')

    out = element_content(der, digest_element)
    return out

# ################################################################################################################################

def _read_signing_time(der:'bytes', signed_attributes:'DERElement') -> 'dtnone':
    """ Finds and parses the optional signing-time attribute (RFC 5652 section 11.3).
    """
    time_element = _read_attribute(der, signed_attributes, OID.Signing_Time)

    if not time_element:
        return None

    text = element_content(der, time_element).decode('ascii')

    # UTCTime carries a two-digit year pivoting at 2050, GeneralizedTime a four-digit one.
    if time_element.tag == Tag.UTC_Time:
        parsed = datetime.strptime(text, '%y%m%d%H%M%SZ')
    elif time_element.tag == Tag.Generalized_Time:
        parsed = datetime.strptime(text, '%Y%m%d%H%M%SZ')

    # .. any other encoding is not one RFC 5652 allows for this attribute.
    else:
        return None

    out = parsed.replace(tzinfo=timezone.utc)
    return out

# ################################################################################################################################

def _read_attached_certificates(der:'bytes', children:'der_element_list') -> 'certificate_list':
    """ Loads whichever certificates the sender attached to the signature.
    """

    # Our response to produce
    out:'certificate_list' = []

    for child in children:
        if child.tag == Tag.Context_0:
            for certificate_element in der_children(der, child):
                raw = element_bytes(der, certificate_element)
                certificate = load_der_x509_certificate(raw)
                out.append(certificate)

    return out

# ################################################################################################################################

def _find_signer_certificate(
    signer_issuer:'bytes',
    serial_number:'int',
    attached:'certificate_list',
    keystore:'Keystore',
    accepted_certificates:'certificate_list | None',
    ) -> 'Certificate':
    """ Finds the certificate a signer identifier names, among the ones attached to the signature
    and the configured trust material.

    The certificates field is optional (RFC 5652 section 5.1) - some peers attach nothing and
    count on the verifier holding their certificate already, so the attached ones are searched
    first and the configured trust material after them.
    """
    candidates:'certificate_list' = list(attached)

    if accepted_certificates:
        candidates.extend(accepted_certificates)

    if keystore.peer_signing_certificate:
        candidates.append(keystore.peer_signing_certificate)

    for certificate in candidates:
        issuer_bytes = certificate.issuer.public_bytes()
        if issuer_bytes == signer_issuer:
            if certificate.serial_number == serial_number:
                out = certificate
                break
    else:
        raise AS2SecurityException(
            AS2Error.Authentication_Failed, 'Signer certificate is neither attached to the signature nor configured')

    return out

# ################################################################################################################################

def _check_signer_is_trusted(
    signer_certificate:'Certificate',
    attached:'certificate_list',
    keystore:'Keystore',
    accepted_certificates:'certificate_list | None',
    ) -> 'None':
    """ Decides whether a cryptographically valid signature came from a signer we trust.
    """
    # With a rotation list given, the list itself is the trust decision - the signer must be
    # one of its entries, which during an overlap window means either the old or the new one ..
    if accepted_certificates:

        if signer_certificate not in accepted_certificates:
            raise AS2SecurityException(
                AS2Error.Authentication_Failed, 'Signer certificate is not among the accepted ones')

    # .. without one, the keystore decides - the chain starts at the signer's certificate
    # and any other attached certificates are potential intermediates.
    else:
        chain:'certificate_list' = [signer_certificate]

        for certificate in attached:
            if certificate != signer_certificate:
                chain.append(certificate)

        try:
            validate_certificate_chain(chain, keystore)
        except XMLSecurityException as e:
            detail = str(e)
            raise AS2SecurityException(AS2Error.Authentication_Failed, detail) from None

# ################################################################################################################################

def _verify_signed_data(
    content:'bytes',
    der:'bytes',
    keystore:'Keystore',
    accepted_certificates:'certificate_list | None' = None,
    ) -> 'anytuple':
    """ Walks a CMS SignedData structure per RFC 5652: extracts the signer's certificate
    and signed attributes, checks the content digest and verifies the signature value.
    Returns the signer's certificate and the digest algorithm name.
    """
    content_type_oid, explicit_content = read_content_info(der)

    if content_type_oid != OID.Signed_Data:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'CMS content type is not SignedData')

    signed_data = read_der_element(der, explicit_content.content_offset)
    children = der_children(der, signed_data)

    # Collect the certificates the sender attached ..
    certificates = _read_attached_certificates(der, children)

    # .. and the first signer - AS2 messages have exactly one.
    signer_infos = children[-1]
    signer_list = der_children(der, signer_infos)
    signer_info = signer_list[0]

    fields = der_children(der, signer_info)
    signer_id = fields[1]
    digest_algorithm = fields[2]

    # The signed attributes are optional - when present they carry the content digest.
    signed_attributes = None
    next_index = 3

    if fields[next_index].tag == Tag.Context_0:
        signed_attributes = fields[next_index]
        next_index += 1

    signature_element = fields[next_index + 1]
    signature = element_content(der, signature_element)

    # Resolve the digest algorithm the signature used.
    algorithm_children = der_children(der, digest_algorithm)
    digest_oid = element_bytes(der, algorithm_children[0])

    if not (digest_name := Digest_Name_By_OID.get(digest_oid)):
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Unsupported digest algorithm in SignerInfo')

    hash_class = Digest_By_Name[digest_name]

    # The signer identifier names the certificate by issuer and serial number.
    sid_children = der_children(der, signer_id)
    signer_issuer = element_bytes(der, sid_children[0])
    serial_content = element_content(der, sid_children[1])
    serial_number = int.from_bytes(serial_content, 'big')

    signer_certificate = _find_signer_certificate(
        signer_issuer, serial_number, certificates, keystore, accepted_certificates)

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

        # The attribute is peer-supplied and this comparison decides whether the signature is
        # honored at all, so it must not reveal how far a guessed digest got before diverging.
        if not compare_digest(message_digest, content_digest):
            raise AS2SecurityException(
                AS2Error.Integrity_Check_Failed, 'Content digest does not match the message-digest attribute')

        # For the signature check the IMPLICIT [0] tag reverts to the SET OF it replaced (RFC 5652 section 5.4).
        attributes_encoded = element_bytes(der, signed_attributes)
        signed_bytes = bytes([Tag.Set]) + attributes_encoded[1:]

    # .. without them the signature covers the content directly.
    else:
        signed_bytes = content

    signer_public_key = signer_certificate.public_key()
    public_key = cast_('RSAPublicKey', signer_public_key)

    padding = PKCS1v15()
    hash_algorithm_for_signature = hash_class()

    try:
        public_key.verify(signature, signed_bytes, padding, hash_algorithm_for_signature)
    except InvalidSignature:
        raise AS2SecurityException(AS2Error.Integrity_Check_Failed, 'Signature verification failed') from None

    _check_signer_is_trusted(signer_certificate, certificates, keystore, accepted_certificates)

    out = (signer_certificate, digest_name, signing_time)
    return out

# ################################################################################################################################

def verify(
    part:'SMIMEPart',
    keystore:'Keystore',
    accepted_certificates:'certificate_list | None' = None,
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
        raise AS2ProtocolException(
            AS2Error.Insufficient_Message_Security, f'Expected multipart/signed, received `{media_type}`')

    if not (boundary := parameters.get('boundary')):
        raise AS2ProtocolException(
            AS2Error.Unexpected_Processing_Error, 'multipart/signed without a boundary parameter')

    content, signature_der = _split_signed(part.data, boundary)

    try:
        # Streaming producers encode the signature with BER indefinite lengths.
        signature_der = to_definite_der(signature_der)

        signer_certificate, digest_name, signing_time = _verify_signed_data(
            content, signature_der, keystore, accepted_certificates)
    except (AS2MalformedCMSException, IndexError, ValueError, RecursionError) as e:
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
