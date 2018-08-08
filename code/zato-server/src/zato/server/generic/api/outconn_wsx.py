# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common import ZATO_NONE
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config, server):
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

    def add_client(self):
        print(222, self)
        conn = 123
        self.client.put_client(conn)

# ################################################################################################################################
