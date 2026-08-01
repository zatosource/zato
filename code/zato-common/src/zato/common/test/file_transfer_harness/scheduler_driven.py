# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# How long to wait for a fire event to deliver a file, in seconds
_fire_wait_seconds = 45

# How long to wait before deciding that no fire event is coming, in seconds
_quiet_wait_seconds = 15

# How long to give a run to put a file out of the way after the delivery it recorded, in seconds
_ack_wait_seconds = 15

# ################################################################################################################################
# ################################################################################################################################

def _starting_now() -> 'str':
    """ A start date that lets the scheduler fire straight away.
    """
    now = datetime.now(timezone.utc)

    out = now.isoformat()
    return out

# ################################################################################################################################

def _starting_much_later() -> 'str':
    """ A start date far enough ahead that no fire event can arrive while the test runs.
    """
    now = datetime.now(timezone.utc)
    later = now + timedelta(days=1)

    out = later.isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.slow
class SchedulerDrivenTests(FileTransferScheduleTestBase):
    """ Schedules driven by the scheduler itself rather than by a hand-made invocation of the dispatch service.
    """

    def test_a_fire_event_delivers_a_file(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.move')

        harness.write(directory, 'delivered.txt', 'Payload delivered by the scheduler')

        _ = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now())

        entries = harness.deliveries.wait_for_count(schedule_name, 1, _fire_wait_seconds)

        assert entries[0]['file_name'] == 'delivered.txt'
        assert entries[0]['data'] == 'Payload delivered by the scheduler'

        # The file was moved away, so the fires that follow find nothing to do
        entries = harness.deliveries.wait_for_quiet(schedule_name, 3)

        assert len(entries) == 1
        harness.assert_names(harness.move_directory_of(directory), ['delivered.txt'], timeout=_ack_wait_seconds)

# ################################################################################################################################

    def test_a_fire_event_deletes_a_file(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.delete')

        harness.write(directory, 'ephemeral.txt', 'Payload the scheduler deletes once it is through')

        _ = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now(),
            on_success=_scheduler.OnSuccess.Delete, move_directory='')

        entries = harness.deliveries.wait_for_count(schedule_name, 1, _fire_wait_seconds)

        assert entries[0]['file_name'] == 'ephemeral.txt'

        # Nothing was moved anywhere, the file is simply gone. The record of the delivery reaches this test
        # before the run that produced it is over, so the file goes away a moment after it is recorded.
        harness.assert_names(directory, [], timeout=_ack_wait_seconds)

# ################################################################################################################################

    def test_an_inactive_schedule_never_fires(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.inactive')

        harness.write(directory, 'untouched.txt', 'Payload no fire event will ever reach')

        _ = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now(), is_active=False)

        entries = harness.deliveries.wait_for_quiet(schedule_name, _quiet_wait_seconds)

        assert entries == []
        harness.assert_names(directory, ['untouched.txt'])

# ################################################################################################################################

    def test_a_schedule_starting_later_never_fires_now(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.later')

        harness.write(directory, 'untouched.txt', 'Payload for a schedule that starts tomorrow')

        _ = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_much_later())

        entries = harness.deliveries.wait_for_quiet(schedule_name, _quiet_wait_seconds)

        assert entries == []
        harness.assert_names(directory, ['untouched.txt'])

# ################################################################################################################################

    def test_an_edit_reaches_the_running_scheduler(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.edited')

        harness.write(directory, 'first.txt', 'Payload of the directory the schedule started with')

        created = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now())

        entries = harness.deliveries.wait_for_count(schedule_name, 1, _fire_wait_seconds)
        assert entries[0]['file_name'] == 'first.txt'

        # The schedule is pointed at another directory while the scheduler is running ..
        _ = harness.client.edit_schedule(conn.id, created['id'], schedule_name, other_directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now())

        # .. and a file dropped there is delivered, which the old directory could never have produced.
        harness.write(other_directory, 'second.txt', 'Payload of the directory the schedule was moved to')

        entries = harness.deliveries.wait_for_count(schedule_name, 2, _fire_wait_seconds)

        delivered = harness.delivered_names(schedule_name)
        assert delivered == ['first.txt', 'second.txt']

# ################################################################################################################################

    def test_a_deleted_schedule_stops_firing(self, harness:'Harness', scheduler_process:'any_') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('fire.deleted')

        harness.write(directory, 'first.txt', 'Payload delivered before the schedule was deleted')

        created = harness.client.create_schedule(conn.id, schedule_name, directory,
            run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=_starting_now())

        _ = harness.deliveries.wait_for_count(schedule_name, 1, _fire_wait_seconds)

        harness.client.delete_schedule(conn.id, created['id'])

        # A file dropped after the schedule was deleted has nothing left to pick it up
        harness.write(directory, 'second.txt', 'Payload nothing is left to deliver')

        entries = harness.deliveries.wait_for_quiet(schedule_name, _quiet_wait_seconds)

        assert len(entries) == 1
        assert harness.exists(directory, 'second.txt')

# ################################################################################################################################
# ################################################################################################################################
