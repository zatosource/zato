# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class SignalKind:
    """ The kinds of signal a message exchange ends with, the same for every protocol.
    """
    No_Signal = 'none'
    Receipt   = 'receipt'
    Error     = 'error'
    Pong      = 'pong'
    Status    = 'status'

# ################################################################################################################################
# ################################################################################################################################

class FinalState:
    """ Where the exchange of one message ended.
    """
    Delivered = 'delivered'
    Held      = 'held'
    Rejected  = 'rejected'
    Duplicate = 'duplicate'
    Failed    = 'failed'
    Answered  = 'answered'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Outcome:
    """ The normalized result of one message exchange. Every protocol produces it, and two implementations
    agree on an exchange when their outcomes are equal field by field.
    """
    # Whether the payloads were handed over to the application.
    delivered: bool = False

    # The base64 SHA-256 digest of each delivered payload, in the order they were delivered.
    payload_digests: 'strlist'

    # What kind of signal the exchange produced.
    signal_kind: str = SignalKind.No_Signal

    # The protocol's own error code and severity, when the signal is an error.
    error_code:     str = ''
    error_severity: str = ''

    # Whether the message, or the receipt for it, had a signature that verified.
    signature_verified: bool = False

    # Whether the message was recognized as a duplicate of one received earlier.
    duplicate: bool = False

    # How many times the message was delivered again after its first delivery.
    retry_count: int = 0

    # Where the exchange ended.
    final_state: str = FinalState.Rejected

    def __init__(self) -> 'None':
        self.payload_digests = []

# ################################################################################################################################
# ################################################################################################################################
