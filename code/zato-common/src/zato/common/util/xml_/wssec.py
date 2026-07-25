# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from datetime import datetime, timezone
from io import BytesIO

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.x509 import BasicConstraints, ExtensionNotFound, KeyUsage
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.serialization import Encoding, load_der_public_key

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import is_string_equal
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, NS, TokenType, Transform
from zato.common.util.xml_.core import new_id, parse_xml, qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.token import build_pkipath, parse_pkipath, parse_x509v3
from zato.common.util.xml_.xmlsec import canonicalize_exclusive, decode_base64, digest_bytes, digest_element, encode_base64, \
    find_by_wsu_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
    from zato.common.typing_ import any_, anydict, bytesnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anydict = anydict
    bytesnone = bytesnone
    Ed25519PrivateKey = Ed25519PrivateKey
    Ed25519PublicKey = Ed25519PublicKey
    RSAPrivateKey = RSAPrivateKey
    RSAPublicKey = RSAPublicKey
    X25519PrivateKey = X25519PrivateKey
    X25519PublicKey = X25519PublicKey

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'

# AES key sizes used by the key derivation and recovery helpers.
_content_key_size_bytes = 16

# The digest algorithms a ds:Reference may declare. The digest is recomputed with SHA-256, so
# this list says which identifiers actually mean SHA-256 - anything else has to be refused
# rather than silently verified against an algorithm the sender did not use.
Accepted_Digest_Methods = {
    Algorithm.SHA256,
}

# The transforms a ds:Reference may declare. Exclusive canonicalization and the enveloped-signature
# transform are applied when verifying element references, the two SwA transforms when verifying
# attachment references. A transform outside this set is refused rather than ignored.
Accepted_Transforms = {
    Algorithm.C14N_Exclusive,
    Transform.Attachment_Ciphertext,
    Transform.Attachment_Content,
    Transform.Enveloped,
}

# The smallest RSA modulus accepted when verifying a signature. 1024-bit RSA is within reach of
# a well-funded attacker, so a signature that verifies under a key that small is not evidence
# of anything - the algorithm identifier says nothing about key size, so it is checked separately.
Minimum_RSA_Key_Size_Bits = 2048

# ################################################################################################################################
# ################################################################################################################################

def add_binary_security_token(security:'any_', keystore:'Keystore', token_type:'str') -> 'str':
    """ Adds the BinarySecurityToken carrying our signing certificate (or the whole chain
    for PKIPath) and returns its wsu:Id for the signature to reference.
    """
    token_id = new_id('X509-')

    # A PKIPath token carries the entire chain, the X509v3 one just the leaf certificate.
    if token_type == TokenType.PKIPath:
        token_bytes = build_pkipath(keystore.signing_certificate_chain)
    else:
        token_bytes = keystore.signing_certificate.public_bytes(Encoding.DER)

    token = etree.SubElement(security, qname(NS.WSSE, 'BinarySecurityToken'))
    token.set('EncodingType', TokenType.Base64Binary)
    token.set('ValueType', token_type)
    token.set(_wsu_id, token_id)
    token.text = encode_base64(token_bytes)

    out = token_id
    return out

# ################################################################################################################################

def add_element_reference(signed_info:'any_', root:'any_', wsu_id:'str') -> 'None':
    """ Adds a ds:Reference over an element identified by its wsu:Id -
    the element is canonicalized exclusively and hashed with SHA-256.
    """
    element = find_by_wsu_id(root, wsu_id)

    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'#{wsu_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Algorithm.C14N_Exclusive)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_element(element)

# ################################################################################################################################

def add_attachment_reference(signed_info:'any_', content_id:'str', data:'bytes') -> 'None':
    """ Adds a ds:Reference over a MIME attachment using the SwA content transform -
    for binary content the transform is simply a SHA-256 hash over the raw part bytes.
    """
    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'cid:{content_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Transform.Attachment_Content)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_bytes(data)

# ################################################################################################################################

def compute_signature_value(signed_info:'any_', keystore:'Keystore', signature_algorithm:'str') -> 'bytes':
    """ Canonicalizes ds:SignedInfo and signs it with our private key.
    """
    canonical = canonicalize_exclusive(signed_info)

    # Ed25519 keys sign the bytes directly, RSA uses PKCS#1 v1.5 with SHA-256
    # as mandated by the rsa-sha256 algorithm identifier.
    if signature_algorithm == Algorithm.Ed25519:
        ed25519_key = cast_('Ed25519PrivateKey', keystore.signing_key)
        out = ed25519_key.sign(canonical)
    else:
        rsa_key = cast_('RSAPrivateKey', keystore.signing_key)
        out = rsa_key.sign(canonical, PKCS1v15(), SHA256())

    return out

