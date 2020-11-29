"""
# -*- coding: utf-8 -*-

# Zato
from zato.server.connection.file_client.base import BaseFileClient
from zato.server.connection.sftp import SFTPIPCFacade
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class FTPFileClient(BaseFileClient):
    def __init__(self, conn, config):
        # type: (SFTPConnection) -> None
        super().__init__(config)
        self.conn = conn

# ################################################################################################################################

    def create_directory(self, path):
        # self.conn.makedir(path)
        pass

# ################################################################################################################################

    def xdelete_directory(self, path):
        # self.conn.removetree(path)
        pass

# ################################################################################################################################

    def xget(self, path):
        # (str, str) -> str
        # return self.conn.readbytes(path)
        pass

# ################################################################################################################################

    def xget_as_file_object(self, path, file_object):
        # type: (str, BinaryIO) -> None
        # self.conn.download(path, file_object)
        pass

# ################################################################################################################################

    def xstore(self, path, data):
        # type: (str, object) -> None
        '''
        if not isinstance(data, bytes):
            data = data.encode(self.config['encoding'])
        self.conn.writebytes(path, data)
        '''

# ################################################################################################################################

    def xdelete_file(self, path):
        # type: (str) -> None
        #self.conn.remove(path)
        pass

# ################################################################################################################################

    def xlist(self, path):
        # Returns a list of directories and files for input path.
        # type: (str) -> list
        '''
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
        '''

# ################################################################################################################################

    def xtouch(self, path):
        # Touches a remote file by overwriting its contents with itself.
        '''
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
        '''

# ################################################################################################################################

    def xping(self):
        #return self.conn.exists('/')
        pass

# ################################################################################################################################

    def xclose(self):
        #self.conn.close()
        pass

# ################################################################################################################################
# ################################################################################################################################

class SFTPService1(Service):
    pass

"""
