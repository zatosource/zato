# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase
from zato.common.test.file_transfer_harness.client import Start_Date_Never

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
# ################################################################################################################################

class CrudTests(FileTransferScheduleTestBase):
    """ A schedule and the scheduler job that mirrors it stay in step through every change
    either of them goes through.
    """

    def test_create_schedule_creates_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'invoices.hourly', directory)

        schedule_id = response['id']
        job_id = response['job_id']

        # The id is the schedule's own, generated when it was created and unrelated to its name
        assert schedule_id
        assert schedule_id != 'invoices.hourly'

        # The job exists, is interval-based and points back to its connection
        job = harness.job_of(conn, 'invoices.hourly')

        assert int(job['id']) == int(job_id)
        assert job['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED
        assert job['service_name'] == _scheduler.Dispatch_Service[harness.adapter.conn_type]
        assert int(job['minutes']) == 5
        assert int(job[SchedulerLink.Conn_ID]) == int(conn.id)
        assert job[SchedulerLink.Conn_Type] == harness.adapter.conn_type
        assert job[SchedulerLink.Kind] == schedule_id

        # The job's extra data carries the connection's identity and the full schedule
        extra = loads(job['extra'])

        assert int(extra[_scheduler.Extra_Conn_ID]) == int(conn.id)
        assert extra[_scheduler.Extra_Conn_Name] == conn.name
        assert extra[_scheduler.Extra_Conn_Type] == harness.adapter.conn_type
        assert extra[_scheduler.Extra_Schedule]['directory'] == directory

        # The connection's own list mirrors the job
        schedule = harness.client.require_schedule(conn.id, schedule_id)

        assert schedule['name'] == 'invoices.hourly'
        assert schedule['directory'] == directory
        assert schedule['pattern'] == _scheduler.Default_Pattern
        assert schedule['run_every'] == 5
        assert schedule['run_unit'] == _scheduler.Unit.Minutes
        assert int(schedule['job_id']) == int(job_id)

# ################################################################################################################################

    def test_edit_schedule_updates_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'reports.daily', directory)

        schedule_id = response['id']
        job_id = response['job_id']

        # Change the interval and the directory through the schedule's edit
        _ = harness.client.edit_schedule(conn.id, schedule_id, 'reports.daily', other_directory,
            run_every=3, run_unit=_scheduler.Unit.Hours)

        # It is still the same job, just with a new interval and extra data
        job = harness.job_of(conn, 'reports.daily')

        assert int(job['id']) == int(job_id)
        assert int(job['hours']) == 3
        assert int(job['minutes']) == 0

        extra = loads(job['extra'])
        assert extra[_scheduler.Extra_Schedule]['directory'] == other_directory

        # The connection's own list reflects the edit as well
        schedule = harness.client.require_schedule(conn.id, schedule_id)

        assert schedule['directory'] == other_directory
        assert schedule['run_every'] == 3
        assert schedule['run_unit'] == _scheduler.Unit.Hours

# ################################################################################################################################

    def test_job_edit_syncs_back_to_schedule(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'sync.back', directory)

        schedule_id = response['id']
        job_id = response['job_id']

        job_name = harness.client.job_name(conn.name, 'sync.back')
        job = harness.client.get_job(job_name)

        # Edit the job directly, the way the scheduler UI does it - changing its interval
        harness.client.edit_job(job_id, job_name, minutes=7, extra=job['extra'])

        # The connection's schedule entry now shows the job's new interval
        schedule = harness.client.require_schedule(conn.id, schedule_id)

        assert schedule['run_every'] == 7
        assert schedule['run_unit'] == _scheduler.Unit.Minutes
        assert int(schedule['job_id']) == int(job_id)

# ################################################################################################################################

    def test_job_delete_removes_schedule_entry(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'to.be.deleted', directory)

        schedule_id = response['id']
        job_id = response['job_id']

        # Delete the job directly, the way the scheduler UI does it
        harness.client.delete_job(job_id)

        # The schedule entry is gone from the connection as well
        assert harness.client.get_schedule(conn.id, schedule_id) is None

# ################################################################################################################################

    def test_delete_schedule_deletes_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'short.lived', directory)
        schedule_id = response['id']

        assert harness.job_exists(conn, 'short.lived')

        harness.client.delete_schedule(conn.id, schedule_id)

        # Both the job and the entry are gone
        assert not harness.job_exists(conn, 'short.lived')
        assert harness.client.get_schedule(conn.id, schedule_id) is None

