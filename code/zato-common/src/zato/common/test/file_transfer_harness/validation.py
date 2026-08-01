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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# A connection ID that no connection ever carries
_missing_conn_id = 987654321

# ################################################################################################################################
# ################################################################################################################################

class ValidationTests(FileTransferScheduleTestBase):
    """ A schedule that could not run is refused when it is created rather than when it fires,
    and a refused schedule leaves neither an entry nor a job behind.
    """

    def test_duplicate_schedule_name_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()

        _ = harness.client.create_schedule(conn.id, 'only.once', directory)

        with pytest.raises(Exception, match='already exists'):
            _ = harness.client.create_schedule(conn.id, 'only.once', other_directory)

        # There is still just the one schedule
        schedules = harness.client.get_schedules(conn.id)
        assert len(schedules) == 1

# ################################################################################################################################

    def test_marker_mode_without_suffix_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='Marker suffix'):
            _ = harness.client.create_schedule(conn.id, 'no.marker.suffix', directory,
                ready_how=_scheduler.ReadyHow.Marker, marker_suffix='')

        # Neither a schedule nor a job were created
        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'no.marker.suffix')

# ################################################################################################################################

    def test_move_without_destination_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='Move directory'):
            _ = harness.client.create_schedule(conn.id, 'nowhere.to.move', directory,
                on_success=_scheduler.OnSuccess.Move, move_directory='')

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'nowhere.to.move')

# ################################################################################################################################

    def test_run_every_below_one_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='Run-every'):
            _ = harness.client.create_schedule(conn.id, 'never.runs', directory, run_every=0)

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'never.runs')

# ################################################################################################################################

    def test_unknown_run_unit_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='Run unit'):
            _ = harness.client.create_schedule(conn.id, 'unknown.unit', directory, run_unit='fortnights')

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'unknown.unit')

# ################################################################################################################################

    def test_unknown_ready_how_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='Ready-how'):
            _ = harness.client.create_schedule(conn.id, 'unknown.readiness', directory, ready_how='whenever')

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'unknown.readiness')

# ################################################################################################################################

    def test_unknown_on_success_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='On-success'):
            _ = harness.client.create_schedule(conn.id, 'unknown.outcome', directory, on_success='archive')

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'unknown.outcome')

# ################################################################################################################################

    def test_unknown_target_service_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='does not exist'):
            _ = harness.client.create_schedule(conn.id, 'unknown.service', directory,
                service='file-transfer-scheduler-test.service-that-was-never-deployed')

        assert harness.client.get_schedules(conn.id) == []
        assert not harness.job_exists(conn, 'unknown.service')

# ################################################################################################################################

    def test_missing_conn_is_rejected(self, harness:'Harness') -> 'None':

        directory = harness.make_directory()

        with pytest.raises(Exception, match='does not exist'):
            _ = harness.client.create_schedule(_missing_conn_id, 'no.such.conn', directory)

# ################################################################################################################################

    def test_conn_of_another_type_is_rejected(self, harness:'Harness') -> 'None':

        name = harness.adapter.new_conn_name()
        conn_id = harness.client.create_foreign_conn(name)

        directory = harness.make_directory()

        with pytest.raises(Exception, match='is not an SFTP or SMB connection'):
            _ = harness.client.create_schedule(conn_id, 'wrong.kind.of.conn', directory)

# ################################################################################################################################

    def test_edit_of_missing_schedule_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()

        with pytest.raises(Exception, match='does not exist'):
            _ = harness.client.edit_schedule(conn.id, 'never.created', 'never.created', directory)

# ################################################################################################################################

    def test_delete_of_missing_schedule_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()

        with pytest.raises(Exception, match='does not exist'):
            harness.client.delete_schedule(conn.id, 'never.created')

# ################################################################################################################################

    def test_rename_onto_another_schedule_is_rejected(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        first_directory = harness.make_directory()
        second_directory = harness.make_directory()

        first = harness.client.create_schedule(conn.id, 'invoices.morning', first_directory)
        _ = harness.client.create_schedule(conn.id, 'invoices.evening', second_directory)

        # Renaming the first one onto the second one's name must be refused
        with pytest.raises(Exception, match='already exists'):
            _ = harness.client.edit_schedule(conn.id, first['id'], 'invoices.evening', first_directory)

        # Both are still there under their own names
        schedules = harness.client.get_schedules(conn.id)
        assert len(schedules) == 2

        unchanged = harness.client.require_schedule(conn.id, first['id'])
        assert unchanged['name'] == 'invoices.morning'

# ################################################################################################################################

    def test_edit_keeping_its_own_name_is_accepted(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        other_directory = harness.make_directory()

        created = harness.client.create_schedule(conn.id, 'invoices.morning', directory)

        # A schedule keeping the name it already has is not a collision with itself
        _ = harness.client.edit_schedule(conn.id, created['id'], 'invoices.morning', other_directory)

        schedule = harness.client.require_schedule(conn.id, created['id'])
        assert schedule['directory'] == other_directory

# ################################################################################################################################
# ################################################################################################################################
