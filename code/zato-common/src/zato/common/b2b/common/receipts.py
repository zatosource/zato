# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.common.exceptions import B2BException
from zato.common.util.xml_.constants import NS
from zato.common.util.xml_.core import element_attribute, element_text, qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strset, strstrdict
    any_ = any_
    anylist = anylist
    strset = strset
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ReceiptException(B2BException):
    """ Raised when a signed receipt does not account for exactly what was sent.
    """

# ################################################################################################################################
# ################################################################################################################################

def collect_sent_digests(signature:'any_') -> 'strstrdict':
    """ Maps each signed reference URI of an outgoing ds:Signature to its digest value.
    A receipt is to echo these back.
    """

    # Our response to produce
    out:'strstrdict' = {}

    signed_info_name = qname(NS.DS, 'SignedInfo')
    reference_name = qname(NS.DS, 'Reference')
    digest_value_name = qname(NS.DS, 'DigestValue')

    signed_info = signature.find(signed_info_name)
    references = signed_info.findall(reference_name)

    for reference in references:
        digest_value = reference.find(digest_value_name)

        uri = element_attribute(reference, 'URI')
        digest_text = element_text(digest_value)
        digest_parts = digest_text.split()

        out[uri] = ''.join(digest_parts)

    return out

# ################################################################################################################################

def check_echoed_digests(references:'anylist', sent_digests:'strstrdict') -> 'None':
    """ Compares the ds:Reference elements echoed in a receipt with the digests that were sent.
    Every reference that was sent is to come back with the digest it was sent with, and nothing
    else may come back.
    """
    digest_value_name = qname(NS.DS, 'DigestValue')

    echoed_uris:'strset' = set()

    for reference in references:
        uri = element_attribute(reference, 'URI')
        digest_value = reference.find(digest_value_name)

        # The echoed digest may have whitespace inserted by the responder's serializer.
        digest_text = element_text(digest_value)
        digest_parts = digest_text.split()
        echoed = ''.join(digest_parts)

        if uri not in sent_digests:
            raise ReceiptException(f'Receipt echoes `{uri}`, which was not sent')

        sent = sent_digests[uri]

        if echoed != sent:
            raise ReceiptException(f'Receipt digest mismatch for `{uri}` - sent `{sent}`, receipt has `{echoed}`')

        echoed_uris.add(uri)

    for uri in sent_digests:
        if uri not in echoed_uris:
            raise ReceiptException(f'Receipt does not account for `{uri}`')

# ################################################################################################################################
# ################################################################################################################################
