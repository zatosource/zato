# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.api import wait_until_port_free

# ################################################################################################################################
# ################################################################################################################################

def wait_for_ports(*data): # type: ignore
    """ Blocks until input TCP ports are free.
    """
    for port, component in data: # type: ignore
        if not wait_until_port_free(port, 10):
            print(f'Port taken {port} ({component})')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    print()
    print(111, sys.argv)
    print()

    if len(sys.argv) == 2:
        argv1 = sys.argv[1]
        scheduler_only = argv1 == 'scheduler-only'
        no_scheduler   = argv1 == 'no-scheduler'
    else:
        scheduler_only = False
        no_scheduler   = False

    # To be populated
    data = []

    if scheduler_only:


    # Base configuration, always used
    data = [ # type: ignore
        [31530, 'Scheduler']
    ]

    if not scheduler_only:
        data.extend([
            [8183,  'Dashboard'],
            [11223, 'Load-balancer'],
            [20151, 'Load-balancer\'s agent'],

            # Servers come last because they may be the last to stop
            # in case we are being called during an environment's restart.
            [17010, 'server1'],
            [17011, 'server2']
    ])

    wait_for_ports(*data)

# ################################################################################################################################
# ################################################################################################################################
