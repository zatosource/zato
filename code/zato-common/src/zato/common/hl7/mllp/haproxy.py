# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import socket
from logging import getLogger

# Zato
from zato.common.haproxy.config import find_haproxy_config, reload_haproxy

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

__all__ = ('find_haproxy_config', 'reload_haproxy', 'resolve_internal_port', 'update_mllp_backend_port')

# ################################################################################################################################
# ################################################################################################################################

_Default_Internal_Port = 31312
_Default_Port_Offset   = 100

# If this environment variable is set, the internal MLLP server binds to exactly this port
_Env_Port_Name = 'Zato_HL7_MLLP_Port'

# Pattern matching the "server mllp1 127.0.0.1:NNNNN" line in the mllp_backend section
_MLLP_Backend_Server_Pattern = re.compile(r'(\s+server\s+mllp1\s+127\.0\.0\.1:)\d+')

# ################################################################################################################################
# ################################################################################################################################

def update_mllp_backend_port(config_path:'str', internal_port:'int') -> 'None':
    """ Updates the mllp_backend server line in haproxy.cfg to point to the given internal port.
    """

    # Read the current configuration ..
    with open(config_path, 'r') as config_file:
        content = config_file.read()

    # .. replace the port number on the mllp_backend server line ..
    replacement = f'\\g<1>{internal_port}'
    updated_content = _MLLP_Backend_Server_Pattern.sub(replacement, content)

    # .. write the updated configuration back.
    with open(config_path, 'w') as config_file:
        _ = config_file.write(updated_content)

    logger.info('Updated mllp_backend port to %d in %s', internal_port, config_path)

# ################################################################################################################################

def resolve_internal_port(
    base_port:'int' = _Default_Internal_Port,
    offset:'int' = _Default_Port_Offset,
    ) -> 'int':
    """ Finds a free port for the internal MLLP server by starting at base_port
    and incrementing until a free port is found. If the Zato_HL7_MLLP_Port
    environment variable is set, that exact port is used instead.
    """

    # An explicitly configured port always wins - this is what tests use to know the port upfront
    env_port = os.environ.get(_Env_Port_Name)
    if env_port:
        out = int(env_port)
        logger.info('Using internal MLLP port %d from %s', out, _Env_Port_Name)
        return out

    candidate_port = base_port

    while True:

        # Try to bind a test socket to see if the port is free ..
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            test_socket.bind(('127.0.0.1', candidate_port))
            test_socket.close()

            logger.info('Resolved internal MLLP port %d', candidate_port)

            out = candidate_port
            return out

        except OSError:

            # .. port is taken, try the next one ..
            logger.debug('Port %d is in use, trying next', candidate_port)
            test_socket.close()
            candidate_port += 1

# ################################################################################################################################
# ################################################################################################################################
