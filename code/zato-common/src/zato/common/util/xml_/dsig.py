# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from hashlib import sha256

# Zato
from zato.common.crypto.api import is_string_equal
from zato.common.util.xml_.constants import Algorithm, NS, Transform
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.token import parse_x509v3
from zato.common.util.xml_.signature import verify_signature_bytes
from zato.common.util.xml_.trust import validate_certificate_chain
from zato.common.util.xml_.xmlsec import canonicalize_exclusive, canonicalize_inclusive, decode_base64, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    Keystore = Keystore

# ################################################################################################################################
# ################################################################################################################################

# The canonicalization methods recognized here. Documents of this family are signed with Canonical
# XML 1.0 in practice, and the exclusive form is recognized as well.
_accepted_canonicalization = {
    Algorithm.C14N,
    Algorithm.C14N_Exclusive,
}

# The identifiers that name SHA-256, which is the digest every reference is recomputed with.
_accepted_digest_methods = {
    Algorithm.SHA256,
}

# ################################################################################################################################
# ################################################################################################################################

def _require_child(parent:'any_', element_name:'str', description:'str') -> 'any_':
    """ Returns a child element the signature syntax makes mandatory.
    """
    out = parent.find(element_name)

    if out is None:
        raise XMLSecurityException(f'Signature has no {description}')

    return out

# ################################################################################################################################

def _require_algorithm(element:'any_', description:'str') -> 'str':
    """ Returns the Algorithm attribute of one of the method elements.
    """
    out = element.get('Algorithm')

    if out is None:
        raise XMLSecurityException(f'{description} has no Algorithm')

    return out

# ################################################################################################################################

def _text_of(element:'any_') -> 'str':
    """ Returns the text of an element, which an empty element genuinely carries as None.
    """
    out = element.text

    if out is None:
        out = ''

    return out

# ################################################################################################################################

def _canonicalize(element:'any_', algorithm:'str') -> 'bytes':
    """ Canonicalizes an element with the method the algorithm identifier names.
    """
    if algorithm == Algorithm.C14N:
        out = canonicalize_inclusive(element)

    elif algorithm == Algorithm.C14N_Exclusive:
        out = canonicalize_exclusive(element)

    else:
        raise XMLSecurityUnsupportedAlgorithm(f'Unsupported canonicalization method `{algorithm}`')

    return out

# ################################################################################################################################

def _digest(data:'bytes') -> 'str':
    """ Returns the base64 SHA-256 digest of canonical bytes.
    """
    digest = sha256(data).digest()

    out = encode_base64(digest)
    return out

# ################################################################################################################################

def _extract_certificate_chain(signature:'any_') -> 'certificate_list':
    """ Returns the signer's certificate as named by ds:KeyInfo/ds:X509Data/ds:X509Certificate.
    """
    key_info = _require_child(signature, qname(NS.DS, 'KeyInfo'), 'KeyInfo')
    certificate_element = _require_child(key_info, f'.//{qname(NS.DS, "X509Certificate")}', 'X509Certificate')

    leaf = parse_x509v3(decode_base64(_text_of(certificate_element)))

    out = [leaf]
    return out

# ################################################################################################################################

def _check_transforms(transforms:'any_') -> 'None':
    """ Requires the enveloped-signature transform and refuses any transform this module does not
    apply. A canonicalization transform is applied when the digest is computed.
    """
    has_enveloped = False

    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        algorithm = _require_algorithm(transform, 'Transform')

        if algorithm == Transform.Enveloped:
            has_enveloped = True

        elif algorithm not in _accepted_canonicalization:
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported transform `{algorithm}`')

    if not has_enveloped:
        raise XMLSecurityException('Reference does not declare the enveloped-signature transform')

# ################################################################################################################################

def _reference_canonicalization(transforms:'any_', signed_info:'any_') -> 'str':
    """ Returns the method a reference is canonicalized with - the one its own transforms name, or
    the method of ds:SignedInfo when the transforms name none.
    """
    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        algorithm = _require_algorithm(transform, 'Transform')

        if algorithm in _accepted_canonicalization:
            out = algorithm
            break
    else:
        canonicalization_method = _require_child(
            signed_info, qname(NS.DS, 'CanonicalizationMethod'), 'CanonicalizationMethod')
        out = _require_algorithm(canonicalization_method, 'CanonicalizationMethod')

    return out

