# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an outgoing e-mail is recorded as - the keys of the document a message-sent row carries,
# shared by the connection that writes it and by the resend that reads it back.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The recipients as they were given, apart from the comma-joined form the screen reads
Key_Recipients = 'recipients'

# What decides how the body is encoded and framed
Key_Headers    = 'headers'
Key_Is_HTML    = 'is_html'
Key_Charset    = 'charset'
Key_Is_RFC2231 = 'is_rfc2231'

# ################################################################################################################################

def split_addresses(value:'any_') -> 'strlist':
    """ Message recipients arrive as one address or as a list of them - either way,
    what is kept for a resend is the list, because that is what goes back out.
    """

    # Our response to produce
    out:'strlist' = []

    if isinstance(value, str):
        if value:
            out.append(value)

    elif value:
        out.extend(value)

    return out

# ################################################################################################################################
# ################################################################################################################################
