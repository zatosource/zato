# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sqlite3
import unittest
from time import monotonic, sleep

# SQLAlchemy
from sqlalchemy import text

# Test helpers
from _suite import AuditSuite
from live_otel.containers import read_records, wait_for_record

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditEvent, AuditSource
from zato.common.audit_log.sqlite_writes import env_config
from zato.common.db_env.engine import get_env_engine
from zato.common.test.conftest_base_multi_cpu import ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, new_connection
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Channel_Name = 'test.multi-cpu.audit.echo'
    Channel_Path = '/test/multi-cpu/audit/echo'

    # How many requests the test sends, each over a new connection, which the kernel assigns to one of the workers
    Request_Count = 48

    # How long the workers have to write the events of every request, in seconds
    Deadline = 60.0

    # How long the collector has after the last record arrived to write any record sent twice, in seconds
    Export_Settle_Time = 3.0

    Event_Query = """
        select event.id, event.cid, event.event_type, attr.value
        from event
        left join event_attr attr on attr.event_id = event.id and attr.name = :attr_name
        where event.source = :source and event.object_name = :object_name
    """

# ################################################################################################################################
# ################################################################################################################################

def _read_events() -> 'anylist':
    """ Returns the ID, the correlation ID, the type and the worker slot attribute of each event of the channel,
    from the audit database that the server writes to.
    """
    params = {
        'attr_name': WorkerSlotCtx.Attr_Name,
        'source': AuditSource.REST_Channel,
        'object_name': ModuleCtx.Channel_Name,
    }

    # The file of the server is read without becoming a writer of it ..
    if os.environ[AuditLogCtx.Env_Type] == AuditLogCtx.Type_SQLite:
        path = os.environ[AuditLogCtx.Env_Name]

        with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
            cursor = connection.execute(ModuleCtx.Event_Query, params)
            out = [tuple(row) for row in cursor.fetchall()]

    # .. while the PostgreSQL database of the suite is read as any client reads it.
    else:
        with get_env_engine(env_config).connect() as connection:
            result = connection.execute(text(ModuleCtx.Event_Query), params)
            out = [tuple(row) for row in result.fetchall()]

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAuditEventsAcrossWorkers(unittest.TestCase):
    """ The events of requests that every worker serves land in the one audit database of the server,
    each once, under an ID of its own and with the slot of the worker that served the request,
    and the collector receives each of them once.
    """

    def test_events_of_every_worker(self) -> 'None':

        slot_by_cid:'dict[str, str]' = {}

        for _ in range(ModuleCtx.Request_Count):
            connection = new_connection()
            connection.request('GET', ModuleCtx.Channel_Path)
            response = connection.getresponse()
            body = response.read()
            connection.close()

            self.assertEqual(response.status, MultiCPUCtx.Status_OK, body)

            data = json.loads(body)
            slot_by_cid[data['cid']] = str(data['slot'])

        # Every worker served some of the requests ..
        self.assertEqual(set(slot_by_cid.values()), {str(slot) for slot in range(MultiCPUTestConfig.worker_count)})

        # .. each of which has a request event and a response event, once all of them are written ..
        expected_count = 2 * len(slot_by_cid)
        deadline = monotonic() + ModuleCtx.Deadline

        while True:
            events = [event for event in _read_events() if event[1] in slot_by_cid]

            if len(events) >= expected_count:
                break

            if monotonic() > deadline:
                raise Exception(f'Found {len(events)} of {expected_count} events')

            sleep(MultiCPUCtx.Poll_Interval)

        self.assertEqual(len(events), expected_count)
        self.assertEqual(len({event_id for event_id, _, _, _ in events}), expected_count)

        # .. which share the correlation ID of their request and name the slot of the worker that served it.
        event_types_by_cid:'dict[str, list[str]]' = {}

        for _, cid, event_type, worker_slot in events:
            self.assertEqual(worker_slot, slot_by_cid[cid], f'Event {event_type} of {cid}')
            event_types_by_cid.setdefault(cid, []).append(event_type)

        for cid, event_types in event_types_by_cid.items():
            self.assertEqual(sorted(event_types), [AuditEvent.Request_Received, AuditEvent.Response_Sent], cid)

        # The collector receives a record of every event ..
        event_ids = [event_id for event_id, _, _, _ in events]

        for event_id in event_ids:
            _ = wait_for_record(AuditSuite.collector_output_path, event_id, timeout=ModuleCtx.Deadline)

        # .. and no more than one, whichever worker exported it.
        sleep(ModuleCtx.Export_Settle_Time)
        records = read_records(AuditSuite.collector_output_path)

        for event_id in event_ids:
            self.assertEqual(len(records[event_id]), 1, f'Records of event {event_id}')

# ################################################################################################################################
# ################################################################################################################################
