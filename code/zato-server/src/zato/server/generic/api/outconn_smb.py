# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# smbprotocol
import smbclient
from smbprotocol.exceptions import SMBOSError

# Zato
from zato.common.api import SMB
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from smbprotocol.session import Session
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_smb_config_defaults:'dict[str, object]' = {
    'host': '',
    'port': SMB.DEFAULT.PORT,
    'username': '',
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_smb_int_config_keys = ('port',)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_smb_bool_config_keys = ()

# ################################################################################################################################
# ################################################################################################################################

class SMBClient:
    """ Wraps access to remote SMB shares via the smbprotocol library.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':

        self.config = config
        self.server = server

        self.id = self.config.id           # type: int
        self.name = self.config.name       # type: str
        self.is_active = self.config.is_active # type: bool

        self.host = self.config.host         # type: str
        self.port = self.config.port         # type: int
        self.username = self.config.username # type: str

        # The connection's password - it may be missing if the connection was created without one
        password = self.config.secret
        if password is None:
            password = ''
        self.password = password # type: str

        # Credentials given to each operation - the library registers and caches sessions on first use,
        # keyed by host, port and username, which means that callers never need to register anything themselves.
        self.conn_kwargs:'stranydict' = {
            'username': self.username,
            'password': self.password,
            'port': self.port,
        }

        # Added for API completeness
        self.is_connected = True

# ################################################################################################################################

    def to_unc(self, remote_path:'str') -> 'str':
        """ Converts a remote path in the format of share/dir/file.txt to a UNC path of \\\\host\\share\\dir\\file.txt.
        """

        # Remove any leading slashes ..
        remote_path = remote_path.lstrip('/')

        # .. turn forward slashes into backslashes ..
        remote_path = remote_path.replace('/', '\\')

        # .. and prefix it all with the host to form a full UNC path.
        out = '\\\\{}\\{}'.format(self.host, remote_path)

        return out

# ################################################################################################################################

    def ping(self) -> 'None':

        # Establish or reuse a session - this runs the full protocol negotiation
        # and the NTLM or Kerberos authentication with the remote server ..
        session:'Session' = smbclient.register_session(self.host, **self.conn_kwargs)

        # .. and send an echo request over that session to confirm that the server actually responds.
        _ = session.connection.echo(sid=session.session_id)

# ################################################################################################################################

    def connect(self) -> 'None':
        # We do not maintain long-running connections ourselves but we still ping the remote end
        # to make sure we are actually able to authenticate with it.
        self.ping()
        logger.info('SMB ping OK; name:`%s`, host:`%s`, port:`%s`', self.name, self.host, self.port)

# ################################################################################################################################

    def close(self) -> 'None':
        # Closes the underlying connection to the server along with all of its sessions
        smbclient.delete_session(self.host, port=self.port)

# ################################################################################################################################

    def zato_delete_impl(self) -> 'None':
        self.close()

# ################################################################################################################################

    def stat(self, remote_path:'str') -> 'any_':

        unc_path = self.to_unc(remote_path)

        out = smbclient.stat(unc_path, **self.conn_kwargs)
        return out

# ################################################################################################################################

    def exists(self, remote_path:'str') -> 'bool':

        unc_path = self.to_unc(remote_path)

        # The path exists only if the remote server can tell us anything about it
        try:
            _ = smbclient.stat(unc_path, **self.conn_kwargs)
        except SMBOSError:
            out = False
        else:
            out = True

        return out

# ################################################################################################################################

    def scandir(self, remote_path:'str') -> 'anylist':

        unc_path = self.to_unc(remote_path)

        # Materialize the generator so that the underlying handles are not held open longer than needed
        out = []
        for entry in smbclient.scandir(unc_path, **self.conn_kwargs):
            out.append(entry)

        return out

# ################################################################################################################################

    def read(self, remote_path:'str') -> 'bytes':

        unc_path = self.to_unc(remote_path)

        with smbclient.open_file(unc_path, mode='rb', **self.conn_kwargs) as remote_file:
            out = remote_file.read()

        return out

# ################################################################################################################################

    def write(self, remote_path:'str', data:'bytes') -> 'None':

        unc_path = self.to_unc(remote_path)

        # Writing always overwrites, which is why any existing file is deleted first ..
        if self.exists(remote_path):
            self.remove(remote_path)

        # .. and the file is now created anew - note that the 'x' mode maps to the FILE_CREATE disposition,
        # which, unlike the overwrite-if dispositions, is handled correctly by all the SMB server implementations.
        with smbclient.open_file(unc_path, mode='xb', **self.conn_kwargs) as remote_file:
            _ = remote_file.write(data)

# ################################################################################################################################

    def remove(self, remote_path:'str') -> 'None':

        unc_path = self.to_unc(remote_path)

        smbclient.remove(unc_path, **self.conn_kwargs)

# ################################################################################################################################

    def rmdir(self, remote_path:'str') -> 'None':

        unc_path = self.to_unc(remote_path)

        smbclient.rmdir(unc_path, **self.conn_kwargs)

# ################################################################################################################################

    def makedirs(self, remote_path:'str', exist_ok:'bool'=False) -> 'None':

        unc_path = self.to_unc(remote_path)

        smbclient.makedirs(unc_path, exist_ok=exist_ok, **self.conn_kwargs)

# ################################################################################################################################

    def rename(self, from_path:'str', to_path:'str') -> 'None':

        from_unc_path = self.to_unc(from_path)
        to_unc_path = self.to_unc(to_path)

        # A rename always overwrites its target, which is why the target is created first if it does not exist yet -
        # this is needed because some SMB server implementations report a missing target with a status code
        # that the client library does not recognize, whereas an existing target is handled correctly everywhere ..
        if not self.exists(to_path):
            with smbclient.open_file(to_unc_path, mode='xb', **self.conn_kwargs):
                pass

        # .. and now the source can replace the target.
        smbclient.replace(from_unc_path, to_unc_path, **self.conn_kwargs)

# ################################################################################################################################
# ################################################################################################################################

class OutconnSMBWrapper(Wrapper):
    """ Wraps a queue of connections to SMB.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = '{}:{}'.format(config.host, config.port)
        super(OutconnSMBWrapper, self).__init__(config, 'outgoing SMB', server)

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('SMBClient', client)
            client.ping()

# ################################################################################################################################

    def add_client(self) -> 'None':
        try:
            conn = SMBClient(self.config, self.server)
        except Exception:
            logger.warning('SMB client could not be built `%s`', format_exc())
        else:
            _ = self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
