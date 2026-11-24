# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Audit events are committed to the SQLite file of the Zato database while another process, bound to no writer queue,
# commits to the same file at short intervals. Every audit commit waits for the lock of the file within the busy timeout
# and none of them fails.

# stdlib
import os
import shutil
import tempfile
import time
import traceback
from multiprocessing import get_context

# gevent
from gevent import reinit

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, event_table
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.engine import get_cached_engine_count
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.sql_conformance.disk import get_disk_dir
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.synchronize import Event
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict, strlist

    Connection = Connection
    Engine = Engine
    Event = Event
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory under which each test has a directory of its own
    Dir_Name = 'database-file-contention'

    # The object of the audit events of the test
    Object_Name = 'database-file.contention.channel'

    # How many audit events the test process commits
    Event_Count = 300

    # Every event with an index divisible by this has a payload of its own, the others repeat one payload
    Distinct_Payload_Interval = 2

    # The payload that the events without a payload of their own repeat
    Repeated_Payload = 'Order status request from Maria Johnson'

    # The pause of the other process between its commits, in seconds, which is the pace of the pub/sub cleanup
    Other_Pause = 0.025

    # How long the test waits for the other process to report and to exit, in seconds
    Report_Timeout = 60.0

    # What the other process sends once its engine is open
    Ready = 'ready'

# ################################################################################################################################
# ################################################################################################################################

# The other process is forked before the test process opens its engine, so that it inherits no connection of its pool
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _commit_until_stopped(db_path:'str', stop_event:'Event', conn:'Connection') -> 'None':
    """ Commits audit events to the file at short intervals until the test sets the stop event,
    and reports how many it committed and the errors it received.
    """
    exit_code = 1

    try:

        # The hub of gevent and its thread pool are those of this process ..
        reinit()

        os.environ[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
        os.environ[DatabaseEnv.Env_Path] = db_path

        # .. the engine creates the file with its schema before the test process opens it ..
        _ = get_database_engine()
        conn.send(ModuleCtx.Ready)

        audit_log = new_test_audit_log()

        commit_count = 0
        errors:'strlist' = []

        # .. the events are committed one by one, each with a payload of its own ..
        while not stop_event.is_set():

            data = f'Shipment {commit_count} for John Smith'

            try:
                _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, ModuleCtx.Object_Name,
                    cid=f'cid-other-{commit_count}', outcome=AuditOutcome.OK, data=data)
            except Exception as e:
                errors.append(f'{type(e).__name__}: {e}')
            else:
                commit_count += 1

            time.sleep(ModuleCtx.Other_Pause)

        # .. and the outcome goes to the test process.
        report:'stranydict' = {
            'commit_count': commit_count,
            'errors': errors,
        }

        conn.send(report)
        exit_code = 0

    # The exception reaches the output of the test, since the process exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _get_payload(index:'int') -> 'str':
    """ Returns the payload of an event of the test process, either one of its own or the repeated one.
    """
    remainder = index % ModuleCtx.Distinct_Payload_Interval

    if remainder == 0:
        out = f'Order {index} from John Smith'
    else:
        out = ModuleCtx.Repeated_Payload

    return out

# ################################################################################################################################

def _commit_events() -> 'strlist':
    """ Commits the audit events of the test process, each of which looks up its payload before its first insert,
    and returns the errors it received.
    """
    audit_log = new_test_audit_log()

    out:'strlist' = []

    for index in range(ModuleCtx.Event_Count):

        data = _get_payload(index)

        try:
            _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, ModuleCtx.Object_Name,
                cid=f'cid-test-{index}', outcome=AuditOutcome.OK, data=data)
        except Exception as e:
            out.append(f'{type(e).__name__}: {e}')

    return out

# ################################################################################################################################

def _count_events(engine:'Engine') -> 'int':
    """ Returns how many audit events the file holds.
    """
    query = select(func.count()).select_from(event_table)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = result.scalar_one()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_audit_commits_wait_for_a_writer_outside_the_queue() -> 'None':
    """ Each audit commit of the test process waits for the lock that the other process holds or has just released,
    and each event of both processes is in the file.
    """

    # No engine of an earlier test is left for the other process to inherit
    assert get_cached_engine_count() == 0

    base_dir = get_disk_dir(ModuleCtx.Dir_Name)
    database_dir = tempfile.mkdtemp(dir=base_dir)

    db_path = os.path.join(database_dir, DatabaseEnv.File_Name)

    stop_event = _context.Event()
    parent_conn, child_conn = _context.Pipe()

    process = _context.Process(target=_commit_until_stopped, args=(db_path, stop_event, child_conn))

    try:

        # The other process creates the file and starts its commits ..
        process.start()

        assert parent_conn.poll(ModuleCtx.Report_Timeout)

        ready = parent_conn.recv()
        assert ready == ModuleCtx.Ready

        with file_database_engine(database_dir) as engine:

            # .. the test process commits its events in the meantime ..
            errors = _commit_events()

            # .. the other process stops and reports ..
            stop_event.set()

            assert parent_conn.poll(ModuleCtx.Report_Timeout)
            report = parent_conn.recv()

            process.join(ModuleCtx.Report_Timeout)
            assert process.exitcode == 0

            # .. no commit of either process failed ..
            assert errors == []
            assert report['errors'] == []
            assert report['commit_count'] > 0

            # .. and the events of both processes are all in the file.
            event_count = _count_events(engine)
            expected_count = ModuleCtx.Event_Count + report['commit_count']

            assert event_count == expected_count

    finally:
        if process.is_alive():
            process.kill()
            process.join(ModuleCtx.Report_Timeout)

        shutil.rmtree(database_dir)

# ################################################################################################################################
# ################################################################################################################################
