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

def get_scheduler_data():
    return [[31530, 'Scheduler']] # type: ignore

# ################################################################################################################################

def get_non_scheduler_data():
    return [
        [8183,  'Dashboard'], # type: ignore
        [11223, 'Load-balancer'],
        [20151, 'Load-balancer\'s agent'],

        # Servers come last because they may be the last to stop
        # in case we are being called during an environment's restart.
        [17010, 'server1'],
        [17011, 'server2']
    ]

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    if len(sys.argv) == 2:
        argv1 = sys.argv[1]
        scheduler_only = argv1 == 'scheduler-only'
        no_scheduler   = argv1 == 'no-scheduler'
        needs_scheduler = not no_scheduler
    else:
        scheduler_only  = False
        no_scheduler    = False
        needs_scheduler = True

    data = []
    scheduler_data     = get_scheduler_data()     # type: ignore
    non_scheduler_data = get_non_scheduler_data() # type: ignore

    if scheduler_only:
        data.extend(scheduler_data)
    else:
        if needs_scheduler:
            data.extend(scheduler_data)
        data.extend(non_scheduler_data)

    wait_for_ports(*data)

# ################################################################################################################################
# ################################################################################################################################
