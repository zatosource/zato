# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

class Default:

    # This is relative to server.conf's main.work_dir
    fs_data_path = 'events'

    # Sync database to disk once in that many events ..
    sync_threshold = 120_000

    # .. or once in that many milliseconds.
    sync_interval = 120_000

# ################################################################################################################################
# ################################################################################################################################

# All event actions possible
class Action:

    Ping      = b'01'
    PingReply = b'02'
    Push      = b'03'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PushCtx:
    id: str
    cid: str
    timestamp: str

    source_type: str
    source_id: str

    object_type: str
    object_id: str

    source_type: str
    source_id: str

    recipient_type: str
    recipient_id: str

    total_time_ms: int

# ################################################################################################################################
# ################################################################################################################################
