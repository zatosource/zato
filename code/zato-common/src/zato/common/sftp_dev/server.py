# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import errno
import os
import socket
import threading
import time
from subprocess import PIPE, run as subprocess_run
from base64 import decodebytes
from logging import Logger, LoggerAdapter, getLogger
from typing import Literal

# paramiko
import paramiko
from paramiko import ServerInterface, SFTPAttributes, SFTPHandle, SFTPServer, SFTPServerInterface
from paramiko.common import AUTH_FAILED, AUTH_SUCCESSFUL, OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED, OPEN_SUCCEEDED
from paramiko.sftp import SFTP_NO_SUCH_FILE, SFTP_PERMISSION_DENIED

# Zato
from zato.common.sftp_dev.constants import Bind_Host, Login_User_Public_Key_Names

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from paramiko import PKey
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How long a listening socket waits for the next client while shutting down, in seconds
_accept_timeout = 1.0

# How long the SSH transport waits for the client to open a channel, in seconds
_channel_accept_timeout = 20.0

# How long a client handler sleeps while waiting for the transport to close, in seconds
_transport_poll_interval = 0.2

# File name of the persisted host key under each server's directory
_host_key_file_name = 'host_key'

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

def _load_openssh_public_key(path:'str') -> 'PKey':
    """ Reads one line from an OpenSSH public key file and returns the corresponding key object.
    """
    with open(path, encoding='utf8') as public_key_file:
        line = public_key_file.readline().strip()

    parts = line.split()

    if len(parts) < 2:
        raise Exception('Public key file `{}` is not in OpenSSH format'.format(path))

    key_type = parts[0]
    key_blob = decodebytes(parts[1].encode('ascii'))

    if key_type == 'ssh-rsa':
        out = paramiko.RSAKey(data=key_blob)
    elif key_type == 'ssh-ed25519':
        out = paramiko.Ed25519Key(data=key_blob)
    elif key_type in ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521'):
        out = paramiko.ECDSAKey(data=key_blob)
    else:
        raise Exception('Unsupported public key type `{}` in `{}`'.format(key_type, path))

    return out

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
# ################################################################################################################################

class DevSFTPFileHandle(SFTPHandle):
    """ A readable or writable handle backed by a real file on disk.
    """

    def __init__(self, flags:'int', real_path:'str') -> 'None':
        super().__init__(flags)
        self.real_path = real_path

        if flags & os.O_WRONLY and not flags & os.O_RDWR:
            if flags & os.O_APPEND:
                mode = 'ab'
            else:
                mode = 'wb'

            self.writefile = open(real_path, mode)
        elif flags & os.O_RDWR:
            self.writefile = open(real_path, 'r+b')
            self.readfile = self.writefile
        else:
            self.readfile = open(real_path, 'rb')

# ################################################################################################################################

class DevRootSFTPServer(SFTPServerInterface):
    """ Serves a single directory tree through the SFTP protocol.
    """

    def __init__(self, server:'ServerInterface', root_dir:'str', activity_logger:'PrefixedLoggerAdapter') -> 'None':
        super().__init__(server)
        self.root_dir = os.path.abspath(root_dir)
        self.activity_logger = activity_logger

# ################################################################################################################################

    def _real_path(self, path:'str') -> 'str':
        """ Maps an SFTP path to an absolute path confined to root_dir.
        """
        if path.startswith('/'):
            relative = path[1:]
        else:
            relative = path

        relative = os.path.normpath(relative)

        if relative.startswith('..'):
            raise PermissionError('Path escapes the SFTP root')

        full_path = os.path.join(self.root_dir, relative)
        full_path = os.path.abspath(full_path)

        if not full_path.startswith(self.root_dir):
            raise PermissionError('Path escapes the SFTP root')

        return full_path

# ################################################################################################################################

    def _stat_path(self, path:'str') -> 'SFTPAttributes | int':
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        try:
            stat_result = os.stat(real_path)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return SFTP_NO_SUCH_FILE

            return SFTP_PERMISSION_DENIED

        out = SFTPAttributes.from_stat(stat_result)
        out.filename = os.path.basename(real_path)

        return out

