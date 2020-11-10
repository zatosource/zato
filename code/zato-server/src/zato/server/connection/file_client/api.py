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

zato_indicator = 'zato.zato'

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
                'last_accessed': item.accessed,
                'last_modified': item.modified,
                'is_directory': item.is_dir,
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

    def touch(self, old_path):
        #resource = self.conn.openbin(path, mode='ab+')
        #resource.seek(0)
        #resource.write(b'1')
        #print(555, self.conn.getsize(path))
        #resource.close()
        #print(333, resource.mode.appending)
        #pass

        dir_name, file_name = os.path.split(old_path)
        print(111, dir_name)
        print(222, file_name)

        new_file_name = '{}.{}.{}'.format(zato_indicator, file_name, zato_indicator)
        new_path = os.path.join(dir_name, new_file_name)

        # Assign a new name ..
        self.conn.ftp.rename(old_path, new_path)

        from time import sleep
        sleep(1)

        # .. and rename it back to the original value,
        # changing the file's modification time in this way.
        self.conn.ftp.rename(new_path, old_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # pyfilesystem
    from fs.ftpfs import FTPFS

    host = 'localhost'
    user = 'zzz'
    password = 'zzz'
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
