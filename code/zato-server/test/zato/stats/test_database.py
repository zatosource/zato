# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from datetime import datetime
from tempfile import gettempdir
from time import sleep
from unittest import main, TestCase

# Pandas
import pandas as pd

# Zato
from zato.common.events.common import EventInfo, PushCtx
from zato.common.test import rand_int, rand_string
from zato.common.typing_ import asdict, from_dict
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase, OpCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pandas import DataFrame

    DataFrame = DataFrame

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

idx_str_map = {
    1: 'a',
    2: 'b',
    3: 'c',
}

# ################################################################################################################################
# ################################################################################################################################

class EventsDatabaseTestCase(TestCase):

# ################################################################################################################################

    def yield_events(self, len_events=None, len_services=None, iter_multiplier=None):

        len_events      = len_events      or Default.LenEvents
        len_services    = len_services    or Default.LenServices
        iter_multiplier = iter_multiplier or Default.IterMultiplier

        for service_idx in range(1, len_services+1):

            service_idx_str = idx_str_map[service_idx]
            service_name = 'service-{}'.format(service_idx)

            for event_idx in range(1, len_events+1):
                event_idx_str = str(event_idx)

                id  = 'id-{}{}'.format(service_idx_str, event_idx)
                cid = 'cid-{}{}'.format(service_idx_str, event_idx)

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

    def get_events_db(self, logger=None, fs_data_path=None, sync_threshold=None, sync_interval=None):

        logger = logger or zato_logger
        fs_data_path = fs_data_path or rand_string(prefix='fs_data_path')
        sync_threshold = sync_threshold or rand_int()
        sync_interval  = sync_interval  or rand_int()

        return EventsDatabase(logger, fs_data_path, sync_threshold, sync_interval)

# ################################################################################################################################

    def test_init(self):

        sync_threshold = rand_int()
        sync_interval  = rand_int()

        events_db = self.get_events_db(sync_threshold=sync_threshold, sync_interval=sync_interval)

        self.assertEqual(events_db.sync_threshold, sync_threshold)
        self.assertEqual(events_db.sync_interval, sync_interval)

