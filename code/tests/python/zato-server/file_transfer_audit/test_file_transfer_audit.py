# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit trail an outgoing file transfer connection leaves - one event per read,
# store and delete, with the source, outcome and duration the alerting collectors
# measure. The connection under test runs against a local directory behind the same
# client interface the SMB wrapper drives, so the whole recording path is real
# and no remote server is needed.

# stdlib
import os
from contextlib import contextmanager
from json import loads

# Bunch
from zato.common.ext.bunch import Bunch

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_sql.env import database_env
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.server.connection.smb import SMBConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-file-transfer-server'

# The name the connection under test goes by
Connection_Name = 'test.file.transfer'

# The correlation id the operations under test run with
Test_CID = 'test-file-transfer-cid'

# What the store and read operations move
Test_File_Name = 'invoice.pdf'
Test_File_Data = b'Test invoice content'

# A path no operation can find
Missing_File_Name = 'missing-report.pdf'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

class LocalDirectoryClient:
    """ The client interface the SMB wrapper drives, backed by a local directory.
    """
    def __init__(self, base_dir:'str') -> 'None':
        self.base_dir = base_dir

    def _full_path(self, remote_path:'str') -> 'str':
        out = os.path.join(self.base_dir, remote_path)
        return out

    def read(self, remote_path:'str') -> 'bytes':
        with open(self._full_path(remote_path), 'rb') as file:
            out = file.read()
        return out

    def write(self, remote_path:'str', data:'bytes') -> 'None':
        with open(self._full_path(remote_path), 'wb') as file:
            _ = file.write(data)

    def remove(self, remote_path:'str') -> 'None':
        os.remove(self._full_path(remote_path))

# ################################################################################################################################
# ################################################################################################################################

class LocalDirectoryWrapper:
    """ Carries what the connection object reads off its wrapper - the client,
    the audit writer and the connection's configuration.
    """
    def __init__(self, base_dir:'str') -> 'None':
        self.config = Bunch(name=Connection_Name)
        self.audit_log = AuditLog(Server_Name)
        self.should_store_content = False
        self._client = LocalDirectoryClient(base_dir)

    @contextmanager
    def client(self, should_block:'bool'=False, block_timeout:'any_'=None) -> 'any_':
        yield self._client

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _audit_db_env(tmp_path:'any_', check_name:'str') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database of one check's own.
    """
    directory = os.path.join(str(tmp_path), check_name)
    os.makedirs(directory)

    db_path = os.path.join(directory, 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def _new_connection(tmp_path:'any_', check_name:'str') -> 'SMBConnection':
    """ Builds the connection under test over a local directory of one check's own.
    """
    base_dir = os.path.join(str(tmp_path), check_name + '-files')
    os.makedirs(base_dir)

    wrapper = LocalDirectoryWrapper(base_dir)

    out = SMBConnection(Test_CID, wrapper)
    return out

# ################################################################################################################################

def _get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_store_is_recorded(tmp_path:'any_') -> 'None':
    """ Writing a file leaves one store event with the size and outcome.
    """
    with _audit_db_env(tmp_path, 'store'):

        conn = _new_connection(tmp_path, 'store')
        conn.write(Test_File_Data, Test_File_Name)

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['object_name'] == Connection_Name
        assert event['endpoint'] == Test_File_Name
        assert event['outcome'] == AuditOutcome.OK
        assert event['server_name'] == Server_Name
        assert event['cid'] == Test_CID
        assert event['size'] == len(Test_File_Data)
        assert event['duration_ms'] >= 0

        summary = loads(event['data'])

        assert summary['operation'] == 'store'
        assert summary['remote_path'] == Test_File_Name

# ################################################################################################################################

def test_a_read_is_recorded(tmp_path:'any_') -> 'None':
    """ Reading a file leaves one read event with the size that came back.
    """
    with _audit_db_env(tmp_path, 'read'):

        conn = _new_connection(tmp_path, 'read')
        conn.write(Test_File_Data, Test_File_Name)

        data = conn.read(Test_File_Name)
        assert data == Test_File_Data

        events = _get_events()
        assert len(events) == 2

        event = events[1]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['outcome'] == AuditOutcome.OK
        assert event['size'] == len(Test_File_Data)

        summary = loads(event['data'])

        assert summary['operation'] == 'read'
        assert summary['remote_path'] == Test_File_Name

# ################################################################################################################################

def test_a_failed_read_is_recorded(tmp_path:'any_') -> 'None':
    """ A read that found nothing leaves one error event before the caller
    learns about it.
    """
    with _audit_db_env(tmp_path, 'failed-read'):

        conn = _new_connection(tmp_path, 'failed-read')

        try:
            _ = conn.read(Missing_File_Name)
        except Exception:
            pass
        else:
            raise Exception('A failed read was expected to propagate')

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['outcome'] == AuditOutcome.Error

        summary = loads(event['data'])

        assert summary['operation'] == 'read'
        assert summary['error']

# ################################################################################################################################

def test_a_delete_is_recorded(tmp_path:'any_') -> 'None':
    """ Deleting a file leaves one delete event.
    """
    with _audit_db_env(tmp_path, 'delete'):

        conn = _new_connection(tmp_path, 'delete')
        conn.write(Test_File_Data, Test_File_Name)

        conn.delete_file(Test_File_Name)

        events = _get_events()
        assert len(events) == 2

        event = events[1]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['outcome'] == AuditOutcome.OK

        summary = loads(event['data'])

        assert summary['operation'] == 'delete'
        assert summary['remote_path'] == Test_File_Name

# ################################################################################################################################
# ################################################################################################################################
