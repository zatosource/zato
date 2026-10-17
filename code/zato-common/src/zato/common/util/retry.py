# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How many times a failed attempt is retried and how long to wait between attempts - shared by outgoing connections
# and by the push delivery of published messages, each with a default set of its own.

# stdlib
from datetime import timedelta
from random import uniform

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    datetime = datetime
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# The shortest sleep to fall back to when backing off would otherwise sleep for no time at all,
# which would turn the loop into a tight one against an endpoint that is already unwell.
Minimum_Sleep_Time = 1

# The schedule of the AMQP-backed topics' delivery - the first attempts sleep for the shorter time, the later ones
# for the longer, and this many attempts is where the switch is.
_early_attempt_count = 12
_early_sleep_time = 5.0
_late_sleep_time = 10.0

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

def get_remaining_time(start_time:'datetime', max_seconds:'int') -> 'timedelta':
    """ How much of a time budget that started at the given time is left.
    """
    max_duration = timedelta(seconds=max_seconds)
    elapsed = utcnow() - start_time
    out = max_duration - elapsed

    return out

# ################################################################################################################################

def get_sleep_time(
    start_time:'datetime',
    max_seconds:'int',
    attempt_number:'int',
    jitter_range:'float'=2.0,
) -> 'float':
    """ How long to sleep before the given attempt of a delivery running against a time budget - no time at all
    once the budget is spent or when the sleep would not fit in what is left of it.
    """
    time_remaining = get_remaining_time(start_time, max_seconds)
    time_remaining_seconds = max(0, time_remaining.total_seconds())

    if time_remaining_seconds <= 0:
        return 0.0

    if attempt_number <= _early_attempt_count:
        base_sleep = _early_sleep_time
    else:
        base_sleep = _late_sleep_time

    jitter = uniform(0, jitter_range)
    out = base_sleep + jitter

    if out > time_remaining_seconds:
        return 0.0

    return out

# ################################################################################################################################
# ################################################################################################################################
