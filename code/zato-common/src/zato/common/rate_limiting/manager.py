# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rate_limiting.cidr import SlottedCIDRMatcher
from zato.common.rate_limiting.fixed_window import FixedWindowRegistry
from zato.common.rate_limiting.token_bucket import TokenBucketRegistry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rate_limiting.cidr import SlottedCheckResult
    from zato.common.typing_ import strdictlist

# ################################################################################################################################
# ################################################################################################################################

channel_matcher_dict = dict[int, SlottedCIDRMatcher]

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManager:
    """ Holds per-channel SlottedCIDRMatcher instances and shared token bucket and fixed window registries.
    """

    def __init__(self) -> 'None':
        self._matchers:'channel_matcher_dict' = {}
        self._token_buckets = TokenBucketRegistry()
        self._fixed_windows = FixedWindowRegistry()

# ################################################################################################################################

    def set_channel_config(self, channel_id:'int', rule_dicts:'strdictlist') -> 'None':
        """ Parses and stores rate-limiting rules for a channel, replacing any previous config.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all(rule_dicts)
        self._matchers[channel_id] = matcher

# ################################################################################################################################

    def check(self, channel_id:'int', client_ip:'str', now_us:'int', key_prefix:'str'='') -> 'SlottedCheckResult | None':
        """ Checks rate limits for the given channel and client IP.

        Returns None if the channel has no rate-limiting config or the client IP does not match any rule.
        """
        matcher = self._matchers.get(channel_id)

        if matcher is None:
            return None

        result = matcher.check(client_ip, self._token_buckets, self._fixed_windows, now_us, key_prefix)

        return result

# ################################################################################################################################

    def has_channel(self, channel_id:'int') -> 'bool':
        """ Returns True if the channel has any rate-limiting config.
        """
        return channel_id in self._matchers

# ################################################################################################################################

    def remove_channel(self, channel_id:'int') -> 'None':
        """ Removes rate-limiting config for a channel.
        """
        self._matchers.pop(channel_id, None)

# ################################################################################################################################

    def clear_rule_counters(self, channel_id:'int', rule_index:'int', key_prefix:'str'='') -> 'None':
        """ Clears all token bucket and fixed window counters for a specific rule of a channel.
        """
        matcher = self._matchers.get(channel_id)

        if matcher is None:
            return

        rule = matcher._rules[rule_index]

        for entry in rule.entries:
            prefix = f'{key_prefix}{entry.key}:'
            self._token_buckets.remove_by_prefix(prefix)
            self._fixed_windows.remove_by_prefix(prefix)

# ################################################################################################################################
# ################################################################################################################################
