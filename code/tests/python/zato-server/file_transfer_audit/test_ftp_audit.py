# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A file handed to an FTP server leaves one request-sent event saying which connection
# moved which path, how big the file was and how it ended - a failed operation too.
# The bytes themselves are kept only behind the connection's flag, and an oversized
# file keeps its metadata while losing its bytes.

# stdlib
from hashlib import sha256
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments, Env_Max_Attachment_Size
from zato.common.audit_log.file_transfer import Operation_Delete, Operation_Move, Operation_Store

# Test support
from audit_env import audit_db_env
from ftp_stub import new_ftp_connection, ClientRecorder, Connection_Name, File_Content, RaisingClient, Raised_Error, \
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

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            event = dict(row._mapping)
            out.append(event)

    return out

# ################################################################################################################################

def _get_attributes(event_id:'int') -> 'any_':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'any_' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            name = row[0]
            out[name] = row[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_store_writes_one_event_with_the_path_and_size(tmp_path:'os.PathLike') -> 'None':
    """ Writing a file to a server is one event with everything an auditor asks about.
    """
    with audit_db_env(tmp_path):

        ftp_client = ClientRecorder()
        conn = new_ftp_connection(ftp_client)

        conn.write(File_Content, Remote_Path)

        # The file went where it was told to go ..
        assert ftp_client.written == [(Remote_Path, File_Content)]

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

        # The event carries a SHA-256 digest of the bytes as a searchable attribute.
        event_id = event['id']
        attributes = _get_attributes(event_id)

        expected_checksum = sha256(File_Content).hexdigest()
        assert attributes['checksum'] == expected_checksum

# ################################################################################################################################

def test_a_raising_store_writes_the_error_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A server that went away leaves an error entry before the caller learns about it.
    """
    with audit_db_env(tmp_path):

        conn = new_ftp_connection(RaisingClient())

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

        conn = new_ftp_connection(ClientRecorder(), should_store_content=True)
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event = events[0]
        event_id = event['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1

        item = items[0]

        assert item['filename'] == 'results.csv'
        assert item['is_content_kept'] is True

        attachment_id = item['id']
        stored = get_attachment(engine, attachment_id)

        assert stored['content'] == File_Content

# ################################################################################################################################

def test_the_flag_turned_off_stores_no_bytes(tmp_path:'os.PathLike') -> 'None':
    """ By default the trail says what moved but never carries the file itself.
    """
    with audit_db_env(tmp_path):

        conn = new_ftp_connection(ClientRecorder())
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event = events[0]
        event_id = event['id']

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

        conn = new_ftp_connection(ClientRecorder(), should_store_content=True)
        conn.write(File_Content, Remote_Path)

        events = _get_events()
        event = events[0]
        event_id = event['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1

        item = items[0]

        assert item['filename'] == 'results.csv'
        assert item['size'] == len(File_Content)
        assert item['is_content_kept'] is False

        attachment_id = item['id']
        stored = get_attachment(engine, attachment_id)

        assert stored['content'] == b''

# ################################################################################################################################

def test_a_delete_writes_one_event_too(tmp_path:'os.PathLike') -> 'None':
    """ Taking a file off a server is as much of an operation as putting it there.
    """
    with audit_db_env(tmp_path):

        ftp_client = ClientRecorder()
        conn = new_ftp_connection(ftp_client)

        conn.delete_file(Remote_Path)

        assert ftp_client.removed == [Remote_Path]

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['endpoint'] == Remote_Path
        assert event['outcome'] == AuditOutcome.OK

        summary = loads(event['data'])
        assert summary['operation'] == Operation_Delete

# ################################################################################################################################

def test_a_move_writes_one_event_with_both_paths(tmp_path:'os.PathLike') -> 'None':
    """ Renaming a file on a server is one event saying where the file went.
    """
    with audit_db_env(tmp_path):

        to_path = 'documents/archive/results.csv'

        ftp_client = ClientRecorder()
        conn = new_ftp_connection(ftp_client)

        conn.move(Remote_Path, to_path)

        assert ftp_client.renamed == [(Remote_Path, to_path)]

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['endpoint'] == Remote_Path
        assert event['outcome'] == AuditOutcome.OK

        summary = loads(event['data'])

        assert summary['operation'] == Operation_Move
        assert summary['to_path'] == to_path

# ################################################################################################################################

def test_a_raising_move_writes_the_error_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A rename the server refused leaves an error entry before the caller learns about it.
    """
    with audit_db_env(tmp_path):

        to_path = 'documents/archive/results.csv'

        conn = new_ftp_connection(RaisingClient())

        try:
            conn.move(Remote_Path, to_path)
        except Exception:
            pass
        else:
            raise Exception('A failed move was expected to propagate')

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['outcome'] == AuditOutcome.Error
        assert Raised_Error in event['data']

        summary = loads(event['data'])

        assert summary['operation'] == Operation_Move
        assert summary['to_path'] == to_path

# ################################################################################################################################
# ################################################################################################################################
