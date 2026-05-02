# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
from dataclasses import dataclass

# Zato
from zato.common.rate_limiting.common import RateLimitError
from zato.common.rate_limiting.fixed_window import FixedWindowConfig
from zato.common.rate_limiting.token_bucket import TokenBucketConfig

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
        entries = [CIDREntry.from_string(value) for value in cidr_list]

        out = class_()
        out.entries             = entries
        out.token_bucket_config = token_bucket_config
        out.fixed_window_config = fixed_window_config
        return out

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

class CIDRMatcher:
    """ Holds an ordered list of CIDR rules and resolves client IPs to the first matching rule.
    """

    def __init__(self) -> 'None':
        self._rules:'list[CIDRRule]' = []

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
