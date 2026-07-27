# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What each destination of a channel is actually sent. A service may say nothing at all,
# in which case every destination receives the message as it arrived - which is what lets a
# channel have no service. It may set one payload for all of them, or one for a single
# destination by name, and naming a destination with nothing to send drops that destination
# for this message alone.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import dict_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anynone
    anydict = anydict
    anynone = anynone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PayloadOverrides:
    """ What a service said about what its channel's destinations receive.
    """

    # The payload every destination receives, when the service set one.
    broadcast: 'any_' = None

    # Whether the service set the broadcast payload at all - it is not the same
    # as having set it to nothing.
    has_broadcast: bool = False

    # The payload one named destination receives, overriding the broadcast. A destination
    # named here with nothing to send receives no message at all.
    per_destination: 'anydict' = dict_field()

# ################################################################################################################################

def new_overrides() -> 'PayloadOverrides':
    """ Builds an empty set of overrides - a service that says nothing leaves it this way.
    """

    # Our response to produce
    out = PayloadOverrides()

    out.broadcast = None
    out.has_broadcast = False
    out.per_destination = {}

    return out

# ################################################################################################################################

def resolve_payload(name:'str', overrides:'PayloadOverrides', request_payload:'any_') -> 'anynone':
    """ Returns what one destination is sent, or nothing at all when the destination
    is to be dropped for this message.
    """

    # A destination named by the service receives what the service named it with,
    # which is nothing at all when the service dropped it ..
    if name in overrides.per_destination:
        out = overrides.per_destination[name]

    # .. a payload set for all of them comes next ..
    elif overrides.has_broadcast:
        out = overrides.broadcast

    # .. and with the service saying nothing, the destination receives the message as it arrived.
    else:
        out = request_payload

    return out

# ################################################################################################################################
# ################################################################################################################################
