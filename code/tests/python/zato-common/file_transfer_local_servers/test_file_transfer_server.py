# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo file transfer server, run as a process of its own - plain FTP takes a login, FTPS refuses
# a cleartext one and takes an encrypted one, SMB serves both of its shares to the right password only,
# and SIGTERM ends the process along with its pid file.

# stdlib
import os
import signal
import sys
from ftplib import error_perm, FTP, FTP_TLS
from io import BytesIO
from json import dumps
from ssl import CERT_NONE, create_default_context
from subprocess import Popen
from time import monotonic, sleep

# pytest
import pytest

# smbprotocol
import smbclient
from smbprotocol.exceptions import LogonFailure, SMBAuthenticationError

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.demo.file_transfer_server import Module_Name, write_self_signed_certificate
from zato.common.typing_ import cast_
from zato.common.util.local_server import Local_Host, read_pid_file, reuse_or_pick_port, start_logged_process, \
    stop_popen, wait_until_accepting_connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, intlist

# ################################################################################################################################
# ################################################################################################################################

# How long the process may take to record its pid or to end, in seconds
_process_timeout = 15.0

# How long to sleep between two looks at the process, in seconds
_poll_interval = 0.1

# How long an FTP session may take, in seconds
_ftp_timeout = 30

_ftp_username  = 'initech'
_ftps_username = 'umbrella'
_smb_username  = 'hooli'

_smb_share_names = ['hooli', 'wonka']

_invoice = b'invoice_id,customer,amount\nINV-1001,John Smith,120.50\n'

# ################################################################################################################################
# ################################################################################################################################

def _pick_ports(count:'int') -> 'intlist':

    out:'intlist' = []

    for _ in range(count):
        port = reuse_or_pick_port(0, out)
        out.append(port)

    return out

# ################################################################################################################################

def _build_config(tmp_path:'Path') -> 'anydict':
    """ A configuration with two FTP users, two SMB shares and one SMB user, every password random.
    """
    server_dir = tmp_path / 'server'
    server_dir.mkdir()

    ftp_home = tmp_path / 'ftp' / _ftp_username
    ftp_home.mkdir(parents=True)

    ftps_home = tmp_path / 'ftp' / _ftps_username
    ftps_home.mkdir(parents=True)

    shares = []

    for share_name in _smb_share_names:
        share_path = tmp_path / 'smb' / share_name
        share_path.mkdir(parents=True)
        shares.append({'name': share_name, 'path': str(share_path)})

    ftp_port, ftps_port, smb_port = _pick_ports(3)

    certificate_path = write_self_signed_certificate(str(server_dir))

    out:'anydict' = {
        'host': Local_Host,
        'ftp_port': ftp_port,
        'ftps_port': ftps_port,
        'smb_port': smb_port,
        'certificate_path': certificate_path,
        'pid_file_path': str(server_dir / 'demo-server.pid'),
        'log_file_path': str(server_dir / 'demo-server.log'),
        'ftp_users': [
            {'username': _ftp_username, 'password': CryptoManager.generate_password(to_str=True), 'home': str(ftp_home)},
            {'username': _ftps_username, 'password': CryptoManager.generate_password(to_str=True), 'home': str(ftps_home)},
        ],
        'smb_shares': shares,
        'smb_users': [
            {'username': _smb_username, 'password': CryptoManager.generate_password(to_str=True)},
        ],
    }

    config_path = server_dir / 'demo-server.json'
    _ = config_path.write_text(dumps(out))

    out['config_path'] = str(config_path)

    return out

# ################################################################################################################################

def _wait_for_pid(pid_file_path:'str') -> 'int':

    deadline = monotonic() + _process_timeout

    while monotonic() < deadline:
        if pid := read_pid_file(pid_file_path):
            return pid
        sleep(_poll_interval)

    raise Exception(f'No pid file appeared in {pid_file_path}')

# ################################################################################################################################

def _user_password(config:'anydict', key:'str', username:'str') -> 'str':

    for user in config[key]:
        if user['username'] == username:
            out = user['password']
            break
    else:
        raise Exception(f'No user `{username}` under `{key}`')

    return out

# ################################################################################################################################

