# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import socket
from cStringIO import StringIO
from time import time
from traceback import format_exc

logger = logging.getLogger(__name__)

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

            while time() <=  end:
                data = client.recv(4096)
                if data:
                    buff.write(data)
                else:
                    return buff.getvalue()
        except Exception, e:
            msg = 'An error has occurred, e=[{e}]'.format(e=format_exc(e))
            logger.error(msg)
            raise
        finally:
            client.close()
