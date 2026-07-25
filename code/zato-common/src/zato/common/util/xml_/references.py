# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from io import BytesIO

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import is_string_equal
from zato.common.util.xml_.constants import Algorithm, NS, Transform, WSU_ID
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.mime_ import strpartdict
from zato.common.util.xml_.xmlsec import digest_bytes, digest_element, find_by_wsu_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The digest algorithms a ds:Reference may declare. The digest is recomputed with SHA-256, so
# this list says which identifiers actually mean SHA-256.
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

# ################################################################################################################################
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

        wsu_id = element.get(WSU_ID)
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
    """ Returns the one element a signature reference names. An id carried by more than one element
    is refused rather than resolved to the first match in document order.
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
    """ Rejects a ds:Transform this implementation does not apply. Every transform a reference
    declares is one the digest recomputation performs, so a transform outside the accepted set
    means the reference cannot be recomputed the way it was computed.
    """
    if transforms is None:
        return

    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        algorithm = transform.get('Algorithm')

        if algorithm not in Accepted_Transforms:
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported transform `{algorithm}` on reference `{uri}`')

# ################################################################################################################################

def verify_one_reference(reference:'any_', envelope:'any_', part_index:'strpartdict', id_index:'anydict') -> 'any_':
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
        part = part_index.get(content_id)

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
    # A reference may carry no transforms at all.
    if transforms is None:
        out = False

    else:
        for transform in transforms.findall(qname(NS.DS, 'Transform')):
            if transform.get('Algorithm') == Transform.Enveloped:
                out = True
                break
        else:
            out = False

    return out

# ################################################################################################################################

def _without_signature(element:'any_') -> 'any_':
    """ Returns a copy of an element with its immediate ds:Signature child removed,
    which is how the enveloped-signature transform is applied.
    """
    # A detached copy is what gets pruned, so the document the caller holds is left as it stands.
    out = deepcopy(element)

    signature = out.find(qname(NS.DS, 'Signature'))
    if signature is not None:
        out.remove(signature)

    return out

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
