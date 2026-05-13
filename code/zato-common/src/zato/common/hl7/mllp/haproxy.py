# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import signal
import socket
import subprocess
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Internal_Port = 31312
_Default_Port_Offset   = 100

# Pattern matching the "server mllp1 127.0.0.1:NNNNN" line in the mllp_backend section
_MLLP_Backend_Server_Pattern = re.compile(r'(\s+server\s+mllp1\s+127\.0\.0\.1:)\d+')

# ################################################################################################################################
# ################################################################################################################################

def find_haproxy_config(server_base_directory:'str') -> 'str':
    """ Resolves the path to haproxy.cfg from the server's base directory.
    The server sits in e.g. /opt/zato/env/qs-1/server1 and haproxy.cfg
    is one level up at /opt/zato/env/qs-1/haproxy.cfg.
    """

    # Go up one level from the server directory to the environment root ..
    environment_directory = os.path.join(server_base_directory, '..')
    environment_directory = os.path.abspath(environment_directory)

    # .. and build the path to haproxy.cfg.
    out = os.path.join(environment_directory, 'haproxy.cfg')

    return out

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
        config_file.write(updated_content)

    logger.info('Updated mllp_backend port to %d in %s', internal_port, config_path)

# ################################################################################################################################

def reload_haproxy() -> 'bool':
    """ Sends SIGHUP to the running HAProxy process for a graceful configuration reload.
    Returns True if the signal was sent successfully.
    """

    # Find the HAProxy process ..
    result = subprocess.run(
        ['pgrep', '-f', 'haproxy.*haproxy.cfg'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning('Could not find a running HAProxy process to reload')
        return False

    if not result.stdout.strip():
        logger.warning('pgrep returned empty output when looking for HAProxy')
        return False

    # .. send SIGHUP to each matching process ..
    pid_list = result.stdout.strip().split('\n')
    has_signaled = False

    for pid_string in pid_list:

        if not pid_string.strip():
            continue

        pid = int(pid_string.strip())

        try:
            os.kill(pid, signal.SIGHUP)
            logger.info('Sent SIGHUP to HAProxy process %d', pid)
            has_signaled = True
        except ProcessLookupError:
            logger.warning('HAProxy process %d no longer exists', pid)
        except PermissionError:
            logger.warning('No permission to signal HAProxy process %d', pid)

    return has_signaled

# ################################################################################################################################

def resolve_internal_port(
    base_port:'int' = _Default_Internal_Port,
    offset:'int' = _Default_Port_Offset,
    ) -> 'int':
    """ Finds a free port for the internal MLLP server by starting at base_port
    and incrementing until a free port is found.
    """

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
