# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Callable
    from multiprocessing.connection import Connection
    from pathlib import Path
    from zato.common.typing_ import dict_

    Connection = Connection
    Path = Path

    writerdict = dict_[str, Callable[[], object]]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Queue = 0

    # The config process holds the turn and the worker writes
    Holder_Place = 1
    Writer_Place = 0

    # How long each write waits for the turn that the holder never gives up, in seconds
    Deadline = 0.2

    # How long the test waits for the worker to report and to exit, in seconds
    Report_Timeout = 60.0

    # The values that the writes of the worker refer to
    Server_Name = 'zato-test'
    Event_ID = 1
    Parent_Event_ID = 2
    Job_ID = 1
    Current_Run = 1
    Dedup_Key = 'resubmit:1:payload'
    Rule_Name = 'feed-silent'
    Repeated_Object = 'channel.repeated'
    New_Object = 'channel.new'

# ################################################################################################################################
# ################################################################################################################################

# The worker is forked, as the arbiter forks it, so that it inherits the mapping and the descriptors
_context = get_context('fork')

_region_config = {
    'queue_count': 1,
    'lock_capacity': 0,
}

# ################################################################################################################################
# ################################################################################################################################

def _write_through_every_writer(region:'SharedRegion', db_path:'str', conn:'Connection') -> 'None':
    """ Calls every writer of the audit database while the config process holds the turn of its file,
    and reports the name of the exception that each call raised, or the name of its result.
    """
    exit_code = 1

    try:

        # The worker runs under gevent, as a server does, so call_database runs the writes in the pool of the hub ..
        from gevent import monkey, reinit
        reinit()
        _ = monkey.patch_all()

        from zato.common.alerting.model import AlertRule, Finding
        from zato.common.alerting.store import raise_alert
        from zato.common.audit_log.api import AuditLink, AuditLog, get_audit_engine, ModuleCtx as AuditLogCtx
        from zato.common.audit_log.dedup import acquire_dedup_key, complete_dedup_key, release_dedup_key
        from zato.common.audit_log.file_transfer_run import update_run_event, write_run_error
        from zato.common.audit_log.scheduler import append_job_log_entry, record_job_complete, record_job_timeout
        from zato.common.db_env.engine import set_process_queue
        from zato.common.db_env.process_queue import ProcessQueue
        from zato.common.util.api import utcnow

        os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
        os.environ[AuditLogCtx.Env_Name] = db_path

        engine = get_audit_engine()
        audit_log = AuditLog(ModuleCtx.Server_Name)
        now = utcnow()

        rule = AlertRule()
        rule.name = ModuleCtx.Rule_Name

        repeated_finding = Finding()
        repeated_finding.object_name = ModuleCtx.Repeated_Object

        new_finding = Finding()
        new_finding.object_name = ModuleCtx.New_Object

        # .. one alert exists before the queue is in use, so that raising it again updates its row ..
        _ = raise_alert(engine, rule, repeated_finding, now)

        # .. and from now on, the writes of the worker take turns with those of the config process.
        process_queue = ProcessQueue(region, ModuleCtx.Queue, ModuleCtx.Writer_Place, ModuleCtx.Deadline)
        set_process_queue(engine, process_queue)

        writers:'writerdict' = {
            'record_job_complete': lambda: record_job_complete(ModuleCtx.Event_ID, outcome='ok', duration_ms=1, error=''),
            'record_job_timeout': lambda: record_job_timeout(ModuleCtx.Job_ID, ModuleCtx.Current_Run, elapsed_ms=1, error=''),
            'append_job_log_entry': lambda: append_job_log_entry(ModuleCtx.Event_ID, now, 'INFO', 'Message'),
            'update_run_event': lambda: update_run_event(ModuleCtx.Event_ID, outcome='ok'),
            'write_run_error': lambda: write_run_error(ModuleCtx.Event_ID, now, 'Error'),
            'acquire_dedup_key': lambda: acquire_dedup_key(engine, ModuleCtx.Dedup_Key, 'cid', 'resubmit'),
            'complete_dedup_key': lambda: complete_dedup_key(engine, ModuleCtx.Dedup_Key, 'ok'),
            'release_dedup_key': lambda: release_dedup_key(engine, ModuleCtx.Dedup_Key),
            'raise_alert_repeated': lambda: raise_alert(engine, rule, repeated_finding, now),
            'raise_alert_new': lambda: raise_alert(engine, rule, new_finding, now),
            'add_links': lambda: audit_log.add_links(ModuleCtx.Event_ID, [ModuleCtx.Parent_Event_ID], AuditLink.Resubmit_Of),
        }

        outcomes:'dict_[str, str]' = {}

        for name, writer in writers.items():
            try:
                result = writer()
            except Exception as exception:
                outcomes[name] = type(exception).__name__
            else:
                outcomes[name] = type(result).__name__

        conn.send(outcomes)
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_every_writer_of_the_audit_database_waits_for_its_turn(tmp_path:'Path') -> 'None':
    region = SharedRegion(_region_config)
    db_path = str(tmp_path / 'audit.db')

    # The config process takes the turn of the file and keeps it throughout ..
    _ = region.queue_enter(ModuleCtx.Queue, ModuleCtx.Holder_Place)
    assert region.queue_poll(ModuleCtx.Queue, ModuleCtx.Holder_Place)

    parent_conn, child_conn = _context.Pipe()
    process = _context.Process(target=_write_through_every_writer, args=(region, db_path, child_conn))
    process.start()

    assert parent_conn.poll(ModuleCtx.Report_Timeout)
    outcomes = parent_conn.recv()

    process.join(ModuleCtx.Report_Timeout)
    assert process.exitcode == 0

    region.queue_release(ModuleCtx.Queue, ModuleCtx.Holder_Place)

    # .. so every write of the worker waits in the queue until its deadline and runs no statement of its own.
    unqueued:'dict_[str, str]' = {}

    for name, outcome in outcomes.items():
        if outcome != 'ProcessQueueTimeout':
            unqueued[name] = outcome

    assert unqueued == {}
    assert len(outcomes) == 11

# ################################################################################################################################
# ################################################################################################################################
