# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# gevent
from gevent import sleep

# pytest
import pytest

# Zato
from conftest import ModuleCtx
from live_sql.env import database_env
from support import Object_Name, Server_Name
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.db_env.engine import _checkpointer_cache
from zato.common.db_env.sqlite_checkpoint import Autocheckpoint_Pages, Checkpoint_Interval_Seconds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.db_env.sqlite_checkpoint import WALCheckpointer

    Engine = Engine
    WALCheckpointer = WALCheckpointer

    strgen = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

# How many events the test writes
_event_count = 200

# How many checkpoint intervals the test waits for a background checkpoint at most
_max_intervals = 20

# ################################################################################################################################
# ################################################################################################################################

def _get_checkpointer(engine:'Engine') -> 'WALCheckpointer':
    """ Returns the background checkpointer of an engine.
    """
    for checkpointer in _checkpointer_cache.values():
        if checkpointer.engine is engine:
            return checkpointer

    # .. an engine of the audit log on SQLite always has one.
    else:
        raise Exception('No checkpointer found for the engine')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def sqlite_db_path(tmp_path:'os.PathLike') -> 'strgen':
    """ Opens the SQLite audit database before the test, as a server opens it at startup. The schema is created
    outside the monitored test because each of its statements waits for the log to be flushed to disk.
    """
    db_path = os.path.join(str(tmp_path), ModuleCtx.SQLite_File_Name)

    details = {
        'type': 'sqlite',
        'name': db_path,
    }

    with database_env(details):
        _ = get_database_engine()
        yield db_path

# ################################################################################################################################

def test_wal_is_checkpointed_in_background(sqlite_db_path:'str') -> 'None':
    """ The commits of the SQLite audit database leave the WAL to a thread of its own, which copies it into
    the database file, and the thread stops along with its engine.
    """
    engine = get_database_engine()
    checkpointer = _get_checkpointer(engine)

    # The connections checkpoint by themselves only once the log is much longer ..
    with engine.connect() as connection:
        result = connection.exec_driver_sql('pragma wal_autocheckpoint')
        limit = result.scalar()

    assert limit == Autocheckpoint_Pages

    # .. the events are written to the log ..
    audit_log = AuditLog(Server_Name)

    for index in range(_event_count):
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
            cid=f'cid-{index}', msg_id=f'msg-{index}', outcome=AuditOutcome.OK, data=f'Order {index} from John Smith')

    size_after_writes = os.path.getsize(sqlite_db_path)

    # .. and the background checkpoint copies them into the database file.
    for _ in range(_max_intervals):
        sleep(Checkpoint_Interval_Seconds)
        if os.path.getsize(sqlite_db_path) > size_after_writes:
            break

    assert os.path.getsize(sqlite_db_path) > size_after_writes

    # The checkpoints end with the engine.
    dispose_database_engine()

    checkpointer._thread.join(Checkpoint_Interval_Seconds * 4)
    assert not checkpointer._thread.is_alive()

# ################################################################################################################################
# ################################################################################################################################
