# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from .base import BaseFileClient

# ################################################################################################################################
# ################################################################################################################################

if 0:

    # stdlib
    from typing import BinaryIO

    # pyfilesystem
    from fs.ftpfs import FTPFS
    from fs.info import Info

    BinaryIO = BinaryIO
    FTPFS = FTPFS
    Info = Info

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The 'touch' command cannot be executed for files longer than that many bytes
touch_max_size = 200_000

# ################################################################################################################################
# ################################################################################################################################

class FTPFileClient(BaseFileClient):
    def __init__(self, conn, config):
        # type: (FTPFS) -> None
        super().__init__(config)
        self.conn = conn

# ################################################################################################################################

    def create_directory(self, path):
        self.conn.makedir(path)

# ################################################################################################################################

    def delete_directory(self, path):
        self.conn.removetree(path)

# ################################################################################################################################

    def get(self, path):
        # (str, str) -> str
        return self.conn.readbytes(path)

# ################################################################################################################################

    def get_as_file_object(self, path, file_object):
        # type: (str, BinaryIO) -> None
        self.conn.download(path, file_object)

# ################################################################################################################################

    def move_file(self, path_from, path_to):
        # type: (str, str)
        self.conn.move(path_from, path_to)

# ################################################################################################################################

    def store(self, path, data):
        # type: (str, object) -> None
        if not isinstance(data, bytes):
            data = data.encode(self.config['encoding'])

        self.conn.writebytes(path, data)

# ################################################################################################################################

    def delete_file(self, path):
        # type: (str) -> None
        self.conn.remove(path)

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
                'is_dir': item.is_dir,
                'last_modified': item.modified,
                'has_touch': item.size < touch_max_size
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

    def path_exists(self, path):
        # type: (str) -> bool
        return self.conn.exists(path)

# ################################################################################################################################

    def ping(self):
        return self.path_exists('.')

# ################################################################################################################################

    def close(self):
        self.conn.close()

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

    config = {
        'encoding': 'utf8'
    }

    client = FTPFileClient(conn, config)

    # client.create_directory('aaa2')
    # client.delete_directory('aaa2')

    path = '/aaa2/abc.txt2'

    client.store(path, 'zzzz')
    client.touch(path)

    result = client.list('/aaa2')

    for item in result['file_list']: # type: dict
        print('ITEM', item)

    data = client.download(path)
    print('DATA', data)

    client.delete_file(path)

# ################################################################################################################################
# ################################################################################################################################
