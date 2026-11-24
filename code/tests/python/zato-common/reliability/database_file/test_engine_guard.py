# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite file of the Zato database is removed or replaced while a process uses it through the engine factory.
# The process neither reads nor writes the database again, acknowledges no commit made into the removed file,
# refuses publications and audit events, and creates no new file in place of the one that was removed.

# stdlib
import hashlib
import logging
import os
import shutil
import tempfile
from typing import NamedTuple

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import event as sa_event
from sqlalchemy import inspect

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLink, AuditSource, event_table
from zato.common.db_env.database import dispose_database_engine, get_database_engine, is_database_lost
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.sqlite_identity import DatabaseFileReplaced
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.schema import message_table
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.sql_conformance.disk import get_disk_dir
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_

    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logrecordlist = list[logging.LogRecord]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory under which each test has a directory of its own
    Dir_Name = 'database-file-engine'

    # The logger that records a file that was removed or replaced
    Identity_Logger_Name = 'zato.common.db_env.sqlite_identity'

    # The files that SQLite keeps next to a database in the WAL mode
    Companion_Suffixes = ('-wal', '-shm')

    # The suffix of the copy of a database that replaces it
    Copy_Suffix = '.copy'

    # The topic of the publications and the object of the audit events of the tests
    Topic_Name = 'database-file.engine'
    Object_Name = 'database-file.engine.channel'

    # The events of the lineage link that the tests write
    Child_Event_ID  = 2
    Parent_Event_ID = 1

# ################################################################################################################################
# ################################################################################################################################

class DatabaseFile(NamedTuple):
    """ The engine of the Zato database of a test and the path of its SQLite file.
    """
    engine: 'Engine'
    path: 'str'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database() -> 'any_':
    """ The Zato database of a test, in a SQLite file of a directory of its own.
    """
    base_dir = get_disk_dir(ModuleCtx.Dir_Name)
    database_dir = tempfile.mkdtemp(dir=base_dir)

    db_path = os.path.join(database_dir, DatabaseEnv.File_Name)

    try:
        with file_database_engine(database_dir) as engine:
            yield DatabaseFile(engine, db_path)
    finally:
        shutil.rmtree(database_dir)

# ################################################################################################################################
# ################################################################################################################################

def _remove_database(db_path:'str') -> 'None':
    """ Removes a database file together with the files that SQLite keeps next to it, as a restore script does.
    """
    os.remove(db_path)

    for suffix in ModuleCtx.Companion_Suffixes:
        companion_path = db_path + suffix

        if os.path.exists(companion_path):
            os.remove(companion_path)

# ################################################################################################################################

class _RemovalOnCommit:
    """ Removes a database file when a transaction of an engine is about to commit.
    """
    def __init__(self, db_path:'str') -> 'None':
        self.db_path = db_path

    def on_commit(self, connection:'Connection') -> 'None':
        _remove_database(self.db_path)

# ################################################################################################################################

def _open_connection(engine:'Engine') -> 'None':
    """ Checks out a connection of the pool of an engine and returns it to the pool.
    """
    connection = engine.connect()
    connection.close()

# ################################################################################################################################

def _get_digest(path:'str') -> 'str':
    """ Returns the SHA-256 digest of the content of a file.
    """
    with open(path, 'rb') as input_file:
        data = input_file.read()

    content_hash = hashlib.sha256(data)

    out = content_hash.hexdigest()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_new_file_is_created_with_its_schema(database:'DatabaseFile') -> 'None':
    """ An engine for a path whose identity the process has not recorded creates the file and its schema.
    """
    assert os.path.exists(database.path)

    inspector = inspect(database.engine)
    table_names = inspector.get_table_names()

    assert event_table.name in table_names
    assert message_table.name in table_names

# ################################################################################################################################

