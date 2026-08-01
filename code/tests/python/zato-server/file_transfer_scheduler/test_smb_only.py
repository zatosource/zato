# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.test.file_transfer_harness.smb_adapter import SMBAdapter

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

_move_directory = _scheduler.Default_Move_Directory

# How long a schedule that fires by the hour leaves its pooled connection sitting idle, in seconds -
# short enough for a test to wait it out, long enough for a session to be more than moments old.
_idle_time = 10

# A secret that the server will not accept
_secret_that_is_refused = 'Not.The.Secret.The.Server.Knows'

# ################################################################################################################################
# ################################################################################################################################

class TestSMBOnly(FileTransferScheduleTestBase):
    """ Behaviour that only an SMB connection has, so there is nothing to share with another protocol.
    """

    @pytest.fixture()
    def adapter(self, smb_adapter:'SMBAdapter') -> 'SMBAdapter':
        return smb_adapter

# ################################################################################################################################

    @pytest.mark.slow
    def test_a_run_after_the_connection_sat_idle(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('idle.session')

        harness.write(directory, 'first.txt', 'Delivered by the run that opened the session')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['first.txt']

        # A schedule firing by the hour leaves its pooled connection idle in between
        time.sleep(_idle_time)

        harness.write(directory, 'second.txt', 'Delivered by the run that found the session idle')
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['first.txt', 'second.txt']
        harness.assert_names(harness.move_directory_of(directory), ['first.txt', 'second.txt'])

# ################################################################################################################################

    def test_a_directory_that_does_not_name_its_share(self, harness:'Harness', adapter:'SMBAdapter') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('no.share.named')

        harness.write(directory, 'invoice.txt', 'A payload behind a directory that names no share')

        # The share's name is what a remote path starts with, and this one starts without it
        share_prefix = adapter.server.share_name + '/'
        without_the_share = directory[len(share_prefix):]

        schedule = harness.create_schedule(conn, schedule_name, without_the_share)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # A directory nobody can resolve delivers nothing and takes nothing away
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################

    def test_a_directory_that_is_a_file(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('directory.is.a.file')

        harness.write(directory, 'invoice.txt', 'A payload that is a file rather than a directory')

        # The schedule is pointed at the file itself rather than at the directory holding it
        as_a_directory = harness.adapter.remote_join(directory, 'invoice.txt')

        schedule = harness.create_schedule(conn, schedule_name, as_a_directory)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################

    def test_a_run_with_a_secret_the_server_refuses(self, harness:'Harness') -> 'None':

        conn = harness.new_conn(secret=_secret_that_is_refused)

        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('secret.refused')

        harness.write(directory, 'invoice.txt', 'A payload nothing can authenticate for')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # Nothing went through and the file is exactly where it was ..
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

        # .. and once the connection carries the secret the server knows, the file goes through.
        harness.client.edit_conn(conn.id, conn.name)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']
        harness.assert_names(harness.move_directory_of(directory), ['invoice.txt'])

# ################################################################################################################################
# ################################################################################################################################
