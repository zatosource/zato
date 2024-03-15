# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.events.client import Client as EventsClient
from zato.common.events.common import EventInfo, PushCtx
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

event_type_req      = EventInfo.EventType.service_request
event_type_resp     = EventInfo.EventType.service_response
object_type_service = EventInfo.CommonObject.service

# ################################################################################################################################
# ################################################################################################################################

class ServiceStatsClient:
    def __init__(self, impl_class=None):
        # type: (object) -> None
        self.host = '<ServiceStatsClient-host>'
        self.port = -1
        self.impl = None # type: EventsClient
        self.impl_class = impl_class or EventsClient
        self.backlog = []
        self.lock = RLock()

# ################################################################################################################################

    def init(self, host, port):
        # type: (str, int) -> None
        self.host = host
        self.port = port

        with self.lock:
            self.impl = self.impl_class(self.host, self.port)
            self.impl.connect()

# ################################################################################################################################

    def run(self):
        self.impl.run()

# ################################################################################################################################

    def _push_backlog(self):
        """ Pushes an event to the backend, assuming that we have access to the backend already.
        """
        # type: (str, str, str, int, str) -> None

        # Make sure we are connected to the backend ..
        if self.impl:

            # .. ensure no updates to the backlog while we run ..
            with self.lock:

                # .. get all enqueued events ..
                for item in self.backlog[:]: # type: PushCtx

                    # .. push each to the backend ..
                    self.impl.push(item)

                    # .. and remove it from the queue ..
                    self.backlog.remove(item)

# ################################################################################################################################

    def push(self, cid, timestamp, service_name, is_request, total_time_ms=0, id=None):
        """ Accepts information about the service, enqueues it as a push context and tries to empty the backlog.
        The reason we first need the backlog is that we may not be connected to the backend yet
        when this method executes. That is we need a staging area, a backlog, first.
        """
        # type: (str, str, str, int, str) -> None

        # Fill out the details of a context object ..
        ctx = PushCtx()
        ctx.id = id or new_cid()
        ctx.cid = cid
        ctx.timestamp = timestamp
        ctx.event_type = event_type_req if is_request else event_type_resp
        ctx.object_type = object_type_service
        ctx.object_id = service_name
        ctx.total_time_ms = total_time_ms

        # .. push the event to the backlog queue, using a lock to ensure the backlog is not modified in between ..
        with self.lock:
            self.backlog.append(ctx)

        # .. and try to send it to the backend now.
        self._push_backlog()

# ################################################################################################################################

    def get_table(self):
        with self.lock:
            return self.impl.get_table()

# ################################################################################################################################

    def sync_state(self):

        with self.lock:
            self.impl.sync_state()

# ################################################################################################################################
# ################################################################################################################################
