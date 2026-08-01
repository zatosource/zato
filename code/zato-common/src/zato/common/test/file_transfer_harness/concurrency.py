# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Thread

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase
from zato.common.test.file_transfer_harness.evidence import Service_Slow_Store

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Connection, Harness
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# How many files the competing consumers share between themselves
_shared_file_count = 12

# ################################################################################################################################
# ################################################################################################################################

def _run_together(harness:'Harness', conn:'Connection', schedules:'anylist') -> 'anylist':
    """ Starts one run of each of the given schedules at the same time and waits for all of them,
    returning whatever any of them raised.
    """
    errors:'anylist' = []
    threads:'anylist' = []

    def _run_one(schedule:'anydict') -> 'None':
        try:
            harness.run_once(conn, schedule)
        except Exception as e:
            errors.append(e)

    for schedule in schedules:
        thread = Thread(target=_run_one, args=(schedule,), name='zato-test-file-transfer-run', daemon=True)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return errors

# ################################################################################################################################
# ################################################################################################################################

class ConcurrencyTests(FileTransferScheduleTestBase):
    """ What happens when more than one run is under way at the same time over the same files.
    """

    def test_competing_consumers_deliver_each_file_once(self, harness:'Harness') -> 'None':

        harness.require('supports_claim')

        conn = harness.new_conn()
        directory = harness.make_directory()

        first_name = harness.new_schedule_name('consumer.first')
        second_name = harness.new_schedule_name('consumer.second')

        expected:'strlist' = []

        for index in range(_shared_file_count):
            file_name = f'shared-{index:03d}.txt'
            harness.write(directory, file_name, f'Payload of {file_name}')
            expected.append(file_name)

        expected = sorted(expected)

        # Two schedules over one directory, each claiming a file before it reads it
        first = harness.create_schedule(conn, first_name, directory, should_claim=True)
        second = harness.create_schedule(conn, second_name, directory, should_claim=True)

        errors = _run_together(harness, conn, [first, second])
        assert errors == []

        # Between the two of them every file went through exactly once ..
        delivered = harness.delivered_names(first_name) + harness.delivered_names(second_name)
        delivered = sorted(delivered)

        assert delivered == expected

        # .. and every one of them is in the destination, with no claim left behind.
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), expected)

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='Two runs reaching for one file end each other early')
    def test_competing_consumers_without_claiming_lose_no_file(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        first_name = harness.new_schedule_name('unclaimed.first')
        second_name = harness.new_schedule_name('unclaimed.second')

        expected:'strlist' = []

        for index in range(_shared_file_count):
            file_name = f'shared-{index:03d}.txt'
            harness.write(directory, file_name, f'Payload of {file_name}')
            expected.append(file_name)

        expected = sorted(expected)

        # Without claiming, nothing stops the two runs from reaching for the same file
        first = harness.create_schedule(conn, first_name, directory)
        second = harness.create_schedule(conn, second_name, directory)

        _ = _run_together(harness, conn, [first, second])

        # Whatever the two runs made of each other, every file was seen at least once ..
        delivered = harness.delivered_names(first_name) + harness.delivered_names(second_name)
        seen = sorted(set(delivered))

        assert seen == expected

        # .. and none of them was left behind in the directory it came from.
        remaining = harness.names(directory)
        assert remaining == [_move_directory]

# ################################################################################################################################

    def test_a_run_starting_while_another_is_under_way(self, harness:'Harness') -> 'None':

        harness.require('supports_claim')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('overlapping')

        expected:'strlist' = []

        for index in range(4):
            file_name = f'slow-{index:03d}.txt'
            harness.write(directory, file_name, f'Payload of {file_name}')
            expected.append(file_name)

        expected = sorted(expected)

        # The target service takes long enough over each file that the second run starts
        # while the first one is still working through the directory.
        schedule = harness.create_schedule(conn, schedule_name, directory,
            service=Service_Slow_Store, should_claim=True)

        errors = _run_together(harness, conn, [schedule, schedule])
        assert errors == []

        # Claiming is what keeps two overlapping runs from delivering the same file twice
        delivered = harness.delivered_names(schedule_name)
        assert delivered == expected

        harness.assert_names(harness.move_directory_of(directory), expected)

# ################################################################################################################################

    def test_two_schedules_share_a_pool_of_one(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        first_name = harness.new_schedule_name('pooled.first')
        second_name = harness.new_schedule_name('pooled.second')

        harness.write(first_directory, 'first.txt', 'Through the pool from the first schedule')
        harness.write(second_directory, 'second.txt', 'Through the pool from the second schedule')

        # The connection was created with a pool of one, so the two runs have to take turns
        first = harness.create_schedule(conn, first_name, first_directory)
        second = harness.create_schedule(conn, second_name, second_directory)

        errors = _run_together(harness, conn, [first, second])
        assert errors == []

        assert harness.delivered_names(first_name) == ['first.txt']
        assert harness.delivered_names(second_name) == ['second.txt']

# ################################################################################################################################
# ################################################################################################################################
