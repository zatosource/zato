# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter, LocalBackedRemote
from zato.common.test.smb_ import SMBTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Every connection an SMB test creates starts with this
Conn_Name_Prefix = 'test-file-transfer-smb-'

# ################################################################################################################################
# ################################################################################################################################

class SMBAdapter(LocalBackedRemote, FileTransferAdapter):
    """ Runs the shared file transfer schedule tests against a real SMB server.
    """

    conn_type = FileTransfer.ConnType.SMB
    conn_name_prefix = Conn_Name_Prefix

    # The share is backed by a directory of this machine, so a write is visible the moment it returns
    settle_timeout = 0.0

    # An SMB server renames in place, moves and nests directories, and keeps modification times.
    # It has no symbolic links, and two names differing only in case are the same file.
    supports_claim = True
    supports_move = True
    supports_subdirectories = True
    supports_names_with_spaces = True
    supports_server_restart = True
    supports_symlinks = False
    preserves_last_modified = True
    is_case_sensitive = False

# ################################################################################################################################

    def __init__(self) -> 'None':
        self.server = SMBTestServer()

# ################################################################################################################################

    def start_server(self) -> 'None':

        self.server.start()

        # Everything the tests inspect lives under the directory backing the server's only share
        self.local_root = self.server.files_dir

# ################################################################################################################################

    def stop_server(self) -> 'None':
        self.server.stop()

# ################################################################################################################################

    def restart_server(self) -> 'None':
        self.server.restart()

# ################################################################################################################################

    def pause_server(self) -> 'None':
        self.server.pause()

# ################################################################################################################################

    def resume_server(self) -> 'None':
        self.server.resume()

# ################################################################################################################################

    def create_conn_payload(self, name:'str') -> 'anydict':

        out:'anydict' = {
            'host': self.server.host,
            'port': self.server.port,
            'username': self.server.username,
            'secret': self.server.password,
        }

        return out

# ################################################################################################################################

    def edit_conn_payload(self, name:'str') -> 'anydict':

        out = self.create_conn_payload(name)
        return out

# ################################################################################################################################

    def remote_directory_for(self, name:'str') -> 'str':

        # A remote path names the share it lives on before anything else
        out = f'{self.server.share_name}/{name}'
        return out

# ################################################################################################################################

    def to_local(self, remote_path:'str') -> 'str':

        # Everything under the share sits in the directory that backs it, so the share's name
        # is what a remote path carries in place of that directory.
        share_prefix = self.server.share_name + '/'

        if not remote_path.startswith(share_prefix):
            raise Exception(f'Remote path `{remote_path}` does not name the share `{self.server.share_name}`')

        relative_path = remote_path[len(share_prefix):]

        out = f'{self.local_root}/{relative_path}'
        return out

# ################################################################################################################################
# ################################################################################################################################
