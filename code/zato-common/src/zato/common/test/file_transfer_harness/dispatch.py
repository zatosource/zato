# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase
from zato.common.test.file_transfer_harness.evidence import Service_Always_Raise

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# ################################################################################################################################
# ################################################################################################################################

class DispatchTests(FileTransferScheduleTestBase):
    """ One run of a schedule - what it picks up, what it hands to the target service
    and what it leaves behind on the remote side.
    """

    def test_moves_file_on_success(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('move')

        harness.write(directory, 'first.txt', 'First file payload')
        harness.write(directory, 'second.txt', 'Second file payload')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # The target service saw each of the two files exactly once ..
        entries = harness.evidence.by_file_name(schedule_name)
        assert len(entries) == 2

        # .. with the full details of each of them ..
        entry = entries['first.txt']

        assert entry['conn_type'] == harness.adapter.conn_type
        assert entry['conn_name'] == conn.name
        assert entry['directory'] == directory
        assert entry['full_path'] == harness.adapter.remote_join(directory, 'first.txt')
        assert entry['size'] == len('First file payload')
        assert entry['data'] == 'First file payload'
        assert entry['last_modified']

        entry = entries['second.txt']
        assert entry['data'] == 'Second file payload'

        # .. and both files were moved into the destination directory.
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), ['first.txt', 'second.txt'])

# ################################################################################################################################

    def test_deletes_file_on_success(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('delete')

        harness.write(directory, 'ephemeral.txt', 'Payload to delete after processing')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            on_success=_scheduler.OnSuccess.Delete, move_directory='')

        harness.run(conn, schedule)

        # The file was recorded and then deleted rather than moved
        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['data'] == 'Payload to delete after processing'

        harness.assert_names(directory, [])

# ################################################################################################################################

    def test_pattern_leaves_other_files_alone(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('pattern')

        harness.write(directory, 'data.csv', 'name,value')
        harness.write(directory, 'notes.txt', 'Not a CSV file')

        schedule = harness.create_schedule(conn, schedule_name, directory, pattern='*.csv')
        harness.run(conn, schedule)

        # Only the matching file was processed ..
        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['file_name'] == 'data.csv'

        # .. and the other one stays untouched in the directory.
        harness.assert_names(directory, [_move_directory, 'notes.txt'])

# ################################################################################################################################

    def test_pattern_matching_nothing_leaves_the_directory_as_it_was(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('no.match')

        harness.write(directory, 'notes.txt', 'Not a CSV file')

        schedule = harness.create_schedule(conn, schedule_name, directory, pattern='*.csv')
        harness.run(conn, schedule)

        # Nothing was delivered and the move directory was never needed
        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, ['notes.txt'])

# ################################################################################################################################

    def test_error_leaves_file_in_place(self, harness:'Harness') -> 'None':

        harness.require('supports_claim')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('error')

        harness.write(directory, 'unlucky.txt', 'Payload that will not be processed')

        # The target service always raises and the file is claimed before it is read
        schedule = harness.create_schedule(conn, schedule_name, directory,
            service=Service_Always_Raise, should_claim=True)

        harness.run(conn, schedule)

        # Nothing was recorded ..
        assert harness.delivered(schedule_name) == []

        # .. and the file was renamed back after the failure, so the next run can take it again.
        harness.assert_names(directory, ['unlucky.txt'])

# ################################################################################################################################

    def test_error_without_claiming_leaves_file_in_place(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('error.unclaimed')

        harness.write(directory, 'unlucky.txt', 'Payload that will not be processed')

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Always_Raise)
        harness.run(conn, schedule)

        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, ['unlucky.txt'])

# ################################################################################################################################

    def test_empty_directory_is_a_no_op(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('empty')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # Nothing was delivered and the move directory was never created
        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, [])

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='A directory that is not there ends the run with an error')
    def test_missing_directory_is_a_no_op(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('missing')

        # The schedule points at a directory inside the one that exists, which was never created
        missing_directory = harness.adapter.remote_join(directory, 'not-created-yet')

        schedule = harness.create_schedule(conn, schedule_name, missing_directory)

        # A directory that is not there yet is what every feed looks like before its first delivery,
        # so a run that finds none of it has nothing to do rather than something to report.
        harness.run_once(conn, schedule)

        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, [])

# ################################################################################################################################

    def test_subdirectories_are_skipped(self, harness:'Harness') -> 'None':

        harness.require('supports_subdirectories')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('subdirectory')

        _ = harness.make_subdirectory(directory, 'incoming-archive')
        harness.write(directory, 'invoice.txt', 'The only file here')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # Only the file was picked up and the directory stayed where it was
        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(directory, ['incoming-archive', _move_directory])

# ################################################################################################################################

    def test_files_under_a_subdirectory_are_not_reached(self, harness:'Harness') -> 'None':

        harness.require('supports_subdirectories')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('not.recursive')

        nested = harness.make_subdirectory(directory, 'nested')
        harness.write(nested, 'deep.txt', 'A file one level down')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # A schedule looks into its own directory and no further
        assert harness.delivered(schedule_name) == []
        harness.assert_names(nested, ['deep.txt'])

# ################################################################################################################################

    def test_claimed_files_are_skipped(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('claimed.elsewhere')

        # A file another consumer is already working on carries the claim suffix
        claimed_name = 'taken.txt' + _scheduler.Claim_Suffix

        harness.write(directory, claimed_name, 'Someone else is reading this')
        harness.write(directory, 'free.txt', 'Nobody has taken this one')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # Only the file nobody claimed was picked up, and the claimed one stayed exactly as it was
        assert harness.delivered_names(schedule_name) == ['free.txt']
        harness.assert_names(directory, [claimed_name, _move_directory])

# ################################################################################################################################

    def test_trailing_slash_in_the_directory_is_accepted(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('trailing.slash')

        harness.write(directory, 'invoice.txt', 'Payload behind a trailing slash')

        schedule = harness.create_schedule(conn, schedule_name, directory + '/')
        harness.run(conn, schedule)

        # The file was found and moved just as it would have been without the slash
        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(harness.move_directory_of(directory), ['invoice.txt'])

# ################################################################################################################################

    def test_existing_move_directory_is_reused(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('reused.destination')

        # The destination is already there before the first run, holding a file of its own
        move_directory = harness.make_subdirectory(directory, _move_directory)
        harness.write(move_directory, 'from-yesterday.txt', 'Delivered by an earlier run')

        harness.write(directory, 'invoice.txt', 'Delivered by this run')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # The run added to the destination rather than tripping over it
        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(move_directory, ['from-yesterday.txt', 'invoice.txt'])

# ################################################################################################################################

    def test_move_directory_of_another_name_is_honoured(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('own.destination')

        harness.write(directory, 'invoice.txt', 'Payload going somewhere of its own')

        schedule = harness.create_schedule(conn, schedule_name, directory, move_directory='archive')
        harness.run(conn, schedule)

        harness.assert_names(directory, ['archive'])
        harness.assert_names(harness.move_directory_of(directory, 'archive'), ['invoice.txt'])

# ################################################################################################################################
# ################################################################################################################################
