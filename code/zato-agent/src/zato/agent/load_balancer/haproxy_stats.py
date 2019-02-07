# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

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

class HAProxyStats(object):
    """ Used for communicating with HAProxy through its local UNIX socket interface.
    """
    def __init__(self, socket_name=None):
        self.socket_name = socket_name

    def execute(self, command, extra="", timeout=200):
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
            client.send(command + '\n')

            while time() <= end:
                data = client.recv(4096)
                if data:
                    buff.write(data.decode('utf8') if isinstance(data, bytes) else data)
                else:
                    return buff.getvalue()
        except Exception:
            logger.error('An error has occurred, e:`%s`', format_exc())
            raise
        finally:
            client.close()

# ################################################################################################################################
