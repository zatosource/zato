# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a file published to an outgoing SFTP, SMB or FTP connection reaches it - the bytes come
# from the local spool file the publication left behind, the write overwrites so a retry
# after a partial upload starts clean, the spool outlives every failed attempt and goes
# away only once the file was actually written out, and each attempt leaves the write's
# own file-outgoing audit event.

# stdlib
import os
from contextlib import contextmanager
from json import dumps, loads
from unittest.mock import MagicMock

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import GENERIC
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.common.ext.bunch import Bunch
from zato.common.pubsub.outgoing import audit_disabled_conn_types, deliver_envelope, OutgoingType
from zato.common.sftp import SFTPOutput
from zato.server.connection.file_transfer_base import spool_file_payload, Key_Remote_Path, Key_Spool_Path
from zato.server.connection.outgoing_delivery import publishable_generic_types, register_delivery_handlers

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist, stranydict

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
_server_name = 'test-file-delivery-server'

# The connection every test here delivers to
_conn_id = 23
_conn_name = 'Nightly Exports'

# The file the checks move
_remote_path = '/outgoing/report.csv'
_payload = b'code,label\nA1,First\nA2,Second\n'

# What the failing clients say
_raised_error = 'The server went away'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# The line an SFTP listing answers with when the remote file is already there -
# what makes the overwriting write delete it first.
_existing_file_ls_line = '-rw-------    1 user1    group1         336 Mar  3 11:50 report.csv'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _audit_db_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

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
# ################################################################################################################################

class _SFTPClientRecorder:
    """ Stands in for the SFTP client - it remembers the batch commands it was told to run.
    """

    def __init__(self) -> 'None':
        self.commands:'anylist' = []

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        self.commands.append(data)
        out = SFTPOutput(cid, 1, command=data, is_ok=True, stdout='')
        return out

# ################################################################################################################################

class _SFTPExistingFileClient(_SFTPClientRecorder):
    """ An SFTP server whose remote path already holds a file - e.g. what a partial upload
    of an earlier attempt left behind.
    """

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        self.commands.append(data)

        # The listing the overwrite check runs answers with the leftover file
        if data.startswith('ls'):
            out = SFTPOutput(cid, 1, command=data, is_ok=True, stdout=_existing_file_ls_line)
        else:
            out = SFTPOutput(cid, 1, command=data, is_ok=True, stdout='')

        return out

# ################################################################################################################################

class _SFTPRaisingClient(_SFTPClientRecorder):
    """ An SFTP client whose server went away - every command fails.
    """

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        raise Exception(_raised_error)

# ################################################################################################################################

class _SFTPWrapper:
    """ Stands in for an outgoing SFTP connection's wrapper.
    """

    def __init__(self, sftp_client:'_SFTPClientRecorder') -> 'None':
        self.sftp_client = sftp_client
        self.should_store_content = False
        self.audit_log = AuditLog(_server_name)

        self.config = Bunch()
        self.config.name = _conn_name

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.sftp_client

# ################################################################################################################################
# ################################################################################################################################

class _SMBClientRecorder:
    """ Stands in for the SMB client - it remembers what it was told to write.
    """

    def __init__(self) -> 'None':
        self.written:'anylist' = []

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        self.written.append((remote_path, data))

# ################################################################################################################################

class _SMBRaisingClient(_SMBClientRecorder):
    """ An SMB client whose share went away - every write fails.
    """

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        raise Exception(_raised_error)

# ################################################################################################################################

class _SMBWrapper:
    """ Stands in for an outgoing SMB connection's wrapper.
    """

    def __init__(self, smb_client:'_SMBClientRecorder') -> 'None':
        self.smb_client = smb_client
        self.should_store_content = False
        self.audit_log = AuditLog(_server_name)

        self.config = Bunch()
        self.config.name = _conn_name

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.smb_client

# ################################################################################################################################
# ################################################################################################################################

