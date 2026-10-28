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
    from zato.common.typing_ import stranydict, strlist
    stranydict = stranydict
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

class FailureCause:
    """ Why a delivery of a message failed - no answer within the timeout, an HTTP error status, or a protocol error.
    """
    No_Answer      = 'no-answer'
    HTTP_Error     = 'http-error'
    Protocol_Error = 'protocol-error'

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

    # Why the latest delivery failed, and its HTTP status code or protocol error code, empty after a successful one.
    failure_cause:  str = ''
    failure_detail: str = ''

    def __init__(self) -> 'None':
        self.payload_digests = []

# ################################################################################################################################
# ################################################################################################################################

def outcome_to_dict(outcome:'Outcome') -> 'stranydict':
    """ Returns the document an outcome is recorded with in the audit log.
    """
    out:'stranydict' = {
        'delivered': outcome.delivered,
        'payload_digests': outcome.payload_digests,
        'signal_kind': outcome.signal_kind,
        'error_code': outcome.error_code,
        'error_severity': outcome.error_severity,
        'signature_verified': outcome.signature_verified,
        'duplicate': outcome.duplicate,
        'retry_count': outcome.retry_count,
        'final_state': outcome.final_state,
        'failure_cause': outcome.failure_cause,
        'failure_detail': outcome.failure_detail,
    }

    return out

# ################################################################################################################################

def outcome_from_dict(data:'stranydict') -> 'Outcome':
    """ Returns an outcome from the document it is recorded with in the audit log.
    """
    out = Outcome()
    out.delivered = data['delivered']
    out.payload_digests = data['payload_digests']
    out.signal_kind = data['signal_kind']
    out.error_code = data['error_code']
    out.error_severity = data['error_severity']
    out.signature_verified = data['signature_verified']
    out.duplicate = data['duplicate']
    out.retry_count = data['retry_count']
    out.final_state = data['final_state']
    out.failure_cause = data['failure_cause']
    out.failure_detail = data['failure_detail']

    return out

# ################################################################################################################################
# ################################################################################################################################
