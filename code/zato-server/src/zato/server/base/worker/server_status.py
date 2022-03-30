# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class ServerStatus(WorkerImpl):
    """ Callbacks for messages related to current status of servers (e.g. running/shutting down).
    """
    def on_broker_msg_SERVER_STATUS_STATUS_CHANGED(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        """ If current status of any server changes, re-populate local information for all of them.
        """
        self.server.servers.populate_invokers()

# ################################################################################################################################
# ################################################################################################################################
