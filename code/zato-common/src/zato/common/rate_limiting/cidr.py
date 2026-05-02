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

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CIDREntry:
    """ A single parsed CIDR block with its normalised string key.
    """
    network: 'ipaddress.IPv4Network | ipaddress.IPv6Network'
    key:     'str'

    @classmethod
    def from_string(class_:'type[CIDREntry]', value:'str') -> 'CIDREntry': # type: ignore
        """ Parses a CIDR string and builds an entry with the normalised network and its string key.
        """
        network = parse_cidr(value)

        out = class_()
        out.network = network
        out.key     = str(network)
        return out

# ################################################################################################################################
# ################################################################################################################################

def parse_cidr(value:'str') -> 'ipaddress.IPv4Network | ipaddress.IPv6Network':
    """ Parses a CIDR string into a network object. Accepts inputs like '10.0.0.5/24' by normalising to '10.0.0.0/24'.
    """
    try:
        out = ipaddress.ip_network(value, strict=False)
        return out

    except ValueError:
        raise RateLimitError(f'Invalid CIDR notation: {value}')

# ################################################################################################################################

def parse_client_ip(value:'str') -> 'ipaddress.IPv4Address | ipaddress.IPv6Address':
    """ Parses a client IP address string into an address object.
    """
    try:
        out = ipaddress.ip_address(value)
        return out

    except ValueError:
        raise RateLimitError(f'Invalid IP address: {value}')

# ################################################################################################################################
# ################################################################################################################################
