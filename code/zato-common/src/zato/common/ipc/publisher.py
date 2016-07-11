# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.ipc import IPCEndpoint, Request

# ################################################################################################################################

class Publisher(IPCEndpoint):
    """ Sends outgoing IPC messages to any party listening for them.
    """
    socket_method = 'connect'
    socket_type = 'pub'

    def publish(self, payload):
        self.socket.send_pyobj(Request(self.name, self.pid, payload))

# ################################################################################################################################
