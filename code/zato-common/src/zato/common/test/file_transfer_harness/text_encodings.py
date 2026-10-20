# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.file_transfer.api import Default_Encoding, Encoding, Encoding_List
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase
from zato.common.test.file_transfer_harness.deliveries import Service_Store_Text
from zato.common.test.file_transfer_harness.encoding_samples import sample_bytes, sample_lines, sample_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# An encoding that schedules do not offer
_unsupported_encoding = 'koi8-r'

# The name of the file each test puts on the remote side
_file_name = 'customers.txt'

# ################################################################################################################################
# ################################################################################################################################

class EncodingTests(FileTransferScheduleTestBase):
    """ A schedule hands each file to its target service as text in the encoding the schedule names -
    every encoding a schedule offers, over every protocol.
    """

    @pytest.mark.parametrize('encoding', Encoding_List)
    def test_text_is_read_in_the_encoding_of_the_schedule(self, harness:'Harness', encoding:'str') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding')

        data = sample_bytes(encoding)
        harness.write(directory, _file_name, data)

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Store_Text, encoding=encoding)
        harness.run(conn, schedule)

        # The service read the file once, in the schedule's encoding, in full and line by line ..
        entries = harness.delivered(schedule_name)
        assert len(entries) == 1

        entry = entries[0]

        assert entry['encoding'] == encoding
        assert entry['text'] == sample_text(encoding)
        assert entry['lines'] == sample_lines(encoding)

        # .. the bytes were the ones written to the remote side ..
        assert entry['size'] == len(data)
        assert entry['data_digest'] == sha256(data).hexdigest()

        # .. and the file was moved out of the way.
        harness.assert_names(directory, [_move_directory])

# ################################################################################################################################

    @pytest.mark.parametrize('encoding', (Encoding.UTF_8, Encoding.UTF_16_LE, Encoding.UTF_16_BE))
    def test_byte_order_mark_is_not_part_of_the_text(self, harness:'Harness', encoding:'str') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.bom')

        harness.write(directory, _file_name, sample_bytes(encoding, should_add_byte_order_mark=True))

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Store_Text, encoding=encoding)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)
        assert len(entries) == 1

        assert entries[0]['text'] == sample_text(encoding)
        assert entries[0]['lines'] == sample_lines(encoding)

# ################################################################################################################################

    @pytest.mark.parametrize('encoding', (Encoding.CP1252, Encoding.CP1250, Encoding.CP1253, Encoding.CP1255))
    def test_windows_line_breaks_are_not_part_of_lines(self, harness:'Harness', encoding:'str') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.crlf')

        harness.write(directory, _file_name, sample_bytes(encoding, '\r\n'))

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Store_Text, encoding=encoding)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)
        assert len(entries) == 1

        assert entries[0]['lines'] == sample_lines(encoding)

# ################################################################################################################################

    def test_a_schedule_without_an_encoding_reads_utf_8(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.default')

        harness.write(directory, _file_name, sample_bytes(Encoding.UTF_8))

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Store_Text)
        assert schedule['encoding'] == Default_Encoding

        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)
        assert len(entries) == 1

        assert entries[0]['encoding'] == Default_Encoding
        assert entries[0]['text'] == sample_text(Encoding.UTF_8)

# ################################################################################################################################

    @pytest.mark.parametrize('encoding', (Encoding.CP1250, Encoding.CP1253, Encoding.CP1255))
    def test_a_file_in_another_encoding_fails_its_delivery(self, harness:'Harness', encoding:'str') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.mismatch')

        harness.write(directory, _file_name, sample_bytes(encoding))

        # The schedule reads its files as UTF-8, which the bytes of a single-byte encoding are not
        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Store_Text,
            encoding=Encoding.UTF_8)
        harness.run(conn, schedule)

        # Nothing was recorded and the file stays in place for the next run
        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, [_file_name])

# ################################################################################################################################

    def test_the_encoding_is_stored_and_edited(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.edit')

        schedule = harness.create_schedule(conn, schedule_name, directory, encoding=Encoding.ISO_8859_7)
        assert schedule['encoding'] == Encoding.ISO_8859_7

        _ = harness.client.edit_schedule(conn.id, schedule['id'], schedule_name, directory, encoding=Encoding.CP1255)

        edited = harness.client.require_schedule(conn.id, schedule['id'])
        assert edited['encoding'] == Encoding.CP1255

# ################################################################################################################################

    def test_an_unsupported_encoding_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('encoding.unsupported')

        with pytest.raises(Exception, match='Encoding'):
            _ = harness.client.create_schedule(conn.id, schedule_name, directory, encoding=_unsupported_encoding)

        # Neither a schedule nor a job were created
        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, schedule_name)

# ################################################################################################################################
# ################################################################################################################################
