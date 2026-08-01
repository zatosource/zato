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
from zato.common.test.file_transfer_harness.evidence import Failing_File_Token, Service_Fail_Selected, Service_Store_File

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# A file name with a space in it, which is what a person rather than a machine names a report
_name_with_spaces = 'monthly report.csv'

# How deep the nested directory of the nesting test goes
_nesting_names = ['partners', 'northern-europe', 'incoming']

# How many runs a test gives a directory before deciding that whatever is left in it is stuck there.
# One run per file is enough, whichever order the listing brings them in.
_runs_to_settle = 6

# ################################################################################################################################
# ################################################################################################################################

class RobustnessTests(FileTransferScheduleTestBase):
    """ Runs that meet something in the way - a file the target service refuses, a server that went away,
    a name nothing was written to expect.
    """

    def test_a_file_the_service_refuses_does_not_stop_the_others(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('service.refuses.one')

        # The service refuses the one file whose name says so and takes all the others
        expected:'strlist' = []

        harness.write(directory, f'invoice-{Failing_File_Token}.txt', 'The one file the service will not take')

        for index in range(4):
            file_name = f'healthy-{index:03d}.txt'
            harness.write(directory, file_name, f'Payload of {file_name}')
            expected.append(file_name)

        expected = sorted(expected)

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Fail_Selected)
        harness.run(conn, schedule)

        # The healthy files had nothing to do with the refused one and must have gone through
        assert harness.delivered_names(schedule_name) == expected

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='A file that cannot be moved ends the run for the ones behind it')
    def test_a_file_that_cannot_be_moved_does_not_stop_the_others(self, harness:'Harness') -> 'None':

        harness.require('supports_subdirectories')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('move.blocked')

        # Nothing can be moved onto a directory, so this one file will never reach the destination
        destination = harness.make_subdirectory(directory, _move_directory)
        _ = harness.make_subdirectory(destination, 'in-the-way.txt')

        harness.write(directory, 'in-the-way.txt', 'A file whose move cannot go through')

        expected:'strlist' = []

        for index in range(4):
            file_name = f'healthy-{index:03d}.txt'
            harness.write(directory, file_name, f'Payload of {file_name}')
            expected.append(file_name)

        expected = sorted(expected)

        schedule = harness.create_schedule(conn, schedule_name, directory)

        # Whichever order the runs meet the files in, after this many of them the healthy ones
        # have all had their turn unless something is standing in their way run after run.
        for _ in range(_runs_to_settle):
            try:
                harness.run_once(conn, schedule)
            except Exception:
                pass

        delivered = sorted(set(harness.delivered_names(schedule_name)))
        assert delivered == expected

        # The one file that could not be moved is still where it was, ready for another attempt
        assert harness.exists(directory, 'in-the-way.txt')

# ################################################################################################################################

    def test_a_refused_file_is_taken_once_the_service_accepts_it(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('refused.then.taken')

        file_name = f'invoice-{Failing_File_Token}.txt'
        harness.write(directory, file_name, 'A payload the service will take on the second try')

        schedule = harness.create_schedule(conn, schedule_name, directory, service=Service_Fail_Selected)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # Nothing was delivered and the file is still there for a later run ..
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, file_name)

        # .. and once the schedule points at a service that takes it, it goes through.
        schedule_id = schedule['id']

        _ = harness.client.edit_schedule(conn.id, schedule_id, schedule_name, directory,
            service=Service_Store_File)

        schedule = harness.client.require_schedule(conn.id, schedule_id)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == [file_name]
        harness.assert_names(harness.move_directory_of(directory), [file_name])

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='A name with a space in it has no quoting behind it yet')
    def test_a_name_with_spaces_goes_through(self, harness:'Harness') -> 'None':

        harness.require('supports_names_with_spaces')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('names.with.spaces')

        harness.write(directory, _name_with_spaces, 'The figures of the month')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == [_name_with_spaces]
        harness.assert_names(harness.move_directory_of(directory), [_name_with_spaces])