# ################################################################################################################################

def add_key_info_token_reference(signature:'any_', token_id:'str', token_type:'str') -> 'None':
    """ Appends the ds:KeyInfo that points a signature back at its BinarySecurityToken,
    so verifiers know which certificate signed the message.
    """
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    reference = etree.SubElement(token_reference, qname(NS.WSSE, 'Reference'))
    reference.set('URI', f'#{token_id}')
    reference.set('ValueType', token_type)

# ################################################################################################################################

def add_saml_token(security:'any_', assertion:'any_') -> 'str':
    """ Places a SAML 2.0 assertion in the security header as the message's token,
    per the SAML Token Profile 1.1 - security token services such as the Australian
    SBR's VANguard issue these instead of certificates travelling as binary tokens.
    Accepts the assertion as bytes or as an element and returns its ID for the
    signature's key identifier to point at.
    """
    if assertion is None:
        raise XMLSecurityException('No SAML assertion to add as a token')

    if isinstance(assertion, bytes):
        assertion = parse_xml(assertion)

    assertion_id = assertion.get('ID')

    if not assertion_id:
        raise XMLSecurityException('SAML assertion has no ID')

    security.append(assertion)

    out = assertion_id
    return out

# ################################################################################################################################

def add_key_info_saml_reference(signature:'any_', assertion_id:'str') -> 'None':
    """ Appends the ds:KeyInfo that points a signature at a SAML assertion -
    a SecurityTokenReference whose KeyIdentifier carries the assertion's ID,
    per the SAML Token Profile 1.1.
    """
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))

    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    token_reference.set(qname(NS.WSSE11, 'TokenType'), TokenType.SAML20)

    key_identifier = etree.SubElement(token_reference, qname(NS.WSSE, 'KeyIdentifier'))
    key_identifier.set('ValueType', TokenType.SAML_ID)
    key_identifier.text = assertion_id

# ################################################################################################################################
# ################################################################################################################################

def build_id_index(root:'any_') -> 'anydict':
    """ Walks a document once and returns every id it carries, as wsu:Id or as a plain Id,
    mapped to the list of elements carrying it. One walk replaces the per-reference walk
    a signature with several references would otherwise cost, and keeping the full list
    rather than the first match is what lets a caller reject an ambiguous id.
    """
    out = {}

    for element in root.iter():

        # An element may carry the same value under both attribute names, which is not
        # a duplicate, so the two are collapsed before being recorded.
        element_ids = set()

        wsu_id = element.get(_wsu_id)
        if wsu_id is not None:
            element_ids.add(wsu_id)

        plain_id = element.get('Id')
        if plain_id is not None:
            element_ids.add(plain_id)

        for element_id in element_ids:
            if element_id in out:
                out[element_id].append(element)
            else:
                out[element_id] = [element]

    return out

# ################################################################################################################################

def resolve_reference_id(id_index:'anydict', element_id:'str') -> 'any_':
    """ Returns the one element a signature reference names. Two elements carrying the same
    id is the XML signature wrapping attack - the attacker leaves the signed copy somewhere
    the verifier will find it and puts the payload it wants processed where the application
    will find it. Resolving to the first match in document order is what makes that work,
    so an ambiguous id is refused outright rather than resolved.
    """
    if element_id not in id_index:
        raise XMLSecurityException(f'Signed element `{element_id}` is missing')

    matches = id_index[element_id]

    if len(matches) > 1:
        raise XMLSecurityException(f'Id `{element_id}` is carried by {len(matches)} elements')

    out = matches[0]
    return out

# ################################################################################################################################

def find_by_any_id(root:'any_', element_id:'str') -> 'any_':
    """ Returns the element carrying the given id either as wsu:Id or as a plain Id attribute.
    Callers verifying a signature must use build_id_index and resolve_reference_id instead,
    which reject an ambiguous id rather than returning the first match.
    """
    out = find_by_wsu_id(root, element_id)

    if out is None:
        for element in root.iter():
            if element.get('Id') == element_id:
                out = element
                break

    return out

