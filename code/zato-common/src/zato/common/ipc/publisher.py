# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import IPC_ACTION
from zato.common.ipc import IPCEndpoint, Request

# ################################################################################################################################

class Publisher(IPCEndpoint):
    """ Sends outgoing IPC messages to any party listening for them.
    """
    socket_method = 'connect'
    socket_type = 'pub'

    def publish(self, payload, service='', target_pid=None, action=IPC_ACTION.INVOKE_SERVICE):
        request = Request(self.name, self.pid)

        request.payload = payload
        request.service = service
        request.action = action
        request.target_pid = target_pid

        self.socket.send_pyobj(request)

# ################################################################################################################################
