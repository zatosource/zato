# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Each process of a server writes to the Zato database through pub/sub, the audit log, the shared objects
# and the alerts, and holds one engine, one thread lock and one place in the queue of the file for all of them.
# The config process runs the one background checkpointer of the file and the worker runs none.

# Zato
from server_processes import ModuleCtx as ProcessesCtx, receive, ServerProcesses
from zato.common.alerting.model import AlertRule, Finding
from zato.common.alerting.store import raise_alert
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditSource
from zato.common.common_db.store import SharedObjectStore
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.engine import _checkpointer_cache, _engine_cache, _process_queues, _sqlite_file_engine_cache, \
    _sqlite_write_locks
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from zato.common.typing_ import strintdict

    Connection = Connection
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What each process writes
    Topic_Name = 'test.one-engine.topic'
    Sub_Key_Prefix = 'sk.one-engine.'
    Object_Type = 'test.one-engine.object'
    Object_Name_Prefix = 'test.one-engine.'
    Channel_Name = 'test.one-engine.channel'
    Rule_Name = 'test.one-engine.rule'
    Alert_Object_Prefix = 'test.one-engine.alert.'

    # How long the test waits for the report of a process, in seconds
    Report_Timeout = 120.0

# ################################################################################################################################
# ################################################################################################################################

def _write_everything(conn:'Connection', role:'str') -> 'None':
    """ Writes to the Zato database through each of its stores and reports what this process holds for it.
    """
    engine = get_database_engine()

    # Pub/sub and the audit events that its publications record ..
    audit_log = AuditLog(ProcessesCtx.Server_Name)
    backend = SQLPubSubBackend(audit_log=audit_log)

    sub_key = ModuleCtx.Sub_Key_Prefix + role
    backend.subscribe(sub_key, ModuleCtx.Topic_Name)
    _ = backend.publish(ModuleCtx.Topic_Name, role)

    # .. the audit events of a channel ..
    _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, ModuleCtx.Channel_Name)

    # .. the shared objects ..
    store = SharedObjectStore()
    object_name = ModuleCtx.Object_Name_Prefix + role
    data = {'role': role}
    _ = store.compare_and_set(ModuleCtx.Object_Type, object_name, data, None)

    # .. and the alerts.
    rule = AlertRule()
    rule.name = ModuleCtx.Rule_Name

    finding = Finding()
    finding.object_name = ModuleCtx.Alert_Object_Prefix + role

    now = utcnow()
    _ = raise_alert(engine, rule, finding, now)

    report:'strintdict' = {
        'engines': len(_engine_cache),
        'file_engines': len(_sqlite_file_engine_cache),
        'checkpointers': len(_checkpointer_cache),
        'write_locks': len(_sqlite_write_locks),
        'process_queues': len(_process_queues),
    }

    conn.send(report)

# ################################################################################################################################
# ################################################################################################################################

def test_one_engine_per_process(database_path:'str') -> 'None':
    processes = ServerProcesses()

    config_conn = processes.start(ProcessesCtx.Role_Config, _write_everything, ProcessesCtx.Role_Config)
    config_report = receive(config_conn, ModuleCtx.Report_Timeout)

    worker_conn = processes.start(ProcessesCtx.Role_Worker, _write_everything, ProcessesCtx.Role_Worker)
    worker_report = receive(worker_conn, ModuleCtx.Report_Timeout)

    processes.join()

    # Each process holds one engine of the Zato database, one thread lock of its file and one place in its queue ..
    expected_config = {
        'engines': 1,
        'file_engines': 0,
        'checkpointers': 1,
        'write_locks': 1,
        'process_queues': 1,
    }

    # .. and only the config process checkpoints the file.
    expected_worker = {
        'engines': 1,
        'file_engines': 0,
        'checkpointers': 0,
        'write_locks': 1,
        'process_queues': 1,
    }

    assert config_report == expected_config, config_report
    assert worker_report == expected_worker, worker_report

# ################################################################################################################################
# ################################################################################################################################
