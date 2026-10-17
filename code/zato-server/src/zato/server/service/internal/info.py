# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import INFO_FORMAT
from zato.common.component_info import format_info, get_info
from zato.server.service import Service

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
# ################################################################################################################################
