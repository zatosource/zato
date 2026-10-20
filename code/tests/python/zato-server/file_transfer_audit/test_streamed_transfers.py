# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An FTP or SMB upload sends a local file one chunk at a time, a download writes a remote file
# to a local path one chunk at a time, and a read-back verification computes the checksum
# of the stored file one chunk at a time. Each of them leaves the same audit trail
# as a write or a read of bytes held in memory.

# stdlib
import os
from hashlib import sha256
from json import loads

# pytest
from pytest import fixture, mark, raises

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome
from zato.common.audit_log.attachment import get_attachment, list_attachments, Env_Max_Attachment_Size
from zato.common.audit_log.file_transfer import Operation_Read, Operation_Store, Status_Verified, Status_Verify_Failed
from zato.common.file_transfer.api import VerifyHow
from zato.server.connection.file_transfer_verify import FileTransferVerifyError

# Test support
from audit_env import audit_db_env
from ftp_stub import new_ftp_connection, ClientRecorder as FTPClientRecorder, RaisingClient as FTPRaisingClient, \
    Remote_Path as FTP_Remote_Path
from smb_stub import new_smb_connection, ClientRecorder as SMBClientRecorder, RaisingClient as SMBRaisingClient, \
    Remote_Path as SMB_Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

# What the transfers move - many times the stubs' chunk size, with letters whose case a corrupted copy flips
_file_content = b'code,label\nA1,First\nA2,Second\n' * 20

# The name of the local file uploaded and of the one downloaded to
_upload_name   = 'results.csv'
_download_name = 'downloaded.csv'

# A cap on stored content smaller than the file
_small_cap = '10'

# ################################################################################################################################
# ################################################################################################################################

class _CorruptingFTPClient(FTPClientRecorder):
    """ An FTP server whose stored copy differs from what was sent while keeping its size.
    """

    def read_chunks(self, remote_path:'any_', callback:'any_') -> 'None':
        data = self.data_by_path[remote_path]
        callback(data.swapcase())

# ################################################################################################################################

class _CorruptingSMBClient(SMBClientRecorder):
    """ An SMB share whose stored copy differs from what was sent while keeping its size.
    """

    def read_chunks(self, remote_path:'any_', callback:'any_') -> 'None':
        data = self.data_by_path[remote_path]
        callback(data.swapcase())

# ################################################################################################################################
# ################################################################################################################################

class _Protocol:
    """ What a check needs of one protocol - how to build a connection, its stubbed clients and its remote path.
    """

    def __init__(
        self,
        name:'str',
        new_connection:'callable_',
        client_class:'any_',
        raising_class:'any_',
        corrupting_class:'any_',
        remote_path:'str',
        ) -> 'None':
        self.name = name
        self.new_connection = new_connection
        self.client_class = client_class
        self.raising_class = raising_class
        self.corrupting_class = corrupting_class
        self.remote_path = remote_path

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return self.name

# ################################################################################################################################
# ################################################################################################################################

_protocols = [
    _Protocol('ftp', new_ftp_connection, FTPClientRecorder, FTPRaisingClient, _CorruptingFTPClient, FTP_Remote_Path),
    _Protocol('smb', new_smb_connection, SMBClientRecorder, SMBRaisingClient, _CorruptingSMBClient, SMB_Remote_Path),
]

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

def _get_attributes(event_id:'int') -> 'anydict':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            name = row[0]
            out[name] = row[1]

    return out

# ################################################################################################################################

def _get_stored_content(event_id:'int') -> 'anydict':
    """ The one attachment of an event, with its bytes.
    """
    engine = get_audit_engine()

    items = list_attachments(engine, event_id)
    assert len(items) == 1

    attachment_id = items[0]['id']
    out = get_attachment(engine, attachment_id)

    return out

# ################################################################################################################################

def _checksum(data:'bytes') -> 'str':
    hasher = sha256(data)
    out = hasher.hexdigest()
    return out

# ################################################################################################################################
# ################################################################################################################################

@fixture
def local_path(tmp_path:'any_') -> 'str':
    """ A local file for the uploads to send.
    """
    out = os.path.join(str(tmp_path), _upload_name)

    with open(out, 'wb') as local_file:
        _ = local_file.write(_file_content)

    return out

# ################################################################################################################################

