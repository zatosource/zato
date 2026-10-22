# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from hashlib import new as new_hash

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.hashes import SHA1, SHA256
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import load_der_x509_certificate

# lxml
from lxml.etree import Element, SubElement

# Zato
from zato.common.b2b.common.limits import Limits
from zato.common.b2b.ebms2.common import Actor, EbMS2Exception, EbMS2SecurityException, ErrorCode, NS
from zato.common.b2b.ebms2.xml_ import SOAP_Actor
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.xmlsec import canonicalize_inclusive, decode_base64, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.typing_ import any_, anylist, intlist, strset
    from zato.common.util.xml_.keystore import certificate_list
    any_ = any_
    anylist = anylist
    Certificate = Certificate
    certificate_list = certificate_list
    intlist = intlist
    LocalKeys = LocalKeys
    payload_list = payload_list
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

class SignatureAlgorithm:
    RSA_SHA1   = 'http://www.w3.org/2000/09/xmldsig#rsa-sha1'
    RSA_SHA256 = Algorithm.RSA_SHA256

class DigestAlgorithm:
    SHA1   = 'http://www.w3.org/2000/09/xmldsig#sha1'
    SHA256 = Algorithm.SHA256

# The XPath filter transform of the ebMS 2.0 signature profile.
XPath_Transform = 'http://www.w3.org/TR/1999/REC-xpath-19991116'

# The prefix the expression of the XPath filter binds to the SOAP envelope namespace.
_xpath_soap_prefix = 'SOAP'

# The XPath filter that leaves out the header blocks addressed to the next message service handler,
# which may change them in transit.
_xpath_next_msh = f'ancestor-or-self::node()[@{_xpath_soap_prefix}:actor="{Actor.Next_MSH}"]'
_xpath_soap_next = f'ancestor-or-self::node()[@{_xpath_soap_prefix}:actor="{Actor.SOAP_Next}"]'
XPath_Expression = f'not({_xpath_next_msh} | {_xpath_soap_next})'

# ################################################################################################################################

# The hash each signature algorithm signs with.
_signature_hashes = {
    SignatureAlgorithm.RSA_SHA1:   SHA1,
    SignatureAlgorithm.RSA_SHA256: SHA256,
}

# The hashlib name of each digest algorithm.
_digest_names = {
    DigestAlgorithm.SHA1:   'sha1',
    DigestAlgorithm.SHA256: 'sha256',
}

# The short names of the algorithms that agreements may use instead of their URIs.
_signature_algorithm_names = {
    'rsa-sha1':   SignatureAlgorithm.RSA_SHA1,
    'rsa-sha256': SignatureAlgorithm.RSA_SHA256,
    SignatureAlgorithm.RSA_SHA1:   SignatureAlgorithm.RSA_SHA1,
    SignatureAlgorithm.RSA_SHA256: SignatureAlgorithm.RSA_SHA256,
}

_digest_algorithm_names = {
    'sha1':    DigestAlgorithm.SHA1,
    'sha-1':   DigestAlgorithm.SHA1,
    'sha256':  DigestAlgorithm.SHA256,
    'sha-256': DigestAlgorithm.SHA256,
    DigestAlgorithm.SHA1:   DigestAlgorithm.SHA1,
    DigestAlgorithm.SHA256: DigestAlgorithm.SHA256,
}

# The transforms a reference to the envelope may have.
_envelope_transforms:'strset' = {Transform.Enveloped, XPath_Transform, Algorithm.C14N}

# The actors whose header blocks the XPath filter leaves out.
_excluded_actors:'strset' = {Actor.Next_MSH, Actor.SOAP_Next}

_ds_nsmap = {'ds': NS.DS}
_xpath_nsmap = {_xpath_soap_prefix: NS.SOAP}

