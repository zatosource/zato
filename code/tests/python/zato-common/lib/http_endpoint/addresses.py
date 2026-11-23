# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from ipaddress import ip_address

# ################################################################################################################################
# ################################################################################################################################

# An address of TEST-NET-1, which a UDP socket is connected to only to select the address of the outgoing interface.
# A connect of a UDP socket sends no packet.
_route_probe_address = '192.0.2.1'
_route_probe_port = 9

# ################################################################################################################################
# ################################################################################################################################

def get_non_loopback_address() -> 'str':
    """ Returns the IPv4 address of this machine that its default route uses, which is outside the loopback range.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        probe.connect((_route_probe_address, _route_probe_port))
        address, _ = probe.getsockname()
    except OSError as e:
        message = f'This machine has no IPv4 route to {_route_probe_address} and no address outside the loopback range'
        raise Exception(message) from e
    finally:
        probe.close()

    parsed = ip_address(address)

    if parsed.is_loopback:
        raise Exception(f'This machine has no IPv4 address outside the loopback range, its default route uses {address}')

    return address

# ################################################################################################################################
# ################################################################################################################################
