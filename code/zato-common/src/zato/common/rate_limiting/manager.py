# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

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

logger = logging.getLogger('zato_rate_limiting')

matcher_dict = dict[int, SlottedCIDRMatcher]

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManager:
    """ Holds per-channel and per-sec-def SlottedCIDRMatcher instances and shared token bucket and fixed window registries.
    """

    def __init__(self) -> 'None':
        self._channel_matchers:'matcher_dict' = {}
        self._sec_def_matchers:'matcher_dict' = {}
        self._token_buckets = TokenBucketRegistry()
        self._fixed_windows = FixedWindowRegistry()

# ################################################################################################################################

    def set_channel_config(self, channel_id:'int', rule_dicts:'strdictlist') -> 'None':
        """ Parses and stores rate-limiting rules for a channel, replacing any previous config.
        """
        logger.info('set_channel_config; channel_id:%s, rule_count:%s, rule_dicts:%s',
            channel_id, len(rule_dicts), rule_dicts)
        matcher = SlottedCIDRMatcher()
        matcher.replace_all(rule_dicts)
        self._channel_matchers[channel_id] = matcher

# ################################################################################################################################

    def check(self, channel_id:'int', client_ip:'str', now_us:'int', key_prefix:'str'='') -> 'SlottedCheckResult | None':
        """ Checks rate limits for the given channel and client IP.
        """
        matcher = self._channel_matchers.get(channel_id)

        if matcher is None:
            logger.info('check; channel_id:%s, no matcher found', channel_id)
            return None

        result = matcher.check(client_ip, self._token_buckets, self._fixed_windows, now_us, key_prefix)

        logger.info('check; channel_id:%s, client_ip:%s, key_prefix:%s, result:%s',
            channel_id, client_ip, key_prefix, result)

        return result

# ################################################################################################################################

    def has_channel(self, channel_id:'int') -> 'bool':
        """ Returns True if the channel has any rate-limiting config.
        """
        return channel_id in self._channel_matchers

# ################################################################################################################################

    def remove_channel(self, channel_id:'int') -> 'None':
        """ Removes rate-limiting config for a channel.
        """
        self._channel_matchers.pop(channel_id, None)

# ################################################################################################################################

    def clear_rule_counters(self, channel_id:'int', rule_index:'int', key_prefix:'str'='') -> 'None':
        """ Clears all token bucket and fixed window counters for a specific rule of a channel.
        """
        matcher = self._channel_matchers.get(channel_id)

        if matcher is None:
            return

        rule = matcher._rules[rule_index]

        for entry in rule.entries:
            prefix = f'{key_prefix}{entry.key}:'
            self._token_buckets.remove_by_prefix(prefix)
            self._fixed_windows.remove_by_prefix(prefix)

# ################################################################################################################################

    def set_sec_def_config(self, sec_def_id:'int', rule_dicts:'strdictlist') -> 'None':
        """ Parses and stores rate-limiting rules for a security definition, replacing any previous config.
        """
        logger.info('set_sec_def_config; sec_def_id:%s (type:%s), rule_count:%s, rule_dicts:%s',
            sec_def_id, type(sec_def_id).__name__, len(rule_dicts), rule_dicts)
        matcher = SlottedCIDRMatcher()
        matcher.replace_all(rule_dicts)
        self._sec_def_matchers[sec_def_id] = matcher

# ################################################################################################################################

    def check_sec_def(self, sec_def_id:'int', client_ip:'str', now_us:'int', key_prefix:'str'='') -> 'SlottedCheckResult | None':
        """ Checks rate limits for the given security definition and client IP.
        """
        matcher = self._sec_def_matchers.get(sec_def_id)

        if matcher is None:
            logger.info('check_sec_def; sec_def_id:%s (type:%s), no matcher found, known_ids:%s',
                sec_def_id, type(sec_def_id).__name__, list(self._sec_def_matchers.keys()))
            return None

        result = matcher.check(client_ip, self._token_buckets, self._fixed_windows, now_us, key_prefix)

        logger.info('check_sec_def; sec_def_id:%s, client_ip:%s, key_prefix:%s, result:%s',
            sec_def_id, client_ip, key_prefix, result)

        return result

# ################################################################################################################################

    def has_sec_def(self, sec_def_id:'int') -> 'bool':
        """ Returns True if the security definition has any rate-limiting config.
        """
        return sec_def_id in self._sec_def_matchers

# ################################################################################################################################

    def remove_sec_def(self, sec_def_id:'int') -> 'None':
        """ Removes rate-limiting config for a security definition.
        """
        self._sec_def_matchers.pop(sec_def_id, None)

# ################################################################################################################################

    def clear_sec_def_rule_counters(self, sec_def_id:'int', rule_index:'int', key_prefix:'str'='') -> 'None':
        """ Clears all token bucket and fixed window counters for a specific rule of a security definition.
        """
        matcher = self._sec_def_matchers.get(sec_def_id)

        if matcher is None:
            return

        rule = matcher._rules[rule_index]

        for entry in rule.entries:
            prefix = f'{key_prefix}{entry.key}:'
            self._token_buckets.remove_by_prefix(prefix)
            self._fixed_windows.remove_by_prefix(prefix)

# ################################################################################################################################
# ################################################################################################################################
