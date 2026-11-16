# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sqlite3
import subprocess
import unittest
from tempfile import mkdtemp
from time import monotonic, sleep

# Zato
from zato.common.analytics.api import ModuleCtx as AnalyticsCtx
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditEvent
from zato.common.test.conftest_base_multi_cpu import get_json, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_singletons.analytics_rollup')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Channel_Name = 'test.multi-cpu.singletons.audit-echo'
    Channel_Path = '/test/multi-cpu/singletons/audit-echo'

    # How many requests the test sends, each over a new connection, which the kernel assigns to one of the workers
    Request_Count = 64

    # How many rollups run at the same time
    Rollup_Count = 2

    # How long the workers have to write the events of every request and a rollup has to complete, in seconds
    Deadline = 60.0

    Response_Count_Query = 'select count(*) from event where object_name = ? and event_type = ?'
    Usage_Count_Query = 'select coalesce(sum(request_count), 0) from usage where channel = ?'

    File_Name = 'analytics.db'

# ################################################################################################################################
# ################################################################################################################################

def _query_one(path:'str', query:'str', params:'tuple[str, ...]') -> 'int':
    """ Returns the single value of a query against a SQLite file, which the test reads without becoming a writer of it.
    """
    with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
        out = connection.execute(query, params).fetchone()[0]

    return out

# ################################################################################################################################

def _run_rollups(count:'int', analytics_path:'str') -> 'None':
    """ Runs rollups as separate processes started together, as overlapping runs of a scheduler start them.
    """
    env = dict(os.environ)
    env[AnalyticsCtx.Env_Path] = analytics_path

    command = [MultiCPUTestConfig.zato_bin, 'analytics', 'rollup']
    processes:'list[subprocess.Popen[str]]' = []

    for _ in range(count):
        process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        processes.append(process)

    for process in processes:
        output, _ = process.communicate(timeout=ModuleCtx.Deadline)
        logger.info('Rollup -> %s', output.strip())

        if process.returncode != 0:
            raise Exception(f'Rollup exited with {process.returncode} -> {output}')

# ################################################################################################################################
# ################################################################################################################################

class TestAnalyticsRollupAcrossWorkers(unittest.TestCase):
    """ Rollups that overlap count the responses that every worker of the server writes to the audit log once each.
    """

    def test_overlapping_rollups_count_each_response_once(self) -> 'None':

        audit_path = os.environ[AuditLogCtx.Env_Name]
        analytics_path = os.path.join(mkdtemp(prefix='zato_multi_cpu_singletons_analytics_'), ModuleCtx.File_Name)

        # Every worker serves some of the requests ..
        slots:'strset' = set()

        for _ in range(ModuleCtx.Request_Count):
            connection = new_connection()
            response = get_json(connection, ModuleCtx.Channel_Path)
            connection.close()
            slots.add(str(response['slot']))

        self.assertEqual(slots, {str(slot) for slot in range(MultiCPUTestConfig.worker_count)})

        # .. and writes the response event of each to the one audit database ..
        response_params = (ModuleCtx.Channel_Name, AuditEvent.Response_Sent)
        deadline = monotonic() + ModuleCtx.Deadline

        while _query_one(audit_path, ModuleCtx.Response_Count_Query, response_params) < ModuleCtx.Request_Count:

            if monotonic() > deadline:
                raise Exception(f'Not every response event was written within {ModuleCtx.Deadline} s')

            sleep(MultiCPUCtx.Poll_Interval)

        # .. which rollups started together aggregate, followed by one that finds nothing new ..
        _run_rollups(ModuleCtx.Rollup_Count, analytics_path)
        _run_rollups(1, analytics_path)

        # .. and the usage rows of the channel count each request once.
        request_count = _query_one(analytics_path, ModuleCtx.Usage_Count_Query, (ModuleCtx.Channel_Name,))
        self.assertEqual(request_count, ModuleCtx.Request_Count)

# ################################################################################################################################
# ################################################################################################################################
