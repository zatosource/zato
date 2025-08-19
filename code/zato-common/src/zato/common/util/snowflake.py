# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import _thread
import os
import platform
import string
from threading import RLock
from uuid import uuid4

# Zato
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Timestamp precision multiplier for 100-microsecond granularity
_Timestamp_Precision_Multiplier = 10000

# Random sequence configuration
_Sequence_Length = 8

# Module-level storage for OS thread generators
_generators:'anydict' = {}
_generators_lock = _thread.allocate_lock()

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

        # .. initialize timestamp and random sequence tracking.
        self.last_timestamp = 0
        self.used_sequences = set()

# ################################################################################################################################

    def _generate_sequence(self) -> 'str':
        """ Generate a random sequence using UUID4 hex.
        """
        return uuid4().hex[:_Sequence_Length]

# ################################################################################################################################

    def generate_id(self, prefix:'str') -> 'str':
        """ Generate a new snowflake ID in format YYYYMMDD-HHMMSS-ssss-[prefix]rrrr-mmm.

        Where:
            rrrr = 4-character random alphanumeric sequence
            mmm = variable-length machine/instance identifier
            prefix = prefix for sequence component

        Args:
            prefix: Prefix to prepend to sequence component
        """
        with self.lock:

            # Get the current time ..
            now = utcnow()

            # Use 100-microsecond precision for timestamp comparison
            current_timestamp = int(now.timestamp() * _Timestamp_Precision_Multiplier)

            # .. check if we are in the same 100-microsecond window as the last call ..
            if current_timestamp == self.last_timestamp:

                # .. generate a unique random sequence for this window ..
                max_attempts = 1000
                for _ in range(max_attempts):
                    sequence = self._generate_sequence()
                    if sequence not in self.used_sequences:
                        self.used_sequences.add(sequence)
                        break
                else:
                    raise Exception('Sequence collision: unable to generate unique sequence in 100-microsecond window')
            else:

                # .. we are in a new 100-microsecond window so reset the used sequences ..
                self.used_sequences.clear()
                sequence = self._generate_sequence()
                self.used_sequences.add(sequence)
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
            subsecond_part = f'{subsecond:04d}'

            # .. use the machine ID directly ..
            machine_part = self.machine_id

            # .. format the final sequence part with optional prefix ..
            sequence_part = f'{prefix}{sequence}'

            # .. build the complete ID ..
            result = f'{date_part}-{time_part}-{subsecond_part}-{sequence_part}'

            if machine_part:
                result += f'-{machine_part}'

            # .. and return it to our caller.
            return result

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
            hostname = platform.node()
            return hostname

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
                machine_id = get_machine_id()
            _generators[thread_id] = SnowflakeGenerator(machine_id)
        return _generators[thread_id]

# ################################################################################################################################

def new_snowflake(prefix:'str', needs_machine_id:'bool'=True) -> 'str':
    """ Generate a new human-readable snowflake ID.

    Format: YYYYMMDD-HHMMSS-ssss-[prefix]rrrr[-mmm]
    Where:
        rrrr = 4-character random alphanumeric sequence
        mmm = variable-length machine/instance identifier (optional)
        prefix = prefix for sequence component

    Args:
        prefix: Prefix to prepend to sequence component
        needs_machine_id: If True, include machine ID. If False, omit machine ID.

    Returns:
        Snowflake ID string

    Raises:
        Exception: If sequence collision occurs
    """
    # Handle machine_id parameter ..
    if needs_machine_id:
        machine_id = get_machine_id()
    else:
        machine_id = ''

    # Get OS thread-local generator ..
    thread_id = _thread.get_ident()

    if thread_id not in _generators:
        generator = create_snowflake_generator(machine_id)
    else:
        generator = _generators[thread_id]

    # .. and return the ID to our caller.
    return generator.generate_id(prefix)

# ################################################################################################################################

def get_machine_id() -> 'str':
    """ Get machine ID from environment variable or hostname.
    """
    return SnowflakeGenerator.get_machine_id()

# ################################################################################################################################
# ################################################################################################################################
