# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Optional as optional

# Zato
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

class Default:

    # This is relative to server.conf's main.work_dir
    fs_data_path = 'events'

    # Sync database to disk once in that many events ..
    sync_threshold = 30_000

    # .. or once in that many seconds.
    sync_interval = 30

# ################################################################################################################################
# ################################################################################################################################

class EventInfo:

    class EventType:
        service_request = 1_000_000
        service_response = 1_000_001

    class ObjectType:
        service = 2_000_000

# ################################################################################################################################
# ################################################################################################################################

# All event actions possible
class Action:

    Ping           = b'01'
    PingReply      = b'02'
    Push           = b'03'
    GetTable       = b'04'
    GetTableReply  = b'05'
    SyncState      = b'06'

    LenAction = len(Ping)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PushCtx:
    id: str
    cid: str
    timestamp: str
    event_type: int

    source_type: optional[str] = None
    source_id: optional[str] = None

    object_type: int
    object_id: str

    recipient_type: optional[str] = None
    recipient_id: optional[str] = None

    total_time_ms: int

    def __hash__(self):
        return hash(self.id)

# ################################################################################################################################
# ################################################################################################################################
