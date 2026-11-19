# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# smbprotocol
import smbclient
import smbclient.path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a connection attempt may take, in seconds
    Connection_Timeout = 5

    # How long the guest may leave the data of a request unacknowledged before the connection is closed, in milliseconds
    Unacknowledged_Data_Timeout_Ms = 5000

    # Readers and writers on both sides share every file
    Share_Access = 'rwd'

    # The suffix of a file being written, before it is renamed to its final name
    Temp_Suffix = '.harness-tmp'

# ################################################################################################################################
# ################################################################################################################################

class ShareClient:
    """ Reads and writes files on the shares of one guest as one account, with a connection cache of its own,
    so that several accounts can reach the same guest at the same time.
    """
    def __init__(self, host:'str', port:'int', username:'str', password:'str') -> 'None':
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection_cache:'anydict' = {}

# ################################################################################################################################

    def _register_session(self) -> 'None':
        """ Logs on to the guest unless this client is logged on already, over a connection that the client closes
        once the guest leaves its data unacknowledged for too long, e.g. because a firewall rule dropped the connection.
        """
        session = smbclient.register_session(
            self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            connection_timeout=ModuleCtx.Connection_Timeout,
            connection_cache=self.connection_cache,
        )

        sock = session.connection.transport._sock
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, ModuleCtx.Unacknowledged_Data_Timeout_Ms)

# ################################################################################################################################

    def _session_options(self) -> 'anydict':
        self._register_session()

        out = {
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'connection_cache': self.connection_cache,
        }
        return out

# ################################################################################################################################

    def unc(self, share:'str', path:'str'='') -> 'str':
        """ Returns the UNC path of a file or directory in a share, with forward slashes turned into backslashes.
        """
        path = path.replace('/', '\\')

        out = f'\\\\{self.host}\\{share}'

        if path:
            out = f'{out}\\{path}'

        return out

# ################################################################################################################################

    def connect(self) -> 'None':
        """ Logs on to the guest, raising an exception when that is not possible within the connection timeout.
        """
        self._register_session()

# ################################################################################################################################

    def close(self) -> 'None':
        """ Closes every connection this client opened.
        """
        smbclient.reset_connection_cache(fail_on_error=False, connection_cache=self.connection_cache)

# ################################################################################################################################

    def exists(self, share:'str', path:'str') -> 'bool':
        unc = self.unc(share, path)
        options = self._session_options()

        out = smbclient.path.exists(unc, **options)
        return out

# ################################################################################################################################

    def read_bytes(self, share:'str', path:'str', offset:'int'=0) -> 'bytes':
        """ Returns the contents of a file from the given offset onwards, without blocking its writer.
        """
        unc = self.unc(share, path)
        options = self._session_options()

        with smbclient.open_file(unc, mode='rb', share_access=ModuleCtx.Share_Access, **options) as file_:
            _ = file_.seek(offset)
            out = file_.read()

        return out

# ################################################################################################################################

    def read_text(self, share:'str', path:'str') -> 'str':
        data = self.read_bytes(share, path)

        out = data.decode('utf8')
        return out

# ################################################################################################################################

    def write_bytes(self, share:'str', path:'str', data:'bytes') -> 'None':
        """ Writes a file under a temporary name and renames it, so that a reader never sees it partially written.
        """
        temp_path = path + ModuleCtx.Temp_Suffix

        temp_unc = self.unc(share, temp_path)
        unc = self.unc(share, path)
        options = self._session_options()

        with smbclient.open_file(temp_unc, mode='wb', share_access=ModuleCtx.Share_Access, **options) as file_:
            _ = file_.write(data)

        smbclient.replace(temp_unc, unc, **options)

# ################################################################################################################################

    def write_text(self, share:'str', path:'str', text:'str') -> 'None':
        data = text.encode('utf8')
        self.write_bytes(share, path, data)

# ################################################################################################################################

    def makedirs(self, share:'str', path:'str') -> 'None':
        unc = self.unc(share, path)
        options = self._session_options()

        smbclient.makedirs(unc, exist_ok=True, **options)

# ################################################################################################################################

    def remove(self, share:'str', path:'str') -> 'None':
        """ Removes a file, and does nothing if there is no such file.
        """
        if self.exists(share, path):
            unc = self.unc(share, path)
            options = self._session_options()

            smbclient.remove(unc, **options)

# ################################################################################################################################

    def listdir(self, share:'str', path:'str'='') -> 'strlist':
        unc = self.unc(share, path)
        options = self._session_options()

        out = smbclient.listdir(unc, **options)
        return out

# ################################################################################################################################
# ################################################################################################################################
