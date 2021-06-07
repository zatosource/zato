# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.events.client import Client as EventsClient
from zato.common.events.common import EventInfo, PushCtx
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

event_type_req      = EventInfo.EventType.service_request
event_type_resp     = EventInfo.EventType.service_response
object_type_service = EventInfo.ObjectType.service

# ################################################################################################################################
# ################################################################################################################################

class ServiceStatsClient:
    def __init__(self, host, port):
        # type: (str, int) -> None
        self.impl = EventsClient(host, port)

# ################################################################################################################################

    def run(self):
        self.impl.run()

# ################################################################################################################################

    def push(self, cid, timestamp, service_name, is_request, total_time_ms=0, id=None):
        # type: (str, str, str, int, str)

        # Fill out the details of a context object ..
        ctx = PushCtx()
        ctx.id = id or new_cid()
        ctx.cid = cid
        ctx.timestamp = timestamp
        ctx.event_type = event_type_req if is_request else event_type_resp
        ctx.object_type = object_type_service
        ctx.object_id = service_name
        ctx.total_time_ms = total_time_ms

        # .. and push the event to the backend.
        self.impl.push(ctx)

# ################################################################################################################################
# ################################################################################################################################
