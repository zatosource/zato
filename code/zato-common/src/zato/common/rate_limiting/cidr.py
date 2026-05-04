# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import logging
from dataclasses import dataclass

# Zato
from zato.common.rate_limiting.common import hh_mm_to_minutes, now_us_to_minutes, RateLimitError, time_in_range, TimeRange
from zato.common.rate_limiting.fixed_window import FixedWindowCheckResult, FixedWindowConfig, FixedWindowRegistry
from zato.common.rate_limiting.token_bucket import CheckResult, TokenBucketConfig, TokenBucketRegistry

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_rate_limiting')

if 0:
    from zato.common.typing_ import stranydict, strdictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CIDREntry:
    """ A single parsed CIDR block with its normalised string key.
    """
    network: 'ipaddress.IPv4Network | ipaddress.IPv6Network'
    key:     'str'

    @classmethod
    def from_string(class_:'type[CIDREntry]', value:'str') -> 'CIDREntry': # pyright: ignore[reportSelfClsParameterName]
        """ Parses a CIDR string and builds an entry with the normalised network and its string key.
        """
        network = parse_cidr(value)

        out = class_()
        out.network = network
        out.key     = str(network)

        return out

# ################################################################################################################################
# ################################################################################################################################

cidr_entry_list   = list[CIDREntry]
time_range_list   = list[TimeRange]
slotted_rule_list = list['SlottedCIDRRule']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CIDRRule:
    """ A list of CIDR blocks paired with both a token bucket and a fixed window config.
    """
    entries:             'list[CIDREntry]'
    token_bucket_config: 'TokenBucketConfig'
    fixed_window_config: 'FixedWindowConfig'

    @classmethod
    def from_parts(
        class_:'type[CIDRRule]', # pyright: ignore[reportSelfClsParameterName]
        cidr_list:'list[str]',
        token_bucket_config:'TokenBucketConfig',
        fixed_window_config:'FixedWindowConfig',
        ) -> 'CIDRRule':
        """ Builds a rule from a list of CIDR strings and both limiter configs.
        """
        entries:'list[CIDREntry]' = []

        for value in cidr_list:
            entry = CIDREntry.from_string(value)
            entries.append(entry)

        out = class_()
        out.entries             = entries
        out.token_bucket_config = token_bucket_config
        out.fixed_window_config = fixed_window_config

        return out

# ################################################################################################################################

    def match(self, address:'ipaddress.IPv4Address | ipaddress.IPv6Address') -> 'CIDREntry | None':
        """ Returns the first entry whose network contains the address, or None.
        """

        # Walk entries in order ..
        for entry in self.entries:

            # .. skip entries of a different address family (e.g. IPv6 entry vs IPv4 address) ..
            if entry.network.version != address.version:
                continue

            # .. return the first match.
            if address in entry.network:
                return entry

        return None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SlottedCIDRRule:
    """ A list of CIDR blocks paired with an ordered list of time ranges for rate limiting.

    time_range[0] is always the all-day one (is_all_day=True).
    """

    entries:    'cidr_entry_list'
    time_range: 'time_range_list'

# ################################################################################################################################

    @classmethod
    def from_parts(
        class_:'type[SlottedCIDRRule]', # pyright: ignore[reportSelfClsParameterName]
        cidr_list:'strlist',
        time_range:'time_range_list',
        ) -> 'SlottedCIDRRule':
        """ Builds a rule from a list of CIDR strings and an ordered list of TimeRange objects.
        """

        # The time range list must not be empty ..
        if not time_range:
            raise RateLimitError('time_range must not be empty')

        # .. and the first entry must be the all-day one.
        if not time_range[0].is_all_day:
            raise RateLimitError('time_range[0] must be an all-day entry')

        # Parse CIDR strings into entries ..
        entries:'cidr_entry_list' = []

        for value in cidr_list:
            entry = CIDREntry.from_string(value)
            entries.append(entry)

        out = class_()
        out.entries    = entries
        out.time_range = time_range

        return out