# ################################################################################################################################

    def test_conn_delete_removes_jobs(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'first.one', first_directory)
        _ = harness.client.create_schedule(conn.id, 'second.one', second_directory)

        assert harness.job_exists(conn, 'first.one')
        assert harness.job_exists(conn, 'second.one')

        # Deleting the connection removes the jobs of all its schedules
        harness.client.delete_conn(conn.id)

        assert not harness.job_exists(conn, 'first.one')
        assert not harness.job_exists(conn, 'second.one')

# ################################################################################################################################

    def test_conn_rename_renames_jobs(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'renamed.along', directory)

        new_conn_name = harness.adapter.new_conn_name()
        harness.client.edit_conn(conn.id, new_conn_name)

        old_job_name = harness.client.job_name(conn.name, 'renamed.along')
        new_job_name = harness.client.job_name(new_conn_name, 'renamed.along')

        job_names = harness.client.get_job_names()

        # The job now follows the connection's new name ..
        assert new_job_name in job_names
        assert old_job_name not in job_names

        # .. and its extra data carries the new name as well.
        job = harness.client.get_job(new_job_name)
        extra = loads(job['extra'])

        assert extra[_scheduler.Extra_Conn_Name] == new_conn_name

# ################################################################################################################################

    def test_conn_edit_without_rename_preserves_schedules(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'kept.across.edit', directory)
        schedule_id = response['id']

        # An edit that changes nothing about the name must leave the schedules alone
        harness.client.edit_conn(conn.id, conn.name)

        schedule = harness.client.require_schedule(conn.id, schedule_id)

        assert schedule['directory'] == directory
        assert harness.job_exists(conn, 'kept.across.edit')

# ################################################################################################################################

    def test_inactive_schedule_creates_inactive_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        response = harness.client.create_schedule(conn.id, 'switched.off', directory, is_active=False)

        job = harness.job_of(conn, 'switched.off')
        assert not job['is_active']

        schedule = harness.client.require_schedule(conn.id, response['id'])
        assert not schedule['is_active']

# ################################################################################################################################

    def test_run_unit_days_lands_in_the_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'every.two.days', directory,
            run_every=2, run_unit=_scheduler.Unit.Days)

        job = harness.job_of(conn, 'every.two.days')

        assert int(job['days']) == 2
        assert int(job['minutes']) == 0
        assert int(job['hours']) == 0

# ################################################################################################################################

    def test_run_unit_weeks_lands_in_the_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'every.three.weeks', directory,
            run_every=3, run_unit=_scheduler.Unit.Weeks)

        job = harness.job_of(conn, 'every.three.weeks')

        assert int(job['weeks']) == 3
        assert int(job['days']) == 0
        assert int(job['minutes']) == 0

# ################################################################################################################################

    def test_two_schedules_of_one_conn_are_independent(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        first_directory = harness.make_directory()
        second_directory = harness.make_directory()
        third_directory = harness.make_directory()

        first = harness.client.create_schedule(conn.id, 'invoices.morning', first_directory)
        second = harness.client.create_schedule(conn.id, 'invoices.evening', second_directory)

        # Editing one of them must leave the other exactly as it was
        _ = harness.client.edit_schedule(conn.id, first['id'], 'invoices.morning', third_directory, run_every=9)

        untouched = harness.client.require_schedule(conn.id, second['id'])

        assert untouched['directory'] == second_directory
        assert untouched['run_every'] == 5
        assert int(untouched['job_id']) == int(second['job_id'])

        edited = harness.client.require_schedule(conn.id, first['id'])

        assert edited['directory'] == third_directory
        assert edited['run_every'] == 9

        # Both jobs are still there, each with its own interval
        first_job = harness.job_of(conn, 'invoices.morning')
        second_job = harness.job_of(conn, 'invoices.evening')

        assert int(first_job['minutes']) == 9
        assert int(second_job['minutes']) == 5

# ################################################################################################################################

    def test_schedule_start_date_reaches_the_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'starts.later', directory)

        job = harness.job_of(conn, 'starts.later')

        # The date the schedule was given is the date the job starts on, whatever formatting it took on
        assert Start_Date_Never[:10] in job['start_date']

# ################################################################################################################################
# ################################################################################################################################
