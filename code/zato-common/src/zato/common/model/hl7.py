# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = None      # type: int
        self.name = None      # type: str
        self.is_active = None # type: bool
        self.sec_type = None  # type: str
        self.security_id = None # type: str

# ################################################################################################################################
# ################################################################################################################################

class HL7FHIRConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = None      # type: int
        self.name = None      # type: str
        self.is_active = None # type: bool
        self.address = None   # type: str
        self.username = None  # type: str
        self.auth_type = None # type: str
        self.pool_size = None # type: int

# ################################################################################################################################
# ################################################################################################################################