# ################################################################################################################################

    @classmethod
    def from_dict(
        class_:'type[SlottedCIDRRule]', # pyright: ignore[reportSelfClsParameterName]
        data:'stranydict',
        ) -> 'SlottedCIDRRule':
        """ Builds a SlottedCIDRRule from a dict as received from other layers.
        """

        # Parse each time range entry ..
        cidr_list = data['cidr_list']

        raw_time_range = data['time_range']
        time_range:'time_range_list' = []

        for raw_entry in raw_time_range:
            entry = TimeRange.from_dict(raw_entry)
            time_range.append(entry)

        out = class_.from_parts(cidr_list, time_range)
        return out

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':
        """ Serializes this rule to a dict.
        """

        # Build the CIDR list from the parsed entries ..
        cidr_list:'strlist' = []

        for entry in self.entries:
            cidr_list.append(entry.key)

        # .. and serialize each time range.
        time_range:'strdictlist' = []

        for time_range_entry in self.time_range:
            serialized = time_range_entry.to_dict()
            time_range.append(serialized)

        out:'stranydict' = {
            'cidr_list':  cidr_list,
            'time_range': time_range,
        }

        return out

# ################################################################################################################################

    def match(self, address:'ipaddress.IPv4Address | ipaddress.IPv6Address') -> 'CIDREntry | None':
        """ Returns the first entry whose network contains the address, or None.

        An empty entries list means match all IPs - returns a synthetic
        0.0.0.0/0 or ::/0 entry depending on the address family.
        """

        # An empty CIDR list means match all IPs ..
        if not self.entries:
            if address.version == 4:
                return _match_all_v4
            else:
                return _match_all_v6

        # .. otherwise, walk entries in order ..
        for entry in self.entries:

            # .. skip entries of a different address family ..
            if entry.network.version != address.version:
                continue

            # .. return the first match.
            if address in entry.network:
                return entry

        return None

# ################################################################################################################################

    def resolve_time_range(self, now_minutes:'int') -> 'TimeRange':
        """ Returns the first non-disabled time range whose window covers now_minutes.

        Iterates time_range[1:] in user-given order. If no specific range matches,
        returns time_range[0] (the all-day default).
        """

        # Walk the specific (non-all-day) entries in order ..
        for time_range_entry in self.time_range[1:]:

            # .. skip disabled entries ..
            if time_range_entry.disabled:
                continue

            # .. check if the current time is within this entry's window.
            from_minutes = hh_mm_to_minutes(time_range_entry.time_from)
            to_minutes   = hh_mm_to_minutes(time_range_entry.time_to)

            if time_in_range(now_minutes, from_minutes, to_minutes):
                out = time_range_entry
                break

        # .. no specific range matched, use the all-day default.
        else:
            out = self.time_range[0]

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CIDRMatch:
    """ The result of resolving a client IP - pairs the matched rule with the specific entry that matched.
    """
    rule:  'CIDRRule'
    entry: 'CIDREntry'

    @property
    def key(self) -> 'str':
        """ The normalised CIDR string to use as the registry key.
        """
        return self.entry.key

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CIDRCheckResult:
    """ Combined result of checking a client IP against both rate limiters.
    """
    is_allowed:          'bool'
    matched_key:         'str'
    token_bucket_result: 'CheckResult'
    fixed_window_result: 'FixedWindowCheckResult'

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcher:
    """ Holds an ordered list of CIDR rules and resolves client IPs to the first matching rule.
    """

    def __init__(self) -> 'None':
        self._rules:'list[CIDRRule]' = []

# ################################################################################################################################

    def __len__(self) -> 'int':
        return len(self._rules)

# ################################################################################################################################

    def add_rule(
        self,
        cidr_list:'list[str]',
        token_bucket_config:'TokenBucketConfig',
        fixed_window_config:'FixedWindowConfig',
        ) -> 'None':
        """ Creates a CIDRRule from the given parameters and appends it to the list.
        """
        rule = CIDRRule.from_parts(cidr_list, token_bucket_config, fixed_window_config)
        self._rules.append(rule)

# ################################################################################################################################

    def resolve(self, client_ip:'str') -> 'CIDRMatch | None':
        """ Parses the client IP and iterates rules top-to-bottom, returning the first match.
        """

        # Parse the raw IP string ..
        address = parse_client_ip(client_ip)

        # .. walk rules in insertion order ..
        for rule in self._rules:
            entry = rule.match(address)

            # .. if a rule matches, wrap it in a CIDRMatch and return immediately.
            if entry is not None:
                out = CIDRMatch()
                out.rule  = rule
                out.entry = entry
                return out

        return None

