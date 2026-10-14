# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import INFO_FORMAT
from zato.common.component_info import format_info, get_info, get_server_pids
from zato.server.service import List, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GetServerInfo(Service):
    """ Collects information about a server it's invoked on.
    """
    output = 'info',

    def handle(self):
        self.response.content_type = 'application/json'
        self.response.payload.info = format_info(get_info(self.server.base_dir, INFO_FORMAT.JSON), INFO_FORMAT.JSON)

# ################################################################################################################################

class GetWorkerPids(Service):
    """ Returns PIDs of all processes of current server.
    """
    output:'any_' = List('pids')

    def handle(self):
        self.response.payload.pids = get_server_pids(self.server.base_dir)

# ################################################################################################################################
