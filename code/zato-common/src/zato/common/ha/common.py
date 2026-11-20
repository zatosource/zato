# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The configuration of a server that runs under the active-standby node, which keeps a warm server on a host
# without an active server and passes it the referee generation when the host becomes the active one.

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

    # The FIFO through which the node delivers the referee generation to a warm server, which waits for it before
    # it runs any startup hook or opens the Zato database, the same as ENV_ACTIVATION_PATH of zato_ha_core/src/config.rs
    Env_Activation_Path = 'Zato_HA_Activation_Path'

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

    # The exit code of a warm server that the node closed the activation path on without a valid generation
    Activation_Error_Exit_Code = 1

# ################################################################################################################################
# ################################################################################################################################

class ActivationError(Exception):
    """ Raised when the node closes the activation path without a generation or writes one that is not an integer.
    """

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

def wait_for_activation(activation_path:'str') -> 'int':
    """ Blocks until the node opens the activation path for writing, reads the generation that the node writes to it,
    sets it in the environment, from which this process and the processes that it forks read it, and returns it.
    """

    # The open blocks until the node opens the path for writing ..
    with open(activation_path) as activation_file:
        line = activation_file.readline()

    # .. the line has the generation, followed by a newline ..
    generation = line.strip()

    # .. a node that closed the path without a line delivered nothing ..
    if not generation:
        raise ActivationError(f'No generation received through `{activation_path}`')

    # .. and a line that is not an integer is not a generation.
    try:
        out = int(generation)
    except ValueError:
        raise ActivationError(f'Generation `{generation}` received through `{activation_path}` is not an integer')

    os.environ[ModuleCtx.Env_Generation] = generation

    return out

# ################################################################################################################################
# ################################################################################################################################
