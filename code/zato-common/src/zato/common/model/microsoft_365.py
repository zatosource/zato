# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365ConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = -1         # type: int
        self.name = ''         # type: str
        self.is_active = True  # type: bool
        self.tenant_id = ''    # type: str
        self.client_id = ''    # type: str
        self.secret_value = '' # type: str
        self.auth_redirect_url = '' # type: str

# ################################################################################################################################
# ################################################################################################################################
