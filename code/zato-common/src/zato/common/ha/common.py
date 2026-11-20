# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The configuration of a server that runs under the active-standby node, which starts the server only on the active host
# and passes it the referee generation.

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intnone

    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The mode of the environment, set to the active-standby mode on both hosts of a pair
    Env_Mode = 'Zato_HA_Mode'

    # The referee generation under which the node started the server
    Env_Generation = 'Zato_HA_Generation'

    # The timers of the node, in seconds, each of which the node takes from its own defaults unless it is given one
    Env_Heartbeat_Time = 'Zato_HA_Heartbeat_Time'
    Env_Takeover_Time  = 'Zato_HA_Takeover_Time'

    # The value of the mode variable that turns the active-standby mode on
    Mode_Active_Standby = 'active-standby'

# ################################################################################################################################
# ################################################################################################################################

def is_active_standby() -> 'bool':
    """ Returns whether this process runs in an environment of an active-standby pair.
    """
    mode = os.environ.get(ModuleCtx.Env_Mode, '')

    out = mode == ModuleCtx.Mode_Active_Standby
    return out

# ################################################################################################################################

def get_node_generation() -> 'intnone':
    """ Returns the referee generation under which a node started this server, or None for a server that no node started.
    """
    if generation := os.environ.get(ModuleCtx.Env_Generation):
        out = int(generation)
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################
