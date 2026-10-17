# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class DiscordConfigObject:
    def __init__(self) -> 'None':
        self._config_attrs = []
        self.id   = -1                # type: int
        self.name = ''                # type: str
        self.is_active = True         # type: bool
        self.token = ''               # type: str
        self.address = ''             # type: str
        self.timeout = 0              # type: int
        self.default_channel_id = ''  # type: str

# ################################################################################################################################
# ################################################################################################################################
