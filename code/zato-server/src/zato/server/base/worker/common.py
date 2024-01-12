# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from zato.server.connection.http_soap.url_data import URLData
    ParallelServer = ParallelServer
    URLData = URLData

# ################################################################################################################################
# ################################################################################################################################

class WorkerImpl:
    """ Base class for objects that implement worker functionality. Does not implement anything itself,
    instead serving as a common marker for all derived subclasses.
    """
    server: 'ParallelServer'
    url_data: 'URLData'
    worker_idx: 'int'

# ################################################################################################################################

    def on_broker_msg_Common_Sync_Objects(self:'WorkerStore', msg:'Bunch') -> 'None':
        _ = self.server.invoke('pub.zato.common.sync-objects-impl', msg)

# ################################################################################################################################
# ################################################################################################################################
