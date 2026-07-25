# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.soap.envelope import to_bytes
from zato.common.util.xml_.constants import NS
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What a masked value reads as. The same spelling the wrapper uses for the password in its own
# sanitised config, so a reader of either sees the one marker and knows what it means.
Mask = '***'

# The elements that always carry a secret, whatever the connection is configured with. A
# UsernameToken Password is the secret itself in the plaintext profile and a value derived from it
# in the digest one, and neither belongs in a record that outlives the request.
_always_masked = (
    qname(NS.WSSE, 'Password'),
)

# ################################################################################################################################
# ################################################################################################################################

def mask_credentials(envelope:'any_', body_credential_names:'strlist | None'=None) -> 'bytes':
    """ Returns the bytes of an envelope with every credential it carries replaced by a marker.

    An audit log is written to be read later, by more people than the request was made for and for
    longer than the request lived, so a password in it is a password stored in plaintext for as long
    as the log is kept. Masking happens on a copy, so what goes on the wire is untouched.
    """
    masked = deepcopy(envelope)

    for tag in _always_masked:
        for element in masked.iter(tag):
            element.text = Mask

    # A connection may also carry its credentials as plain body elements, and only the connection
    # knows which of the operation's children those are - they are named by its own mapping.
    if body_credential_names:
        _mask_body_credentials(masked, body_credential_names)

    out = to_bytes(masked)
    return out

# ################################################################################################################################

def _mask_body_credentials(envelope:'any_', names:'strlist') -> 'None':
    """ Masks the body elements a connection's credential mapping names.

    The names are matched on the local name alone, because a mapping names an element the way the
    remote service's schema does and the namespace it lands in is the operation's, not the mapping's.
    """
    wanted = set(names)

    for element in envelope.iter():

        # Comments and processing instructions have non-string tags and cannot be credentials.
        tag = element.tag

        if not isinstance(tag, str):
            continue

        local_name = tag.rpartition('}')[2]

        if local_name in wanted:
            element.text = Mask

# ################################################################################################################################
# ################################################################################################################################
