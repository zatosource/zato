# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A file transfer schedule hands each file to its target service in the encoding the schedule names -
# the service reads the text in full or line by line without decoding anything itself. The file
# is read into a local spool file in chunks and the spool file is deleted once the service returns.
# The schedule engine runs for real against a local directory behind the same client interface
# the SMB wrapper drives, so no remote server is needed.

# stdlib
import os
from hashlib import sha256
from json import loads

# pytest
from pytest import fixture, mark

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditOutcome
from zato.common.audit_log.attachment import Env_Max_Attachment_Size, list_attachments
from zato.common.audit_log.file_transfer import load_transfer_content, Operation_Read
from zato.common.file_transfer.api import Default_Encoding, Encoding, Encoding_List
from zato.common.file_transfer.spool import Env_Spool_Directory
from zato.common.test.file_transfer_harness.encoding_samples import sample_bytes, sample_lines, sample_text
from zato.common.typing_ import cast_
from zato.server.service.internal.outgoing.file_transfer.process import process_files

# Test support
from audit_env import audit_db_env
from schedule_stub import events_of_type, get_attrs, get_events, new_environment, new_schedule, Connection_Name, \
    Directory, File_Name, LocalDirectoryClient, Read_Chunk_Size, TextServiceStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The name of the directory the spool files of a test go to
_spool_directory_name = 'spool'

# What a read that breaks off midway says
_broken_read_error = 'The connection was reset during the read'

# ################################################################################################################################
# ################################################################################################################################

class _BrokenReadClient(LocalDirectoryClient):
    """ A directory whose reads break off after the first chunk.
    """

    def read_chunks(self, remote_path:'str', callback:'any_') -> 'None':
        callback(b'The first chunk of the file')
        raise Exception(_broken_read_error)

# ################################################################################################################################
# ################################################################################################################################

@fixture(autouse=True)
def spool_directory(tmp_path:'any_', monkeypatch:'any_') -> 'str':
    """ The spool files of each test go to a directory of their own, so a test can check that none are left behind.
    """
    out = os.path.join(str(tmp_path), _spool_directory_name)
    os.makedirs(out)

    monkeypatch.setenv(Env_Spool_Directory, out)
    return out

# ################################################################################################################################

def _get_read_event(events:'any_') -> 'any_':
    """ The one event that recorded the read operation.
    """
    for item in events:
        if item['event_type'] == AuditEvent.Request_Sent:
            if loads(item['data'])['operation'] == Operation_Read:
                out = item
                break
    else:
        raise Exception('No read event found')

    return out

# ################################################################################################################################

def _run(tmp_path:'any_', file_content:'bytes', **schedule_overrides:'any_') -> 'TextServiceStub':
    """ One schedule run over one file, with a target service that reads the file as text.
    """
    service, context, _ = new_environment(tmp_path, service_class=TextServiceStub, file_content=file_content)
    context[_scheduler.Extra_Schedule] = new_schedule(**schedule_overrides)

    process_files(cast_('any_', service), context)

    out = cast_('TextServiceStub', service)
    return out

# ################################################################################################################################
# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_the_service_reads_the_text_in_the_encoding_of_the_schedule(
    tmp_path:'any_',
    spool_directory:'str',
    encoding:'str',
    ) -> 'None':

    data = sample_bytes(encoding)

    with audit_db_env(tmp_path):

        service = _run(tmp_path, data, encoding=encoding)

        # The service received the file once, as text in the schedule's encoding ..
        assert service.encodings == [encoding]
        assert service.texts == [sample_text(encoding)]
        assert service.lines == [sample_lines(encoding)]

        # .. its bytes exactly as they were on the remote side ..
        assert service.contents == [data]

        _, item = service.invoked[0]
        assert item.size == len(data)

        # .. the delivery event says which encoding the file was read in ..
        events = get_events()
        delivered = events_of_type(events, AuditEvent.Delivered)[0]
        assert loads(delivered['data'])['encoding'] == encoding

        # .. the checksum is the one of the bytes that were read ..
        read = _get_read_event(events)
        attrs = get_attrs(read['id'])
        assert attrs['checksum'] == sha256(data).hexdigest()

        # .. and the spool file is gone.
        assert os.listdir(spool_directory) == []

# ################################################################################################################################

@mark.parametrize('encoding', (Encoding.UTF_8, Encoding.UTF_16_LE, Encoding.UTF_16_BE))
def test_a_byte_order_mark_is_not_part_of_the_text(tmp_path:'any_', encoding:'str') -> 'None':

    data = sample_bytes(encoding, should_add_byte_order_mark=True)

    with audit_db_env(tmp_path):

        service = _run(tmp_path, data, encoding=encoding)

        assert service.texts == [sample_text(encoding)]
        assert service.lines == [sample_lines(encoding)]
        assert service.contents == [data]

# ################################################################################################################################

