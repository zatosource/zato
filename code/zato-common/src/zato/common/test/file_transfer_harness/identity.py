# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from threading import Thread

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# Three names a person would read as three different schedules, all of which slug to one id
_names_slugging_alike = ['Invoices Hourly', 'Invoices-Hourly', 'Invoices_Hourly']

# Two names of Greek and Korean letters, neither of which leaves anything behind when slugged
_unicode_names = ['Λογαριασμοί', '송장']

# How many schedules the concurrent create test asks for at the same time
_concurrent_create_count = 4

# What the scheduler's own UI can put on a job and what a schedule edit must not take away
_job_timeout_ms = 90_000

# How far from now the last modification time of a file just written may be, in seconds
_last_modified_tolerance = 600

# A move destination named in full rather than relative to the directory being polled
_destination_in_full = '/tmp/zato-file-transfer-destination-in-full'

# ################################################################################################################################
# ################################################################################################################################

class IdentityTests(FileTransferScheduleTestBase):
    """ How a schedule is named, what its id then is, and what a schedule and its job do to each other's fields.
    """

    def test_names_that_slug_alike_are_told_apart(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        for name in _names_slugging_alike:
            directory = harness.make_directory()
            _ = harness.client.create_schedule(conn.id, name, directory)

        # Three names a person reads as three schedules must be three schedules
        schedules = harness.client.get_schedules(conn.id)
        assert len(schedules) == len(_names_slugging_alike)

# ################################################################################################################################

    def test_names_of_non_ascii_letters_are_told_apart(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        for name in _unicode_names:
            directory = harness.make_directory()
            _ = harness.client.create_schedule(conn.id, name, directory)

        schedules = harness.client.get_schedules(conn.id)

        assert len(schedules) == len(_unicode_names)

        # Neither of them may have ended up without an id of its own
        ids = set()

        for schedule in schedules:
            assert schedule['id']
            ids.add(schedule['id'])

        assert len(ids) == len(_unicode_names)

# ################################################################################################################################

    def test_a_renamed_schedule_frees_its_old_name(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        created = harness.client.create_schedule(conn.id, 'invoices.hourly', first_directory)

        # The schedule is renamed, so nothing carries the old name any more ..
        _ = harness.client.edit_schedule(conn.id, created['id'], 'invoices.daily', first_directory)

        # .. and a new schedule is free to take it.
        _ = harness.client.create_schedule(conn.id, 'invoices.hourly', second_directory)

        schedules = harness.client.get_schedules(conn.id)
        assert len(schedules) == 2

        names = set()

        for schedule in schedules:
            names.add(schedule['name'])

        assert names == {'invoices.hourly', 'invoices.daily'}

# ################################################################################################################################

    def test_a_renamed_schedule_renames_its_job(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        created = harness.client.create_schedule(conn.id, 'invoices.hourly', directory)

        _ = harness.client.edit_schedule(conn.id, created['id'], 'invoices.daily', directory)

        job_names = harness.client.get_job_names()

        old_job_name = harness.client.job_name(conn.name, 'invoices.hourly')
        new_job_name = harness.client.job_name(conn.name, 'invoices.daily')

        assert new_job_name in job_names
        assert old_job_name not in job_names

# ################################################################################################################################

    def test_two_schedules_of_one_conn_have_their_own_jobs(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        # A schedule named with a dot inside it must not be mistaken for another one
        first = harness.client.create_schedule(conn.id, 'invoices.hourly', first_directory)
        second = harness.client.create_schedule(conn.id, 'invoices.hourly.retry', second_directory)

        assert first['job_id'] != second['job_id']

        assert harness.job_exists(conn, 'invoices.hourly')
        assert harness.job_exists(conn, 'invoices.hourly.retry')

# ################################################################################################################################

    def test_a_job_name_already_taken_is_refused(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        # A job carrying the conventional name is already there before the schedule is created
        job_name = harness.client.job_name(conn.name, 'already.taken')
        _ = harness.client.create_job(job_name)

        with pytest.raises(Exception):
            _ = harness.client.create_schedule(conn.id, 'already.taken', directory)

        # The schedule that could not have a job of its own was not left behind either
        assert harness.client.get_schedule_by_name(conn.id, 'already.taken') is None

# ################################################################################################################################

    def test_a_schedule_edit_keeps_what_the_job_carries(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()

        created = harness.client.create_schedule(conn.id, 'timeout.of.its.own', directory)

        job_name = harness.client.job_name(conn.name, 'timeout.of.its.own')
        job = harness.client.get_job(job_name)

        # The scheduler's own UI puts a run timeout on the job ..
        harness.client.edit_job(created['job_id'], job_name,
            minutes=5, extra=job['extra'], max_execution_time_ms=_job_timeout_ms)

        # .. and an edit of the schedule, which says nothing about timeouts, must leave it alone.
        _ = harness.client.edit_schedule(conn.id, created['id'], 'timeout.of.its.own', other_directory)

        job = harness.client.get_job(job_name)
        assert int(job['max_execution_time_ms']) == _job_timeout_ms

# ################################################################################################################################

    def test_a_job_switched_off_stays_off(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()

        created = harness.client.create_schedule(conn.id, 'switched.off.by.hand', directory)

        job_name = harness.client.job_name(conn.name, 'switched.off.by.hand')
        job = harness.client.get_job(job_name)

        # Somebody switches the job off in the scheduler's own UI ..
        harness.client.edit_job(created['job_id'], job_name, minutes=5, extra=job['extra'], is_active=False)

        # .. and an unrelated edit of the schedule must not switch it back on.
        _ = harness.client.edit_schedule(conn.id, created['id'], 'switched.off.by.hand', other_directory)

        job = harness.client.get_job(job_name)
        assert not job['is_active']

# ################################################################################################################################

    def test_schedules_created_at_the_same_time_all_survive(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        errors:'anylist' = []
        threads:'anylist' = []

        def _create_one(index:'int') -> 'None':
            try:
                directory = harness.make_directory()
                _ = harness.client.create_schedule(conn.id, f'at.once.{index}', directory)
            except Exception as e:
                errors.append(e)

        for index in range(_concurrent_create_count):
            thread = Thread(target=_create_one, args=(index,), name='zato-test-schedule-create', daemon=True)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert errors == []

        # Every one of them asked for a schedule of its own and every one of them must have got it
        schedules = harness.client.get_schedules(conn.id)
        assert len(schedules) == _concurrent_create_count

# ################################################################################################################################

    def test_a_destination_pointing_at_the_directory_is_refused(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        # A destination of a single dot is the directory being polled, so every file would be found again
        with pytest.raises(Exception):
            _ = harness.client.create_schedule(conn.id, 'destination.is.itself', directory, move_directory='.')

# ################################################################################################################################

    def test_a_destination_pointing_upwards_is_refused(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception):
            _ = harness.client.create_schedule(conn.id, 'destination.is.upwards', directory, move_directory='..')

# ################################################################################################################################

    def test_a_destination_named_in_full_is_refused(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        # A destination is always relative to the directory being polled, so a path of its own
        # names nowhere the schedule could put anything
        with pytest.raises(Exception):
            _ = harness.client.create_schedule(conn.id, 'destination.in.full', directory,
                move_directory=_destination_in_full)

# ################################################################################################################################

    def test_the_size_of_an_item_is_the_size_of_its_payload(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('size.of.the.item')

        payload = 'A payload whose length the listing and the download must agree on'
        harness.write(directory, 'invoice.txt', payload)

        # Marker mode runs no stability check, so the listing and the download are all there is
        schedule = harness.create_schedule(conn, schedule_name, directory,
            ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_scheduler.Default_Marker_Suffix)

        harness.write(directory, 'invoice.txt' + _scheduler.Default_Marker_Suffix, '')
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)

        assert len(entries) == 1
        assert entries[0]['size'] == len(payload)
        assert entries[0]['data_length'] == len(payload)

# ################################################################################################################################

    def test_the_last_modification_time_reaches_the_service(self, harness:'Harness') -> 'None':

        harness.require('preserves_last_modified')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('last.modified')

        harness.write(directory, 'invoice.txt', 'A payload written just now')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        entries = harness.delivered(schedule_name)
        assert len(entries) == 1

        last_modified = entries[0]['last_modified']
        assert last_modified

        # The file was written moments ago, so its modification time must say so
        parsed = datetime.fromisoformat(last_modified)

        # A protocol that reports a modification time without a timezone reports it in the one
        # the remote side keeps, which for a test server on this machine is this machine's own.
        if parsed.tzinfo is None:
            parsed = parsed.astimezone()

        now = datetime.now(timezone.utc)
        distance = abs(now - parsed)

        assert distance < timedelta(seconds=_last_modified_tolerance)

# ################################################################################################################################
# ################################################################################################################################
