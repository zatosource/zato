# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import wraps
from logging import getLogger

# Zato
from zato.server.connection.file_client.base import BaseFileClient, PathAccessException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.connection.sftp import SFTPIPCFacade, SFTPInfo

    SFTPIPCFacade = SFTPIPCFacade
    SFTPInfo = SFTPInfo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def ensure_path_exists(func):
    @wraps(func)
    def inner(self, path, *args, **kwargs):
        # type: (SFTPFileClient, str)
        if not self.conn.exists(path):
            raise PathAccessException('Path `{}` could not be accessed'.format(path))
        else:
            return func(self, path, *args, **kwargs)
    return inner

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
        return self.conn.read(path)

# ################################################################################################################################

    @ensure_path_exists
    def store(self, path, data):
        # type: (str, object) -> None
        self.conn.write(data, path)

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

        file_list = []
        directory_list = []

        out = {
            'file_list': file_list,
            'directory_list': directory_list
        }

        for item in result: # type: SFTPInfo
            if item.is_file:
                file_list.append(item.to_dict(False))
            else:
                directory_list.append(item.to_dict(False))

        self.sort_result(out)
        return out

# ################################################################################################################################

    def path_exists(self, path):
        # type: (str) -> bool
        return self.conn.exists(path)

# ################################################################################################################################

    def ping(self):
        return self.conn.ping()

# ################################################################################################################################

    def close(self):
        # Not applicable
        pass

# ################################################################################################################################
# ################################################################################################################################
