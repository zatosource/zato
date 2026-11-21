# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.config_manager import ConfigManager
    from zato.server.connection.http_soap.url_data import URLData
    ParallelServer = ParallelServer
    URLData = URLData

# ################################################################################################################################
# ################################################################################################################################

class ConfigManagerImpl:
    """ Base class for objects that implement config manager functionality. Does not implement anything itself,
    instead serving as a common marker for all derived subclasses.
    """
    server: 'ParallelServer'
    url_data: 'URLData'

# ################################################################################################################################

    def on_config_event_Common_Sync_Objects(self:'ConfigManager', msg:'Bunch') -> 'None':
        _ = self.server.invoke('pub.zato.common.sync-objects-impl', msg)

# ################################################################################################################################
# ################################################################################################################################
