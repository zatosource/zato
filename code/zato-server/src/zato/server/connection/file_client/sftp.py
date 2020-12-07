# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.file_client.base import BaseFileClient, PathAccessException
from zato.server.connection.sftp import SFTPIPCFacade
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def ensure_path_exists(*ignored_args, **ignored_kwargs):
    def _inner(self, path, *ignored_inner_args, **ignored_inner_kwargs):
        # type: (SFTPFileClient, str)
        if not self.conn.exists(path):
            raise PathAccessException('Path `{}` could not be accessed'.format(path))
    return _inner

# ################################################################################################################################

class SFTPFileClient(BaseFileClient):
    def __init__(self, conn, config):
        # type: (SFTPIPCFacade, dict) -> None
        super().__init__(config)
        self.conn = conn

# ################################################################################################################################

    def create_directory(self, path):
        self.conn.create_directory(path)

# ################################################################################################################################

    @ensure_path_exists
    def delete_directory(self, path):
        self.conn.delete_directory(path)

# ################################################################################################################################

    @ensure_path_exists
    def get(self, path):
        # (str) -> str
        return self.conn.download(path)

# ################################################################################################################################

    @ensure_path_exists
    def store(self, path, data):
        # type: (str, object) -> None
        self.conn.write(data, path)

        import struct

# ################################################################################################################################

    @ensure_path_exists
    def delete_file(self, path):
        self.conn.delete_file(path)

# ################################################################################################################################

    @ensure_path_exists
    def list(self, path):
        """ Returns a list of directories and files for input path.
        """
        # type: (str) -> list
        result = self.conn.list(path)

        return result

# ################################################################################################################################

    def ping(self):
        return self.conn.ping()

# ################################################################################################################################

    def close(self):
        # Not applicable
        pass

# ################################################################################################################################
# ################################################################################################################################