def test_a_removed_file_is_refused_and_not_created_again(database:'DatabaseFile', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A connection of a file that was removed is refused each time it is checked out, the removal is logged once,
    and no file appears in place of the removed one.
    """
    _remove_database(database.path)

    with caplog.at_level(logging.CRITICAL, logger=ModuleCtx.Identity_Logger_Name):

        with pytest.raises(DatabaseFileReplaced):
            _open_connection(database.engine)

        with pytest.raises(DatabaseFileReplaced):
            _open_connection(database.engine)

    critical_records:'logrecordlist' = []

    for record in caplog.records:
        if record.name == ModuleCtx.Identity_Logger_Name:
            if record.levelno == logging.CRITICAL:
                critical_records.append(record)

    assert len(critical_records) == 1, critical_records
    assert is_database_lost()
    assert not os.path.exists(database.path)

# ################################################################################################################################

def test_a_replaced_file_is_refused_and_left_unchanged(database:'DatabaseFile') -> 'None':
    """ A file that another file replaced is refused, and the process writes nothing into the replacement.
    """
    copy_path = database.path + ModuleCtx.Copy_Suffix

    _ = shutil.copy2(database.path, copy_path)
    os.replace(copy_path, database.path)

    digest = _get_digest(database.path)

    with pytest.raises(DatabaseFileReplaced):
        _open_connection(database.engine)

    # The pooled connections of the replaced file are closed and no new engine is built for the replacement
    dispose_database_engine()

    with pytest.raises(DatabaseFileReplaced):
        _ = get_database_engine()

    digest_after = _get_digest(database.path)

    assert digest_after == digest

# ################################################################################################################################

def test_an_engine_is_not_built_again_after_the_removal(database:'DatabaseFile') -> 'None':
    """ Once the engine of a removed file is disposed of, no new engine is built, and neither the file
    nor its schema is created again.
    """
    _remove_database(database.path)
    dispose_database_engine()

    with pytest.raises(DatabaseFileReplaced):
        _ = get_database_engine()

    assert not os.path.exists(database.path)

# ################################################################################################################################

def test_a_commit_into_a_removed_file_is_not_acknowledged(database:'DatabaseFile') -> 'None':
    """ A transaction during which the file is removed commits into the removed file, and its caller
    receives DatabaseFileReplaced instead of an acknowledgement.
    """
    audit_log = new_test_audit_log()

    removal = _RemovalOnCommit(database.path)
    sa_event.listen(database.engine, 'commit', removal.on_commit)

    try:
        with pytest.raises(DatabaseFileReplaced):
            _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, ModuleCtx.Object_Name)
    finally:
        sa_event.remove(database.engine, 'commit', removal.on_commit)

    assert is_database_lost()
    assert not os.path.exists(database.path)

# ################################################################################################################################

def test_a_publication_is_refused_after_the_removal(database:'DatabaseFile') -> 'None':
    """ Once the process found the file removed, a publication is refused before any statement is issued.
    """
    backend = SQLPubSubBackend(audit_log=new_test_audit_log())

    _remove_database(database.path)

    with pytest.raises(DatabaseFileReplaced):
        _open_connection(database.engine)

    with pytest.raises(DatabaseFileReplaced):
        _ = backend.publish(ModuleCtx.Topic_Name, 'Order 12345 shipped')

    assert not os.path.exists(database.path)

# ################################################################################################################################

def test_audit_events_are_refused_after_the_removal(database:'DatabaseFile') -> 'None':
    """ Once the process found the file removed, audit events are not written and audit writes are refused,
    and the file is not created again.
    """
    audit_log = new_test_audit_log()

    _remove_database(database.path)

    with pytest.raises(DatabaseFileReplaced):
        _open_connection(database.engine)

    event_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, ModuleCtx.Object_Name)

    assert event_id is None

    parents = [ModuleCtx.Parent_Event_ID]

    with pytest.raises(DatabaseFileReplaced):
        audit_log.add_links(ModuleCtx.Child_Event_ID, parents, AuditLink.Resubmit_Of)

    assert not os.path.exists(database.path)

# ################################################################################################################################
# ################################################################################################################################
