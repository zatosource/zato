# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.file_transfer_harness.base import FileTransferScheduleTestBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.base import Harness
    from zato.common.test.file_transfer_harness.ftp_adapter import FTPAdapter

# ################################################################################################################################
# ################################################################################################################################

# A secret that the server will not accept
_secret_that_is_refused = 'Not.The.Secret.The.Server.Knows'

# ################################################################################################################################
# ################################################################################################################################

class TestFTPOnly(FileTransferScheduleTestBase):
    """ Behaviour that only an FTP connection has, so there is nothing to share with another protocol.
    """

    @pytest.fixture()
    def adapter(self, ftp_adapter:'FTPAdapter') -> 'FTPAdapter':
        return ftp_adapter

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

        move_directory = harness.move_directory_of(directory)
        harness.assert_names(move_directory, ['invoice.txt'])

# ################################################################################################################################

    def test_a_tls_connection_against_a_plain_server(self, harness:'Harness') -> 'None':

        # The connection insists on TLS but the server it points at speaks plain FTP only.
        conn = harness.new_conn(use_ssl=True)

        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('tls.against.plain')

        harness.write(directory, 'invoice.txt', 'A payload behind a handshake that cannot happen')

        schedule = harness.create_schedule(conn, schedule_name, directory)

        try:
            harness.run_once(conn, schedule)
        except Exception:
            pass

        # The handshake could not happen, so nothing went through and the file is exactly where it was.
        assert harness.delivered(schedule_name) == []
        assert harness.exists(directory, 'invoice.txt')

# ################################################################################################################################
# ################################################################################################################################

class TestFTPSOnly(FileTransferScheduleTestBase):
    """ Behaviour of file transfer schedules over FTPS - a server offering TLS
    on both the control and data connections.
    """

    @pytest.fixture()
    def adapter(self, ftps_adapter:'FTPAdapter') -> 'FTPAdapter':
        return ftps_adapter

# ################################################################################################################################

    def test_a_file_is_delivered_over_tls(self, harness:'Harness') -> 'None':

        conn = harness.new_conn()
        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('ftps.delivery')

        harness.write(directory, 'invoice.txt', 'A payload that travels encrypted end to end')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']

        move_directory = harness.move_directory_of(directory)
        harness.assert_names(move_directory, ['invoice.txt'])

# ################################################################################################################################

    def test_a_plain_connection_against_a_tls_server(self, harness:'Harness') -> 'None':

        # The server offers TLS but does not require it, so a plain connection still goes through.
        conn = harness.new_conn(use_ssl=False)

        directory = harness.make_directory()
        schedule_name = harness.new_schedule_name('plain.against.tls')

        harness.write(directory, 'invoice.txt', 'A payload sent over a plain connection')

        schedule = harness.create_schedule(conn, schedule_name, directory)
        harness.run(conn, schedule)

        assert harness.delivered_names(schedule_name) == ['invoice.txt']

        move_directory = harness.move_directory_of(directory)
        harness.assert_names(move_directory, ['invoice.txt'])

# ################################################################################################################################
# ################################################################################################################################