_ds_signature = qname(NS.DS, 'Signature')
_ds_signed_info = qname(NS.DS, 'SignedInfo')
_ds_canonicalization_method = qname(NS.DS, 'CanonicalizationMethod')
_ds_signature_method = qname(NS.DS, 'SignatureMethod')
_ds_reference = qname(NS.DS, 'Reference')
_ds_transforms = qname(NS.DS, 'Transforms')
_ds_transform = qname(NS.DS, 'Transform')
_ds_xpath = qname(NS.DS, 'XPath')
_ds_digest_method = qname(NS.DS, 'DigestMethod')
_ds_digest_value = qname(NS.DS, 'DigestValue')
_ds_signature_value = qname(NS.DS, 'SignatureValue')
_ds_key_info = qname(NS.DS, 'KeyInfo')
_ds_x509_data = qname(NS.DS, 'X509Data')
_ds_x509_certificate = qname(NS.DS, 'X509Certificate')

_soap_header = qname(NS.SOAP, 'Header')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VerifiedSignature:
    """ What a verified signature covers and who made it.
    """
    # Copies of the ds:Reference elements of the SignedInfo, which a signed acknowledgment echoes.
    references: 'anylist'

    # The certificate of the key that made the signature, and the chain that came with it.
    certificate: 'Certificate'
    chain:       'certificate_list'

# ################################################################################################################################
# ################################################################################################################################

def resolve_signature_algorithm(name:'str') -> 'str':
    """ Returns the URI of a signature algorithm an agreement names.
    """
    lower_name = name.lower()

    if not (out := _signature_algorithm_names.get(lower_name)):
        out = _signature_algorithm_names.get(name)

    if not out:
        raise EbMS2Exception(ErrorCode.Not_Supported, f'Signature algorithm `{name}` is not supported')

    return out

# ################################################################################################################################

def resolve_digest_algorithm(name:'str') -> 'str':
    """ Returns the URI of a digest algorithm an agreement names.
    """
    lower_name = name.lower()

    if not (out := _digest_algorithm_names.get(lower_name)):
        out = _digest_algorithm_names.get(name)

    if not out:
        raise EbMS2Exception(ErrorCode.Not_Supported, f'Digest algorithm `{name}` is not supported')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _digest(data:'bytes', digest_algorithm:'str') -> 'str':
    """ Returns the base64 digest of the given bytes.
    """
    hash_name = _digest_names[digest_algorithm]
    digest = new_hash(hash_name, data)
    digest_bytes = digest.digest()

    out = encode_base64(digest_bytes)
    return out

# ################################################################################################################################

def _index_path(element:'any_') -> 'intlist':
    """ Returns the position of an element as the indexes of it and its ancestors under their parents.
    """
    out:'intlist' = []

    while (parent := element.getparent()) is not None:
        index = parent.index(element)
        out.insert(0, index)
        element = parent

    return out

# ################################################################################################################################

def _follow_path(root:'any_', path:'intlist') -> 'any_':
    out = root

    for index in path:
        out = out[index]

    return out

# ################################################################################################################################

def _remove(element:'any_') -> 'None':
    """ Removes an element and everything under it, leaving the text that follows it in place.
    """
    parent = element.getparent()

    if tail := element.tail:

        if (previous := element.getprevious()) is not None:
            if previous.tail is None:
                previous.tail = tail
            else:
                previous.tail = previous.tail + tail

        else:
            if parent.text is None:
                parent.text = tail
            else:
                parent.text = parent.text + tail

    parent.remove(element)

# ################################################################################################################################

def canonicalize_envelope(envelope:'any_', signature:'any_', *, apply_xpath_filter:'bool'=True) -> 'bytes':
    """ Returns the canonical form of the envelope that the reference with an empty URI covers - without the signature
    being computed, which is the enveloped-signature transform, and without the header blocks addressed
    to the next message service handler, which is the XPath filter transform.
    """
    copy = deepcopy(envelope)

    # The signature is in the document when it is being verified, but not yet when it is being computed ..
    if signature is not None:
        path = _index_path(signature)
        signature_copy = _follow_path(copy, path)
        _remove(signature_copy)

    # .. and the header blocks that intermediaries may change are left out.
    if apply_xpath_filter:

        excluded = []

        for element in copy.iter():
            if not isinstance(element.tag, str):
                continue
            if element.get(SOAP_Actor) in _excluded_actors:
                excluded.append(element)

        # An excluded element under another excluded element goes away with its ancestor.
        for element in excluded:
            if element.getparent() is not None:
                _remove(element)

    out = canonicalize_inclusive(copy)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _add_reference(signed_info:'any_', uri:'str', digest_algorithm:'str', digest_value:'str') -> 'any_':

    out = SubElement(signed_info, _ds_reference)
    out.set('URI', uri)

    digest_method = SubElement(out, _ds_digest_method)
    digest_method.set('Algorithm', digest_algorithm)

    digest_value_element = SubElement(out, _ds_digest_value)
    digest_value_element.text = digest_value

    return out

