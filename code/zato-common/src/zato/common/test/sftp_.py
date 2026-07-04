# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
from getpass import getuser
from logging import getLogger
from shutil import rmtree
from subprocess import PIPE, Popen, run as subprocess_run
from tempfile import mkdtemp
from time import sleep

# Zato
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Where the SSH server binary is expected to be found
_sshd_binary = '/usr/sbin/sshd'

# How long to wait for the server to start accepting connections, in seconds
_start_timeout = 10.0

# How long to sleep between connection attempts while waiting for the server, in seconds
_start_sleep_time = 0.1

# The passphrase protecting the encrypted client key - it is used as the connection's password in tests
Default_Key_Passphrase = 'Test.SFTP.Passphrase.1'

# ################################################################################################################################
# ################################################################################################################################

class SFTPTestServer:
    """ Starts a private, non-root SSH server with an SFTP subsystem on a random port for use in tests.
    """
    def __init__(self) -> 'None':

        # Everything the server needs lives in this temporary directory
        self.base_dir = mkdtemp(prefix='zato-test-sftp-')

        # A directory for the remote files that tests operate on, always through absolute paths
        self.files_dir = os.path.join(self.base_dir, 'files')
        os.mkdir(self.files_dir)

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()
        self.username = getuser()

        # The passphrase of the encrypted client key
        self.password = Default_Key_Passphrase

        # Paths to the server's own files
        self.host_key_path = os.path.join(self.base_dir, 'host_key')
        self.config_path = os.path.join(self.base_dir, 'sshd_config')
        self.authorized_keys_path = os.path.join(self.base_dir, 'authorized_keys')
        self.pid_file_path = os.path.join(self.base_dir, 'sshd.pid')

        # Paths to client keys - the encrypted one is protected with self.password
        self.client_key_path = os.path.join(self.base_dir, 'client_key')
        self.client_key_encrypted_path = os.path.join(self.base_dir, 'client_key_encrypted')

        # The server's process, populated in .start
        self.sshd = None # type: Popen | None

# ################################################################################################################################

    @property
    def ssh_options(self) -> 'str':
        """ Client-side options that make it possible to connect to a freshly generated host key without any prompts.
        """
        out = 'StrictHostKeyChecking=no\nUserKnownHostsFile=/dev/null'

        return out

# ################################################################################################################################

    def generate_key(self, path:'str', passphrase:'str'='') -> 'None':
        """ Generates a new SSH key pair under the given path.
        """
        command = ['ssh-keygen', '-q', '-t', 'ed25519', '-f', path, '-N', passphrase]
        result = subprocess_run(command, stdout=PIPE, stderr=PIPE)

        if result.returncode != 0:
            stderr = result.stderr.decode('utf8')
            raise Exception('Could not generate an SSH key under `{}` -> `{}`'.format(path, stderr))

# ################################################################################################################################

    def _write_authorized_keys(self) -> 'None':

        # Collect the public halves of both client keys ..
        public_keys = []

        for private_key_path in [self.client_key_path, self.client_key_encrypted_path]:
            public_key_path = private_key_path + '.pub'
            with open(public_key_path, encoding='utf8') as public_key_file:
                public_keys.append(public_key_file.read().strip())

        # .. write them all out ..
        data = '\n'.join(public_keys) + '\n'

        with open(self.authorized_keys_path, 'w', encoding='utf8') as authorized_keys_file:
            _ = authorized_keys_file.write(data)

        # .. and make sure the file has the permissions the server expects.
        os.chmod(self.authorized_keys_path, 0o600)

# ################################################################################################################################

    def _write_config(self) -> 'None':

        # The server accepts only key-based logins from the current user,
        # listening on the loopback interface only.
        config_lines = [
            'Port {}'.format(self.port),
            'ListenAddress {}'.format(self.host),
            'HostKey {}'.format(self.host_key_path),
            'PidFile {}'.format(self.pid_file_path),
            'AuthorizedKeysFile {}'.format(self.authorized_keys_path),
            'StrictModes no',
            'UsePAM no',
            'UseDNS no',
            'PasswordAuthentication no',
            'KbdInteractiveAuthentication no',
            'PubkeyAuthentication yes',
            'Subsystem sftp internal-sftp',
            'LogLevel INFO',
        ]

        data = '\n'.join(config_lines) + '\n'

        with open(self.config_path, 'w', encoding='utf8') as config_file:
            _ = config_file.write(data)

# ################################################################################################################################

    def _wait_until_accepting_connections(self) -> 'None':

        # Keep trying until the server accepts connections or we run out of time
        attempts = int(_start_timeout / _start_sleep_time)

        for _ in range(attempts):
            try:
                with socket.create_connection((self.host, self.port), timeout=1.0):
                    return
            except OSError:
                sleep(_start_sleep_time)

        # If we are here, the server never came up
        raise Exception('SSH server did not start within {}s on {}:{}'.format(_start_timeout, self.host, self.port))

# ################################################################################################################################

    def start(self) -> 'None':

        # Generate the host key ..
        self.generate_key(self.host_key_path)

        # .. generate both client keys, one of which is protected with a passphrase ..
        self.generate_key(self.client_key_path)
        self.generate_key(self.client_key_encrypted_path, self.password)

        # .. let the server know that both client keys can log in ..
        self._write_authorized_keys()

        # .. write out the server's configuration ..
        self._write_config()

        # .. start the server in the foreground, as the current user, with no root or systemd needed ..
        self.sshd = Popen([_sshd_binary, '-D', '-e', '-f', self.config_path], stdout=PIPE, stderr=PIPE)

        # .. and wait until it accepts connections.
        self._wait_until_accepting_connections()

        logger.info('Test SSH server started on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def stop(self) -> 'None':

        # Stop the server first ..
        if self.sshd:
            self.sshd.terminate()
            _ = self.sshd.wait()
            self.sshd = None

        # .. and only then delete everything it used.
        rmtree(self.base_dir, ignore_errors=True)

        logger.info('Test SSH server stopped (%s)', self.base_dir)

# ################################################################################################################################
# ################################################################################################################################
