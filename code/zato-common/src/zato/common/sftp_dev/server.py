# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import threading
from logging import Logger, LoggerAdapter, getLogger
from subprocess import DEVNULL, PIPE, Popen, STDOUT, run as subprocess_run
from typing import Literal

# Zato
from zato.common.sftp_dev.constants import Bind_Host, Container_Image, Container_Name_Prefix, Login_User_Public_Key_Names
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strlist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The port the OpenSSH server listens on inside its container
_container_port = 22

# How long a container has to stop before it is killed, in seconds
_stop_timeout = 3

# The host key types each server presents, persisted under its directory so that clients keep recognizing the server
_host_key_types = ('ed25519', 'rsa')

# The timestamp a syslog line begins with, which the log line on screen replaces with its own
_syslog_timestamp = re.compile(r'^[A-Z][a-z]{2} [ \d]\d \d{2}:\d{2}:\d{2} ')

# The OpenSSH server configuration - every login is chrooted into its home directory, and the SFTP subsystem
# logs each operation. An SSH agent with many keys offers all of them before a password, hence the number of attempts.
_sshd_config = """
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key
UseDNS no
PermitRootLogin no
X11Forwarding no
AllowTcpForwarding no
MaxAuthTries 30
LogLevel INFO
Subsystem sftp internal-sftp -l INFO
ForceCommand internal-sftp -l INFO
ChrootDirectory %h
""".lstrip()

# Runs in the container before the OpenSSH server starts. A chrooted SFTP session reaches only the syslog socket
# inside its chroot, and the syslog daemon creates its socket where /dev/log points to, so both the server
# and the session log through that one socket, and the daemon writes every line to the container's output.
_syslog_hook = """#!/bin/sh
set -e
mkdir -p /home/{username}/dev
ln -sf /home/{username}/dev/log /dev/log
syslogd -S -O /proc/1/fd/1
"""

# The name of the hook script in the hooks directory
_syslog_hook_name = 'syslog.sh'

# The permissions of the hook script, which the container runs only if it is executable
_syslog_hook_mode = 0o755

# The command the container runs, in the foreground and logging to syslog rather than to its own output
_sshd_command = ['/usr/sbin/sshd', '-D']

# ################################################################################################################################
# ################################################################################################################################

Auth_Mode = Literal['password', 'publickey']

# ################################################################################################################################
# ################################################################################################################################

class PrefixedLoggerAdapter(LoggerAdapter):
    """ Routes every log line through a single logger while keeping each server's output visually separate.
    """

    def __init__(self, wrapped_logger:'Logger', label:'str') -> 'None':
        super().__init__(wrapped_logger, {'label': label})

    def process(self, msg:'str', kwargs:'dict') -> 'tuple':
        extra = self.extra

        if extra is None:
            label = ''
        else:
            label = extra['label']

        out = '[{}] {}'.format(label, msg)
        return out, kwargs

# ################################################################################################################################
# ################################################################################################################################

def load_login_user_public_keys() -> 'strlist':
    """ The public keys found under the login user's ~/.ssh directory.
    """
    ssh_dir = os.path.expanduser('~/.ssh')
    out:'strlist' = []

    for name in Login_User_Public_Key_Names:
        path = os.path.join(ssh_dir, name)

        if os.path.isfile(path):
            out.append(path)

    return out

# ################################################################################################################################

def ensure_sample_tree(root_dir:'str', sample_directories:'tuple', sample_files:'strdict') -> 'None':
    """ Creates the integration directory layout and sample files under root_dir.
    """
    for relative_directory in sample_directories:
        directory = os.path.join(root_dir, relative_directory)
        os.makedirs(directory, exist_ok=True)

    for relative_path, contents in sample_files.items():
        file_path = os.path.join(root_dir, relative_path)
        parent = os.path.dirname(file_path)

        os.makedirs(parent, exist_ok=True)

        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf8') as sample_file:
                _ = sample_file.write(contents)

# ################################################################################################################################

def pull_image() -> 'None':
    """ Pulls the OpenSSH server image once, so that the servers do not pull it each on their own.
    """
    logger.info('Pulling %s', Container_Image)

    result = subprocess_run(['docker', 'pull', '--quiet', Container_Image], stdout=PIPE, stderr=STDOUT, check=False)

    if result.returncode != 0:
        output = result.stdout.decode('utf8')
        raise Exception(f'Could not pull `{Container_Image}` -> `{output}`')

# ################################################################################################################################
# ################################################################################################################################

class DevSFTPServer:
    """ One OpenSSH SFTP server on a fixed port, run in a container whose output is logged line by line.
    """

    def __init__(
        self,
        port:'int',
        auth_mode:'Auth_Mode',
        username:'str',
        password:'str',
        public_key_paths:'strlist',
        data_dir:'str',
        log_label:'str',
        sample_directories:'tuple',
        sample_files:'strdict',
    ) -> 'None':
        self.port = port
        self.auth_mode:'Auth_Mode' = auth_mode
        self.username = username
        self.password = password
        self.public_key_paths = public_key_paths
        self.data_dir = data_dir
        self.log_label = log_label
        self.sample_directories = sample_directories
        self.sample_files = sample_files

        self.container_name = f'{Container_Name_Prefix}{port}'

        # What the server serves, and what configures it
        self.root_dir = os.path.join(self.data_dir, 'files')
        self.hooks_dir = os.path.join(self.data_dir, 'hooks')
        self.config_path = os.path.join(self.data_dir, 'sshd_config')
        self.users_path = os.path.join(self.data_dir, 'users.conf')

        self.activity_logger = PrefixedLoggerAdapter(logger, self.log_label)

        self._process:'Popen | None' = None
        self._reader:'threading.Thread | None' = None

