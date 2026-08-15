# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

def read_invocations(marker_path:'str') -> 'strlist':
    """ The names of every service invocation recorded so far, in order.
    """

    with open(marker_path) as marker_file:
        lines = marker_file.read().splitlines()

    out:'strlist' = []

    for line in lines:
        if line:
            out.append(line)

    return out

# ################################################################################################################################

def count_invocations(marker_path:'str', service_name:'str') -> 'int':
    """ How many times the given service ran so far.
    """
    invocations = read_invocations(marker_path)

    out = invocations.count(service_name)
    return out

# ################################################################################################################################

def read_payload_text(payload_path:'str', offset:'int') -> 'str':
    """ The payloads services recorded since the given offset, as one text.
    """

    with open(payload_path) as payload_file:
        _ = payload_file.seek(offset)
        out = payload_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################
