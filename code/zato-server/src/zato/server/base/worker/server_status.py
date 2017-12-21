# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class ServerStatus(WorkerImpl):
    """ Callbacks for messages related to current status of servers (e.g. running/shutting down).
    """

# ################################################################################################################################

    def on_broker_msg_SERVER_STATUS_STATUS_CHANGED(self, msg):
        """ If current status of any server changes, re-populate local information for all of them.
        """
        self.server.servers.populate_servers()

# ################################################################################################################################