# ################################################################################################################################

    def check(
        self,
        client_ip:'str',
        token_bucket_registry:'TokenBucketRegistry',
        fixed_window_registry:'FixedWindowRegistry',
        now_us:'int',
        ) -> 'CIDRCheckResult | None':
        """ Resolves the client IP to a rule, checks both limiters, and returns the combined result.
        """

        # Find which rule (if any) applies to this client ..
        match = self.resolve(client_ip)

        if match is None:
            return None

        # .. check both limiters using the matched CIDR block as the registry key ..
        key  = match.key
        rule = match.rule

        token_bucket_result = token_bucket_registry.check_inner(key, rule.token_bucket_config, now_us)
        fixed_window_result = fixed_window_registry.check_inner(key, rule.fixed_window_config, now_us)

        # .. combine into a single result.
        out = CIDRCheckResult()
        out.is_allowed          = token_bucket_result.is_allowed and fixed_window_result.is_allowed
        out.matched_key         = key
        out.token_bucket_result = token_bucket_result
        out.fixed_window_result = fixed_window_result

        return out

# ################################################################################################################################

    def remove_rule(self, index:'int') -> 'None':
        """ Removes the rule at the given index.
        """
        del self._rules[index]

# ################################################################################################################################

    def is_empty(self) -> 'bool':
        """ Returns True if no rules are registered.
        """
        return not self._rules

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes all rules.
        """
        self._rules.clear()

# ################################################################################################################################

    def replace_all(self, rule_definitions:'list[tuple[list[str], TokenBucketConfig, FixedWindowConfig]]') -> 'None':
        """ Atomically replaces all rules with a new ordered list.
        """

        # Build the new list first so that a parsing error does not leave us in a half-updated state ..
        new_rules:'list[CIDRRule]' = []

        for cidr_list, token_bucket_config, fixed_window_config in rule_definitions:
            rule = CIDRRule.from_parts(cidr_list, token_bucket_config, fixed_window_config)
            new_rules.append(rule)

        # .. then swap in one shot.
        self._rules = new_rules

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SlottedCIDRMatch:
    """ The result of resolving a client IP against a SlottedCIDRMatcher.
    """

    rule:  'SlottedCIDRRule'
    entry: 'CIDREntry'

    @property
    def key(self) -> 'str':
        """ The normalised CIDR string to use as the registry key.
        """
        return self.entry.key

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SlottedCheckResult:
    """ Result of checking a client IP against a SlottedCIDRMatcher.
    """

    is_disallowed:  'bool'
    is_allowed:     'bool'
    retry_after_us: 'int'
    matched_key:    'str'

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRMatcher:
    """ Holds an ordered list of SlottedCIDRRule objects and resolves client IPs to the first matching rule.
    """

    def __init__(self) -> 'None':
        self._rules:'slotted_rule_list' = []

# ################################################################################################################################

    def __len__(self) -> 'int':
        return len(self._rules)

# ################################################################################################################################

    def resolve(self, client_ip:'str') -> 'SlottedCIDRMatch | None':
        """ Parses the client IP and iterates rules top-to-bottom, returning the first match.
        """

        # Parse the raw IP string ..
        address = parse_client_ip(client_ip)

        # .. walk rules in insertion order ..
        for rule in self._rules:
            entry = rule.match(address)

            if entry is not None:
                out = SlottedCIDRMatch()
                out.rule  = rule
                out.entry = entry
                return out

        return None

# ################################################################################################################################

    def replace_all(self, rule_dicts:'strdictlist') -> 'None':
        """ Atomically replaces all rules by parsing from UI/opaque1 JSON dicts.
        """

        # Build the new list first so that a parsing error does not leave us in a half-updated state ..
        new_rules:'slotted_rule_list' = []

        for rule_dict in rule_dicts:
            rule = SlottedCIDRRule.from_dict(rule_dict)
            new_rules.append(rule)

        # .. then swap in one shot.
        self._rules = new_rules

# ################################################################################################################################

    def to_list(self) -> 'strdictlist':
        """ Serializes all rules back to a list of dicts for JSON storage.
        """
        out:'strdictlist' = []

        for rule in self._rules:
            serialized = rule.to_dict()
            out.append(serialized)

        return out

# ################################################################################################################################

    def is_empty(self) -> 'bool':
        """ Returns True if no rules are registered.
        """
        return not self._rules

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes all rules.
        """
        self._rules.clear()