# ################################################################################################################################

def canonicalize_for_reference(element:'any_', transform:'any_') -> 'bytes':
    """ Canonicalizes an element the way its ds:Transform element prescribes,
    honoring an InclusiveNamespaces PrefixList when one is present.
    """
    inclusive_prefixes = None

    if transform is not None:
        inclusive_namespaces = transform.find(f'{{{Algorithm.C14N_Exclusive}}}InclusiveNamespaces')
        if inclusive_namespaces is not None:
            if prefix_list := inclusive_namespaces.get('PrefixList'):
                inclusive_prefixes = prefix_list.split()

    buffer = BytesIO()
    tree = etree.ElementTree(element)
    tree.write_c14n(buffer, exclusive=True, with_comments=False, inclusive_ns_prefixes=inclusive_prefixes)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def find_part(parts:'part_list', content_id:'str') -> 'any_':
    """ Returns the MIME part matching a cid: reference, or None.
    """
    for part in parts:
        if part.content_id == content_id:
            out = part
            break
    else:
        out = None

    return out

# ################################################################################################################################

def _check_digest_method(reference:'any_', uri:'str') -> 'None':
    """ Rejects a ds:DigestMethod this implementation does not recompute. The digest is always
    recomputed with SHA-256, so accepting a reference that declares anything else would mean
    verifying against an algorithm the sender did not use.
    """
    digest_method = reference.find(qname(NS.DS, 'DigestMethod'))

    if digest_method is None:
        raise XMLSecurityException(f'Reference `{uri}` has no DigestMethod')

    algorithm = digest_method.get('Algorithm')

    if algorithm not in Accepted_Digest_Methods:
        raise XMLSecurityUnsupportedAlgorithm(f'Unsupported digest algorithm `{algorithm}` on reference `{uri}`')

# ################################################################################################################################

def _check_transforms(transforms:'any_', uri:'str') -> 'None':
    """ Rejects a ds:Transform this implementation does not apply. An unrecognised transform was
    previously ignored, which meant the digest was recomputed over a different shape from the one
    the sender hashed - either the reference then fails for the wrong reason or, where the
    transform is a no-op on this document, it passes while the declared processing never happened.
    """
    if transforms is None:
        return

    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        algorithm = transform.get('Algorithm')

        if algorithm not in Accepted_Transforms:
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported transform `{algorithm}` on reference `{uri}`')

# ################################################################################################################################

def verify_one_reference(reference:'any_', envelope:'any_', parts:'part_list', id_index:'anydict') -> 'any_':
    """ Recomputes the digest of one ds:Reference and compares it with the declared value.
    Returns the element the reference covers, or None for an attachment reference, so the
    caller can check that what it goes on to process is what was actually verified.
    """
    uri = reference.get('URI') or ''

    digest_value_element = reference.find(qname(NS.DS, 'DigestValue'))

    if digest_value_element is None:
        raise XMLSecurityException(f'Reference `{uri}` has no DigestValue')

    expected_digest = ''.join((digest_value_element.text or '').split())

    _check_digest_method(reference, uri)

    transform = None
    transforms = reference.find(qname(NS.DS, 'Transforms'))
    if transforms is not None:
        transform = transforms.find(qname(NS.DS, 'Transform'))

    _check_transforms(transforms, uri)

    # An attachment reference hashes the raw bytes of the MIME part ..
    if uri.startswith('cid:'):
        content_id = uri[4:]
        part = find_part(parts, content_id)

        if part is None:
            raise XMLSecurityException(f'Signed part `{content_id}` is missing')

        actual_digest = digest_bytes(part.data)
        out = None

    # .. an element reference canonicalizes the element and hashes that.
    else:
        element_id = uri[1:]

        # This raises when the id names no element or more than one.
        element = resolve_reference_id(id_index, element_id)

        # What the caller processes is the element as it stands in the document, so that is what
        # is reported back even when the digest was taken over a pruned copy of it.
        out = element

        # The enveloped-signature transform means the digest was computed
        # with the ds:Signature element itself removed from the picture.
        if _has_enveloped_transform(transforms):
            element = _without_signature(element)

        canonical = canonicalize_for_reference(element, transform)
        actual_digest = digest_bytes(canonical)

    if not is_string_equal(actual_digest, expected_digest):
        raise XMLSecurityException(f'Digest mismatch for reference `{uri}`')

    return out

