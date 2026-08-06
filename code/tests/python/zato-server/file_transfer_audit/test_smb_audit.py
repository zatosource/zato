# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A file handed to an SMB share leaves one request-sent event saying which connection
# moved which path, how big the file was and how it ended - a failed operation too.
# The bytes themselves are kept only behind the connection's flag, and an oversized
# file keeps its metadata while losing its bytes.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments, Env_Max_Attachment_Size
from zato.common.audit_log.file_transfer import Operation_Delete, Operation_Store

# Test support
from audit_env import audit_db_env
from smb_stub import new_smb_connection, ClientRecorder, Connection_Name, File_Content, RaisingClient, Raised_Error, \
    Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import any_, anylist

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
    """ Writing a file to a share is one event with everything an auditor asks about.
    """
    with audit_db_env(tmp_path):

        smb_client = ClientRecorder()
        conn = new_smb_connection(smb_client)

        conn.write(File_Content, Remote_Path)

        # The file went where it was told to go ..
        assert smb_client.written == [(Remote_Path, File_Content)]

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

        summary = loads(event['data'])

        assert summary['operation'] == Operation_Store
        assert summary['remote_path'] == Remote_Path
        assert summary['size'] == len(File_Content)

# ################################################################################################################################

def test_a_raising_store_writes_the_error_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A share that went away leaves an error entry before the caller learns about it.
    """
    with audit_db_env(tmp_path):

        conn = new_smb_connection(RaisingClient())

        try:
            conn.write(File_Content, Remote_Path)
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

def test_the_flag_turned_on_stores_the_bytes(tmp_path:'os.PathLike') -> 'None':
    """ A connection that asked for its files to be kept can have them reread.
    """
    with audit_db_env(tmp_path):

        conn = new_smb_connection(ClientRecorder(), should_store_content=True)
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1
        assert items[0]['filename'] == 'results.csv'
        assert items[0]['is_content_kept'] is True

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == File_Content

# ################################################################################################################################

def test_the_flag_turned_off_stores_no_bytes(tmp_path:'os.PathLike') -> 'None':
    """ By default the trail says what moved but never carries the file itself.
    """
    with audit_db_env(tmp_path):

        conn = new_smb_connection(ClientRecorder())
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        assert list_attachments(engine, event_id) == []

# ################################################################################################################################

def test_an_oversized_file_keeps_its_metadata_only(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ A file bigger than the cap is still on record - its name and size stay,
    its bytes do not.
    """
    with audit_db_env(tmp_path):

        # A cap smaller than the file about to be moved
        monkeypatch.setenv(Env_Max_Attachment_Size, '10')

        conn = new_smb_connection(ClientRecorder(), should_store_content=True)
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1
        assert items[0]['filename'] == 'results.csv'
        assert items[0]['size'] == len(File_Content)
        assert items[0]['is_content_kept'] is False

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == b''

# ################################################################################################################################

def test_a_delete_writes_one_event_too(tmp_path:'os.PathLike') -> 'None':
    """ Taking a file off a share is as much of an operation as putting it there.
    """
    with audit_db_env(tmp_path):

        smb_client = ClientRecorder()
        conn = new_smb_connection(smb_client)

        conn.delete_file(Remote_Path)

        assert smb_client.removed == [Remote_Path]

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
