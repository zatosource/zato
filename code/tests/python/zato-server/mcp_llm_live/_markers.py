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

def read_hook_lines(hook_path:'str', gateway_name:'str') -> 'strlist':
    """ Every line the hook services recorded for the given gateway so far, in order,
    each without the gateway's name - the kind of record, then what the hook saw.
    """

    with open(hook_path) as hook_file:
        lines = hook_file.read().splitlines()

    out:'strlist' = []

    for line in lines:
        kind, line_gateway, rest = line.split(' ', 2)
        if line_gateway == gateway_name:
            out.append(f'{kind} {rest}'.rstrip())

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
