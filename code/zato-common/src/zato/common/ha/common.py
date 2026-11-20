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

    # The thresholds after which the node finds its server failed and resigns, and the hold-off of a node that resigned,
    # each of which the node takes from its own defaults unless it is given one
    Env_Server_Liveness_Timeout = 'Zato_HA_Server_Liveness_Timeout'
    Env_Server_Start_Timeout    = 'Zato_HA_Server_Start_Timeout'
    Env_Server_Exit_Limit       = 'Zato_HA_Server_Exit_Limit'
    Env_Server_Exit_Window      = 'Zato_HA_Server_Exit_Window'
    Env_Resign_Hold_Off         = 'Zato_HA_Resign_Hold_Off'
    Env_Resign_Hold_Off_Max     = 'Zato_HA_Resign_Hold_Off_Max'

    # The defaults of the timers and thresholds of a node, the same as the DEFAULT_ constants of zato_ha_core/src/config.rs,
    # in seconds, except for the exit limit, which is a number of exits
    Default_Heartbeat_Time          = 0.5
    Default_Takeover_Time           = 6.0
    Default_Server_Liveness_Timeout = 10.0
    Default_Server_Start_Timeout    = 300.0
    Default_Server_Exit_Limit       = 3
    Default_Server_Exit_Window      = 60.0
    Default_Resign_Hold_Off         = 20.0
    Default_Resign_Hold_Off_Max     = 300.0

    # The variable of each timer and threshold of a node with its default
    Timer_Defaults = {
        Env_Heartbeat_Time:          Default_Heartbeat_Time,
        Env_Takeover_Time:           Default_Takeover_Time,
        Env_Server_Liveness_Timeout: Default_Server_Liveness_Timeout,
        Env_Server_Start_Timeout:    Default_Server_Start_Timeout,
        Env_Server_Exit_Limit:       Default_Server_Exit_Limit,
        Env_Server_Exit_Window:      Default_Server_Exit_Window,
        Env_Resign_Hold_Off:         Default_Resign_Hold_Off,
        Env_Resign_Hold_Off_Max:     Default_Resign_Hold_Off_Max,
    }

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
