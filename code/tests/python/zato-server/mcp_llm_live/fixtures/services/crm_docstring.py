# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class DocstringProbe(Service):
    """ Reports the CRM fingerprint of the first build.
    """

    name = 'crm.docstring.probe'
    input = 'revision'

    def handle(self):

        self.response.payload = {
            'revision': self.request.input.revision,
            'fingerprint': 'fp-first',
        }

# ################################################################################################################################
# ################################################################################################################################

# This service deliberately has no docstring - it advertises an empty tool description.
class BlankProbe(Service):

    name = 'crm.blank.probe'
    input = 'revision'

    def handle(self):

        self.response.payload = {
            'revision': self.request.input.revision,
        }

# ################################################################################################################################
# ################################################################################################################################