# ################################################################################################################################

    @pytest.mark.xfail(strict=False, reason='A name with a space in it has no quoting behind it yet')
    def test_a_name_with_spaces_does_not_block_the_others(self, harness:'Harness') -> 'None':

        harness.require('supports_names_with_spaces')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('spaces.and.others')

        harness.write(directory, _name_with_spaces, 'The figures of the month')
        harness.write(directory, 'plain.csv', 'A name nothing can trip over')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        for _ in range(_runs_to_settle):
            try:
                harness.run_once(conn, schedule)
            except Exception:
                pass

        # Whatever became of the awkward name, the plain one had no part in it
        assert 'plain.csv' in harness.delivered_names(schedule_name)

# ################################################################################################################################

    def test_a_deeply_nested_directory(self, harness:'Harness') -> 'None':

        harness.require('supports_subdirectories')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('nested')

        nested = directory

        for name in _nesting_names:
            nested = harness.make_subdirectory(nested, name)

        harness.write(nested, 'invoice.txt', 'A payload several directories down')

        schedule = harness.create_schedule(conn, schedule_name, nested)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(harness.move_directory_of(nested), ['invoice.txt'])

# ################################################################################################################################

    def test_a_move_directory_given_in_full(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        destination = harness.make_directory()
        schedule_name = harness.new_schedule_name('destination.in.full')

        harness.write(directory, 'invoice.txt', 'A payload going to a destination of its own')

        # The destination is named in full rather than relative to the directory being polled
        schedule = harness.create_schedule(conn, schedule_name, directory, move_directory=destination)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']

        # The file left the directory it was picked up from and is where it was sent
        assert not harness.exists(directory, 'invoice.txt')
        harness.assert_names(destination, ['invoice.txt'])

# ################################################################################################################################

    def test_a_run_after_the_server_came_back(self, harness:'Harness') -> 'None':

        harness.require('supports_server_restart')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('server.restart')

        harness.write(directory, 'before.txt', 'Delivered before the server went away')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['before.txt']

        # The remote server goes away, taking every session with it, and comes back
        harness.adapter.restart_server()

        harness.write(directory, 'after.txt', 'Delivered once the server was back')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['after.txt', 'before.txt']
        harness.assert_names(harness.move_directory_of(directory), ['after.txt', 'before.txt'])

# ################################################################################################################################

    def test_a_run_while_the_server_is_away(self, harness:'Harness') -> 'None':

        harness.require('supports_server_restart')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('server.away')

        harness.write(directory, 'waiting.txt', 'A payload nothing can reach for now')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        harness.adapter.stop_server()

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass
        finally:
            harness.adapter.start_server()

        # Nothing was delivered while the server was away, and the file survived it
        assert harness.delivered(schedule_name) == []

        harness.write(directory, 'waiting.txt', 'A payload nothing can reach for now')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['waiting.txt']

# ################################################################################################################################

    def test_a_run_after_the_connection_was_edited(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('conn.edited')

        harness.write(directory, 'before.txt', 'Delivered before the connection was edited')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # The connection is saved again with everything it already had, which is what a user does
        # after changing a field the tests do not touch.
        harness.client.edit_conn(conn.id, conn.name, pool_size=2)

        harness.write(directory, 'after.txt', 'Delivered once the connection was saved again')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['after.txt', 'before.txt']

# ################################################################################################################################

    def test_a_run_of_an_inactive_connection(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('conn.inactive')

        harness.write(directory, 'invoice.txt', 'A payload behind a connection that was switched off')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        # The connection is switched off while its schedule stays on
        harness.client.edit_conn(conn.id, conn.name, is_active=False)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # A connection nobody may use delivers nothing, and the file is exactly where it was
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################

    def test_a_schedule_whose_connection_is_gone(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('conn.deleted')

        harness.write(directory, 'invoice.txt', 'A payload whose connection is no longer there')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        harness.client.delete_conn(conn.id)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # Nothing was delivered and the file survived the connection it came through
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################
# ################################################################################################################################
