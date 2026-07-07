# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from hashlib import sha256
from io import BytesIO

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import NS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'

# ################################################################################################################################
# ################################################################################################################################

def canonicalize_exclusive(element:'any_') -> 'bytes':
    """ Serializes an element with Exclusive XML Canonicalization without comments,
    the canonicalization method both eDelivery generations mandate.
    """
    buffer = BytesIO()
    tree = etree.ElementTree(element)
    tree.write_c14n(buffer, exclusive=True, with_comments=False)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def digest_element(element:'any_') -> 'str':
    """ Returns the base64 SHA-256 digest of the exclusive canonical form of an element.
    """
    canonical = canonicalize_exclusive(element)
    digest = sha256(canonical).digest()

    out = b64encode(digest).decode('ascii')
    return out

# ################################################################################################################################

def digest_bytes(data:'bytes') -> 'str':
    """ Returns the base64 SHA-256 digest of raw bytes - this is the whole of the SwA
    Attachment-Content-Signature-Transform for non-XML content: no canonicalization,
    just a hash over the octets of the MIME part body.
    """
    digest = sha256(data).digest()

    out = b64encode(digest).decode('ascii')
    return out

# ################################################################################################################################

def encode_base64(data:'bytes') -> 'str':
    """ Returns bytes as a base64 string without line breaks.
    """
    out = b64encode(data).decode('ascii')
    return out

# ################################################################################################################################

def decode_base64(data:'str') -> 'bytes':
    """ Decodes a base64 string, tolerating the whitespace that XML pretty-printing may add.
    """
    compact = ''.join(data.split())

    out = b64decode(compact)
    return out

# ################################################################################################################################

def find_by_wsu_id(root:'any_', wsu_id:'str') -> 'any_':
    """ Returns the element carrying the given wsu:Id anywhere under root, or None.
    """
    for element in root.iter():
        if element.get(_wsu_id) == wsu_id:
            out = element
            break
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################
