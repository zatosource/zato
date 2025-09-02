# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import _thread
import os
import platform
import random

# Zato
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################



# Module-level storage for OS thread generators
_generators:'anydict' = {}
_generators_lock = _thread.allocate_lock()

# ################################################################################################################################
# ################################################################################################################################

# Check for environment variable first or use hostname if no such env. variable is given.
_machine_id = os.environ.get('Zato_Instance_Name') or platform.node()

# ################################################################################################################################
# ################################################################################################################################

class SnowflakeGenerator:
    """ Human-readable snowflake ID generator with fixed 28-character format.
    """
    def __init__(self, machine_id:'str') -> 'None':

        # Store the machine ID ..
        self.machine_id = machine_id

# ################################################################################################################################

    def generate_id(self, suffix:'str') -> 'str':
        """ Generate a new snowflake ID in format YYYYMMDD-HHMMSS-ssss-rrrrrrrrrrrrrrrr[suffix]-mmm.

        Where:
            rrrrrrrrrrrrrrrr = 16-character lowercase random hexadecimal (64 bits)
            mmm = variable-length machine/instance identifier
            suffix = suffix for random component

        Args:
            suffix: Suffix to append to random component
        """
        # Get the current time ..
        now = utcnow()

        # Generate date component ..
        date_part = now.strftime('%Y%m%d')

        # .. build the time+subsecond component ..
        time_part = now.strftime('%H%M%S')

        # .. extract subsecond precision by converting microseconds to centiseconds ..
        # .. microseconds range from 0-999999 (6 digits) ..
        # .. dividing by 100 gives 0-9999 (4 digits) ..
        # .. for example: 487123 microseconds becomes 4871 ..
        # .. or 50000 microseconds becomes 500 ..
        # .. or 999999 microseconds becomes 9999 ..
        subsecond = now.microsecond // 100
        subsecond_part = f'{subsecond:04d}'

        # .. use the machine ID directly ..
        machine_part = self.machine_id

        # .. generate 64 bits (16 hex characters) of random data ..
        random_bytes = random.getrandbits(64)
        random_hex = f'{random_bytes:016x}'

        # .. format the final random part with optional suffix ..
        random_part = f'{random_hex}{suffix}'

        # .. build the complete ID ..
        result = f'{date_part}-{time_part}-{subsecond_part}-{random_part}'

        if machine_part:
            result += f'-{machine_part}'

        # .. and return it to our caller.
        return result

# ################################################################################################################################

def create_snowflake_generator(machine_id:'str'='') -> 'SnowflakeGenerator':
    """ Create and cache a generator for the current OS thread.

    Args:
        machine_id: Machine identifier. If empty, auto-detected.

    Returns:
        SnowflakeGenerator instance for current OS thread
    """
    thread_id = _thread.get_ident()

    with _generators_lock:
        if thread_id not in _generators:
            if not machine_id:
                machine_id = _machine_id
            _generators[thread_id] = SnowflakeGenerator(machine_id)
        return _generators[thread_id]

# ################################################################################################################################

def new_snowflake(suffix:'str', needs_machine_id:'bool'=True) -> 'str':
    """ Generate a new human-readable snowflake ID.

    Format: YYYYMMDD-HHMMSS-ssss-rrrrrrrrrrrrrrrr[suffix][-mmm]
    Where:
        rrrrrrrrrrrrrrrr = 16-character lowercase random hexadecimal (64 bits)
        mmm = variable-length machine/instance identifier (optional)
        suffix = suffix for random component

    Args:
        suffix: Suffix to append to random component
        needs_machine_id: If True, include machine ID. If False, omit machine ID.

    Returns:
        Snowflake ID string
    """
    # Handle machine_id parameter ..
    if needs_machine_id:
        machine_id = _machine_id
    else:
        machine_id = ''

    # Get OS thread-local generator ..
    thread_id = _thread.get_ident()

    if thread_id not in _generators:
        generator = create_snowflake_generator(machine_id)
    else:
        generator = _generators[thread_id]

    # .. and return the ID to our caller.
    return generator.generate_id(suffix)

# ################################################################################################################################
# ################################################################################################################################
