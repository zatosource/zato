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
import shlex
from hashlib import sha256
from json import loads

# pytest
from pytest import raises

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments, Env_Max_Attachment_Size
from zato.common.audit_log.file_transfer import Operation_Delete, Operation_Move, Operation_Read, Operation_Store, \
    Status_Verified, Status_Verify_Failed
from zato.common.file_transfer.api import Encoding, VerifyHow
from zato.common.file_transfer.spool import Env_Spool_Directory
from zato.common.test.file_transfer_harness.encoding_samples import sample_bytes
from zato.server.connection.file_transfer_verify import FileTransferVerifyError

# Test support
from audit_env import audit_db_env
from sftp_stub import new_sftp_connection, Cid, ClientRecorder, Connection_Name, RaisingClient, Raised_Error, Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.sftp import SFTPOutput
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# What the upload checks move
_local_content = b'code,label\nA1,First\nA2,Second\n'

# A cap on stored content smaller than the file
_small_cap = '10'

# ################################################################################################################################
# ################################################################################################################################

class _CorruptingClient(ClientRecorder):
    """ An SFTP server whose stored copy differs from what was put while keeping its size.
    """

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':

        out = super().execute(cid, data, log_level)

        if data.startswith('put'):
            remote_path = shlex.split(data)[-1]
            stored = self.content_by_path[remote_path]
            self.content_by_path[remote_path] = stored.swapcase()

        return out

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

        # The client was told to move the file and then to look at what arrived ..
        assert len(sftp_client.commands) == 2
        assert sftp_client.commands[0].startswith('put')
        assert Remote_Path in sftp_client.commands[0]
        assert sftp_client.commands[1].startswith('ls')
        assert Remote_Path in sftp_client.commands[1]

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
        assert sftp_client.commands[0].startswith('rename -l ')
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

def test_a_read_to_spool_writes_the_file_and_one_event(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ A file read into a spool file is described by its size and checksum, and the read
    is one event with the same checksum, the bytes stored when the connection asks for that.
    """
    spool_directory = os.path.join(str(tmp_path), 'spool')
    os.makedirs(spool_directory)
    monkeypatch.setenv(Env_Spool_Directory, spool_directory)

    data = sample_bytes(Encoding.CP1255)

    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        sftp_client.content_by_path[Remote_Path] = data

        conn = new_sftp_connection(sftp_client, should_store_content=True)
        spooled = conn.read_to_spool(Remote_Path)

        # The spool file holds the bytes as they were on the server ..
        with open(spooled.path, 'rb') as spool_file:
            assert spool_file.read() == data

        assert os.path.dirname(spooled.path) == spool_directory
        assert spooled.size == len(data)
        assert spooled.checksum == sha256(data).hexdigest()

        # .. the read is one event with the same checksum ..
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['outcome'] == AuditOutcome.OK
        assert loads(event['data'])['operation'] == Operation_Read
        assert _get_attrs(event['id'])['checksum'] == spooled.checksum

        # .. and the bytes are kept as its attachment.
        engine = get_audit_engine()
        items = list_attachments(engine, event['id'])

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == data

# ################################################################################################################################

def test_a_failed_read_to_spool_leaves_no_spool_file(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ A read the server refused deletes its spool file and leaves an error event.
    """
    spool_directory = os.path.join(str(tmp_path), 'spool')
    os.makedirs(spool_directory)
    monkeypatch.setenv(Env_Spool_Directory, spool_directory)

    with audit_db_env(tmp_path):

        conn = new_sftp_connection(RaisingClient())

        try:
            _ = conn.read_to_spool(Remote_Path)
        except Exception:
            pass
        else:
            raise Exception('A failed read was expected to propagate')

        assert os.listdir(spool_directory) == []

        events = _get_events()
        assert len(events) == 1
        assert events[0]['outcome'] == AuditOutcome.Error
        assert Raised_Error in events[0]['data']

# ################################################################################################################################

def test_a_read_returns_the_bytes_and_leaves_no_spool_file(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ A read hands back the bytes of the file and deletes the spool file it went through.
    """
    spool_directory = os.path.join(str(tmp_path), 'spool')
    os.makedirs(spool_directory)
    monkeypatch.setenv(Env_Spool_Directory, spool_directory)

    data = sample_bytes(Encoding.CP1253)

    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        sftp_client.content_by_path[Remote_Path] = data

        conn = new_sftp_connection(sftp_client)

        assert conn.read(Remote_Path) == data
        assert os.listdir(spool_directory) == []

# ################################################################################################################################

def test_an_oversized_upload_keeps_its_metadata_only(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ An uploaded file over the cap is on record by its name and size, without its bytes.
    """
    with audit_db_env(tmp_path):

        monkeypatch.setenv(Env_Max_Attachment_Size, _small_cap)

        local_path = _new_local_file(tmp_path)

        conn = new_sftp_connection(ClientRecorder(), should_store_content=True)
        _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        events = _get_events()
        event_id = events[0]['id']

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        assert len(items) == 1
        assert items[0]['size'] == len(_local_content)
        assert items[0]['is_content_kept'] is False

# ################################################################################################################################

def test_a_read_back_downloads_the_upload_and_compares_its_checksum(
    tmp_path:'os.PathLike',
    monkeypatch:'any_',
    ) -> 'None':
    """ A read-back verification downloads the stored file into a spool file, compares its checksum
    with the one sent and deletes the spool file, leaving no read event of its own.
    """
    spool_directory = os.path.join(str(tmp_path), 'spool')
    os.makedirs(spool_directory)
    monkeypatch.setenv(Env_Spool_Directory, spool_directory)

    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)
        conn.wrapper.verify_how = VerifyHow.Read_Back

        _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        # The file was put, its size was looked at and it was fetched back ..
        assert sftp_client.commands[0].startswith('put')
        assert sftp_client.commands[1].startswith('ls')
        assert sftp_client.commands[2].startswith('get')

        # .. the spool file it was fetched into is gone ..
        assert os.listdir(spool_directory) == []

        # .. and the store is the one event, with both checksums.
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        summary = loads(event['data'])

        assert event['status'] == Status_Verified
        assert summary['remote_checksum'] == sha256(_local_content).hexdigest()

# ################################################################################################################################

def test_a_read_back_mismatch_raises_and_is_recorded(tmp_path:'os.PathLike', monkeypatch:'any_') -> 'None':
    """ A stored copy of the same size but different bytes fails the verification and leaves no spool file.
    """
    spool_directory = os.path.join(str(tmp_path), 'spool')
    os.makedirs(spool_directory)
    monkeypatch.setenv(Env_Spool_Directory, spool_directory)

    with audit_db_env(tmp_path):

        local_path = _new_local_file(tmp_path)

        conn = new_sftp_connection(_CorruptingClient())
        conn.wrapper.verify_how = VerifyHow.Read_Back

        with raises(FileTransferVerifyError):
            _ = conn.upload(local_path, Remote_Path, _needs_overwrite_check=False)

        assert os.listdir(spool_directory) == []

        # The store's row says the verification failed and a Verify_Failed event follows it
        events = _get_events()
        assert len(events) == 2

        store_event, verify_event = events

        assert store_event['status'] == Status_Verify_Failed
        assert store_event['outcome'] == AuditOutcome.Error
        assert verify_event['event_type'] == AuditEvent.Verify_Failed

# ################################################################################################################################
# ################################################################################################################################
