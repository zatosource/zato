# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from time import sleep
from unittest import main, TestCase

# dacity
from dacite import from_dict

# Zato
from zato.common.events.common import EventInfo, PushCtx
from zato.common.test import rand_int, rand_string
from zato.common.typing_ import asdict
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
zato_logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class Default:
    LenEvents      = 4
    LenServices    = 3
    IterMultiplier = 11

# ################################################################################################################################
# ################################################################################################################################

class EventsDatabaseTestCase(TestCase):

# ################################################################################################################################

    def yield_events(self, len_events=None, len_services=None, iter_multiplier=None):

        len_events      = len_events      or Default.LenEvents
        len_services    = len_services    or Default.LenServices
        iter_multiplier = iter_multiplier or Default.IterMultiplier

        for service_idx in range(1, len_services+1):

            service_name = 'service-{}'.format(service_idx)

            for event_idx in range(1, len_events+1):
                event_idx_str = str(event_idx)

                id  = 'id-{}-{}'.format(service_idx, event_idx)
                cid = 'cid-{}-{}'.format(service_idx, event_idx)

                ctx = PushCtx()
                ctx.id = id
                ctx.cid = cid
                ctx.timestamp = utcnow().isoformat()
                ctx.event_type = EventInfo.EventType.service_response
                ctx.object_type = EventInfo.ObjectType.service
                ctx.object_id = service_name
                ctx.total_time_ms = service_idx * event_idx * iter_multiplier

                # We are adding a short pause to be better able to observe
                # that each context object has a different timestamp assigned.
                sleep(0.005)

                yield asdict(ctx)

# ################################################################################################################################

    def yield_events_db(self, logger=None, fs_data_path=None, sync_threshold=None, sync_interval=None):

        logger = logger or zato_logger
        fs_data_path = None or rand_string(prefix='fs_data_path')
        sync_threshold = sync_threshold or rand_int()
        sync_interval  = sync_interval  or rand_int()

        return EventsDatabase(logger, fs_data_path, sync_threshold, sync_interval)

# ################################################################################################################################

    def xtest_init(self):

        sync_threshold = rand_int()
        sync_interval  = rand_int()

        events_db = self.yield_events_db(sync_threshold=sync_threshold, sync_interval=sync_interval)

        self.assertEqual(events_db.sync_threshold, sync_threshold)
        self.assertEqual(events_db.sync_interval, sync_interval)

# ################################################################################################################################

    def xtest_push(self):

        data = {
            'key1': rand_string()
        }

        events_db = self.yield_events_db()
        events_db.push(data)

        self.assertEqual(len(events_db.in_ram_store), 1)

        given_data = events_db.in_ram_store[0] # type: dict

        self.assertDictEqual(data, given_data)

# ################################################################################################################################

    def test_get_data_from_ram(self):

        start = utcnow().isoformat()
        events_db = self.yield_events_db()

        for event_data in self.yield_events():
            events_db.push(event_data)

        self.assertEqual(len(events_db.in_ram_store), Default.LenEvents * Default.LenServices)

        ctx_list = []

        for item in events_db.in_ram_store:
            ctx = from_dict(PushCtx, item)
            ctx_list.append(ctx)

        print(len(ctx_list))

        ctx1 = ctx_list[0]   # type: PushCtx
        ctx2 = ctx_list[1]   # type: PushCtx
        ctx3 = ctx_list[2]   # type: PushCtx
        ctx4 = ctx_list[3]   # type: PushCtx
        ctx5 = ctx_list[4]   # type: PushCtx
        ctx6 = ctx_list[5]   # type: PushCtx
        ctx7 = ctx_list[6]   # type: PushCtx
        ctx8 = ctx_list[7]   # type: PushCtx
        ctx9 = ctx_list[8]   # type: PushCtx
        ctx10 = ctx_list[9]  # type: PushCtx
        ctx11 = ctx_list[10] # type: PushCtx
        ctx12 = ctx_list[11] # type: PushCtx

        self.assertEqual(ctx1.id, 'a')

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
