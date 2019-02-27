# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import itertools

# ipaddress
from ipaddress import ip_address, ip_network

# netifaces
from netifaces import AF_INET, ifaddresses as net_ifaddresses, interfaces as net_ifaces

# Python 2/3 compatibility
from builtins import bytes
from future.moves.urllib.parse import urlparse
from six import PY2

# ################################################################################################################################

def to_ip_network(adddress):
    """ Converts address to a network object assuming it is feasible at all, otherwise returns None.
    """
    try:
        return ip_network(adddress)
    except ValueError:
        pass
    else:
        return True

# ################################################################################################################################

def ip_list_from_interface(interface, allow_loopback=False):
    """ Return the list of IP address for the given interface, possibly including loopback addresses
    """
    addresses = []
    af_inet = net_ifaddresses(interface).get(AF_INET)

    if af_inet:
        _addresses = [elem.get('addr') for elem in af_inet]

        if PY2:
            _addresses = [elem.decode('utf8') for elem in _addresses]

        for address in _addresses:
            address = ip_address(address)
            if address.is_loopback and not allow_loopback:
                continue

            addresses.append(address)

    return addresses

# ################################################################################################################################

def get_preferred_ip(base_bind, user_prefs):
    """ Given user preferences, iterate over all address in all interfaces and check if any matches what users prefer.
    Note that preferences can include actual names of interfaces, not only IP or IP ranges.
    """

    # First check out if the base address to bind does not already specify a concrete IP.
    # If it does, then this will be the preferred one.
    parsed = urlparse('https://{}'.format(base_bind))
    if parsed.hostname != '0.0.0.0':
        return parsed.hostname

    # What is preferred
    preferred = user_prefs.ip

    # What actually exists in the system
    current_ifaces = net_ifaces()

    # Would be very weird not to have anything, even loopback, but oh well
    if not current_ifaces:
        return None

    current_ifaces.sort()

    current_addresses = [net_ifaddresses(elem).get(AF_INET) for elem in current_ifaces]
    current_addresses = [[elem.get('addr') for elem in x] for x in current_addresses if x]
    current_addresses = list(itertools.chain.from_iterable(current_addresses))

    # Preferences broken out into interfacs and network ranges/IP addresses
    pref_interfaces = [elem for elem in preferred if elem in net_ifaces()]
    pref_networks = [to_ip_network(elem) for elem in preferred]
    pref_networks = [elem for elem in pref_networks if elem]

    # If users prefer a named interface and we have it then we need to return its IP
    for elem in pref_interfaces:

        # If any named interface is found, returns its first IP, if there is any
        ip_list = ip_list_from_interface(elem, user_prefs.allow_loopback)
        if ip_list:
            return str(ip_list[0])

    # No address has been found by its interface but perhaps one has been specified explicitly
    # or through a network range.
    for current in current_addresses:
        for preferred in pref_networks:
            if ip_address(current.decode('utf8') if isinstance(current, bytes) else current) in preferred:
                return current

    # Ok, still nothing, so we need to find something ourselves
    loopback_ip = None

    # First let's try the first non-loopback interface.
    for elem in current_ifaces:
        for ip in ip_list_from_interface(elem, True):
            if ip.is_loopback:
                loopback_ip = ip
            return str(ip)

    # If there is only loopback and we are allowed to use it then so be it
    if user_prefs.allow_loopback:
        return loopback_ip

# ################################################################################################################################