# ################################################################################################################################

def _has_enveloped_transform(transforms:'any_') -> 'bool':
    """ Returns True if a ds:Transforms element carries the enveloped-signature transform.
    """
    if transforms is None:
        return False

    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        if transform.get('Algorithm') == Transform.Enveloped:
            return True

    return False

# ################################################################################################################################

def _without_signature(element:'any_') -> 'any_':
    """ Returns a copy of an element with its immediate ds:Signature child removed,
    which is how the enveloped-signature transform is applied.
    """
    # deepcopy gives a detached copy that is safe to prune, without the serialize-and-reparse
    # round trip this used to do once per reference - that cost a full parse per reference and
    # was one more place where untrusted XML met a parser.
    out = deepcopy(element)

    signature = out.find(qname(NS.DS, 'Signature'))
    if signature is not None:
        out.remove(signature)

    return out

# ################################################################################################################################

def extract_signer_chain(signature:'any_', security:'any_') -> 'certificate_list':
    """ Resolves the signature's key info to the signer's certificate chain, leaf first -
    either out of the referenced BinarySecurityToken or, for signatures keyed by
    a SAML assertion, out of the assertion's holder-of-key confirmation.
    """
    key_info = signature.find(qname(NS.DS, 'KeyInfo'))
    token_reference = key_info.find(qname(NS.WSSE, 'SecurityTokenReference'))

    if token_reference is None:
        raise XMLSecurityException('Signature has no SecurityTokenReference')

    reference = token_reference.find(qname(NS.WSSE, 'Reference'))

    if reference is None:

        # With no direct reference, the token may be a SAML assertion named by its ID.
        key_identifier = token_reference.find(qname(NS.WSSE, 'KeyIdentifier'))

        if key_identifier is not None and key_identifier.get('ValueType') == TokenType.SAML_ID:
            out = _extract_saml_signer_chain(security, key_identifier.text or '')
            return out

        raise XMLSecurityException('SecurityTokenReference has no Reference')

    token_id = (reference.get('URI') or '')[1:]
    token = find_by_wsu_id(security, token_id)

    if token is None:
        raise XMLSecurityException(f'BinarySecurityToken `{token_id}` is missing')

    token_bytes = decode_base64(token.text or '')
    value_type = token.get('ValueType')

    # A PKIPath token carries the whole chain, an X509v3 one just the leaf.
    if value_type == TokenType.PKIPath:
        out = parse_pkipath(token_bytes)
    else:
        leaf = parse_x509v3(token_bytes)
        out = [leaf]

    return out

# ################################################################################################################################

def _extract_saml_signer_chain(security:'any_', assertion_id:'str') -> 'certificate_list':
    """ Returns the signer's certificate out of a SAML assertion's holder-of-key
    subject confirmation - the assertion vouches that whoever holds the matching
    private key is the subject, so that certificate is what verifies the signature.
    """
    assertion = None

    for candidate in security.findall(qname(NS.SAML2, 'Assertion')):
        if candidate.get('ID') == assertion_id:
            assertion = candidate
            break

    if assertion is None:
        raise XMLSecurityException(f'SAML assertion `{assertion_id}` is missing')

    confirmation = assertion.find(f'.//{qname(NS.SAML2, "SubjectConfirmation")}')

    certificate_element = None
    if confirmation is not None:
        certificate_element = confirmation.find(f'.//{qname(NS.DS, "X509Certificate")}')

    if certificate_element is None:
        raise XMLSecurityException(f'SAML assertion `{assertion_id}` carries no signer certificate')

    leaf = parse_x509v3(decode_base64(certificate_element.text or ''))

    out = [leaf]
    return out

# ################################################################################################################################

def _check_validity_period(certificate:'any_', now:'datetime') -> 'None':
    """ Rejects a certificate outside its validity period.
    """
    if now < certificate.not_valid_before_utc:
        raise XMLSecurityException(f'Certificate `{certificate.subject}` is not yet valid')

    if now > certificate.not_valid_after_utc:
        raise XMLSecurityException(f'Certificate `{certificate.subject}` has expired')

# ################################################################################################################################

