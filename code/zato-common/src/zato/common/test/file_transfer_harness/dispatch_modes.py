# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from hashlib import sha256
from threading import Thread

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory
_marker_suffix = _scheduler.Default_Marker_Suffix

# Names and payloads carrying Dutch, Greek and Korean letters, which is what a real feed brings
_unicode_file_name = 'ijsselmeer-Λογαριασμός-송장.txt'
_unicode_payload = 'Rekening voor de ijsselmeer - Λογαριασμός - 송장 내역'

# A payload that is not text at all, so nothing along the way may decode it
_binary_payload = bytes(range(256)) * 8

# How long a schedule waits for a file to stop changing in the tests that watch one grow, in seconds
_stability_delay = 3

# How long into that wait the file grows, in seconds - early enough for the schedule to still be waiting
_growth_delay = 0.5

# ################################################################################################################################
# ################################################################################################################################

class DispatchModeTests(FileTransferScheduleTestBase):
    """ The two ways a schedule decides that a file is ready, the claiming of a file before it is read,
    and the payloads that go through unchanged.
    """

    def test_marker_mode(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('marker')

        # One upload is complete - its marker is there - and the other one is still in progress
        harness.write(directory, 'complete.txt', 'Complete upload payload')
        harness.write(directory, 'complete.txt' + _marker_suffix, '')
        harness.write(directory, 'incomplete.txt', 'Upload still in progress')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_marker_suffix)

        harness.run(conn, schedule)

        # Only the upload with a marker was processed ..
        assert harness.delivered_names(schedule_name) == ['complete.txt']

        # .. its marker went away together with it, while the incomplete upload stays for the next run.
        harness.assert_names(directory, [_move_directory, 'incomplete.txt'])
        harness.assert_names(harness.move_directory_of(directory), ['complete.txt'])

# ################################################################################################################################

    def test_marker_mode_with_another_suffix(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('marker.custom')

        harness.write(directory, 'orders.csv', 'order,quantity')
        harness.write(directory, 'orders.csv.ready', '')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            ready_how=_scheduler.ReadyHow.Marker, marker_suffix='.ready')

        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['orders.csv']
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), ['orders.csv'])

# ################################################################################################################################

    def test_marker_mode_never_delivers_the_marker_itself(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('marker.only')

        # A marker whose data file never arrived is not something to pick up on its own
        harness.write(directory, 'never-arrived.txt' + _marker_suffix, '')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_marker_suffix)

        harness.run(conn, schedule)

        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, ['never-arrived.txt' + _marker_suffix])

# ################################################################################################################################

    def test_stability_mode_waits_for_a_growing_file(self, harness:'Harness') -> 'None':

        harness.require('preserves_last_modified')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('stability')

        harness.write(directory, 'growing.txt', 'The first half of the payload')

        schedule = harness.create_schedule(conn, schedule_name, directory, stability_delay=_stability_delay)

        # The file grows while the schedule is waiting to see whether it stopped changing
        def _grow_the_file() -> 'None':
            time.sleep(_growth_delay)
            harness.append(directory, 'growing.txt', ' and the second half')

        grower = Thread(target=_grow_the_file, name='zato-test-file-growth', daemon=True)
        grower.start()

        harness.run(conn, schedule)
        grower.join()

        # The upload was still in progress, so nothing was delivered and the file stayed put ..
        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, ['growing.txt'])

        # .. and the next run, with the file no longer changing, takes it.
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['data'] == 'The first half of the payload and the second half'

        harness.assert_names(harness.move_directory_of(directory), ['growing.txt'])

# ################################################################################################################################

    def test_stability_mode_takes_a_file_that_stopped_changing(self, harness:'Harness') -> 'None':

        harness.require('preserves_last_modified')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('stability.settled')

        harness.write(directory, 'settled.txt', 'An upload that finished before the run started')

        schedule = harness.create_schedule(conn, schedule_name, directory, stability_delay=_stability_delay)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['settled.txt']

# ################################################################################################################################

    def test_claiming_delivers_the_file_under_its_own_name(self, harness:'Harness') -> 'None':

        harness.require('supports_claim')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('claim.success')

        harness.write(directory, 'invoice.txt', 'Payload of a claimed file')

        schedule = harness.create_schedule(conn, schedule_name, directory, should_claim=True)
        harness.run(conn, schedule)

        # The service was told the file's real name and path, not the claimed ones ..
        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['file_name'] == 'invoice.txt'
        assert entries[0]['full_path'] == harness.adapter.remote_join(directory, 'invoice.txt')

        # .. and the file reached its destination under its own name, with no claim left behind.
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), ['invoice.txt'])

# ################################################################################################################################

    def test_a_file_that_cannot_be_claimed_is_skipped(self, harness:'Harness') -> 'None':

        harness.require('supports_claim')
        harness.require('supports_subdirectories')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('claim.refused')

        harness.write(directory, 'contested.txt', 'A file this run will not get to keep')
        harness.write(directory, 'free.txt', 'A file nothing stands in the way of')

        # Nothing can be renamed onto a directory, so the claim of this one file cannot go through
        claim_name = 'contested.txt' + _scheduler.Claim_Suffix
        _ = harness.make_subdirectory(directory, claim_name)

        schedule = harness.create_schedule(conn, schedule_name, directory, should_claim=True)
        harness.run(conn, schedule)

        # A claim that does not go through means the file belongs to somebody else, which is not an error -
        # the file stays where it is and the rest of the run carries on.
        assert harness.delivered_names(schedule_name) == ['free.txt']
        harness.assert_names(directory, [claim_name, 'contested.txt', _move_directory])

# ################################################################################################################################

    def test_unicode_names_and_payloads_go_through_unchanged(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('unicode')

        harness.write(directory, _unicode_file_name, _unicode_payload)

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['file_name'] == _unicode_file_name
        assert entries[0]['data'] == _unicode_payload

        # The name survived the move as well
        harness.assert_names(harness.move_directory_of(directory), [_unicode_file_name])

# ################################################################################################################################

    def test_binary_payload_arrives_byte_for_byte(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('binary')

        harness.write(directory, 'payload.bin', _binary_payload)

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        expected_length = len(_binary_payload)
        expected_digest = sha256(_binary_payload).hexdigest()

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['data_length'] == expected_length
        assert entries[0]['data_digest'] == expected_digest
        assert entries[0]['size'] == expected_length

        # What landed in the destination is the same file, byte for byte
        moved = harness.read(harness.move_directory_of(directory), 'payload.bin')
        assert moved == _binary_payload

# ################################################################################################################################

    def test_empty_file_is_delivered(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('empty.file')

        harness.write(directory, 'nothing-inside.txt', '')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['size'] == 0
        assert entries[0]['data'] == ''

        harness.assert_names(harness.move_directory_of(directory), ['nothing-inside.txt'])

# ################################################################################################################################
# ################################################################################################################################