# ################################################################################################################################

    def test_push(self):

        start = utcnow().isoformat()
        events_db = self.get_events_db()

        for event_data in self.yield_events():
            events_db.push(event_data)

        self.assertEqual(len(events_db.in_ram_store), Default.LenEvents * Default.LenServices)

        ctx_list = []

        for item in events_db.in_ram_store:
            ctx = from_dict(PushCtx, item)
            ctx_list.append(ctx)

        self.assertEqual(len(ctx_list), Default.LenEvents * Default.LenServices)
        self.assertEqual(events_db.telemetry[OpCode.Internal.GetFromRAM],  0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.CreateNewDF], 0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.ReadParqet],  0)

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

        #
        # ctx.id
        #

        self.assertEqual(ctx1.id,  'id-a1')
        self.assertEqual(ctx2.id,  'id-a2')
        self.assertEqual(ctx3.id,  'id-a3')
        self.assertEqual(ctx4.id,  'id-a4')

        self.assertEqual(ctx5.id,  'id-b1')
        self.assertEqual(ctx6.id,  'id-b2')
        self.assertEqual(ctx7.id,  'id-b3')
        self.assertEqual(ctx8.id,  'id-b4')

        self.assertEqual(ctx9.id,  'id-c1')
        self.assertEqual(ctx10.id, 'id-c2')
        self.assertEqual(ctx11.id, 'id-c3')
        self.assertEqual(ctx12.id, 'id-c4')

        #
        # ctx.cid
        #

        self.assertEqual(ctx1.cid,  'cid-a1')
        self.assertEqual(ctx2.cid,  'cid-a2')
        self.assertEqual(ctx3.cid,  'cid-a3')
        self.assertEqual(ctx4.cid,  'cid-a4')

        self.assertEqual(ctx5.cid,  'cid-b1')
        self.assertEqual(ctx6.cid,  'cid-b2')
        self.assertEqual(ctx7.cid,  'cid-b3')
        self.assertEqual(ctx8.cid,  'cid-b4')

        self.assertEqual(ctx9.cid,  'cid-c1')
        self.assertEqual(ctx10.cid, 'cid-c2')
        self.assertEqual(ctx11.cid, 'cid-c3')
        self.assertEqual(ctx12.cid, 'cid-c4')

        #
        # ctx.timestamp
        #

        self.assertGreater(ctx1.timestamp,  start)
        self.assertGreater(ctx2.timestamp,  ctx1.timestamp)
        self.assertGreater(ctx3.timestamp,  ctx2.timestamp)
        self.assertGreater(ctx4.timestamp,  ctx3.timestamp)
        self.assertGreater(ctx5.timestamp,  ctx4.timestamp)
        self.assertGreater(ctx6.timestamp,  ctx5.timestamp)
        self.assertGreater(ctx7.timestamp,  ctx6.timestamp)
        self.assertGreater(ctx8.timestamp,  ctx7.timestamp)
        self.assertGreater(ctx9.timestamp,  ctx8.timestamp)
        self.assertGreater(ctx10.timestamp, ctx9.timestamp)
        self.assertGreater(ctx11.timestamp, ctx10.timestamp)
        self.assertGreater(ctx12.timestamp, ctx11.timestamp)

        #
        # ctx.event_type
        #

        self.assertEqual(ctx1.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx2.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx3.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx4.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx5.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx6.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx7.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx8.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx9.event_type,  EventInfo.EventType.service_response)
        self.assertEqual(ctx10.event_type, EventInfo.EventType.service_response)
        self.assertEqual(ctx11.event_type, EventInfo.EventType.service_response)
        self.assertEqual(ctx12.event_type, EventInfo.EventType.service_response)

        #
        # ctx.object_type
        #

        self.assertEqual(ctx1.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx2.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx3.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx4.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx5.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx6.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx7.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx8.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx9.object_type,  EventInfo.ObjectType.service)
        self.assertEqual(ctx10.object_type, EventInfo.ObjectType.service)
        self.assertEqual(ctx11.object_type, EventInfo.ObjectType.service)
        self.assertEqual(ctx12.object_type, EventInfo.ObjectType.service)

        self.assertEqual(ctx1.object_id,  'service-1')
        self.assertEqual(ctx2.object_id,  'service-1')
        self.assertEqual(ctx3.object_id,  'service-1')
        self.assertEqual(ctx4.object_id,  'service-1')
        self.assertEqual(ctx5.object_id,  'service-2')
        self.assertEqual(ctx6.object_id,  'service-2')
        self.assertEqual(ctx7.object_id,  'service-2')
        self.assertEqual(ctx8.object_id,  'service-2')
        self.assertEqual(ctx9.object_id,  'service-3')
        self.assertEqual(ctx10.object_id, 'service-3')
        self.assertEqual(ctx11.object_id, 'service-3')
        self.assertEqual(ctx12.object_id, 'service-3')

        self.assertEqual(ctx1.total_time_ms, 11)
        self.assertEqual(ctx2.total_time_ms, 22)
        self.assertEqual(ctx3.total_time_ms, 33)
        self.assertEqual(ctx4.total_time_ms, 44)
        self.assertEqual(ctx5.total_time_ms, 22)
        self.assertEqual(ctx6.total_time_ms, 44)
        self.assertEqual(ctx7.total_time_ms, 66)
        self.assertEqual(ctx8.total_time_ms, 88)
        self.assertEqual(ctx9.total_time_ms, 33)
        self.assertEqual(ctx10.total_time_ms, 66)
        self.assertEqual(ctx11.total_time_ms, 99)
        self.assertEqual(ctx12.total_time_ms, 132)

# ################################################################################################################################

    def test_get_data_from_storage_path_does_not_exist(self):

        # Be explicit about the fact that we are using a random path, one that does not exist
        fs_data_path = rand_string()

        # Create a new instance
        events_db = self.get_events_db(fs_data_path=fs_data_path)

        # This should return an empty DataFrame because the path did not exist
        data = events_db.get_data_from_storage() # type: DataFrame

        self.assertEqual(len(data), 0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.GetFromRAM],  0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.CreateNewDF], 1)
        self.assertEqual(events_db.telemetry[OpCode.Internal.ReadParqet],  0)

# ################################################################################################################################

    def test_get_data_from_storage_path_exists(self):

        # Be explicit about the fact that we are using a random path, one that does not exist
        file_name = 'zato-test-events-db-' + rand_string()
        temp_dir = gettempdir()

        fs_data_path = os.path.join(temp_dir, file_name)

        # Obtain test data
        test_data = list(self.yield_events())

        # Turn it into a DataFrame
        data_frame = pd.DataFrame(test_data)

        # Save it as as a Parquet file
        data_frame.to_parquet(fs_data_path)

        # Create a new DB instance
        events_db = self.get_events_db(fs_data_path=fs_data_path)

        # This should return an empty DataFrame because the path did not exist
        data = events_db.get_data_from_storage() # type: DataFrame

        self.assertEqual(len(data), len(test_data))
        self.assertEqual(events_db.telemetry[OpCode.Internal.GetFromRAM],  0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.CreateNewDF], 0)
        self.assertEqual(events_db.telemetry[OpCode.Internal.ReadParqet],  1)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
