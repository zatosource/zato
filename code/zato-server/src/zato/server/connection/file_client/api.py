# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from operator import itemgetter

# pyfilesystem
from fs.ftpfs import ftp_errors

# ################################################################################################################################
# ################################################################################################################################

if 0:
    # pyfilesystem
    from fs.ftpfs import FTPFS
    from fs.info import Info

    FTPFS = FTPFS

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The 'touch' command cannot be executed for files longer than that
touch_max_size = 200_000

# ################################################################################################################################
# ################################################################################################################################

class BaseFileClient(object):

    def sort_result(self, result):
        # type: (dict) -> None

        result['directory_list'].sort(key=itemgetter('name'))
        result['file_list'].sort(key=itemgetter('name'))

    def change_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def create_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def list(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def download_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def upload_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def touch(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class FTPFileClient(BaseFileClient):
    def __init__(self, conn):
        # type: (FTPFS) -> None
        self.conn = conn

# ################################################################################################################################

    def create_directory(self, path):
        self.conn.makedir(path)

# ################################################################################################################################

    def list(self, path):
        """ Returns a list of directories and files for input path.
        """
        # type: (str) -> list

        # Response to produce
        out = {
            'directory_list': [],
            'file_list': [],
        }

        # Call the remote resource
        result = self.conn.scandir(path)

        # Process all items produced
        for item in result: # type: Info

            elem = {
                'name': item.name,
                'size': item.size,
                'is_directory': item.is_dir,
                'last_modified': item.modified,
                'is_touch_supported': item.size < touch_max_size
            }

            if item.is_dir:
                out['directory_list'].append(elem)
            else:
                out['file_list'].append(elem)

        # Sort all items by name
        self.sort_result(out)

        # Return the response to our caller
        return out

# ################################################################################################################################

    def touch(self, path):
        """ Touches a remote file by overwriting its contents with itself.
        """
        with self.conn._lock:

            # Get the current size ..
            size = self.conn.getsize(path)

            # .. make sure the file is not too big ..
            if size > touch_max_size:
                raise ValueError('File `{}` is too big for the touch command; size={}; max={}'.format(
                    path, size, touch_max_size))

            # .. read all data in ..
            with conn.openbin(path) as f:
                data = f.read(size)

            # .. and write it under the same path, effectively merely changing its modification time.
            with conn.openbin(path, 'w') as f:
                f.write(data)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # pyfilesystem
    from fs.ftpfs import FTPFS

    host = 'localhost'
    user = 'abc'
    password = 'def'
    port = 11021

    conn = FTPFS(host, user, password, port=port)

    client = FTPFileClient(conn)

    #client.create_directory('aaa2/222')

    client.touch('aaa2/222/abc.txt')
    result = client.list('/aaa2/222')

    for item in result['file_list']: # type: dict
        print(111, item)

# ################################################################################################################################
# ################################################################################################################################
