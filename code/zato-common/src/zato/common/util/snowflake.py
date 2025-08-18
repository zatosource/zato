# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import string
from threading import RLock

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
    def __init__(self, machine_id:'str') -> 'None':

        # Store the machine ID ..
        self.machine_id = machine_id

        # .. create a reentrant lock for thread safety ..
        self.lock = RLock()

        # .. initialize timestamp and sequence tracking.
        self.last_timestamp = 0
        self.sequence = 1

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
                self.sequence = 1
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

            # .. use the machine ID directly ..
            machine_part = self.machine_id

            # .. format the final sequence part ..
            sequence_part = f'{self.sequence:04x}'

            # .. and return the complete ID to our caller.
            return f'{date_part}-{time_subsecond_part}-{machine_part}-{sequence_part}'

# ################################################################################################################################

    @staticmethod
    def _hostname_to_machine_id(hostname:'str') -> 'str':
        """ Convert hostname to 3-character machine ID using digits and lowercase letters.
        """
        # Create hash from hostname ..
        hostname_hash = hash(hostname)

        # .. ensure it's positive ..
        if hostname_hash < 0:
            hostname_hash = -hostname_hash

        # .. convert to base-36 using digits and lowercase letters ..
        chars = string.digits + string.ascii_lowercase
        result = []

        for _ in range(3):
            hostname_hash, remainder = divmod(hostname_hash, 36)
            result.append(chars[remainder])

        # .. and return the result as a string.
        return ''.join(reversed(result))

# ################################################################################################################################

    @staticmethod
    def get_machine_id() -> 'str':
        """ Get machine ID from environment variable or hostname.
        """
        # Check for environment variable first ..
        machine_id = os.environ.get('Zato_Instance_Name')

        if machine_id:
            # .. use it directly if available ..
            return machine_id
        else:
            # .. otherwise get hostname and convert it ..
            hostname = socket.gethostname()
            return SnowflakeGenerator._hostname_to_machine_id(hostname)

# ################################################################################################################################

def new_snowflake(machine_id:'str'='') -> 'str':
    """ Generate a new human-readable snowflake ID.

    Format: YYYYMMDD-HHMMSSssss-mmm-rrrr (28 characters)

    Args:
        machine_id: Machine identifier (3-character string). If None, auto-detected.

    Returns:
        Snowflake ID string

    Raises:
        Exception: If sequence overflows
    """
    # Use auto-detected machine ID if not provided ..
    if not machine_id:
        machine_id = get_machine_id()

    # Create a new generator instance and generate the ID ..
    generator = SnowflakeGenerator(machine_id)

    # .. and return the ID to our caller.
    return generator.generate_id()

# ################################################################################################################################

def get_machine_id() -> 'str':
    """ Get machine ID from environment variable or hostname.
    """
    return SnowflakeGenerator.get_machine_id()

# ################################################################################################################################
# ################################################################################################################################