class _FTPClientRecorder:
    """ Stands in for the FTP client - it remembers what it was told to write.
    """

    def __init__(self) -> 'None':
        self.written:'anylist' = []

# ################################################################################################################################

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        self.written.append((remote_path, data))

# ################################################################################################################################

class _FTPRaisingClient(_FTPClientRecorder):
    """ An FTP client whose server went away - every write fails.
    """

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        raise Exception(_raised_error)

# ################################################################################################################################

class _FTPWrapper:
    """ Stands in for an outgoing FTP connection's wrapper.
    """

    def __init__(self, ftp_client:'_FTPClientRecorder') -> 'None':
        self.ftp_client = ftp_client
        self.should_store_content = False
        self.audit_log = AuditLog(_server_name)

        self.config = Bunch()
        self.config.name = _conn_name

# ################################################################################################################################

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.ftp_client

# ################################################################################################################################
# ################################################################################################################################

def _new_server(conn_type_attr:'str', wrapper:'any_') -> 'MagicMock':
    """ A server whose configuration holds one file transfer connection of the given kind.
    """
    item = Bunch()
    item.id = _conn_id
    item.name = _conn_name
    item.conn = wrapper

    out = MagicMock()
    setattr(out.config_manager, conn_type_attr, {_conn_name: item})

    return out

# ################################################################################################################################

def _get_put_commands(sftp_client:'_SFTPClientRecorder') -> 'anylist':
    """ The put commands the client was told to run.
    """
    out:'anylist' = []

    for item in sftp_client.commands:
        if item.startswith('put'):
            out.append(item)

    return out

# ################################################################################################################################