@mark.parametrize('encoding', (Encoding.CP1252, Encoding.CP1250, Encoding.CP1253, Encoding.CP1255))
def test_windows_line_breaks_are_not_part_of_lines(tmp_path:'any_', encoding:'str') -> 'None':

    data = sample_bytes(encoding, '\r\n')

    with audit_db_env(tmp_path):

        service = _run(tmp_path, data, encoding=encoding)

        assert service.lines == [sample_lines(encoding)]

# ################################################################################################################################

def test_a_schedule_without_an_encoding_reads_utf_8(tmp_path:'any_') -> 'None':

    # The schedule was stored before schedules named an encoding
    schedule = new_schedule()
    assert 'encoding' not in schedule

    with audit_db_env(tmp_path):

        service = _run(tmp_path, sample_bytes(Encoding.UTF_8))

        assert service.encodings == [Default_Encoding]
        assert service.texts == [sample_text(Encoding.UTF_8)]

# ################################################################################################################################

@mark.parametrize('encoding', (Encoding.CP1250, Encoding.CP1253, Encoding.CP1255, Encoding.ISO_8859_2))
def test_a_file_in_another_encoding_fails_its_delivery(tmp_path:'any_', spool_directory:'str', encoding:'str') -> 'None':

    with audit_db_env(tmp_path):

        service = _run(tmp_path, sample_bytes(encoding), encoding=Encoding.UTF_8)

        # The service never got as far as recording the text ..
        assert service.texts == []

        # .. the delivery failed with the decoding error ..
        events = get_events()
        failed = events_of_type(events, AuditEvent.Delivery_Failed)[0]

        assert failed['outcome'] == AuditOutcome.Error
        assert 'UnicodeDecodeError' in failed['data']

        # .. the file stays in place for the next run ..
        base_dir = os.path.join(str(tmp_path), 'files')
        assert os.path.exists(os.path.join(base_dir, Directory, File_Name))

        # .. and the spool file is gone all the same.
        assert os.listdir(spool_directory) == []

# ################################################################################################################################

def test_a_file_is_read_in_many_chunks(tmp_path:'any_') -> 'None':

    encoding = Encoding.CP1257
    data = sample_bytes(encoding) * 50

    # The file is far bigger than one chunk of the client
    assert len(data) > Read_Chunk_Size * 100

    with audit_db_env(tmp_path):

        service = _run(tmp_path, data, encoding=encoding)

        assert service.contents == [data]
        assert service.texts == [sample_text(encoding) * 50]

# ################################################################################################################################

@mark.parametrize('encoding', (Encoding.CP1255, Encoding.ISO_8859_7, Encoding.CP037))
def test_stored_content_is_the_bytes_as_read(tmp_path:'any_', encoding:'str') -> 'None':

    data = sample_bytes(encoding)

    with audit_db_env(tmp_path):

        service, context, _ = new_environment(tmp_path, service_class=TextServiceStub, should_store_content=True,
            file_content=data)
        context[_scheduler.Extra_Schedule] = new_schedule(encoding=encoding)

        process_files(cast_('any_', service), context)

        read = _get_read_event(get_events())

        # The read event keeps the bytes the spool file held, not a decoded form of them
        stored = load_transfer_content(read['cid'])
        assert stored == data

# ################################################################################################################################

def test_a_read_broken_off_midway_leaves_no_spool_file(tmp_path:'any_', spool_directory:'str') -> 'None':

    with audit_db_env(tmp_path):

        service, _, _ = new_environment(tmp_path, client_class=_BrokenReadClient)
        conn = service.smb[Connection_Name]

        remote_path = f'{Directory}/{File_Name}'

        try:
            _ = conn.read_to_spool(remote_path)
        except Exception:
            pass
        else:
            raise Exception('A broken read was expected to propagate')

        # The part that arrived was deleted with the spool file ..
        assert os.listdir(spool_directory) == []

        # .. and the read is on record as an error.
        read = _get_read_event(get_events())

        assert read['outcome'] == AuditOutcome.Error
        assert _broken_read_error in read['data']

# ################################################################################################################################

def test_stored_content_over_the_cap_keeps_only_its_metadata(tmp_path:'any_', monkeypatch:'any_') -> 'None':

    data = sample_bytes(Encoding.CP1250)

    # The cap is one byte short of the file
    max_size = len(data) - 1
    monkeypatch.setenv(Env_Max_Attachment_Size, str(max_size))

    with audit_db_env(tmp_path):

        service, context, _ = new_environment(tmp_path, service_class=TextServiceStub, should_store_content=True,
            file_content=data)
        context[_scheduler.Extra_Schedule] = new_schedule(encoding=Encoding.CP1250)

        process_files(cast_('any_', service), context)

        read = _get_read_event(get_events())

        engine = get_audit_engine()
        items = list_attachments(engine, read['id'])

        assert len(items) == 1
        assert items[0]['size'] == len(data)
        assert items[0]['is_content_kept'] is False

# ################################################################################################################################
# ################################################################################################################################