def _tls_client() -> 'FTP_TLS':
    """ An FTPS client that accepts the server's self-signed certificate.
    """
    context = create_default_context()
    context.check_hostname = False
    context.verify_mode = CERT_NONE

    out = FTP_TLS(context=context, timeout=_ftp_timeout)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def demo_server(tmp_path:'Path') -> 'any_':
    """ Runs the demo server as a process of its own and yields its configuration with the process added.
    """
    config = _build_config(tmp_path)

    command = [sys.executable, '-m', Module_Name, '--config', config['config_path']]
    process = start_logged_process(command, config['log_file_path'])

    try:
        for key in ('ftp_port', 'ftps_port', 'smb_port'):
            wait_until_accepting_connections(config[key], Local_Host, _process_timeout, process)

        config['process'] = process
        config['pid'] = _wait_for_pid(config['pid_file_path'])

        yield config

    finally:
        stop_popen(process)
        smbclient.reset_connection_cache()

# ################################################################################################################################
# ################################################################################################################################

class TestDemoFileTransferServer:

    def test_plain_ftp_login(self, demo_server:'anydict') -> 'None':

        password = _user_password(demo_server, 'ftp_users', _ftp_username)

        ftp = FTP(timeout=_ftp_timeout)
        _ = ftp.connect(Local_Host, demo_server['ftp_port'])
        _ = ftp.login(_ftp_username, password)

        # The user lands in its own home, where it may write and read back
        buffer = BytesIO(_invoice)
        _ = ftp.storbinary('STOR invoice.csv', buffer)

        received = BytesIO()
        _ = ftp.retrbinary('RETR invoice.csv', received.write)

        _ = ftp.quit()

        assert received.getvalue() == _invoice

# ################################################################################################################################

    def test_ftps_refuses_cleartext_and_takes_tls(self, demo_server:'anydict') -> 'None':

        password = _user_password(demo_server, 'ftp_users', _ftps_username)

        # A login over a cleartext control channel is refused ..
        ftp = FTP(timeout=_ftp_timeout)
        _ = ftp.connect(Local_Host, demo_server['ftps_port'])

        with pytest.raises(error_perm):
            _ = ftp.login(_ftps_username, password)

        ftp.close()

        # .. while one over TLS, with the data channel protected too, goes through.
        ftps = _tls_client()
        _ = ftps.connect(Local_Host, demo_server['ftps_port'])
        _ = ftps.login(_ftps_username, password)
        _ = ftps.prot_p()

        buffer = BytesIO(_invoice)
        _ = ftps.storbinary('STOR invoice.csv', buffer)

        received = BytesIO()
        _ = ftps.retrbinary('RETR invoice.csv', received.write)

        _ = ftps.quit()

        assert received.getvalue() == _invoice

        # The file landed in that user's home directory
        for user in demo_server['ftp_users']:
            if user['username'] == _ftps_username:
                stored_path = os.path.join(user['home'], 'invoice.csv')
                break
        else:
            raise Exception(f'No home for `{_ftps_username}`')

        with open(stored_path, 'rb') as stored_file:
            assert stored_file.read() == _invoice

# ################################################################################################################################

    def test_smb_serves_both_shares(self, demo_server:'anydict') -> 'None':

        port = demo_server['smb_port']
        password = _user_password(demo_server, 'smb_users', _smb_username)

        _ = smbclient.register_session(Local_Host, username=_smb_username, password=password, port=port)

        for share_name in _smb_share_names:

            remote_path = f'\\\\{Local_Host}\\{share_name}\\invoice.csv'

            # The file is created rather than overwritten, the same way the outgoing SMB connection writes.
            with smbclient.open_file(remote_path, mode='xb', port=port) as remote_file:
                _ = remote_file.write(_invoice)

            with smbclient.open_file(remote_path, mode='rb', port=port) as remote_file:
                received = remote_file.read()

            assert received == _invoice

# ################################################################################################################################

    def test_smb_refuses_a_wrong_password(self, demo_server:'anydict') -> 'None':

        port = demo_server['smb_port']
        wrong_password = CryptoManager.generate_password(to_str=True)
        wrong_password = cast_('str', wrong_password)

        with pytest.raises((LogonFailure, SMBAuthenticationError)):
            _ = smbclient.register_session(Local_Host, username=_smb_username, password=wrong_password, port=port)

# ################################################################################################################################

    def test_sigterm_ends_the_process_and_its_pid_file(self, demo_server:'anydict') -> 'None':

        process:'Popen' = demo_server['process']
        pid_file_path = demo_server['pid_file_path']

        assert os.path.exists(pid_file_path)

        process.send_signal(signal.SIGTERM)
        exit_code = process.wait(timeout=_process_timeout)

        assert exit_code == 0
        assert not os.path.exists(pid_file_path)

# ################################################################################################################################
# ################################################################################################################################
