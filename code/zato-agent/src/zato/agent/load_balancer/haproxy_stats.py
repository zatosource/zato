# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
from io import StringIO
from time import time
from traceback import format_exc

# Python 2/3 compatibility
from builtins import bytes

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class HAProxyStats:
    """ Used for communicating with HAProxy through its local UNIX socket interface.
    """
    socket_name: str

    def __init__(self, socket_name='<default>'):
        self.socket_name = socket_name

    def execute(self, command, extra='', timeout=200) -> str:
        """ Executes a HAProxy command by sending a message to a HAProxy's local
        UNIX socket and waiting up to 'timeout' milliseconds for the response.
        """
        if extra:
            command = command + ' ' + extra

        buff = StringIO()
        end = time() + timeout

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            client.connect(self.socket_name)
            client.send((command + '\n').encode('utf8'))

            while time() <= end:
                data = client.recv(4096)
                if data:
                    buff.write(data.decode('utf8') if isinstance(data, bytes) else data)
                else:
                    break
        except Exception:
            logger.error('An error has occurred, e:`%s`', format_exc())
            raise
        finally:
            client.close()

        return buff.getvalue()

# ################################################################################################################################
