# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class DeployProbe(Service):
    """ Reports the CRM deployment revision this service was built with.
    """

    name = 'crm.deploy.probe'
    input = 'revision'

    def handle(self):

        revision = self.request.input.revision

        self.response.payload = {
            'revision': revision,
            'build': 'first',
        }

# ################################################################################################################################
# ################################################################################################################################
