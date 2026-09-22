# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

# The environment variable moving every standalone block, and its default
Port_Base_Env     = 'Zato_HL7_Live_Port_Base'
Default_Port_Base = 31500

# How many ports one system's standalone block spans
Block_Size = 20

# ################################################################################################################################
# ################################################################################################################################

def _override_env_name(system:'str', purpose:'str') -> 'str':
    """ The environment variable overriding one standalone port, e.g. Zato_HL7_Live_Openhim_Api_Port.
    """
    system_part  = system.title().replace('_', '')
    purpose_part = purpose.title().replace('_', '')

    out = f'Zato_HL7_Live_{system_part}_{purpose_part}_Port'
    return out

# ################################################################################################################################

def _read_port_base() -> 'int':
    """ Returns the base of the standalone blocks, from the environment when it is set.
    """
    if value := os.environ.get(Port_Base_Env):
        out = int(value)
    else:
        out = Default_Port_Base

    return out

# ################################################################################################################################
# ################################################################################################################################

class PortPlan:
    """ Assigns a host port to each purpose a system publishes - a fixed block per system, so a person can find it.
    """

    def __init__(self, system:'str', block_number:'int', purposes:'strtuple') -> 'None':
        self.system = system
        self.block_number = block_number
        self.purposes = purposes

# ################################################################################################################################

    def standalone(self) -> 'strintdict':
        """ The system's fixed block above the base, each port replaceable through its own environment variable.
        """
        base = _read_port_base()
        block_start = base + self.block_number * Block_Size

        out:'strintdict' = {}

        for purpose_index, purpose in enumerate(self.purposes):
            env_name = _override_env_name(self.system, purpose)

            if value := os.environ.get(env_name):
                out[purpose] = int(value)
            else:
                out[purpose] = block_start + purpose_index

        return out

# ################################################################################################################################

    def describe(self, ports:'strintdict') -> 'str':
        """ One line per purpose, naming the port and the variable that moves it.
        """
        lines:'strlist' = []

        for purpose in self.purposes:
            env_name = _override_env_name(self.system, purpose)
            port = ports[purpose]
            lines.append(f'  {purpose:<14} {port:<6} ({env_name})')

        out = '\n'.join(lines)
        return out

# ################################################################################################################################
# ################################################################################################################################