def _check_is_certificate_authority(certificate:'any_') -> 'None':
    """ Rejects an issuer that is not marked as a certificate authority. Without this check any
    leaf certificate issued by a trusted CA can be used to issue further certificates, so a
    holder of one ordinary certificate could mint a chain for any identity it likes.
    """
    try:
        basic_constraints = certificate.extensions.get_extension_for_class(BasicConstraints)
    except ExtensionNotFound:
        raise XMLSecurityException(f'Issuer `{certificate.subject}` carries no basicConstraints extension')

    if not basic_constraints.value.ca:
        raise XMLSecurityException(f'Issuer `{certificate.subject}` is not a certificate authority')

# ################################################################################################################################

def _check_key_usage(certificate:'any_', usage_name:'str') -> 'None':
    """ Rejects a certificate whose keyUsage extension excludes the use it is being put to.
    A certificate with the extension absent is unconstrained, which is what the specification
    says, so only an extension that is present and says no is a failure.
    """
    try:
        key_usage = certificate.extensions.get_extension_for_class(KeyUsage)
    except ExtensionNotFound:
        return

    if not getattr(key_usage.value, usage_name):
        raise XMLSecurityException(f'Certificate `{certificate.subject}` is not permitted to {usage_name.replace("_", " ")}')

# ################################################################################################################################

def validate_certificate_chain(chain:'certificate_list', keystore:'Keystore') -> 'None':
    """ Establishes trust in the signer's certificate. With trust anchors configured,
    the chain must lead from the leaf to one of them with valid signatures and periods.
    Without anchors, the leaf must equal the pinned peer certificate.
    """
    now = datetime.now(timezone.utc)
    leaf = chain[0]

    # Trust has to come from something the operator configured. The signer's certificate arrives
    # inside the message being verified, so with neither anchors nor a pinned certificate there is
    # nothing to check it against and any self-signed certificate an attacker generates would be
    # accepted. Returning without validating here is the difference between a signature that
    # proves who sent the message and one that proves only that somebody signed something.
    if not keystore.trust_anchors:

        pinned = keystore.peer_signing_certificate

        if not pinned:
            raise XMLSecurityException('No trust anchors and no pinned peer certificate are configured')

        if leaf != pinned:
            raise XMLSecurityException('Signer certificate does not match the pinned one')

        # A pinned certificate still expires - the anchor-walking branch below checks this for
        # every certificate it sees and the pinned branch has to do the same.
        _check_validity_period(leaf, now)
        _check_key_usage(leaf, 'digital_signature')

        return

    # Walk from the leaf upwards - each certificate must be within its validity period
    # and signed either by the next chain element or directly by a trust anchor.
    anchors_by_subject = {}
    for anchor in keystore.trust_anchors:
        anchors_by_subject[anchor.subject.rfc4514_string()] = anchor

    _check_key_usage(leaf, 'digital_signature')

    current = leaf
    remaining = chain[1:]

    while True:
        _check_validity_period(current, now)

        issuer_name = current.issuer.rfc4514_string()

        # The current certificate chains directly to a trust anchor - verify and we are done.
        if anchor := anchors_by_subject.get(issuer_name):
            _check_validity_period(anchor, now)
            _check_is_certificate_authority(anchor)
            _check_key_usage(anchor, 'key_cert_sign')
            current.verify_directly_issued_by(anchor)
            break

        # Otherwise the next chain element must be the issuer.
        if not remaining:
            raise XMLSecurityException(f'No trust anchor found for issuer `{issuer_name}`')

        issuer = remaining[0]
        remaining = remaining[1:]

        _check_is_certificate_authority(issuer)
        _check_key_usage(issuer, 'key_cert_sign')

        current.verify_directly_issued_by(issuer)
        current = issuer

# ################################################################################################################################

