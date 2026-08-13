# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A file handed to an SFTP server leaves one request-sent event saying which connection
# moved which path, how big the file was and how it ended - a failed operation too.
# The file's bytes are never stored, only what moved and how.

# stdlib
import os
from hashlib import sha256
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.audit_log.file_transfer import Operation_Delete, Operation_Move, Operation_Store

# Test support
from audit_env import audit_db_env
from sftp_stub import new_sftp_connection, Cid, ClientRecorder, Connection_Name, RaisingClient, Raised_Error, Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# What the upload checks move
_local_content = b'code,label\nA1,First\nA2,Second\n'

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

def _get_attrs(event_id:'int') -> 'any_':
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

def _new_local_file(tmp_path:'os.PathLike') -> 'str':
    """ A local file for the uploads to move, of a known size.
    """
    out = os.path.join(str(tmp_path), 'results.csv')

    with open(out, 'wb') as file:
        _ = file.write(_local_content)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_an_upload_writes_one_event_with_the_path_and_size(tmp_path:'os.PathLike') -> 'None':
    """ Uploading a file to a server is one event with everything an auditor asks about.
    """
    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        # The client was told to move the file ..
        assert len(sftp_client.commands) == 1
        assert sftp_client.commands[0].startswith('put')
        assert Remote_Path in sftp_client.commands[0]

        # .. and the operation left exactly one trail entry.
        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.File_Outgoing
        assert event['event_type'] == AuditEvent.Request_Sent
        assert event['object_name'] == Connection_Name
        assert event['endpoint'] == Remote_Path
        assert event['size'] == len(_local_content)
        assert event['outcome'] == AuditOutcome.OK
        assert event['cid'] == Cid

        summary = loads(event['data'])

        assert summary['operation'] == Operation_Store
        assert summary['remote_path'] == Remote_Path
        assert summary['size'] == len(_local_content)

        # The event carries a SHA-256 digest of the bytes as a searchable attribute
        attrs = _get_attrs(event['id'])
        assert attrs['checksum'] == sha256(_local_content).hexdigest()

# ################################################################################################################################

def test_a_raising_upload_writes_the_error_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A server that went away leaves an error entry before the caller learns about it.
    """
    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        conn = new_sftp_connection(RaisingClient())

        try:
            _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)
        except Exception:
            pass
        else:
            raise Exception('A failed upload was expected to propagate')

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['outcome'] == AuditOutcome.Error
        assert Raised_Error in event['data']

# ################################################################################################################################

def test_no_bytes_are_ever_stored(tmp_path:'os.PathLike') -> 'None':
    """ The trail says what moved but never carries the file itself.
    """
    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        conn = new_sftp_connection(ClientRecorder())
        _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        assert list_attachments(engine, event_id) == []

# ################################################################################################################################

def test_a_delete_writes_one_event_too(tmp_path:'os.PathLike') -> 'None':
    """ Taking a file off a server is as much of an operation as putting it there.
    """
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        _ = conn.delete_file(Remote_Path, needs_check=False)

        assert len(sftp_client.commands) == 1
        assert sftp_client.commands[0].startswith('rm')
        assert Remote_Path in sftp_client.commands[0]

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

        to_path = '/documents/archive/results.csv'

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        _ = conn.move(Remote_Path, to_path)

        assert len(sftp_client.commands) == 1
        assert sftp_client.commands[0].startswith('rename')
        assert Remote_Path in sftp_client.commands[0]
        assert to_path in sftp_client.commands[0]

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

        to_path = '/documents/archive/results.csv'

        conn = new_sftp_connection(RaisingClient())

        try:
            _ = conn.move(Remote_Path, to_path)
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

def test_the_flag_turned_on_stores_the_bytes(tmp_path:'os.PathLike') -> 'None':
    """ A connection that asked for its files to be kept can have them reread.
    """
    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        conn = new_sftp_connection(ClientRecorder(), should_store_content=True)
        _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1
        assert items[0]['filename'] == 'results.csv'
        assert items[0]['is_content_kept'] is True

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == _local_content

# ################################################################################################################################
# ################################################################################################################################
