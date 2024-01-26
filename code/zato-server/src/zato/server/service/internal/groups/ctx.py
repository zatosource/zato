# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.groups.ctx import SecurityGroupsCtxBuilder
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class BuildCtx(Service):
    name = 'dev.groups.build-ctx'

    def handle(self):

        channel_id = 85
        security_groups = [1, 3]

        builder = SecurityGroupsCtxBuilder(self.server)
        _ = builder.build_ctx(channel_id, security_groups)

# ################################################################################################################################