# ################################################################################################################################

def _check_document_reference(root:'any_', signed_info:'any_') -> 'None':
    """ Recomputes the digest of the one reference the signature is required to carry, which covers
    the whole document with the ds:Signature element taken out of it.
    """
    references = signed_info.findall(qname(NS.DS, 'Reference'))
    reference_count = len(references)

    if reference_count != 1:
        raise XMLSecurityException(f'Signature carries {reference_count} references, expected one')

    reference = references[0]

    # An empty URI names the document itself. An id may be used instead, in which case it is required
    # to be the id of the root element, that being the only element this covers.
    uri = reference.get('URI')

    if uri:
        root_id = root.get('Id')

        if uri != f'#{root_id}':
            raise XMLSecurityException(f'Reference `{uri}` does not cover the document')

    digest_method = _require_child(reference, qname(NS.DS, 'DigestMethod'), 'DigestMethod')
    digest_algorithm = _require_algorithm(digest_method, 'DigestMethod')

    if digest_algorithm not in _accepted_digest_methods:
        raise XMLSecurityUnsupportedAlgorithm(f'Unsupported digest algorithm `{digest_algorithm}`')

    digest_value_element = _require_child(reference, qname(NS.DS, 'DigestValue'), 'DigestValue')
    digest_text = _text_of(digest_value_element)
    expected_digest = ''.join(digest_text.split())

    transforms = _require_child(reference, qname(NS.DS, 'Transforms'), 'Transforms')
    _check_transforms(transforms)

    # The enveloped-signature transform digests the document with the signature removed. The copy
    # leaves the document itself as the caller passed it in.
    covered = deepcopy(root)
    covered_signature = covered.find(qname(NS.DS, 'Signature'))

    if covered_signature is not None:
        covered.remove(covered_signature)

    canonicalization = _reference_canonicalization(transforms, signed_info)
    canonical = _canonicalize(covered, canonicalization)

    actual_digest = _digest(canonical)

    if not is_string_equal(actual_digest, expected_digest):
        raise XMLSecurityException('Document digest mismatch')

# ################################################################################################################################

def verify_enveloped_signature(root:'any_', keystore:'Keystore') -> 'certificate_list':
    """ Verifies an enveloped XML Signature over a whole document, the shape used outside the
    WS-Security family - SMP service metadata among others. Returns the signer's chain.

    The signature is required to be a direct child of the root element and to carry one reference
    covering the document. Trust comes from the keystore, as it does everywhere else.
    """
    signature = root.find(qname(NS.DS, 'Signature'))

    if signature is None:
        raise XMLSecurityException('Document is not signed')

    chain = _extract_certificate_chain(signature)
    validate_certificate_chain(chain, keystore)

    signed_info = _require_child(signature, qname(NS.DS, 'SignedInfo'), 'SignedInfo')

    _check_document_reference(root, signed_info)

    signature_method = _require_child(signed_info, qname(NS.DS, 'SignatureMethod'), 'SignatureMethod')
    signature_algorithm = _require_algorithm(signature_method, 'SignatureMethod')

    signature_value_element = _require_child(signature, qname(NS.DS, 'SignatureValue'), 'SignatureValue')
    signature_bytes = decode_base64(_text_of(signature_value_element))

    # SignedInfo is canonicalized with its own declared method, which need not be the one the
    # reference was canonicalized with.
    canonicalization_method = _require_child(
        signed_info, qname(NS.DS, 'CanonicalizationMethod'), 'CanonicalizationMethod')
    canonicalization = _require_algorithm(canonicalization_method, 'CanonicalizationMethod')

    canonical = _canonicalize(signed_info, canonicalization)

    verify_signature_bytes(signature_bytes, canonical, signature_algorithm, chain)

    out = chain
    return out

# ################################################################################################################################
# ################################################################################################################################