# ################################################################################################################################

def sign_envelope(
    envelope:'any_',
    payloads:'payload_list',
    local_keys:'LocalKeys',
    signature_algorithm:'str',
    digest_algorithm:'str',
    ) -> 'any_':
    """ Signs an envelope and its payloads with the ebMS 2.0 XMLDSig profile, placing the ds:Signature in the SOAP Header.
    """
    signing_key = local_keys.signing_key

    if not isinstance(signing_key, RSAPrivateKey):
        raise EbMS2Exception(ErrorCode.Not_Supported, 'The signing key is not an RSA key')

    hash_class = _signature_hashes[signature_algorithm]

    # The envelope is digested before the signature goes into it, which is what the enveloped transform yields.
    canonical_envelope = canonicalize_envelope(envelope, None)
    envelope_digest = _digest(canonical_envelope, digest_algorithm)

    out = _new_signature(envelope)

    signed_info = SubElement(out, _ds_signed_info)

    canonicalization_method = SubElement(signed_info, _ds_canonicalization_method)
    canonicalization_method.set('Algorithm', Algorithm.C14N)

    signature_method = SubElement(signed_info, _ds_signature_method)
    signature_method.set('Algorithm', signature_algorithm)

    envelope_reference = _add_reference(signed_info, '', digest_algorithm, envelope_digest)

    # The transforms precede the digest method in a reference.
    transforms = Element(_ds_transforms)
    envelope_reference.insert(0, transforms)

    enveloped = SubElement(transforms, _ds_transform)
    enveloped.set('Algorithm', Transform.Enveloped)

    xpath_transform = SubElement(transforms, _ds_transform)
    xpath_transform.set('Algorithm', XPath_Transform)

    xpath = SubElement(xpath_transform, _ds_xpath, nsmap=_xpath_nsmap)
    xpath.text = XPath_Expression

    c14n = SubElement(transforms, _ds_transform)
    c14n.set('Algorithm', Algorithm.C14N)

    for payload in payloads:
        payload_digest = _digest(payload.data, digest_algorithm)
        payload_uri = f'cid:{payload.content_id}'
        _ = _add_reference(signed_info, payload_uri, digest_algorithm, payload_digest)

    # The SignedInfo is canonicalized where it stands, so that it has the namespace context it is verified in.
    canonical_signed_info = canonicalize_inclusive(signed_info)
    padding = PKCS1v15()
    hash_algorithm = hash_class()
    signature_bytes = signing_key.sign(canonical_signed_info, padding, hash_algorithm)

    signature_value = SubElement(out, _ds_signature_value)
    signature_value.text = encode_base64(signature_bytes)

    key_info = SubElement(out, _ds_key_info)
    x509_data = SubElement(key_info, _ds_x509_data)

    for certificate in local_keys.signing_certificate_chain:
        der = certificate.public_bytes(Encoding.DER)
        certificate_element = SubElement(x509_data, _ds_x509_certificate)
        certificate_element.text = encode_base64(der)

    return out

# ################################################################################################################################

def _new_signature(envelope:'any_') -> 'any_':
    """ Appends an empty ds:Signature to the SOAP Header of an envelope.
    """
    soap_header = envelope.find(_soap_header)

    out = SubElement(soap_header, _ds_signature, nsmap=_ds_nsmap)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _normalize_expression(xpath:'any_') -> 'str':
    """ Returns the expression of a ds:XPath with the prefix of the SOAP envelope namespace written as SOAP,
    without whitespace and with double quotes only, so that equivalent expressions compare equal.
    """
    if (expression := xpath.text) is None:
        expression = ''

    for prefix, namespace in xpath.nsmap.items():
        if namespace == NS.SOAP:
            if prefix:
                expression = expression.replace(f'{prefix}:actor', f'{_xpath_soap_prefix}:actor')

    expression = expression.replace("\'", '"')
    pieces = expression.split()

    out = ''.join(pieces)
    return out

