# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class KeysightVisionConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id   = -1         # type: int
        self.name = ''         # type: str
        self.is_active = True  # type: bool
        self.address  = ''     # type: str
        self.username = ''     # type: str
        self.sec_tls_ca_cert_id = -1 # type: int

# ################################################################################################################################
# ################################################################################################################################
