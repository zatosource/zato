# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from getpass import getuser
from logging import getLogger
from shutil import rmtree
from subprocess import PIPE, Popen, run as subprocess_run

# Zato
from zato.common.util.local_server import is_accepting_connections, is_expected_process, Local_Host, read_pid_file, \
    start_logged_process, stop_pid, stop_popen, wait_until_accepting_connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Where the SSH server binary is expected to be found
SSHD_Binary = '/usr/sbin/sshd'

# How long to wait for the server to start accepting connections, in seconds
_start_timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

def has_sshd() -> 'bool':
    """ Whether the SSH server binary is installed on this machine.
    """
    out = os.path.exists(SSHD_Binary)
    return out

# ################################################################################################################################
# ################################################################################################################################

class LocalSFTPServer:
    """ A private, non-root SSH server with an SFTP subsystem, listening on 127.0.0.1 only and accepting
    key-based logins of the current user. Everything it uses lives in its base directory.
    """
    def __init__(self, base_dir:'str', port:'int') -> 'None':

        self.base_dir = base_dir

        # Connection details for clients
        self.host = Local_Host
        self.port = port
        self.username = getuser()

        # Paths to the server's own files
        self.host_key_path = os.path.join(self.base_dir, 'host_key')
        self.config_path = os.path.join(self.base_dir, 'sshd_config')
        self.authorized_keys_path = os.path.join(self.base_dir, 'authorized_keys')
        self.pid_file_path = os.path.join(self.base_dir, 'sshd.pid')

        # The key clients log in with
        self.client_key_path = os.path.join(self.base_dir, 'client_key')

        # Where the server's output goes - nowhere unless a path is set
        self.log_path = ''

        # The server's process, if this very process started it
        self.sshd:'Popen | None' = None

# ################################################################################################################################

    @property
    def ssh_options(self) -> 'str':
        """ Client-side options that make it possible to connect to a freshly generated host key without any prompts.
        """
        out = 'StrictHostKeyChecking=no\nUserKnownHostsFile=/dev/null'

        return out

# ################################################################################################################################

    def get_client_key_paths(self) -> 'strlist':
        """ The private keys whose public halves may log in.
        """
        out = [self.client_key_path]
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

    def _ensure_key(self, path:'str', passphrase:'str'='') -> 'None':
        """ Generates a key pair unless both of its halves are already there.
        """
        public_key_path = path + '.pub'

        if os.path.exists(path):
            if os.path.exists(public_key_path):
                return

        # A half left on its own would make the key generator ask whether to overwrite it.
        for item in (path, public_key_path):
            if os.path.exists(item):
                os.remove(item)

        self.generate_key(path, passphrase)

# ################################################################################################################################

    def ensure_keys(self) -> 'None':
        """ Generates the host key and the client key, unless they exist already.
        """
        self._ensure_key(self.host_key_path)
        self._ensure_key(self.client_key_path)

# ################################################################################################################################

    def write_authorized_keys(self) -> 'None':

        # Collect the public halves of all the client keys ..
        public_keys = []

        for private_key_path in self.get_client_key_paths():
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

    def write_config(self) -> 'None':

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

    def prepare(self) -> 'None':
        """ Builds whatever is missing in the base directory - the keys are kept if they exist,
        while the list of authorized keys and the configuration are always written anew.
        """
        os.makedirs(self.base_dir, exist_ok=True)

        self.ensure_keys()
        self.write_authorized_keys()
        self.write_config()

# ################################################################################################################################

    def read_pid(self) -> 'int':
        """ The pid of the server, as the server itself recorded it, zero if there is none.
        """
        out = read_pid_file(self.pid_file_path)
        return out

# ################################################################################################################################

    def is_running(self) -> 'bool':
        """ Whether a server using this base directory's configuration is alive and accepting connections,
        whichever process started it.
        """
        pid = self.read_pid()

        if not is_expected_process(pid, self.config_path):
            return False

        out = is_accepting_connections(self.port, self.host)
        return out

# ################################################################################################################################

    def start_process(self) -> 'None':

        # The server runs in the foreground, as the current user, with no root or systemd needed.
        command = [SSHD_Binary, '-D', '-e', '-f', self.config_path]
        self.sshd = start_logged_process(command, self.log_path)

        wait_until_accepting_connections(self.port, self.host, _start_timeout, self.sshd)

# ################################################################################################################################

    def stop_process(self) -> 'None':
        """ Stops the server - the process this very process started if there is one,
        otherwise the one the pid file names, provided it still runs this configuration.
        """
        if self.sshd:
            stop_popen(self.sshd)
            self.sshd = None
        else:
            pid = self.read_pid()
            _ = stop_pid(pid, self.config_path)

# ################################################################################################################################

    def start(self) -> 'None':

        # Build everything the server needs ..
        self.prepare()

        # .. and start it, waiting until it accepts connections.
        self.start_process()

        logger.info('Local SSH server started on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def stop(self) -> 'None':

        # Stop the server first ..
        self.stop_process()

        # .. and only then delete everything it used.
        rmtree(self.base_dir, ignore_errors=True)

        logger.info('Local SSH server stopped (%s)', self.base_dir)

# ################################################################################################################################
# ################################################################################################################################
