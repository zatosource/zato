# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class AuditLogEvent:
    def __init__(self):
        self._config_attrs = []
        self.server_name = ''
        self.server_pid = ''
        self.type_   = ''
        self.object_id = ''
        self.conn_id = ''
        self.direction = ''
        self.data = ''
        self.timestamp = None # type: str
        self.timestamp_utc = None
        self.msg_id = ''
        self.in_reply_to = ''

# ################################################################################################################################
# ################################################################################################################################