# The expected XPath filter in the form the received ones are compared in.
_expected_expression = ''.join(XPath_Expression.split())

# ################################################################################################################################

def _require_algorithm(element:'any_', name:'str', allowed:'any_') -> 'str':
    """ Returns the Algorithm of a ds: element, which is to be one of the allowed ones.
    """
    if element is None:
        raise EbMS2SecurityException(f'Element `ds:{name}` is missing')

    algorithm = element.get('Algorithm')

    if algorithm not in allowed:
        raise EbMS2SecurityException(f'Algorithm `{algorithm}` of `ds:{name}` is not supported')

    out = algorithm
    return out

# ################################################################################################################################

def _check_envelope_transforms(reference:'any_') -> 'bool':
    """ Checks the transforms of the reference to the envelope. Returns whether they include the XPath filter.
    """

    # Our response to produce
    out = False

    if (transforms := reference.find(_ds_transforms)) is None:
        raise EbMS2SecurityException('The reference to the envelope has no transforms')

    has_enveloped = False

    for transform in transforms.iter(_ds_transform):

        algorithm = transform.get('Algorithm')

        if algorithm not in _envelope_transforms:
            raise EbMS2SecurityException(f'Transform `{algorithm}` is not supported')

        if algorithm == Transform.Enveloped:
            has_enveloped = True

        if algorithm == XPath_Transform:

            if (xpath := transform.find(_ds_xpath)) is None:
                raise EbMS2SecurityException('The XPath transform has no ds:XPath')

            expression = _normalize_expression(xpath)

            if expression != _expected_expression:
                raise EbMS2SecurityException(f'The XPath filter is not the one of ebMS 2.0 -> `{xpath.text}`')

            out = True

    if not has_enveloped:
        raise EbMS2SecurityException('The reference to the envelope has no enveloped-signature transform')

    return out

# ################################################################################################################################

def _reference_digest(reference:'any_') -> 'str':
    """ Returns the DigestValue of a reference without the whitespace a serializer may have put into it.
    """
    if (digest_value := reference.find(_ds_digest_value)) is None:
        raise EbMS2SecurityException('A reference has no ds:DigestValue')

    if (text := digest_value.text) is None:
        text = ''

    pieces = text.split()

    out = ''.join(pieces)
    return out

# ################################################################################################################################

def _order_chain(certificates:'certificate_list') -> 'certificate_list':
    """ Returns the certificates of a KeyInfo with the signer's certificate first, followed by the ones that issued it.
    """
    issuer_names = set()

    for certificate in certificates:
        issuer_names.add(certificate.issuer)

    # The signer's certificate is the one that issued none of the others.
    for certificate in certificates:
        if certificate.subject not in issuer_names:
            leaf = certificate
            break
    else:
        leaf = certificates[0]

    out:'certificate_list' = [leaf]

    for certificate in certificates:
        if certificate is not leaf:
            out.append(certificate)

    return out

# ################################################################################################################################

def _read_chain(signature:'any_', expected_certificate:'Certificate | None') -> 'certificate_list':
    """ Returns the certificate chain the KeyInfo of a signature has, or the expected certificate if there is no KeyInfo.
    """
    certificates:'certificate_list' = []

    if (key_info := signature.find(_ds_key_info)) is not None:
        for x509_data in key_info.iter(_ds_x509_data):
            for certificate_element in x509_data.iter(_ds_x509_certificate):

                if (text := certificate_element.text) is None:
                    text = ''

                try:
                    der = decode_base64(text)
                    certificate = load_der_x509_certificate(der)
                except ValueError as e:
                    raise EbMS2SecurityException(f'A certificate of the signature cannot be loaded -> {e}')

                certificates.append(certificate)

    if certificates:
        out = _order_chain(certificates)

    elif expected_certificate:
        out = [expected_certificate]

    else:
        raise EbMS2SecurityException('The signature has no certificate and the agreement names none')

    return out