def verify_signature_value(signature:'any_', chain:'certificate_list') -> 'None':
    """ Canonicalizes ds:SignedInfo and checks the signature value against the leaf public key.
    """
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    signature_method = signed_info.find(qname(NS.DS, 'SignatureMethod'))
    algorithm = signature_method.get('Algorithm')

    # The canonicalization of SignedInfo may carry its own PrefixList.
    canonicalization_method = signed_info.find(qname(NS.DS, 'CanonicalizationMethod'))
    canonical = canonicalize_for_reference(signed_info, canonicalization_method)

    signature_value_element = signature.find(qname(NS.DS, 'SignatureValue'))
    signature_bytes = decode_base64(signature_value_element.text or '')

    leaf = chain[0]
    public_key = leaf.public_key()

    try:
        if algorithm == Algorithm.Ed25519:
            ed25519_key = cast_('Ed25519PublicKey', public_key)
            ed25519_key.verify(signature_bytes, canonical)
        elif algorithm == Algorithm.RSA_SHA256:
            rsa_key = cast_('RSAPublicKey', public_key)

            # A signature under a key small enough to factor verifies just as cleanly as one
            # under a strong key, so the size is checked before the signature is believed.
            if rsa_key.key_size < Minimum_RSA_Key_Size_Bits:
                raise XMLSecurityException(
                    f'RSA key of {rsa_key.key_size} bits is below the minimum of {Minimum_RSA_Key_Size_Bits}')

            rsa_key.verify(signature_bytes, canonical, PKCS1v15(), SHA256())
        else:
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported signature algorithm `{algorithm}`')
    except InvalidSignature:
        raise XMLSecurityException('Signature value does not verify')

# ################################################################################################################################
# ################################################################################################################################

def derive_key_encryption_key(shared_secret:'bytes', info:'bytes') -> 'bytes':
    """ Derives an AES key-wrapping key from an X25519 shared secret with HKDF-SHA256.
    """
    hkdf = HKDF(algorithm=SHA256(), length=_content_key_size_bytes, salt=None, info=info)

    out = hkdf.derive(shared_secret)
    return out

# ################################################################################################################################

def recover_content_key(encrypted_key:'any_', keystore:'Keystore', hkdf_info:'bytesnone'=None) -> 'bytes':
    """ Recovers the AES content key from an xenc:EncryptedKey, whichever
    of the two supported key transport mechanisms protected it.
    """
    encryption_method = encrypted_key.find(qname(NS.XENC, 'EncryptionMethod'))
    algorithm = encryption_method.get('Algorithm')

    cipher_data = encrypted_key.find(qname(NS.XENC, 'CipherData'))
    cipher_value = cipher_data.find(qname(NS.XENC, 'CipherValue'))
    wrapped_key = decode_base64(cipher_value.text or '')

    # RSA-OAEP key transport - our RSA key decrypts the wrapped key directly.
    if algorithm == Algorithm.RSA_OAEP:
        oaep_padding = OAEP(mgf=MGF1(SHA256()), algorithm=SHA256(), label=None)
        rsa_key = cast_('RSAPrivateKey', keystore.decryption_key)

        # Every failure reason collapses into the same message. A padding failure that reads
        # differently from a length failure is what a Bleichenbacher-style oracle needs, so the
        # AES-GCM path already does this and the RSA path has to match it.
        try:
            out = rsa_key.decrypt(wrapped_key, oaep_padding)
        except Exception:
            raise XMLSecurityException('Could not recover the content key')

        return out

    # AES key wrap after X25519 agreement - rebuild the shared secret
    # from the sender's ephemeral public key, derive the wrapping key, unwrap.
    if algorithm == Algorithm.AES128_KeyWrap:

        # The derivation info string is protocol-specific, so without one this mechanism is unavailable.
        if hkdf_info is None:
            raise XMLSecurityUnsupportedAlgorithm('Key agreement requires an HKDF info string')

        key_info = encrypted_key.find(qname(NS.DS, 'KeyInfo'))
        agreement_method = key_info.find(qname(NS.XENC, 'AgreementMethod'))
        originator = agreement_method.find(qname(NS.XENC, 'OriginatorKeyInfo'))
        key_value = originator.find(qname(NS.DS, 'KeyValue'))
        der_key_value = key_value.find(qname(NS.XMLDSIG11, 'DEREncodedKeyValue'))

        ephemeral_bytes = decode_base64(der_key_value.text or '')
        ephemeral_public_key = cast_('X25519PublicKey', load_der_public_key(ephemeral_bytes))

        x25519_key = cast_('X25519PrivateKey', keystore.decryption_key)
        shared_secret = x25519_key.exchange(ephemeral_public_key)
        key_encryption_key = derive_key_encryption_key(shared_secret, hkdf_info)

        out = aes_key_unwrap(key_encryption_key, wrapped_key)
        return out

    raise XMLSecurityUnsupportedAlgorithm(f'Unsupported key transport algorithm `{algorithm}`')

# ################################################################################################################################
# ################################################################################################################################