# ################################################################################################################################

    def _host_key_path(self, key_type:'str') -> 'str':
        out = os.path.join(self.data_dir, f'ssh_host_{key_type}_key')
        return out

# ################################################################################################################################

    def _ensure_host_keys(self) -> 'None':

        for key_type in _host_key_types:

            path = self._host_key_path(key_type)
            if os.path.isfile(path):
                continue

            command = ['ssh-keygen', '-q', '-t', key_type, '-f', path, '-N', '']
            result = subprocess_run(command, stdout=PIPE, stderr=PIPE, check=False)

            if result.returncode != 0:
                stderr = result.stderr.decode('utf8')
                raise Exception(f'Could not generate host key under `{path}` -> `{stderr}`')

            self.activity_logger.info('Generated host key at %s', path)

# ################################################################################################################################

    def _write_configuration(self) -> 'None':

        # The OpenSSH server's own configuration ..
        with open(self.config_path, 'w', encoding='utf8') as config_file:
            _ = config_file.write(_sshd_config)

        # .. the one account, owned by the user running this process, so that what it writes stays accessible here,
        # .. with an empty password locking the account to its public keys ..
        uid = os.getuid()
        gid = os.getgid()

        if self.auth_mode == 'password':
            password = self.password
        else:
            password = ''

        with open(self.users_path, 'w', encoding='utf8') as users_file:
            _ = users_file.write(f'{self.username}:{password}:{uid}:{gid}\n')

        # .. and the hook that makes the server log every operation.
        os.makedirs(self.hooks_dir, exist_ok=True)

        hook_path = os.path.join(self.hooks_dir, _syslog_hook_name)
        hook = _syslog_hook.format(username=self.username)

        with open(hook_path, 'w', encoding='utf8') as hook_file:
            _ = hook_file.write(hook)

        os.chmod(hook_path, _syslog_hook_mode)

# ################################################################################################################################

    def prepare(self) -> 'None':
        os.makedirs(self.root_dir, exist_ok=True)
        ensure_sample_tree(self.root_dir, self.sample_directories, self.sample_files)
        self._ensure_host_keys()
        self._write_configuration()

# ################################################################################################################################

    def _build_command(self) -> 'strlist':

        home = f'/home/{self.username}'

        out = [
            'docker', 'run', '--rm',
            '--name', self.container_name,
            '--publish', f'{Bind_Host}:{self.port}:{_container_port}',
            '--volume', '/etc/localtime:/etc/localtime:ro',
            '--volume', f'{self.config_path}:/etc/ssh/sshd_config:ro',
            '--volume', f'{self.users_path}:/etc/sftp/users.conf:ro',
            '--volume', f'{self.hooks_dir}:/etc/sftp.d:ro',
        ]

        # The host keys are not read-only because the container restricts their permissions on startup
        for key_type in _host_key_types:
            path = self._host_key_path(key_type)
            out.extend(['--volume', f'{path}:/etc/ssh/ssh_host_{key_type}_key'])
            out.extend(['--volume', f'{path}.pub:/etc/ssh/ssh_host_{key_type}_key.pub'])

        # The home directory itself belongs to root, as the chroot requires, so each top-level directory
        # of the served tree is mounted into it on its own, which is what the account can write to.
        for name in sorted(os.listdir(self.root_dir)):
            path = os.path.join(self.root_dir, name)
            if os.path.isdir(path):
                out.extend(['--volume', f'{path}:{home}/{name}'])

        # The container appends every key it finds in this directory to the account's authorized keys
        for path in self.public_key_paths:
            name = os.path.basename(path)
            out.extend(['--volume', f'{path}:{home}/.ssh/keys/{name}:ro'])

        out.append(Container_Image)
        out.extend(_sshd_command)

        return out

# ################################################################################################################################

    def _remove_container(self) -> 'None':
        """ Removes the server's container, if one is left over from an earlier run.
        """
        _ = subprocess_run(['docker', 'rm', '--force', self.container_name], stdout=DEVNULL, stderr=DEVNULL, check=False)

# ################################################################################################################################

    def _log_output(self, process:'Popen') -> 'None':
        """ Logs each line of the container's output under the server's label, in place of the line's own timestamp.
        """
        output = cast_('any_', process.stdout)

        for line in output:
            line = line.rstrip()
            line = _syslog_timestamp.sub('', line)
            self.activity_logger.info(line)

        exit_code = process.wait()
        self.activity_logger.info('Container %s exited with code %s', self.container_name, exit_code)

# ################################################################################################################################

    def start(self) -> 'None':

        self.prepare()
        self._remove_container()

        command = self._build_command()

        # The container gets a session of its own, so that a Ctrl-C reaches this process only, which then stops it
        self._process = Popen(command, stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, text=True, errors='replace',
            start_new_session=True)

        self._reader = threading.Thread(target=self._log_output, args=(self._process,), daemon=True)
        self._reader.start()

        self.activity_logger.info('Starting %s on port %s, user %s (%s)', self.container_name, self.port, self.username,
            self.auth_mode)

# ################################################################################################################################

    def stop(self) -> 'None':

        _ = subprocess_run(['docker', 'stop', '--time', str(_stop_timeout), self.container_name],
            stdout=DEVNULL, stderr=DEVNULL, check=False)

        if self._reader:
            self._reader.join()

# ################################################################################################################################
# ################################################################################################################################
