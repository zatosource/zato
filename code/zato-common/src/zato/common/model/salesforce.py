# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class SalesforceConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = None      # type: int
        self.name = None      # type: str
        self.is_active = None # type: bool
        self.api_version = None  # type: str
        self.username = None # type: str

# ################################################################################################################################
# ################################################################################################################################
