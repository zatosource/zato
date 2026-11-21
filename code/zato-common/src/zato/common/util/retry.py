# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How many times a failed attempt is retried and how long to wait between attempts - shared by outgoing connections
# and by the push delivery of published messages, each with a default set of its own.

# Zato
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# The shortest sleep to fall back to when backing off would otherwise sleep for no time at all,
# which would turn the loop into a tight one against an endpoint that is already unwell.
Minimum_Sleep_Time = 1

# ################################################################################################################################
# ################################################################################################################################

class RetryPolicy:
    """ How many times a failed attempt is retried and how long to wait between attempts.

    The four settings live in a connection's opaque attributes or travel with a published message. The ceiling
    on a single sleep and the jitter come from the default set the policy was built with.
    """
    __slots__ = 'max_retries', 'sleep_time', 'backoff_threshold', 'backoff_multiplier', 'max_sleep_time', 'jitter_percent'

    def __init__(
        self,
        max_retries,        # type: int
        sleep_time,         # type: int
        backoff_threshold,  # type: int
        backoff_multiplier, # type: int
        max_sleep_time,     # type: int
        jitter_percent,     # type: int
    ) -> 'None':
        self.max_retries = max_retries
        self.sleep_time = sleep_time
        self.backoff_threshold = backoff_threshold
        self.backoff_multiplier = backoff_multiplier
        self.max_sleep_time = max_sleep_time
        self.jitter_percent = jitter_percent

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict', defaults:'any_') -> 'RetryPolicy':
        """ Builds a policy out of a config, falling back to the given default set
        for whatever the config does not say.
        """
        out = RetryPolicy(
            _resolve(config, _retry.Field_Max_Retries, defaults.Default_Max_Retries),
            _resolve(config, _retry.Field_Sleep_Time, defaults.Default_Sleep_Time),
            _resolve(config, _retry.Field_Backoff_Threshold, defaults.Default_Backoff_Threshold),
            _resolve(config, _retry.Field_Backoff_Multiplier, defaults.Default_Backoff_Multiplier),
            defaults.Max_Sleep_Time,
            defaults.Jitter_Percent,
        )
        return out

# ################################################################################################################################
# ################################################################################################################################

def _resolve(config:'stranydict', name:'str', default:'int') -> 'int':
    """ Returns one retry setting from a config, or the given default.
    """
    out = config.get(name)

    if out is None:
        out = default

    return out

# ################################################################################################################################

def get_first_sleep_time(policy:'RetryPolicy') -> 'int':
    """ How long the first sleep is - the configured sleep time, held under both the per-sleep ceiling and the total budget.
    """
    out = min(policy.sleep_time, policy.max_sleep_time, policy.backoff_threshold)
    return out

# ################################################################################################################################

def get_next_sleep_time(policy:'RetryPolicy', current_sleep_time:'int', total_sleep_time:'int') -> 'int':
    """ How long the sleep after the one just made is - it grows by the multiplier but is held under both
    the per-sleep ceiling and whatever is left of the total budget, so a loop cannot overshoot the threshold,
    and it is never no time at all, which would turn a loop into a tight one against an endpoint that is unwell.
    """
    next_sleep_time = current_sleep_time * policy.backoff_multiplier
    remaining = policy.backoff_threshold - total_sleep_time
    out = min(next_sleep_time, policy.max_sleep_time, remaining)

    if out <= 0:
        out = Minimum_Sleep_Time

    return out

# ################################################################################################################################
# ################################################################################################################################
