# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = -1          # type: int
        self.name = ''          # type: str
        self.is_active = True   # type: bool
        self.address = ''       # type: str
        self.tenant_id = ''     # type: str
        self.client_id = ''     # type: str
        self.client_secret = '' # type: str

# ################################################################################################################################
# ################################################################################################################################
