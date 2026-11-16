# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import re
import sqlite3
import unittest
from time import monotonic, sleep

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditSource
from zato.common.test.conftest_base_multi_cpu import connection_to_slot, get_json, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_singletons.audit_retention')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many requests the test sends through each slot, each of which the audit log records as two events,
    # so that every worker writes more events than the number after which it requests a retention run
    Requests_Per_Slot = 520

    # The slot whose worker runs audit log retention
    Singleton_Slot = 0

    # How long retention has to run after the last request, in seconds
    Deadline = 60.0

    # How long the log is observed after the first run, so that a run of any other worker is recorded as well
    Settle_Period = 10.0

    # The separator of the fields of a line of the server log, the third of which is the process ID and the thread
    Log_Field_Separator = ' - '
    Log_Process_Field = 2

    Deleted_Pattern = re.compile(rf'Audit log retention deleted (\d+) {AuditSource.REST_Channel} events?')

    Archive_Kind_Event = 'event'

    Event_Query = 'select id, cid, event_type from event where id in ({})'

# ################################################################################################################################
# ################################################################################################################################

def _get_deleted_lines() -> 'strlist':
    """ Returns the lines of the server log that report the deletion of events of the REST channels.
    """
    path = os.path.join(MultiCPUTestConfig.server_directory, MultiCPUCtx.Log_Path)

    with open(path) as log_file:
        lines = log_file.read().splitlines()

    out:'strlist' = []

    for line in lines:
        if ModuleCtx.Deleted_Pattern.search(line):
            out.append(line)

    return out

# ################################################################################################################################

def _get_archived_events() -> 'list[tuple[int, str, str]]':
    """ Returns the ID, the correlation ID and the type of each event of the REST channels in the archive files,
    once per line that holds it. SQLite gives the ID of a deleted event to the next event written,
    so an event is identified by all three.
    """
    out:'list[tuple[int, str, str]]' = []

    for file_name in sorted(os.listdir(SingletonsConfig.archive_dir)):
        path = os.path.join(SingletonsConfig.archive_dir, file_name)

        with open(path) as archive_file:
            for line in archive_file:
                row = json.loads(line)

                if row['kind'] == ModuleCtx.Archive_Kind_Event and row['source'] == AuditSource.REST_Channel:
                    out.append((row['id'], row['cid'], row['event_type']))

    return out

# ################################################################################################################################

def _get_stored_events(event_ids:'intlist') -> 'set[tuple[int, str, str]]':
    """ Returns the ID, the correlation ID and the type of each event in the audit database under one of the IDs,
    which the test reads without becoming a writer of the database.
    """
    path = os.environ[AuditLogCtx.Env_Name]
    placeholders = ', '.join('?' * len(event_ids))
    query = ModuleCtx.Event_Query.format(placeholders)

    out:'set[tuple[int, str, str]]' = set()

    with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
        for event_id, cid, event_type in connection.execute(query, event_ids):
            out.add((event_id, cid, event_type))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAuditRetentionAcrossWorkers(unittest.TestCase):
    """ Every worker requests audit log retention after the events it writes, and the worker of slot 0 alone runs it,
    so each expired event is deleted and archived once.
    """

    def test_retention_runs_in_one_worker(self) -> 'None':

        # The process of the worker that runs retention ..
        connection = connection_to_slot(ModuleCtx.Singleton_Slot)
        singleton_pid = get_json(connection, MultiCPUCtx.Worker_Slot_Path)['pid']
        connection.close()

        # .. each worker records the events of its requests until it requests a run ..
        for slot in range(MultiCPUTestConfig.worker_count):

            connection = connection_to_slot(slot)

            for _ in range(ModuleCtx.Requests_Per_Slot):
                response = get_json(connection, MultiCPUCtx.Worker_Slot_Path)
                self.assertEqual(response['slot'], slot)

            connection.close()

        # .. retention runs at least once ..
        deadline = monotonic() + ModuleCtx.Deadline

        while not _get_deleted_lines():

            if monotonic() > deadline:
                raise Exception(f'No retention run within {ModuleCtx.Deadline} s')

            sleep(MultiCPUCtx.Poll_Interval)

        sleep(ModuleCtx.Settle_Period)

        # .. and every run took place in the worker of slot 0 ..
        deleted_lines = _get_deleted_lines()
        deleted_count = 0

        for line in deleted_lines:
            process_field = line.split(ModuleCtx.Log_Field_Separator)[ModuleCtx.Log_Process_Field]
            pid = int(process_field.split(':')[0])
            self.assertEqual(pid, singleton_pid, line)

            line_deleted_count = ModuleCtx.Deleted_Pattern.findall(line)[0]
            deleted_count += int(line_deleted_count)

        logger.info('Retention runs: %d, deleted events: %d', len(deleted_lines), deleted_count)

        # .. which archived each event that it deleted once ..
        archived_events = _get_archived_events()
        archived_event_set = set(archived_events)

        self.assertEqual(len(archived_events), deleted_count)
        self.assertEqual(len(archived_event_set), deleted_count)

        # .. and none of which remains in the database.
        archived_ids:'intlist' = []

        for event_id, _, _ in archived_events:
            archived_ids.append(event_id)

        stored_events = _get_stored_events(archived_ids)
        self.assertEqual(archived_event_set & stored_events, set())

# ################################################################################################################################
# ################################################################################################################################
