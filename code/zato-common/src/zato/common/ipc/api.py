# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.ipc.forwarder import Forwarder
from zato.common.ipc.publisher import Publisher
from zato.common.ipc.subscriber import Subscriber
from zato.common.util import spawn_greenlet

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class IPCAPI(object):
    """ API through which IPC is performed.
    """
    def __init__(self, is_forwarder, name=None, on_message_callback=None, pid=None):
        self.is_forwarder = is_forwarder
        self.name = name
        self.on_message_callback = on_message_callback
        self.pid = pid

    def run(self):

        if self.is_forwarder:
            spawn_greenlet(Forwarder, self.name, self.pid)
        else:
            self.publisher = Publisher(self.name, self.pid)
            self.subscriber = Subscriber(self.on_message_callback, self.name, self.pid)
            spawn_greenlet(self.subscriber.serve_forever)

    def publish(self, payload):
        self.publisher.publish(payload)

# ################################################################################################################################