# ################################################################################################################################

def verify_envelope(
    envelope:'any_',
    signature:'any_',
    payloads:'payload_list',
    expected_certificate:'Certificate | None',
    ) -> 'VerifiedSignature':
    """ Verifies a ds:Signature of the ebMS 2.0 profile - its references to the envelope and to every payload,
    and its signature value. Establishing trust in the certificate is left to the caller.
    """
    signed_info = signature.find(_ds_signed_info)

    if signed_info is None:
        raise EbMS2SecurityException('The signature has no ds:SignedInfo')

    canonicalization_method = signed_info.find(_ds_canonicalization_method)
    _ = _require_algorithm(canonicalization_method, 'CanonicalizationMethod', {Algorithm.C14N})

    signature_method = signed_info.find(_ds_signature_method)
    signature_algorithm = _require_algorithm(signature_method, 'SignatureMethod', _signature_hashes)

    payloads_by_uri = {}

    for payload in payloads:
        payload_uri = f'cid:{payload.content_id}'
        payloads_by_uri[payload_uri] = payload

    signed_uris:'strset' = set()

    out = VerifiedSignature()
    out.references = []

    # Every reference is to digest to what it says ..
    for reference in signed_info.iter(_ds_reference):

        uri = reference.get('URI')

        if uri in signed_uris:
            raise EbMS2SecurityException(f'Reference `{uri}` occurs more than once')

        digest_method = reference.find(_ds_digest_method)
        digest_algorithm = _require_algorithm(digest_method, 'DigestMethod', _digest_names)

        if uri == '':
            apply_xpath_filter = _check_envelope_transforms(reference)
            data = canonicalize_envelope(envelope, signature, apply_xpath_filter=apply_xpath_filter)

        elif payload := payloads_by_uri.get(uri):
            if reference.find(_ds_transforms) is not None:
                raise EbMS2SecurityException(f'Reference `{uri}` has transforms, which are not supported for payloads')
            data = payload.data

        else:
            raise EbMS2SecurityException(f'Reference `{uri}` names neither the envelope nor a payload')

        computed = _digest(data, digest_algorithm)
        received = _reference_digest(reference)

        if computed != received:
            raise EbMS2SecurityException(f'Digest of `{uri}` does not match')

        signed_uris.add(uri)

        reference_copy = deepcopy(reference)
        out.references.append(reference_copy)

    # .. the envelope and every payload are to be signed ..
    if '' not in signed_uris:
        raise EbMS2SecurityException('The signature does not cover the envelope')

    for payload_uri in payloads_by_uri:
        if payload_uri not in signed_uris:
            raise EbMS2SecurityException(f'The signature does not cover `{payload_uri}`')

    # .. and the signature value is to verify with the signer's key.
    chain = _read_chain(signature, expected_certificate)
    certificate = chain[0]
    public_key = certificate.public_key()

    if not isinstance(public_key, RSAPublicKey):
        raise EbMS2SecurityException('The signer\'s key is not an RSA key')

    if public_key.key_size < Limits.Min_RSA_Key_Size_Bits:
        raise EbMS2SecurityException(
            f'The signer\'s key has {public_key.key_size} bits, fewer than {Limits.Min_RSA_Key_Size_Bits}')

    if (signature_value := signature.find(_ds_signature_value)) is None:
        raise EbMS2SecurityException('The signature has no ds:SignatureValue')

    if (signature_text := signature_value.text) is None:
        signature_text = ''

    try:
        signature_bytes = decode_base64(signature_text)
    except ValueError as e:
        raise EbMS2SecurityException(f'The signature value is not valid base64 -> {e}')

    canonical_signed_info = canonicalize_inclusive(signed_info)
    hash_class = _signature_hashes[signature_algorithm]
    padding = PKCS1v15()
    hash_algorithm = hash_class()

    try:
        public_key.verify(signature_bytes, canonical_signed_info, padding, hash_algorithm)
    except InvalidSignature:
        raise EbMS2SecurityException('The signature value does not verify')

    out.certificate = certificate
    out.chain = chain

    return out

# ################################################################################################################################
# ################################################################################################################################
