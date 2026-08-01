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
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase
from zato.common.test.file_transfer_harness.evidence import Max_Recorded_Payload_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory
_marker_suffix = _scheduler.Default_Marker_Suffix

# How many files one run of the volume test puts through the schedule
_volume_file_count = 50

# How large the file of the size test is - one line repeated until it is several megabytes
_large_file_line = 'Order line for a partner feed that sends its whole day in one file\n'
_large_file_line_count = 60_000

# ################################################################################################################################
# ################################################################################################################################

class UsageTests(FileTransferScheduleTestBase):
    """ Schedules doing what a real feed does - the same directory receiving files run after run,
    a whole day's worth of them at once, and several schedules sharing one connection.
    """

    def test_each_run_takes_only_what_is_new(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('repeated.runs')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        # The first delivery of the day ..
        harness.write(directory, 'morning.txt', 'The morning batch')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['morning.txt']

        # .. a run with nothing new to find ..
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['morning.txt']

        # .. the second delivery ..
        harness.write(directory, 'midday.txt', 'The midday batch')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['midday.txt', 'morning.txt']

        # .. and the third, with everything accumulating in the destination and nothing repeating.
        harness.write(directory, 'evening.txt', 'The evening batch')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['evening.txt', 'midday.txt', 'morning.txt']

        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), ['evening.txt', 'midday.txt', 'morning.txt'])