# ################################################################################################################################

    def check(
        self,
        client_ip:'str',
        token_bucket_registry:'TokenBucketRegistry',
        fixed_window_registry:'FixedWindowRegistry',
        now_us:'int',
        key_prefix:'str' = '',
        ) -> 'SlottedCheckResult | None':
        """ Resolves the client IP to a rule and time range, then checks both limiters.
        """

        # Find which rule (if any) applies to this client ..
        match = self.resolve(client_ip)

        if match is None:
            logger.info('check; client_ip:%s, no matching rule', client_ip)
            return None

        # .. determine which time range is active right now ..
        now_minutes  = now_us_to_minutes(now_us)
        time_range   = match.rule.resolve_time_range(now_minutes)

        logger.info('check; client_ip:%s, matched_key:%s, time_range is_all_day:%s, disabled:%s, disallowed:%s, rate:%s, burst:%s, limit:%s, limit_unit:%s',
            client_ip, match.key, time_range.is_all_day, time_range.disabled, time_range.disallowed,
            time_range.rate, time_range.burst, time_range.limit, time_range.limit_unit)

        # .. if the resolved time range is disabled, no rate limiting applies ..
        if time_range.disabled:
            logger.info('check; client_ip:%s, time_range disabled, skipping', client_ip)
            return None

        cidr_key     = match.key

        # .. build a composite key so each time range has its own counters ..
        time_range_index = match.rule.time_range.index(time_range)
        composite_key    = f'{key_prefix}{cidr_key}:{time_range_index}'

        # Our response to produce
        out = SlottedCheckResult()
        out.matched_key = composite_key

        # .. if this time range is disallowed, the caller must kill the TCP connection immediately ..
        if time_range.disallowed:
            out.is_disallowed  = True
            out.is_allowed     = False
            out.retry_after_us = 0
            logger.info('check; client_ip:%s, composite_key:%s, disallowed', client_ip, composite_key)
            return out

        out.is_disallowed = False

        # .. otherwise, check both limiters ..
        token_bucket_config = TokenBucketConfig.from_parts(time_range.rate, time_range.burst)
        fixed_window_config = FixedWindowConfig.from_parts(time_range.limit, time_range.limit_unit)

        token_bucket_result = token_bucket_registry.check_inner(composite_key, token_bucket_config, now_us)
        fixed_window_result = fixed_window_registry.check_inner(composite_key, fixed_window_config, now_us)

        out.is_allowed = token_bucket_result.is_allowed and fixed_window_result.is_allowed

        # .. pick the longer retry-after of the two.
        out.retry_after_us = max(token_bucket_result.retry_after_us, fixed_window_result.retry_after_us)

        logger.info('check; client_ip:%s, composite_key:%s, is_allowed:%s, tb_allowed:%s, fw_allowed:%s, retry_after_us:%s',
            client_ip, composite_key, out.is_allowed, token_bucket_result.is_allowed,
            fixed_window_result.is_allowed, out.retry_after_us)

        return out

# ################################################################################################################################
# ################################################################################################################################

def parse_cidr(value:'str') -> 'ipaddress.IPv4Network | ipaddress.IPv6Network':
    """ Parses a CIDR string into a network object. Accepts inputs like '10.0.0.5/24' by normalising to '10.0.0.0/24'.
    """
    try:
        out = ipaddress.ip_network(value, strict=False)

    except ValueError:
        raise RateLimitError(f'Invalid CIDR notation: {value}') from None

    return out

# ################################################################################################################################

def parse_client_ip(value:'str') -> 'ipaddress.IPv4Address | ipaddress.IPv6Address':
    """ Parses a client IP address string into an address object.
    """
    try:
        out = ipaddress.ip_address(value)

    except ValueError:
        raise RateLimitError(f'Invalid IP address: {value}') from None

    return out

# ################################################################################################################################

# Synthetic match-all entries for rules with an empty CIDR list,
# defined after parse_cidr is available.
_match_all_v4 = CIDREntry.from_string('0.0.0.0/0')
_match_all_v6 = CIDREntry.from_string('::/0')

# ################################################################################################################################
# ################################################################################################################################
