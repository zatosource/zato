# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from getpass import getuser
from shutil import copyfile
from subprocess import run as subprocess_run

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter, LocalBackedRemote
from zato.common.test.sftp_ import SFTPTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The name of the environment variable through which a server finds the SFTP client key on disk
Key_Env_Name = 'Zato_Test_FT_SFTP_Key_File'

# Every connection an SFTP test creates starts with this
Conn_Name_Prefix = 'test-file-transfer-sftp-'

# The permissions an SSH private key must carry for the client to accept it
_key_permissions = 0o600

# ################################################################################################################################
# ################################################################################################################################

class SFTPAdapter(FileTransferAdapter, LocalBackedRemote):
    """ Runs the shared file transfer schedule tests against a real SSH server with an SFTP subsystem.
    """

    conn_type = FileTransfer.ConnType.SFTP
    conn_name_prefix = Conn_Name_Prefix

    # The server serves this machine's own filesystem, so a write is visible the moment it returns
    settle_timeout = 0.0

    # An SFTP server renames in place, moves, nests directories and keeps modification times,
    # and the filesystem underneath it tells two names apart by case.
    supports_claim = True
    supports_move = True
    supports_subdirectories = True
    supports_names_with_spaces = True
    supports_server_restart = True
    supports_symlinks = True
    preserves_last_modified = True
    is_case_sensitive = True

# ################################################################################################################################

    def __init__(self, key_path:'str') -> 'None':

        # The Zato server reads the client key through an environment variable, so the path is fixed
        # before the server starts while the key itself is written out only once the test server runs.
        self.key_path = key_path

        self.server = SFTPTestServer()
        self.username = getuser()

# ################################################################################################################################

    def start_server(self) -> 'None':

        self.server.start()

        # The port may have been used by an earlier run with a different host key, so any entry
        # recorded in the user's known_hosts file must go away first ..
        address = f'[{self.server.host}]:{self.server.port}'
        _ = subprocess_run(['ssh-keygen', '-R', address], capture_output=True)

        # .. the Zato server looks for the key under the path its environment variable already names ..
        _ = copyfile(self.server.client_key_path, self.key_path)
        os.chmod(self.key_path, _key_permissions)

        # .. and everything the tests inspect lives under the directory the server serves.
        self.local_root = self.server.files_dir

# ################################################################################################################################

    def stop_server(self) -> 'None':
        self.server.stop()

# ################################################################################################################################

    def restart_server(self) -> 'None':
        self.server.restart()

# ################################################################################################################################

    def create_conn_payload(self, name:'str') -> 'anydict':

        out:'anydict' = {
            'address': f'{self.server.host}:{self.server.port}',
            'username': self.username,
            'private_key': Key_Env_Name,
            'strict_host_key_checking': False,
        }

        return out

# ################################################################################################################################

    def edit_conn_payload(self, name:'str') -> 'anydict':

        out = self.create_conn_payload(name)
        return out

# ################################################################################################################################

    def remote_directory_for(self, name:'str') -> 'str':

        # The server serves absolute paths of this machine, so a remote path is a local path
        out = f'{self.local_root}/{name}'
        return out

# ################################################################################################################################

    def to_local(self, remote_path:'str') -> 'str':

        out = remote_path
        return out

# ################################################################################################################################
# ################################################################################################################################
