# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from shutil import move as shutil_move

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.test.file_transfer_harness.sftp_adapter import SFTPAdapter

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# Where the client key is put out of the way while a test runs without it
_key_backup_suffix = '.taken-away'

# ################################################################################################################################
# ################################################################################################################################

class TestSFTPOnly(FileTransferScheduleTestBase):
    """ Behaviour that only an SFTP connection has, so there is nothing to share with another protocol.
    """

    @pytest.fixture()
    def adapter(self, sftp_adapter:'SFTPAdapter') -> 'SFTPAdapter':
        return sftp_adapter

# ################################################################################################################################

    def test_a_symlink_is_not_a_file_to_pick_up(self, harness:'Harness') -> 'None':

        harness.require('supports_symlinks')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('symlink')

        harness.write(directory, 'invoice.txt', 'The file the link points at')
        harness.make_symlink(directory, 'invoice-link.txt', 'invoice.txt')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        # A listing gives a symlink a type of its own, so only the file itself is picked up
        assert harness.delivered_names(schedule_name) == ['invoice.txt']

        # The link stays exactly where it was, now pointing at nothing
        harness.assert_names(directory, ['invoice-link.txt', _move_directory])

# ################################################################################################################################

    def test_a_connection_checking_host_keys(self, harness:'Harness') -> 'None':

        conn = harness.new_conn(strict_host_key_checking=True)

        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('strict.host.keys')

        harness.write(directory, 'invoice.txt', 'A payload behind a host key nothing has seen before')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        # The test server's host key is generated fresh for each run, so nothing has it on record
        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # Whatever the connection made of the host key, no file went missing over it
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################

    def test_a_run_without_the_private_key(self, harness:'Harness', adapter:'SFTPAdapter') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('no.private.key')

        harness.write(directory, 'invoice.txt', 'A payload nothing can authenticate for')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        key_path = adapter.key_path
        backup_path = key_path + _key_backup_suffix

        # The key the connection authenticates with is taken away between two runs
        _ = shutil_move(key_path, backup_path)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass
        finally:
            _ = shutil_move(backup_path, key_path)

        # The run could not go through and the file is exactly where it was ..
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

        # .. and once the key is back, the file goes through.
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']

# ################################################################################################################################

    def test_deleting_a_file_that_is_not_a_plain_file(self, harness:'Harness') -> 'None':

        harness.require('supports_symlinks')

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('delete.link')

        harness.write(directory, 'invoice.txt', 'The file the link points at')
        harness.make_symlink(directory, 'invoice-link.txt', 'invoice.txt')

        schedule = harness.create_schedule(conn, schedule_name, directory,
            on_success=_scheduler.OnSuccess.Delete, move_directory='')

        harness.run(conn, schedule)

        # The file was deleted and the link, which was never a candidate, is still listed
        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(directory, ['invoice-link.txt'])

# ################################################################################################################################
# ################################################################################################################################
