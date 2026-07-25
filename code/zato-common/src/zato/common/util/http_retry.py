# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import sleep

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

# Zato
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict
    any_ = any_
    callable_ = callable_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

_retry = HTTP_SOAP.Retry

# The shortest sleep to fall back to when backing off would otherwise sleep for no time at all,
# which would turn the loop into a tight one against an endpoint that is already unwell.
Minimum_Sleep_Time = 1

# ################################################################################################################################
# ################################################################################################################################

class RetryPolicy:
    """ How many times a transport failure is retried and how long to wait between attempts.

    The four settings live in a connection's opaque attributes and are shown by the dashboard for
    both outgoing REST and outgoing SOAP. Keeping them in one object is what lets the REST and the
    declarative SOAP path share the same loop - the SOAP path used to show the four fields and then
    send through a code path that had no retries in it at all.
    """
    __slots__ = 'max_retries', 'sleep_time', 'backoff_threshold', 'backoff_multiplier'

    def __init__(
        self,
        max_retries,       # type: int
        sleep_time,        # type: int
        backoff_threshold, # type: int
        backoff_multiplier # type: int
    ) -> 'None':
        self.max_retries = max_retries
        self.sleep_time = sleep_time
        self.backoff_threshold = backoff_threshold
        self.backoff_multiplier = backoff_multiplier

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict') -> 'RetryPolicy':
        """ Builds a policy out of a connection's config, falling back to the shared defaults
        for a connection that was never configured with retries.
        """
        out = RetryPolicy(
            _resolve(config, _retry.Field_Max_Retries, _retry.Default_Max_Retries),
            _resolve(config, _retry.Field_Sleep_Time, _retry.Default_Sleep_Time),
            _resolve(config, _retry.Field_Backoff_Threshold, _retry.Default_Backoff_Threshold),
            _resolve(config, _retry.Field_Backoff_Multiplier, _retry.Default_Backoff_Multiplier),
        )
        return out

# ################################################################################################################################
# ################################################################################################################################

def _resolve(config:'stranydict', name:'str', default:'int') -> 'int':
    """ Returns one retry setting from a connection's config, or the shared default.
    """
    out = config.get(name)

    if out is None:
        out = default

    return out

# ################################################################################################################################

def send_with_retry(policy:'RetryPolicy', send:'callable_', cid:'str', label:'str') -> 'any_':
    """ Runs send, retrying it on a transport-level failure for as long as the policy allows.

    Only timeouts and connection errors are retried. A response that arrived, whatever its status
    code, is the endpoint's answer and belongs to the caller, and an application-level failure is
    not something a second identical request would resolve.
    """
    attempt = 0
    total_sleep_time = 0
    current_sleep_time = policy.sleep_time

    while True:
        try:
            return send()

        except (RequestsTimeout, RequestsConnectionError) as e:

            # Both the attempt count and the total time spent sleeping are caps, so a policy with a
            # generous retry count still gives up once it has waited as long as it is allowed to.
            can_retry_by_attempt = attempt < policy.max_retries
            can_retry_by_time = total_sleep_time < policy.backoff_threshold

            if not (can_retry_by_attempt and can_retry_by_time):
                raise

            attempt += 1
            logger.warning('%s retry cid=%s; attempt=%s; sleep=%s; error=%s',
                label, cid, attempt, current_sleep_time, e)

            sleep(current_sleep_time)
            total_sleep_time += current_sleep_time

            # The next sleep grows by the multiplier but is held under both the per-sleep ceiling
            # and whatever is left of the total budget, so the loop cannot overshoot the threshold.
            next_sleep_time = current_sleep_time * policy.backoff_multiplier
            remaining = policy.backoff_threshold - total_sleep_time
            current_sleep_time = min(next_sleep_time, _retry.Max_Sleep_Time, remaining)

            if current_sleep_time <= 0:
                current_sleep_time = Minimum_Sleep_Time

# ################################################################################################################################
# ################################################################################################################################
