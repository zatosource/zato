# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The local SSH server - it starts, accepts an sftp login with its client key, records its pid,
# can be stopped by a process that did not start it, and its stop leaves nothing behind.

# stdlib
import os
from subprocess import run as subprocess_run
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.sftp_local import has_sshd, LocalSFTPServer
from zato.common.util.local_server import is_accepting_connections, is_expected_process
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

# How long the server may take to record its pid, in seconds
_pid_file_timeout = 5.0

# How long to sleep between two looks at the pid file, in seconds
_pid_file_poll_interval = 0.1

# How long one sftp session may take, in seconds
_sftp_timeout = 30

pytestmark = pytest.mark.skipif(not has_sshd(), reason='No SSH server binary on this machine')

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_pid(server:'LocalSFTPServer') -> 'int':
    """ Waits until the server records its pid and returns it.
    """
    deadline = monotonic() + _pid_file_timeout

    while monotonic() < deadline:
        if pid := server.read_pid():
            return pid
        sleep(_pid_file_poll_interval)

    raise Exception(f'No pid file appeared in {server.pid_file_path}')

# ################################################################################################################################

def _run_sftp(server:'LocalSFTPServer', commands:'str') -> 'str':
    """ Runs one batch of sftp commands with the server's client key and returns what they printed.
    """
    command = [
        'sftp',
        '-i', server.client_key_path,
        '-o', 'IdentitiesOnly=yes',
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-P', str(server.port),
        '-b', '-',
        f'{server.username}@{server.host}',
    ]

    result = subprocess_run(command, input=commands, capture_output=True, text=True, timeout=_sftp_timeout)

    assert result.returncode == 0, f'sftp failed -> {result.stderr}'

    out = result.stdout
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLocalSFTPServer:

    def test_start_login_and_stop(self, tmp_path:'Path') -> 'None':

        base_dir = str(tmp_path / 'sshd')
        port = get_free_port()

        server = LocalSFTPServer(base_dir, port)
        server.start()

        try:

            # The server records its pid, and that pid is the server running this very configuration ..
            pid = _wait_for_pid(server)
            assert is_expected_process(pid, server.config_path)
            assert server.is_running()

            # .. it accepts a login with the client key and serves this machine's files ..
            files_dir = tmp_path / 'files'
            files_dir.mkdir()

            local_file = tmp_path / 'invoice.csv'
            _ = local_file.write_text('invoice_id,customer,amount\nINV-1001,John Smith,120.50\n')

            _ = _run_sftp(server, f'put {local_file} {files_dir}/invoice.csv\n')

            uploaded = files_dir / 'invoice.csv'
            assert uploaded.read_text() == local_file.read_text()

        finally:
            server.stop()

        # .. and once stopped, nothing listens, the process is gone and so is everything it used.
        assert not is_accepting_connections(port)
        assert not is_expected_process(pid, server.config_path)
        assert not os.path.exists(base_dir)

# ################################################################################################################################

    def test_another_process_stops_it_through_its_pid_file(self, tmp_path:'Path') -> 'None':

        base_dir = str(tmp_path / 'sshd')
        port = get_free_port()

        # One instance starts the server ..
        first = LocalSFTPServer(base_dir, port)
        first.start()

        try:
            pid = _wait_for_pid(first)

            # .. another one, with no process of its own, recognizes it ..
            second = LocalSFTPServer(base_dir, port)
            assert second.sshd is None
            assert second.is_running()

            # .. and stops it through the pid file.
            second.stop_process()

            assert not is_expected_process(pid, first.config_path)
            assert not is_accepting_connections(port)

        finally:
            first.stop()

# ################################################################################################################################

    def test_prepare_keeps_existing_keys(self, tmp_path:'Path') -> 'None':

        base_dir = str(tmp_path / 'sshd')

        server = LocalSFTPServer(base_dir, get_free_port())
        server.prepare()

        with open(server.client_key_path, encoding='utf8') as key_file:
            first_key = key_file.read()

        # A second preparation, e.g. on a different port, keeps the keys ..
        server.port = get_free_port()
        server.prepare()

        with open(server.client_key_path, encoding='utf8') as key_file:
            second_key = key_file.read()

        assert first_key == second_key

        # .. while the configuration follows the new port.
        with open(server.config_path, encoding='utf8') as config_file:
            config = config_file.read()

        assert f'Port {server.port}\n' in config

# ################################################################################################################################
# ################################################################################################################################