@fixture
def download_path(tmp_path:'any_') -> 'str':
    """ Where the downloads write to - nothing is there before a download.
    """
    out = os.path.join(str(tmp_path), _download_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_an_upload_sends_the_file_from_a_file_object(tmp_path:'any_', local_path:'str', protocol:'_Protocol') -> 'None':
    """ An upload hands the client the local file to read, never its bytes, and records one verified store.
    """
    with audit_db_env(tmp_path):

        client = protocol.client_class()
        conn = protocol.new_connection(client)

        conn.upload(local_path, protocol.remote_path)

        # The file was sent from a file object and nothing was written from bytes in memory ..
        assert client.streamed == [protocol.remote_path]
        assert client.written == []
        assert client.data_by_path[protocol.remote_path] == _file_content

        # .. and the store is one event with the size, the checksum and the verified status.
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['outcome'] == AuditOutcome.OK
        assert event['size'] == len(_file_content)
        assert event['status'] == Status_Verified
        assert loads(event['data'])['operation'] == Operation_Store
        assert _get_attributes(event['id'])['checksum'] == _checksum(_file_content)

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_an_upload_keeps_the_bytes_when_asked(tmp_path:'any_', local_path:'str', protocol:'_Protocol') -> 'None':
    """ A connection that keeps its files has the uploaded bytes read from the local file into the audit log.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.client_class(), should_store_content=True)
        conn.upload(local_path, protocol.remote_path)

        event = _get_events()[0]
        stored = _get_stored_content(event['id'])

        assert stored['content'] == _file_content

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_an_oversized_upload_keeps_its_metadata_only(
    tmp_path:'any_',
    local_path:'str',
    protocol:'_Protocol',
    monkeypatch:'any_',
    ) -> 'None':
    """ An uploaded file over the cap is on record by its name and size, without its bytes.
    """
    with audit_db_env(tmp_path):

        monkeypatch.setenv(Env_Max_Attachment_Size, _small_cap)

        conn = protocol.new_connection(protocol.client_class(), should_store_content=True)
        conn.upload(local_path, protocol.remote_path)

        event = _get_events()[0]
        stored = _get_stored_content(event['id'])

        assert stored['content'] == b''
        assert stored['size'] == len(_file_content)

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_raising_upload_records_the_error(tmp_path:'any_', local_path:'str', protocol:'_Protocol') -> 'None':
    """ An upload the server refused leaves an error event with the size of the local file.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.raising_class())

        with raises(Exception):
            conn.upload(local_path, protocol.remote_path)

        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['outcome'] == AuditOutcome.Error
        assert event['size'] == len(_file_content)

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_read_back_compares_the_checksum_of_the_stored_upload(
    tmp_path:'any_',
    local_path:'str',
    protocol:'_Protocol',
    ) -> 'None':
    """ A read-back verification computes the checksum of the stored file and records it next to the one sent.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.client_class())
        conn.wrapper.verify_how = VerifyHow.Read_Back

        conn.upload(local_path, protocol.remote_path)

        # The read-back is part of the store and leaves no read event of its own
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        summary = loads(event['data'])

        assert event['status'] == Status_Verified
        assert summary['verify_how'] == VerifyHow.Read_Back
        assert summary['remote_checksum'] == _checksum(_file_content)

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_read_back_compares_the_checksum_of_a_written_file(tmp_path:'any_', protocol:'_Protocol') -> 'None':
    """ Bytes written from memory are verified by the same checksum read back one chunk at a time.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.client_class())
        conn.wrapper.verify_how = VerifyHow.Read_Back

        conn.write(_file_content, protocol.remote_path)

        event = _get_events()[0]
        summary = loads(event['data'])

        assert event['status'] == Status_Verified
        assert summary['remote_checksum'] == _checksum(_file_content)

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_read_back_mismatch_raises_and_is_recorded(tmp_path:'any_', local_path:'str', protocol:'_Protocol') -> 'None':
    """ A stored copy of the same size but different bytes fails the verification.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.corrupting_class())
        conn.wrapper.verify_how = VerifyHow.Read_Back

        with raises(FileTransferVerifyError):
            conn.upload(local_path, protocol.remote_path)

        # The store's row says the verification failed and a Verify_Failed event follows it
        events = _get_events()
        assert len(events) == 2

        store_event, verify_event = events

        assert store_event['status'] == Status_Verify_Failed
        assert store_event['outcome'] == AuditOutcome.Error
        assert verify_event['event_type'] == AuditEvent.Verify_Failed

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_download_writes_the_local_file_and_one_event(tmp_path:'any_', download_path:'str', protocol:'_Protocol') -> 'None':
    """ A download writes the remote bytes to the local path and records one read with their checksum,
    the bytes kept when the connection asks for that.
    """
    with audit_db_env(tmp_path):

        client = protocol.client_class()
        client.data_by_path[protocol.remote_path] = _file_content

        conn = protocol.new_connection(client, should_store_content=True)
        conn.download_file(protocol.remote_path, download_path)

        # The local file holds the bytes as they were on the server ..
        with open(download_path, 'rb') as downloaded:
            assert downloaded.read() == _file_content

        # .. the download is one read event with their checksum ..
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['outcome'] == AuditOutcome.OK
        assert event['size'] == len(_file_content)
        assert loads(event['data'])['operation'] == Operation_Read
        assert _get_attributes(event['id'])['checksum'] == _checksum(_file_content)

        # .. and the bytes are kept as its attachment.
        stored = _get_stored_content(event['id'])
        assert stored['content'] == _file_content

# ################################################################################################################################

@mark.parametrize('protocol', _protocols, ids=repr)
def test_a_failed_download_leaves_no_local_file(tmp_path:'any_', download_path:'str', protocol:'_Protocol') -> 'None':
    """ A download the server refused deletes what it began to write and leaves an error event.
    """
    with audit_db_env(tmp_path):

        conn = protocol.new_connection(protocol.raising_class())

        with raises(Exception):
            conn.download_file(protocol.remote_path, download_path)

        assert not os.path.exists(download_path)

        events = _get_events()
        assert len(events) == 1
        assert events[0]['outcome'] == AuditOutcome.Error

# ################################################################################################################################
# ################################################################################################################################