# ################################################################################################################################

    def list_folder(self, path:'str'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        if not os.path.isdir(real_path):
            return SFTP_NO_SUCH_FILE

        out = []

        for name in os.listdir(real_path):
            entry_path = os.path.join(real_path, name)
            stat_result = os.stat(entry_path)
            attributes = SFTPAttributes.from_stat(stat_result)
            attributes.filename = name
            out.append(attributes)

        self.activity_logger.info('LIST %s (%s entries)', path or '/', len(out))

        return out

# ################################################################################################################################

    def stat(self, path:'str'):
        return self._stat_path(path)

# ################################################################################################################################

    def lstat(self, path:'str'):
        return self._stat_path(path)

# ################################################################################################################################

    def open(self, path:'str', flags:'int', attr:'SFTPAttributes'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        if flags & os.O_CREAT:
            parent = os.path.dirname(real_path)
            os.makedirs(parent, exist_ok=True)

        try:
            handle = DevSFTPFileHandle(flags, real_path)
        except OSError:
            return SFTP_PERMISSION_DENIED

        if flags & os.O_CREAT:
            self.activity_logger.info('OPEN %s (create)', path)
        else:
            self.activity_logger.info('OPEN %s', path)

        return handle

# ################################################################################################################################

    def remove(self, path:'str'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        try:
            os.remove(real_path)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return SFTP_NO_SUCH_FILE

            return SFTP_PERMISSION_DENIED

        self.activity_logger.info('REMOVE %s', path)

        return 0

# ################################################################################################################################

    def rename(self, oldpath:'str', newpath:'str'):
        try:
            old_real = self._real_path(oldpath)
            new_real = self._real_path(newpath)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        try:
            os.rename(old_real, new_real)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return SFTP_NO_SUCH_FILE

            return SFTP_PERMISSION_DENIED

        self.activity_logger.info('RENAME %s -> %s', oldpath, newpath)

        return 0

# ################################################################################################################################

    def mkdir(self, path:'str', attr:'SFTPAttributes'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        try:
            os.mkdir(real_path)
        except OSError:
            return SFTP_PERMISSION_DENIED

        self.activity_logger.info('MKDIR %s', path)

        return 0

# ################################################################################################################################

    def rmdir(self, path:'str'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        try:
            os.rmdir(real_path)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return SFTP_NO_SUCH_FILE

            return SFTP_PERMISSION_DENIED

        self.activity_logger.info('RMDIR %s', path)

        return 0

# ################################################################################################################################

    def realpath(self, path:'str'):
        try:
            real_path = self._real_path(path)
        except PermissionError:
            return SFTP_PERMISSION_DENIED

        if not os.path.exists(real_path):
            return SFTP_NO_SUCH_FILE

        if real_path == self.root_dir:
            out = '/'
        else:
            suffix = os.path.relpath(real_path, self.root_dir)
            out = '/' + suffix.replace(os.sep, '/')

        return out

# ################################################################################################################################
# ################################################################################################################################

class DevSSHServerInterface(ServerInterface):
    """ Accepts either password or public-key authentication for one configured account.
    """

    def __init__(
        self,
        auth_mode:'Auth_Mode',
        username:'str',
        password:'str',
        public_key_paths:'strlist',
        activity_logger:'PrefixedLoggerAdapter',
    ) -> 'None':
        self.auth_mode = auth_mode
        self.username = username
        self.password = password
        self.public_key_paths = public_key_paths
        self.activity_logger = activity_logger

# ################################################################################################################################

    def get_allowed_auths(self, username:'str') -> 'str':
        if username != self.username:
            return ''

        if self.auth_mode == 'password':
            out = 'password'
        else:
            out = 'publickey'

        return out

# ################################################################################################################################

    def check_auth_password(self, username:'str', password:'str') -> 'int':
        if self.auth_mode != 'password':
            return AUTH_FAILED

        if username == self.username and password == self.password:
            self.activity_logger.info('Client authenticated as %s (password)', username)
            return AUTH_SUCCESSFUL

        self.activity_logger.warning('Password authentication failed for user %s', username)

        return AUTH_FAILED

# ################################################################################################################################

    def check_auth_publickey(self, username:'str', key:'PKey') -> 'int':
        if self.auth_mode != 'publickey':
            return AUTH_FAILED

        if username != self.username:
            return AUTH_FAILED

        for path in self.public_key_paths:
            allowed = _load_openssh_public_key(path)

            if key == allowed:
                self.activity_logger.info('Client authenticated as %s (public key %s)', username, path)
                return AUTH_SUCCESSFUL

        self.activity_logger.warning('Public key authentication failed for user %s', username)

        return AUTH_FAILED

# ################################################################################################################################

    def check_channel_request(self, kind:'str', chanid:'int') -> 'int':
        if kind == 'session':
            return OPEN_SUCCEEDED

        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

# ################################################################################################################################
# ################################################################################################################################

class DevSFTPServer:
    """ One Paramiko-based SFTP listener on a fixed port, run from a background thread.
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

        self.root_dir = os.path.join(self.data_dir, 'files')
        self.host_key_path = os.path.join(self.data_dir, _host_key_file_name)

        self.activity_logger = PrefixedLoggerAdapter(logger, self.log_label)

        self._listen_socket:'socket.socket | None' = None
        self._thread:'threading.Thread | None' = None
        self._shutdown = threading.Event()

# ################################################################################################################################

    def prepare(self) -> 'None':
        os.makedirs(self.root_dir, exist_ok=True)
        ensure_sample_tree(self.root_dir, self.sample_directories, self.sample_files)
        self._ensure_host_key()

# ################################################################################################################################

    def _ensure_host_key(self) -> 'None':
        if os.path.isfile(self.host_key_path):
            return

        command = ['ssh-keygen', '-q', '-t', 'ed25519', '-f', self.host_key_path, '-N', '']
        result = subprocess_run(command, stdout=PIPE, stderr=PIPE)

        if result.returncode != 0:
            stderr = result.stderr.decode('utf8')
            raise Exception('Could not generate host key under `{}` -> `{}`'.format(self.host_key_path, stderr))

        self.activity_logger.info('Generated host key at %s', self.host_key_path)

# ################################################################################################################################

    def _load_host_key(self) -> 'paramiko.PKey':
        out = paramiko.Ed25519Key(filename=self.host_key_path)
        return out

# ################################################################################################################################

    def _handle_client(self, client_socket:'socket.socket', peer:'tuple') -> 'None':
        transport = paramiko.Transport(client_socket)
        transport.set_subsystem_handler('sftp', SFTPServer, DevRootSFTPServer, self.root_dir, self.activity_logger)

        host_key = self._load_host_key()
        transport.add_server_key(host_key)

        ssh_server = DevSSHServerInterface(
            self.auth_mode,
            self.username,
            self.password,
            self.public_key_paths,
            self.activity_logger,
        )

        try:
            transport.start_server(server=ssh_server)
        except paramiko.SSHException as exc:
            self.activity_logger.warning('SSH handshake failed with %s: %s', peer[0], exc)
            transport.close()
            return

        channel = transport.accept(_channel_accept_timeout)

        if channel is None:
            self.activity_logger.warning('Client %s opened no SSH channel', peer[0])
            transport.close()
            return

        self.activity_logger.info('SFTP session started from %s', peer[0])

        while transport.is_active():
            time.sleep(_transport_poll_interval)

        self.activity_logger.info('SFTP session ended from %s', peer[0])

        transport.close()

# ################################################################################################################################

    def _serve(self) -> 'None':
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.settimeout(_accept_timeout)
        listen_socket.bind((Bind_Host, self.port))
        listen_socket.listen(100)

        self._listen_socket = listen_socket

        self.activity_logger.info(
            'Listening on %s:%s as %s (%s auth), files under %s',
            Bind_Host,
            self.port,
            self.username,
            self.auth_mode,
            self.root_dir,
        )

        while not self._shutdown.is_set():
            try:
                client_socket, peer = listen_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            handler = threading.Thread(
                target=self._handle_client,
                args=(client_socket, peer),
                name='sftp-dev-{}-client'.format(self.port),
                daemon=True,
            )
            handler.start()

        listen_socket.close()
        self._listen_socket = None

# ################################################################################################################################

    def start(self) -> 'None':
        self.prepare()

        self._shutdown.clear()

        self._thread = threading.Thread(
            target=self._serve,
            name='sftp-dev-{}'.format(self.port),
            daemon=True,
        )
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        self._shutdown.set()

        if self._listen_socket:
            self._listen_socket.close()

        if self._thread:
            self._thread.join()
            self._thread = None

        self.activity_logger.info('Stopped')

# ################################################################################################################################
# ################################################################################################################################
