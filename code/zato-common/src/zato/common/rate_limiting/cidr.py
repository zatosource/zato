# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
from dataclasses import dataclass

# Zato
from zato.common.rate_limiting.common import RateLimitError, TimeRange
from zato.common.rate_limiting.fixed_window import FixedWindowCheckResult, FixedWindowConfig, FixedWindowRegistry
from zato.common.rate_limiting.token_bucket import CheckResult, TokenBucketConfig, TokenBucketRegistry

if 0:
    from zato.common.typing_ import strlist

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

cidr_entry_list  = list[CIDREntry]
time_range_list  = list[TimeRange]

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

    def match(self, address:'ipaddress.IPv4Address | ipaddress.IPv6Address') -> 'CIDREntry | None':
        """ Returns the first entry whose network contains the address, or None.
        """

        # Walk entries in order ..
        for entry in self.entries:

            # .. skip entries of a different address family ..
            if entry.network.version != address.version:
                continue

            # .. return the first match.
            if address in entry.network:
                return entry

        return None

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
# ################################################################################################################################
