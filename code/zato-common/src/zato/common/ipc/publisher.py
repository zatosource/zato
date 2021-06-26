# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.api import IPC
from zato.common.ipc import IPCEndpoint, Request

# ################################################################################################################################

class Publisher(IPCEndpoint):
    """ Sends outgoing IPC messages to any party listening for them.
    """
    socket_method = 'connect'
    socket_type = 'pub'

    def publish(self, payload, service='', target_pid=None, action=IPC.ACTION.INVOKE_SERVICE, reply_to_fifo=None):
        request = Request(self.name, self.pid)

        request.payload = payload
        request.service = service
        request.action = action
        request.target_pid = target_pid
        request.reply_to_fifo = reply_to_fifo

        self.socket.send_pyobj(request)

# ################################################################################################################################
