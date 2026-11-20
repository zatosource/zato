# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A process that reserves ports or a name, writes them to its standard output as one line of JSON,
# and holds them until its standard input is closed or the process is killed.
#
# Usage: reservation_holder.py ports <count> <purpose>
#        reservation_holder.py name <prefix>

# stdlib
import json
import sys

# Zato
from zato.common.test.reservation import reserve_name, reserve_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, intlist

# ################################################################################################################################
# ################################################################################################################################

def _hold_ports(count:'int', purpose:'str') -> 'None':
    """ Reserves the ports and writes them out.
    """
    ports:'intlist' = []
    reservations:'anylist' = []

    for _ in range(count):
        reservation = reserve_port(purpose)
        reservations.append(reservation)
        ports.append(reservation.port)

    data = json.dumps(ports)
    _ = sys.stdout.write(data + '\n')
    sys.stdout.flush()

    # The reservations are held until the test closes the standard input.
    _ = sys.stdin.read()

# ################################################################################################################################

def _hold_name(prefix:'str') -> 'None':
    """ Reserves the name and writes it out.
    """
    reservation = reserve_name(prefix)

    data = json.dumps(reservation.name)
    _ = sys.stdout.write(data + '\n')
    sys.stdout.flush()

    # The reservation is held until the test closes the standard input.
    _ = sys.stdin.read()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    mode = sys.argv[1]

    if mode == 'ports':
        count = int(sys.argv[2])
        _hold_ports(count, sys.argv[3])

    # .. anything else holds a name.
    else:
        _hold_name(sys.argv[2])

# ################################################################################################################################
# ################################################################################################################################
