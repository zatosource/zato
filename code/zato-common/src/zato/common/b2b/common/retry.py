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
    from datetime import datetime, timedelta
    from zato.common.typing_ import dtnone
    datetime = datetime
    dtnone = dtnone
    timedelta = timedelta

# ################################################################################################################################
# ################################################################################################################################

class RetryAction:
    """ What a sender does next with a message that expects a receipt.
    """
    Resend  = 'resend'
    Wait    = 'wait'
    Give_Up = 'give-up'
    Done    = 'done'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RetryPolicy:
    """ How many times an unanswered message is sent again after its first delivery, and how long
    each delivery waits for its receipt.
    """
    retries:        int
    retry_interval: 'timedelta'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RetryState:
    """ Where the delivery of one message stands.
    """
    # How many deliveries the message has had, the first one included.
    attempt_count: int

    # When the most recent delivery was made.
    last_attempt_at: 'datetime'

    # The moment after which the message may no longer be delivered, if it has one.
    expires_at: 'dtnone' = None

    # Whether the receipt has arrived.
    is_answered: bool = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RetryDecision:
    """ The next action for one message and the moment it applies at.
    """
    action: str
    at:     'datetime'

# ################################################################################################################################
# ################################################################################################################################

def next_action(policy:'RetryPolicy', state:'RetryState', now:'datetime') -> 'RetryDecision':
    """ Returns what is to happen next with a message that expects a receipt.
    """

    # Our response to produce
    out = RetryDecision()
    out.at = now

    # The receipt for the current or for an earlier delivery has arrived ..
    if state.is_answered:
        out.action = RetryAction.Done
        return out

    # .. the current delivery is answered within its interval, or not at all ..
    due_at = state.last_attempt_at + policy.retry_interval
    retry_count = state.attempt_count - 1
    has_retries_left = retry_count < policy.retries

    # .. a message that expires before its next delivery is not sent again, though the answer to the current delivery,
    # which may be an error reporting the expiry, is awaited for the whole interval ..
    if state.expires_at:
        if state.expires_at <= due_at:
            has_retries_left = False

    # .. it is still within that interval ..
    if now < due_at:
        out.action = RetryAction.Wait
        out.at = due_at

    # .. it is past the interval with retries left ..
    elif has_retries_left:
        out.action = RetryAction.Resend

    # .. or it is past the interval with none left.
    else:
        out.action = RetryAction.Give_Up

    return out

# ################################################################################################################################
# ################################################################################################################################
