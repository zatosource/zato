# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The headers of a 429 - what a caller over its limit is told about when to come back and how much of its
# quota is left, computed once here so the HTTP channel and the services answering their own 429s agree.

from __future__ import annotations

# stdlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rate_limiting.cidr import SlottedCheckResult
    from zato.common.typing_ import strdict
    SlottedCheckResult = SlottedCheckResult
    strdict = strdict

# ################################################################################################################################
# ################################################################################################################################

# The one header every 429 carries and the two a security definition's limit adds -
# a channel's own limit is infrastructure protection and says nothing about quotas.
Header_Retry_After          = 'Retry-After'
Header_Rate_Limit_Limit     = 'X-RateLimit-Limit'
Header_Rate_Limit_Remaining = 'X-RateLimit-Remaining'

_microseconds_per_second = 1_000_000

# Where a service that answers its own 429s finds the check result of the caller its security definition's
# limit refused - the HTTP channel sets it in the request context only when such a service is behind the channel.
Rate_Limit_Result_Key = 'zato.http.rate_limit.result'

# ################################################################################################################################
# ################################################################################################################################

def _datetime_utcnow() -> 'datetime':
    """ The clock a Retry-After date is computed from - a function so tests can pin it.
    """
    out = datetime.now(timezone.utc)
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RateLimitHeaders:
    """ What a 429 tells its caller - the whole seconds until a retry may succeed and the headers to send.
    """
    retry_after_seconds:'int' = 0
    headers:'strdict' = field(default_factory=dict)

# ################################################################################################################################
# ################################################################################################################################

def get_retry_after_seconds(rate_limit_result:'SlottedCheckResult') -> 'int':
    """ The microseconds of a check result as whole seconds, rounded up so a caller never retries too early.
    """
    retry_after_us = rate_limit_result.retry_after_us
    out = retry_after_us // _microseconds_per_second

    if retry_after_us % _microseconds_per_second:
        out += 1

    return out

# ################################################################################################################################

def build_rate_limit_headers(rate_limit_result:'SlottedCheckResult', *, needs_quota_headers:'bool') -> 'RateLimitHeaders':
    """ The headers of one 429 - Retry-After as an HTTP date and, for a security definition's limit,
    the quota headers saying what the limit is and how much of it remains.
    """
    out = RateLimitHeaders()
    out.retry_after_seconds = get_retry_after_seconds(rate_limit_result)
    out.headers = {}

    now = _datetime_utcnow()
    retry_at = now + timedelta(seconds=out.retry_after_seconds)
    out.headers[Header_Retry_After] = format_datetime(retry_at, usegmt=True)

    if needs_quota_headers:
        out.headers[Header_Rate_Limit_Limit] = str(rate_limit_result.limit)
        out.headers[Header_Rate_Limit_Remaining] = str(rate_limit_result.remaining)

    return out

# ################################################################################################################################
# ################################################################################################################################
