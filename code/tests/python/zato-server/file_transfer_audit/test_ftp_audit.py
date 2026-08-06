# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A file handed to an FTP server leaves one request-sent event saying which connection
# moved which path, how big the file was and how it ended - a failed operation too.
# FTP operations carry no service context, so each event runs under a correlation id
# of its own, and the file's bytes are never stored.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import list_attachments
from zato.common.audit_log.file_transfer import Operation_Delete, Operation_Store

# Test support
from audit_env import audit_db_env
from ftp_stub import new_ftp_facade, patched_fs, Connection_Name, File_Content, Raised_Error, Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import anylist

    os = os

# ################################################################################################################################
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

def test_a_store_writes_one_event_with_the_path_and_size(tmp_path:'os.PathLike') -> 'None':
    """ Writing a file to a server is one event with everything an auditor asks about.
    """
    with audit_db_env(tmp_path), patched_fs() as recorder:

        ftp = new_ftp_facade()
        ftp.writebytes(Remote_Path, File_Content)

        # The file went where it was told to go ..
        assert recorder.written == [(Remote_Path, File_Content)]

        # .. and the operation left exactly one trail entry.
        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['object_name'] == Connection_Name
        assert event['endpoint'] == Remote_Path
        assert event['size'] == len(File_Content)
        assert event['outcome'] == AuditOutcome.OK

        # Each FTP operation runs under a correlation id of its own
        assert event['cid']

        summary = loads(event['data'])

        assert summary['operation'] == Operation_Store
        assert summary['remote_path'] == Remote_Path
        assert summary['size'] == len(File_Content)

# ################################################################################################################################

def test_a_raising_store_writes_the_error_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A server that went away leaves an error entry before the caller learns about it.
    """
    with audit_db_env(tmp_path), patched_fs(should_raise=True):

        ftp = new_ftp_facade()

        try:
            ftp.writebytes(Remote_Path, File_Content)
        except Exception:
            pass
        else:
            raise Exception('A failed write was expected to propagate')

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['outcome'] == AuditOutcome.Error
        assert Raised_Error in event['data']

# ################################################################################################################################

def test_no_bytes_are_ever_stored(tmp_path:'os.PathLike') -> 'None':
    """ The trail says what moved but never carries the file itself.
    """
    with audit_db_env(tmp_path), patched_fs():

        ftp = new_ftp_facade()
        ftp.writebytes(Remote_Path, File_Content)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        assert list_attachments(engine, event_id) == []

# ################################################################################################################################

def test_a_delete_writes_one_event_too(tmp_path:'os.PathLike') -> 'None':
    """ Taking a file off a server is as much of an operation as putting it there.
    """
    with audit_db_env(tmp_path), patched_fs() as recorder:

        ftp = new_ftp_facade()
        ftp.remove(Remote_Path)

        assert recorder.removed == [Remote_Path]

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['endpoint'] == Remote_Path
        assert event['outcome'] == AuditOutcome.OK

        summary = loads(event['data'])
        assert summary['operation'] == Operation_Delete

# ################################################################################################################################
# ################################################################################################################################
