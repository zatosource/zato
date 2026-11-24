# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared region of a server, which the arbiter creates before it forks the config process and the worker.
# The table of keyed locks has a fixed capacity, chosen here for every server.

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The keyed locks and counters of the outgoing queues
    Lock_Capacity = 4096

# ################################################################################################################################
# ################################################################################################################################

def new_server_region() -> 'SharedRegion':
    """ Returns the region of a server.
    """
    out = SharedRegion({
        'lock_capacity': ModuleCtx.Lock_Capacity,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################