# ################################################################################################################################

    def test_a_file_arriving_after_the_listing_waits_for_the_next_run(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('arrived.late')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        harness.write(directory, 'on-time.txt', 'Present when the run started')
        harness.run(conn, schedule)

        # A file that turned up once the run was over is simply the next run's business
        harness.write(directory, 'late.txt', 'Turned up after the run')

        assert harness.delivered_names(schedule_name) == ['on-time.txt']

        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['late.txt', 'on-time.txt']

# ################################################################################################################################

    def test_the_same_file_name_arriving_twice_keeps_both(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('same.name.twice')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        # A daily feed sends the same name every day ..
        harness.write(directory, 'orders.csv', 'order,quantity\nfirst-day,1')
        harness.run(conn, schedule)

        harness.write(directory, 'orders.csv', 'order,quantity\nsecond-day,2')
        harness.run(conn, schedule)

        # .. and both days were delivered ..
        entries = harness.delivered(schedule_name)
        assert len(entries) == 2

        # .. so both days must still be there afterwards, neither of them written over by the other.
        moved = harness.names(harness.move_directory_of(directory))
        assert len(moved) == 2

# ################################################################################################################################

    @pytest.mark.slow
    def test_a_whole_batch_goes_through_in_one_run(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('volume')

        expected:'strlist' = []

        for index in range(_volume_file_count):
            file_name = f'order-{index:04d}.csv'
            harness.write(directory, file_name, f'order,quantity\n{file_name},{index}')
            expected.append(file_name)

        expected = sorted(expected)

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # Every file was delivered exactly once, none lost and none repeated ..
        assert harness.delivered_names(schedule_name) == expected

        # .. and every one of them reached the destination.
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), expected)

# ################################################################################################################################

    @pytest.mark.slow
    def test_a_large_file_arrives_whole(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('large')

        payload = (_large_file_line * _large_file_line_count).encode('utf8')
        expected_length = len(payload)
        expected_digest = sha256(payload).hexdigest()

        # The test is only worth running on a payload too large to be kept in the evidence in full
        assert expected_length > Max_Recorded_Payload_Size

        harness.write(directory, 'one-whole-day.csv', payload)

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['size'] == expected_length
        assert entries[0]['data_length'] == expected_length
        assert entries[0]['data_digest'] == expected_digest

        moved = harness.read(harness.move_directory_of(directory), 'one-whole-day.csv')
        assert len(moved) == expected_length

# ################################################################################################################################

    def test_a_partner_feed_from_the_drop_to_the_destination(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('partner.feed')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            pattern='orders_*.csv', ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_marker_suffix)

        # The partner starts its upload and the run finds it incomplete ..
        harness.write(directory, 'orders_20260801.csv', 'order,quantity\nfirst,1')
        harness.run(conn, schedule)

        assert harness.delivered(schedule_name) == []
        harness.assert_names(directory, ['orders_20260801.csv'])

        # .. the partner finishes and puts down its marker ..
        harness.write(directory, 'orders_20260801.csv' + _marker_suffix, '')
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['file_name'] == 'orders_20260801.csv'
        assert entries[0]['data'] == 'order,quantity\nfirst,1'

        # .. the file is in the destination and the marker is gone ..
        harness.assert_names(directory, [_move_directory])
        harness.assert_names(harness.move_directory_of(directory), ['orders_20260801.csv'])

        # .. and the next run has nothing left to do.
        harness.run(conn, schedule)

        assert len(harness.delivered(schedule_name)) == 1

# ################################################################################################################################

    def test_two_schedules_over_one_directory_keep_to_their_patterns(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        csv_schedule_name = harness.new_schedule_name('feed.csv')
        xml_schedule_name = harness.new_schedule_name('feed.xml')

        harness.write(directory, 'orders.csv', 'order,quantity')
        harness.write(directory, 'orders.xml', '<orders/>')
        harness.write(directory, 'readme.txt', 'Neither of the two schedules wants this')

        csv_schedule = harness.create_schedule(conn, csv_schedule_name, directory,
            pattern='*.csv', move_directory='csv-archive')

        xml_schedule = harness.create_schedule(conn, xml_schedule_name, directory,
            pattern='*.xml', move_directory='xml-archive')

        harness.run(conn, csv_schedule)
        harness.run(conn, xml_schedule)

        # Each schedule took its own file and neither touched the other's ..
        assert harness.delivered_names(csv_schedule_name) == ['orders.csv']
        assert harness.delivered_names(xml_schedule_name) == ['orders.xml']

        # .. each one has its own destination ..
        harness.assert_names(harness.move_directory_of(directory, 'csv-archive'), ['orders.csv'])
        harness.assert_names(harness.move_directory_of(directory, 'xml-archive'), ['orders.xml'])

        # .. and the file neither of them matched is still waiting.
        harness.assert_names(directory, ['csv-archive', 'readme.txt', 'xml-archive'])

# ################################################################################################################################

    def test_two_schedules_over_their_own_directories(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        first_schedule_name = harness.new_schedule_name('branch.north')
        second_schedule_name = harness.new_schedule_name('branch.south')

        harness.write(first_directory, 'north.csv', 'Sales of the northern branch')
        harness.write(second_directory, 'south.csv', 'Sales of the southern branch')

        first_schedule = harness.create_schedule(conn, first_schedule_name, first_directory)
        second_schedule = harness.create_schedule(conn, second_schedule_name, second_directory)

        harness.run(conn, first_schedule)
        harness.run(conn, second_schedule)

        assert harness.delivered_names(first_schedule_name) == ['north.csv']
        assert harness.delivered_names(second_schedule_name) == ['south.csv']

        harness.assert_names(harness.move_directory_of(first_directory), ['north.csv'])
        harness.assert_names(harness.move_directory_of(second_directory), ['south.csv'])

# ################################################################################################################################

    def test_two_connections_over_their_own_directories(self, harness:'Harness') -> 'None':

        first_conn = harness.new_conn()
        second_conn = harness.new_conn()

        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        first_schedule_name = harness.new_schedule_name('partner.first')
        second_schedule_name = harness.new_schedule_name('partner.second')

        harness.write(first_directory, 'first.csv', 'What the first partner sent')
        harness.write(second_directory, 'second.csv', 'What the second partner sent')

        first_schedule = harness.create_schedule(first_conn, first_schedule_name, first_directory)
        second_schedule = harness.create_schedule(second_conn, second_schedule_name, second_directory)

        harness.run(first_conn, first_schedule)
        harness.run(second_conn, second_schedule)

        # Each connection reports itself as the one the file came through
        first_entries = harness.delivered(first_schedule_name)
        second_entries = harness.delivered(second_schedule_name)

        assert len(first_entries) == 1
        assert len(second_entries) == 1

        assert first_entries[0]['conn_name'] == first_conn.name
        assert second_entries[0]['conn_name'] == second_conn.name

# ################################################################################################################################
# ################################################################################################################################
