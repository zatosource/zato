# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import errno
import socket

# Zato
from zato.common.test.reservation import PortInUse

# ################################################################################################################################
# ################################################################################################################################

# How many connections a listener keeps pending before it accepts them
_backlog = 1024

# ################################################################################################################################
# ################################################################################################################################

def bind_listener(host:'str', port:'int') -> 'socket.socket':
    """ Returns a non-blocking listener bound to the host and the port, raising PortInUse when another socket uses the port.
    """
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        listener.bind((host, port))
    except OSError as e:
        listener.close()

        if e.errno == errno.EADDRINUSE:
            raise PortInUse(f'Port {port} of {host} is in use') from e

        # .. any other error of the bind is not a matter of the port.
        else:
            raise

    listener.listen(_backlog)

    # The server accepts connections until the listener has none pending, which requires a non-blocking listener
    # in a process that gevent did not patch.
    listener.setblocking(False)

    return listener

# ################################################################################################################################
# ################################################################################################################################
