# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from email.utils import parsedate_to_datetime
from http.client import TOO_MANY_REQUESTS
from logging import getLogger
from time import sleep

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.time_ import utcnow

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

# The header an endpoint answers a rate-limited request with to say how long to wait
# before making the next one.
Retry_After_Header = 'Retry-After'

# ################################################################################################################################
# ################################################################################################################################

class RetryPolicy:
    """ How many times a failed attempt is retried and how long to wait between attempts.

    The four settings live in a connection's opaque attributes and are shown by the dashboard for
    both outgoing REST and outgoing SOAP. Keeping them in one object is what lets the REST and the
    declarative SOAP path share one loop.
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

def get_retry_after(response:'any_') -> 'int':
    """ Returns how many seconds an endpoint asked us to wait before the next attempt,
    or zero when it did not say. The header carries either a number of seconds or a date.
    """
    value = response.headers.get(Retry_After_Header)

    if not value:
        return 0

    value = value.strip()

    # A plain number is a number of seconds to wait ..
    if value.isdigit():
        out = int(value)
        return out

    # .. anything else is a date to wait until, and an endpoint that spells it in a way
    # .. the standard does not describe is treated as one that said nothing ..
    try:
        when = parsedate_to_datetime(value)
    except ValueError:
        logger.info('Ignoring unparseable %s header -> `%s`', Retry_After_Header, value)
        return 0

    # .. a date that has already passed means there is nothing left to wait for.
    seconds = int((when - utcnow()).total_seconds())

    if seconds < 0:
        seconds = 0

    out = seconds
    return out

# ################################################################################################################################

def send_with_retry(policy:'RetryPolicy', send:'callable_', cid:'str', label:'str') -> 'any_':
    """ Runs send, retrying it for as long as the policy allows.

    Timeouts and connection errors are retried, and so is a response that says the request was made
    too soon rather than that it was wrong - such an endpoint may say how long to wait, and that
    instruction is followed in place of the policy's own schedule. Any other response is the
    endpoint's answer and belongs to the caller, an application-level failure not being something
    a second identical request would resolve.
    """
    attempt = 0
    total_sleep_time = 0
    current_sleep_time = policy.sleep_time

    while True:

        # What the attempt produced - a response, or the error that stopped one from arriving
        response = None
        error = None

        try:
            response = send()
        except (RequestsTimeout, RequestsConnectionError) as e:
            error = e

        # An answer other than a rate-limited one goes straight back to the caller ..
        if response is not None:
            if response.status_code != TOO_MANY_REQUESTS:
                return response

        # .. otherwise both the attempt count and the total time spent sleeping are caps, so a policy
        # .. with a generous retry count still gives up once it has waited as long as it is allowed to ..
        needs_retry = False

        if attempt < policy.max_retries:
            if total_sleep_time < policy.backoff_threshold:
                needs_retry = True

        # .. with nothing left to try, a failure to send is raised and a rate-limited response
        # .. is returned, that being the endpoint's own answer ..
        if not needs_retry:
            if error:
                raise error
            return response

        # .. an endpoint that said how long to wait is waited for that long instead of for what the
        # .. policy's schedule says, unless the wait it asked for does not fit in the total budget,
        # .. in which case there is no point in retrying at all ..
        if response is not None:
            retry_after = get_retry_after(response)
            if retry_after:
                remaining_budget = policy.backoff_threshold - total_sleep_time
                if retry_after > remaining_budget:
                    return response
                current_sleep_time = retry_after

        attempt += 1

        if error:
            reason = error
        else:
            reason = f'HTTP {TOO_MANY_REQUESTS}'

        logger.warning('%s retry cid=%s; attempt=%s; sleep=%s; reason=%s',
            label, cid, attempt, current_sleep_time, reason)

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
