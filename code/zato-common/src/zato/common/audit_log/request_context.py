# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The keys one recorded outgoing call is stored under, along with the redaction of the headers
# among them.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist, strstrdict
    stranydict = stranydict
    strlist = strlist
    strstrdict = strstrdict

    redactedheaders = tuple[strstrdict, strlist]

# ################################################################################################################################
# ################################################################################################################################

# The keys the stored document carries.
Key_Payload      = 'payload'
Key_Method       = 'method'
Key_Address      = 'address'
Key_Params       = 'params'
Key_Headers      = 'headers'
Key_Redacted     = 'redacted'
Key_Payload_Kind = 'payload_kind'

# What the stored payload is when it describes an object rather than being the bytes that went out.
Payload_Kind_Described = 'described'

# What a value kept out of the audit log reads as, spelled the same way a masked SOAP credential is.
Redacted_Value = '***'

# Header names that always carry a credential.
_redacted_header_names = frozenset({'authorization', 'proxy-authorization', 'cookie'})

# Fragments that mark a header name as carrying a credential.
_redacted_header_fragments = ('auth', 'key', 'token', 'secret', 'signature', 'password', 'credential')

# ################################################################################################################################
# ################################################################################################################################

def is_redacted_header(name:'str') -> 'bool':
    """ Whether one header carries a credential and is therefore never stored. A header name is
    case-insensitive on the wire, so the comparison ignores letter case too.
    """
    lower_name = name.lower()

    # Our response to produce
    out = lower_name in _redacted_header_names

    if not out:
        for fragment in _redacted_header_fragments:
            if fragment in lower_name:
                out = True
                break

    return out

# ################################################################################################################################

def redact_headers(headers:'strstrdict') -> 'redactedheaders':
    """ Returns the headers as they are stored, with every credential among them replaced by
    a marker, along with the names of the ones replaced.
    """
    stored:'strstrdict' = {}
    redacted:'strlist' = []

    for name, value in headers.items():

        if is_redacted_header(name):
            stored[name] = Redacted_Value
            redacted.append(name)
        else:
            stored[name] = value

    # Our response to produce
    out = stored, redacted

    return out

# ################################################################################################################################

def build_request_context(
    payload:'str',
    method:'str',
    address:'str',
    params:'stranydict',
    headers:'strstrdict',
    *,
    is_described:'bool' = False,
    redacted:'strlist | None' = None,
    ) -> 'stranydict':
    """ Builds the document one outgoing request is recorded as - everything repeating that one
    call needs, with the credentials among the headers replaced by a marker. A caller that already
    replaced something in the body itself names it here, so the one row names all of them together.
    """
    stored_headers, header_redacted = redact_headers(headers)

    if redacted is None:
        redacted = header_redacted
    else:
        redacted = list(redacted) + header_redacted

    # Our response to produce
    out:'stranydict' = {
        Key_Payload: payload,
        Key_Method: method,
        Key_Address: address,
        Key_Params: params,
        Key_Headers: stored_headers,
    }

    # The key is there only when something was replaced.
    if redacted:
        out[Key_Redacted] = redacted

    if is_described:
        out[Key_Payload_Kind] = Payload_Kind_Described

    return out

# ################################################################################################################################
# ################################################################################################################################
