# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second, Microtokens_Per_Token, RateLimitError

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CheckResult:
    """ Result of a rate limit check.
    """
    is_allowed:       'bool'
    tokens_remaining: 'int'
    retry_after_us:   'int'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TokenBucketConfig:
    """ Configuration for a single token bucket.
    """
    rate:                     'int'
    burst_allowed:            'int'
    refill_rate_micro_per_us: 'int'

    @classmethod
    def from_parts(class_, rate:'int', burst_allowed:'int') -> 'TokenBucketConfig': # pyright: ignore[reportSelfClsParameterName]
        """ Creates a config from rate (tokens/second) and burst capacity.
        """
        out = class_()
        out.rate                     = rate
        out.burst_allowed            = burst_allowed
        out.refill_rate_micro_per_us = rate

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _BucketState:
    """ Internal bucket state stored per key.
    """
    tokens_remaining_micro: 'int'
    last_refill_us:         'int'

# ################################################################################################################################
# ################################################################################################################################

def _consume_or_deny(
    bucket:'_BucketState',
    config:'TokenBucketConfig',
    burst_micro:'int',
    now_us:'int',
    ) -> 'CheckResult':
    """ Refills tokens based on elapsed time, clamps to burst limit,
    then either deducts one token (allow) or records the deficit (deny).
    """

    # Our response to produce
    out = CheckResult()

    #  Compute how many microtokens accumulated since the last refill ..
    elapsed_us  = max(0, now_us - bucket.last_refill_us)
    added_micro = min(elapsed_us * config.refill_rate_micro_per_us, burst_micro)
    refilled    = min(bucket.tokens_remaining_micro + added_micro, burst_micro)

    # .. record this moment as the new refill baseline ..
    bucket.last_refill_us = now_us

    # .. if at least one full token is available, consume it and allow ..
    if refilled >= Microtokens_Per_Token:
        new_tokens = refilled - Microtokens_Per_Token
        bucket.tokens_remaining_micro = new_tokens

        out.is_allowed       = True
        out.tokens_remaining = new_tokens // Microtokens_Per_Token
        out.retry_after_us   = 0

    # .. otherwise the bucket is empty, so record what is left ..
    else:
        bucket.tokens_remaining_micro = refilled

        # .. figure out how long the caller needs to wait for one full token;
        # .. if the refill rate is positive, compute from the deficit ..
        deficit_micro = Microtokens_Per_Token - refilled

        if config.refill_rate_micro_per_us > 0:
            retry_us = deficit_micro // config.refill_rate_micro_per_us + 1

        # .. otherwise no tokens will ever arrive, so fall back to one second ..
        else:
            retry_us = Microseconds_Per_Second

        # .. and deny the request.
        out.is_allowed       = False
        out.tokens_remaining = 0
        out.retry_after_us   = retry_us

    return out

# ################################################################################################################################
# ################################################################################################################################

class TokenBucketRegistry:
    """ Top-level rate limiter registry holding all buckets across all keys.
    """

    def __init__(self) -> 'None':
        self._buckets:'dict[str, _BucketState]' = {}

# ################################################################################################################################

    def __len__(self) -> 'int':
        return len(self._buckets)

# ################################################################################################################################

    def check_inner(self, key:'str', config:'TokenBucketConfig', now_us:'int') -> 'CheckResult':
        """ Core check logic, separated from any framework wrapper for testability.
        """

        #  Pre-compute the burst capacity in microtokens ..
        burst_micro = config.burst_allowed * Microtokens_Per_Token

        if burst_micro < config.burst_allowed:
            raise RateLimitError(
                f'Overflow: burst_allowed ({config.burst_allowed}) * Microtokens_Per_Token'
            )

        # .. look up or create the per-key bucket ..
        bucket = self._buckets.get(key)

        if bucket is None:
            bucket = _BucketState()
            bucket.tokens_remaining_micro = burst_micro
            bucket.last_refill_us         = now_us
            self._buckets[key] = bucket

        # .. and decide whether the request is allowed.
        out = _consume_or_deny(bucket, config, burst_micro, now_us)

        return out

# ################################################################################################################################

    def remove(self, key:'str') -> 'None':
        """ Removes the bucket for the given key, if any.
        """
        _ = self._buckets.pop(key, None)

# ################################################################################################################################

    def is_empty(self) -> 'bool':
        """ Returns True if no buckets are registered.
        """
        return not self._buckets

# ################################################################################################################################

    def remove_by_prefix(self, prefix:'str') -> 'None':
        """ Removes all buckets whose key starts with the given prefix.
        """
        keys_to_remove = [key for key in self._buckets if key.startswith(prefix)]
        for key in keys_to_remove:
            del self._buckets[key]

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes all buckets.
        """
        self._buckets.clear()

# ################################################################################################################################
# ################################################################################################################################
