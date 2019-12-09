# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Unlike zato.common.odb.model - this place is where DB-independent models are kept,
# regardless if they're backed by an SQL database or not.

# ################################################################################################################################
# ################################################################################################################################

class SFTPChannel(object):
    def __init__(self):
        self._config_attrs = []
        self.id   = None               # type: int
        self.name = None               # type: str
        self.is_active = None          # type: bool
        self.address = None            # type: str
        self.service_name = None       # type: str
        self.topic_name = None         # type: str
        self.idle_timeout = None       # type: int
        self.keep_alive_timeout = None # type: int
        self.host_key = None           # type: str

# ################################################################################################################################

    def to_dict(self):
        out = {}
        for name in self._config_attrs:
            value = getattr(self, name)
            out[name] = value
        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(config):
        # type: (dict) -> SFTPChannel
        out = SFTPChannel()
        for k, v in config.items():
            out._config_attrs.append(k)
            setattr(out, k, v)
        return out

# ################################################################################################################################
# ################################################################################################################################