def _new_envelope(conn_type:'str', spool_path:'str') -> 'stranydict':
    """ The envelope a queued file transfer turns into - the bytes stay in the spool file
    and only its path and the remote destination travel through the queue.
    """
    out = {
        'conn_type': conn_type,
        'conn_id': _conn_id,
        'conn_name': _conn_name,
        'data': dumps({
            Key_Spool_Path: spool_path,
            Key_Remote_Path: _remote_path,
        }),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_file_types_are_registered_without_pubsub_audit() -> 'None':
    """ The file types deliver through the shared queue but their deliveries are recorded
    as file-outgoing events by the connections themselves, so their topics stay out
    of the pub/sub audit log.
    """
    register_delivery_handlers()

    assert OutgoingType.SFTP in audit_disabled_conn_types
    assert OutgoingType.SMB in audit_disabled_conn_types
    assert OutgoingType.FTP in audit_disabled_conn_types

# ################################################################################################################################

def test_the_file_types_use_the_generic_rename_and_delete_machinery() -> 'None':
    """ A rename moves a connection's queue and a delete drops it through the same map
    the FHIR connections already use, so the file types only need to be in it.
    """
    assert publishable_generic_types[GENERIC.CONNECTION.TYPE.OUTCONN_SFTP] == OutgoingType.SFTP
    assert publishable_generic_types[GENERIC.CONNECTION.TYPE.OUTCONN_SMB] == OutgoingType.SMB
    assert publishable_generic_types[GENERIC.CONNECTION.TYPE.OUTCONN_FTP] == OutgoingType.FTP

# ################################################################################################################################

def test_a_queued_file_reaches_the_sftp_connection_and_the_spool_goes_away(tmp_path:'any_') -> 'None':
    """ A delivered file was written to the remote path, its spool file is gone
    and the write left its own audit event.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        sftp_client = _SFTPClientRecorder()
        server = _new_server('outconn_sftp', _SFTPWrapper(sftp_client))

        spool_path = spool_file_payload(_payload)

        deliver_envelope(server, 'test-cid', _new_envelope(OutgoingType.SFTP, spool_path))

        # The file went out to the remote path ..
        put_commands = _get_put_commands(sftp_client)
        assert len(put_commands) == 1
        assert _remote_path in put_commands[0]

        # .. the spool file is gone now that the file was written out ..
        assert not os.path.exists(spool_path)

        # .. and the write recorded the attempt as its own file-outgoing event.
        events = _get_events()

        store_events:'anylist' = []

        for item in events:
            if loads(item['data'])['operation'] == 'store':
                store_events.append(item)

        assert len(store_events) == 1

        event = store_events[0]
        assert event['source'] == AuditSource.File_Outgoing
        assert event['object_name'] == _conn_name
        assert event['endpoint'] == _remote_path
        assert event['outcome'] == AuditOutcome.OK
        assert event['size'] == len(_payload)

# ################################################################################################################################

def test_a_failed_sftp_delivery_keeps_the_spool_for_the_retry(tmp_path:'any_') -> 'None':
    """ A delivery the server refused raises, which keeps the message queued, and the spool
    file stays in place so the retry has the same bytes to send.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        server = _new_server('outconn_sftp', _SFTPWrapper(_SFTPRaisingClient()))

        spool_path = spool_file_payload(_payload)
        envelope = _new_envelope(OutgoingType.SFTP, spool_path)

        try:
            deliver_envelope(server, 'test-cid', envelope)
        except Exception:
            pass
        else:
            raise Exception('A failed delivery was expected to propagate')

        # The bytes wait for the retry ..
        assert os.path.exists(spool_path)

        # .. and once the server is back, the same envelope goes through and the spool goes away.
        sftp_client = _SFTPClientRecorder()
        server = _new_server('outconn_sftp', _SFTPWrapper(sftp_client))

        deliver_envelope(server, 'test-cid', envelope)

        assert not os.path.exists(spool_path)

        put_commands = _get_put_commands(sftp_client)
        assert len(put_commands) == 1

# ################################################################################################################################

def test_an_sftp_retry_overwrites_what_a_partial_upload_left(tmp_path:'any_') -> 'None':
    """ A remote path already holding a file - e.g. half of an earlier attempt - is deleted
    before the write, so a retry starts clean.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        sftp_client = _SFTPExistingFileClient()
        server = _new_server('outconn_sftp', _SFTPWrapper(sftp_client))

        spool_path = spool_file_payload(_payload)

        deliver_envelope(server, 'test-cid', _new_envelope(OutgoingType.SFTP, spool_path))

        # The leftover was removed before the file went out
        rm_index = None
        put_index = None

        for index, command in enumerate(sftp_client.commands):
            if command.startswith('rm') and rm_index is None:
                rm_index = index
            if command.startswith('put') and put_index is None:
                put_index = index

        assert rm_index is not None
        assert put_index is not None
        assert rm_index < put_index

# ################################################################################################################################

def test_a_queued_file_reaches_the_smb_connection_and_the_spool_goes_away(tmp_path:'any_') -> 'None':
    """ A delivered file was written to the share, its spool file is gone
    and the write left its own audit event.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        smb_client = _SMBClientRecorder()
        server = _new_server('outconn_smb', _SMBWrapper(smb_client))

        spool_path = spool_file_payload(_payload)

        deliver_envelope(server, 'test-cid', _new_envelope(OutgoingType.SMB, spool_path))

        # The bytes reached the share whole ..
        assert smb_client.written == [(_remote_path, _payload)]

        # .. the spool file is gone now that the file was written out ..
        assert not os.path.exists(spool_path)

        # .. and the write recorded the attempt as its own file-outgoing event.
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['source'] == AuditSource.File_Outgoing
        assert event['object_name'] == _conn_name
        assert event['endpoint'] == _remote_path
        assert event['outcome'] == AuditOutcome.OK

# ################################################################################################################################

def test_a_failed_smb_delivery_keeps_the_spool_for_the_retry(tmp_path:'any_') -> 'None':
    """ A delivery the share refused raises, which keeps the message queued, and the spool
    file stays in place so the retry has the same bytes to send.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        server = _new_server('outconn_smb', _SMBWrapper(_SMBRaisingClient()))

        spool_path = spool_file_payload(_payload)
        envelope = _new_envelope(OutgoingType.SMB, spool_path)

        try:
            deliver_envelope(server, 'test-cid', envelope)
        except Exception:
            pass
        else:
            raise Exception('A failed delivery was expected to propagate')

        # The bytes wait for the retry ..
        assert os.path.exists(spool_path)

        # .. and once the share is back, the same envelope goes through and the spool goes away.
        smb_client = _SMBClientRecorder()
        server = _new_server('outconn_smb', _SMBWrapper(smb_client))

        deliver_envelope(server, 'test-cid', envelope)

        assert not os.path.exists(spool_path)
        assert smb_client.written == [(_remote_path, _payload)]

# ################################################################################################################################

def test_a_queued_file_reaches_the_ftp_connection_and_the_spool_goes_away(tmp_path:'any_') -> 'None':
    """ A delivered file was written to the server, its spool file is gone
    and the write left its own audit event.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        ftp_client = _FTPClientRecorder()
        wrapper = _FTPWrapper(ftp_client)
        server = _new_server('outconn_ftp', wrapper)

        spool_path = spool_file_payload(_payload)
        envelope = _new_envelope(OutgoingType.FTP, spool_path)

        deliver_envelope(server, 'test-cid', envelope)

        # The bytes reached the server whole ..
        assert ftp_client.written == [(_remote_path, _payload)]

        # .. the spool file is gone now that the file was written out ..
        assert not os.path.exists(spool_path)

        # .. and the write recorded the attempt as its own file-outgoing event.
        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['source'] == AuditSource.File_Outgoing
        assert event['object_name'] == _conn_name
        assert event['endpoint'] == _remote_path
        assert event['outcome'] == AuditOutcome.OK

# ################################################################################################################################

def test_a_failed_ftp_delivery_keeps_the_spool_for_the_retry(tmp_path:'any_') -> 'None':
    """ A delivery the server refused raises, which keeps the message queued, and the spool
    file stays in place so the retry has the same bytes to send.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        raising_client = _FTPRaisingClient()
        wrapper = _FTPWrapper(raising_client)
        server = _new_server('outconn_ftp', wrapper)

        spool_path = spool_file_payload(_payload)
        envelope = _new_envelope(OutgoingType.FTP, spool_path)

        try:
            deliver_envelope(server, 'test-cid', envelope)
        except Exception:
            pass
        else:
            raise Exception('A failed delivery was expected to propagate')

        # The bytes wait for the retry ..
        assert os.path.exists(spool_path)

        # .. and once the server is back, the same envelope goes through and the spool goes away.
        ftp_client = _FTPClientRecorder()
        wrapper = _FTPWrapper(ftp_client)
        server = _new_server('outconn_ftp', wrapper)

        deliver_envelope(server, 'test-cid', envelope)

        assert not os.path.exists(spool_path)
        assert ftp_client.written == [(_remote_path, _payload)]

# ################################################################################################################################

def test_a_connection_that_is_gone_raises(tmp_path:'any_') -> 'None':
    """ A connection that was deleted is no longer anywhere to be found, so a message
    naming it is an error rather than something quietly dropped.
    """
    with _audit_db_env(tmp_path):

        register_delivery_handlers()

        server = MagicMock()
        server.config_manager.outconn_sftp = {}

        spool_path = spool_file_payload(_payload)
        envelope = _new_envelope(OutgoingType.SFTP, spool_path)

        try:
            deliver_envelope(server, 'test-cid', envelope)
        except Exception as e:
            assert str(_conn_id) in str(e)
        else:
            raise Exception('A delivery to a deleted connection was expected to propagate')

        # The bytes are still there for when the message is given up on or the connection returns
        assert os.path.exists(spool_path)

# ################################################################################################################################
# ################################################################################################################################
