# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The throwaway Redis an SMS suite's server remembers seen events in.

# stdlib
import socket
import subprocess
import time

# Test support
from live_sms.ports import Host

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the Redis is given to open its port
Redis_Wait_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

def start_redis(port:'int') -> 'any_':
    """ Starts a Redis with no persistence in its own session and waits for its port.
    """
    command = ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no']
    out = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    deadline = time.monotonic() + Redis_Wait_Timeout

    while time.monotonic() < deadline:
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex((Host, port)) == 0:
                return out
        time.sleep(0.2)

    out.kill()
    raise Exception(f'Redis did not open port {port} within {Redis_Wait_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################
