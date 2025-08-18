# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import string
import threading

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    pass

# ################################################################################################################################
# ################################################################################################################################

class SnowflakeGenerator:
    """ Human-readable snowflake ID generator with fixed 28-character format.
    """
    def __init__(self, machine_id:'int') -> 'None':

        # Store the machine ID ..
        self.machine_id = machine_id

        # .. create a reentrant lock for thread safety ..
        self.lock = threading.RLock()

        # .. initialize timestamp and sequence tracking.
        self.last_timestamp = 0
        self.sequence = 0

# ################################################################################################################################

    def generate_id(self) -> 'str':
        """ Generate a new snowflake ID in format YYYYMMDD-HHMMSSssss-mmm-rrrr.
        """
        with self.lock:

            # Get the current time ..
            now = utcnow()
            current_timestamp = int(now.timestamp() * 1000)

            # .. check if we are in the same millisecond as the last call ..
            if current_timestamp == self.last_timestamp:

                # .. if so, increment the sequence ..
                self.sequence += 1

                # .. but raise an exception if it overflows ..
                if self.sequence > 65535:
                    raise Exception('Sequence overflow: too many IDs generated in same millisecond')
            else:

                # .. we are in a new millisecond so reset the sequence ..
                self.sequence = 0
                self.last_timestamp = current_timestamp

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
            time_subsecond_part = f'{time_part}{subsecond:04d}'

            # .. encode the machine ID as base-36 ..
            chars = string.digits + string.ascii_lowercase
            machine_part = ''
            temp_id = self.machine_id
            for _ in range(3):
                temp_id, remainder = divmod(temp_id, 36)
                machine_part = chars[remainder] + machine_part

            # .. format the final sequence part ..
            sequence_part = f'{self.sequence:04x}'

            # .. and return the complete ID to our caller.
            return f'{date_part}-{time_subsecond_part}-{machine_part}-{sequence_part}'

# ################################################################################################################################
# ################################################################################################################################

def new_snowflake(machine_id:'int'=0) -> 'str':
    """ Generate a new human-readable snowflake ID.
    
    Format: YYYYMMDD-HHMMSSssss-mmm-rrrr (28 characters)
    
    Args:
        machine_id: Machine identifier (0-46655), defaults to 0
        
    Returns:
        Snowflake ID string
        
    Raises:
        Exception: If sequence overflows or machine_id is out of range
    """
    # Create a new generator instance and generate the ID ..
    generator = SnowflakeGenerator(machine_id)
    
    # .. and return the ID to our caller.
    return generator.generate_id()

# ################################################################################################################################
# ################################################################################################################################