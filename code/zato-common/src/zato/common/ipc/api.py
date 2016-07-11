# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.common.ipc.forwarder import Forwarder
from zato.common.ipc.publisher import Publisher
from zato.common.ipc.subscriber import Subscriber

# ################################################################################################################################

class IPCAPI(object):
    """ API through which IPC is performed.
    """
    def __init__(self, is_forwarder, name=None, on_message_callback=None):
        self.name = name
        self.pid = os.getpid()

        if is_forwarder:
            self.forwarder = Forwarder(self.name, self.pid)
        else:
            self.publisher = Publisher(self.name, self.pid)
            self.subscriber = Subscriber(on_message_callback, self.name, self.pid)

    def publish(self, payload):
        self.publisher.publish(payload)

# ################################################################################################################################
