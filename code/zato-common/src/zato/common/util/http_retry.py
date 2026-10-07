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
from zato.common.util.retry import get_first_sleep_time, get_next_sleep_time
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_
    from zato.common.util.retry import RetryPolicy
    any_ = any_
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# The header an endpoint answers a rate-limited request with to say how long to wait
# before making the next one.
Retry_After_Header = 'Retry-After'

# ################################################################################################################################
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
    current_sleep_time = get_first_sleep_time(policy)

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

        current_sleep_time = get_next_sleep_time(policy, current_sleep_time, total_sleep_time)

# ################################################################################################################################
# ################################################################################################################################
