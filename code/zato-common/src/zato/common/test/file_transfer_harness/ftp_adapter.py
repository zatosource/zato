# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FileTransfer
from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter, LocalBackedRemote
from zato.common.test.ftp_ import FTPTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Every connection an FTP test creates starts with this.
Conn_Name_Prefix = 'test-file-transfer-ftp-'

# ################################################################################################################################
# ################################################################################################################################

class FTPAdapter(LocalBackedRemote, FileTransferAdapter):
    """ Runs the shared file transfer schedule tests against a real FTP server.
    """

    conn_type        = FileTransfer.ConnType.FTP
    conn_name_prefix = Conn_Name_Prefix

    # Writes are visible immediately, the served directory is local.
    settle_timeout = 0.0

    # An FTP server renames in place, moves and nests directories, and keeps modification times.
    # The account's paths are case sensitive and symbolic links cannot be created over the protocol.
    supports_claim             = True
    supports_move              = True
    supports_subdirectories    = True
    supports_names_with_spaces = True
    supports_server_restart    = True
    supports_symlinks          = False
    preserves_last_modified    = True
    is_case_sensitive          = True

# ################################################################################################################################

    def __init__(self, use_ssl:'bool' = False) -> 'None':
        self.server = FTPTestServer(use_ssl=use_ssl)

# ################################################################################################################################

    def start_server(self) -> 'None':

        self.server.start()

        # Everything the tests inspect lives under the directory the server serves.
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
            'use_ssl': self.server.use_ssl,
        }

        return out

# ################################################################################################################################

    def edit_conn_payload(self, name:'str') -> 'anydict':

        out = self.create_conn_payload(name)
        return out

# ################################################################################################################################

    def remote_directory_for(self, name:'str') -> 'str':

        # A remote path is relative to the account's root directory, which is the served directory itself.
        out = name
        return out

# ################################################################################################################################

    def to_local(self, remote_path:'str') -> 'str':

        # The account's root directory is the served directory, so a remote path
        # is simply relative to it.
        out = f'{self.local_root}/{remote_path}'
        return out

# ################################################################################################################################
# ################################################################################################################################
