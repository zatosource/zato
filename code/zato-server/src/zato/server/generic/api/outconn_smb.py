# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from contextlib import contextmanager
from io import BytesIO
from logging import getLogger
from shutil import copyfileobj
from traceback import format_exc

# smbprotocol
import smbclient
from smbclient._io import SMBFileTransaction, SMBRawIO, set_info
from smbprotocol.exceptions import SMBException, SMBOSError, SMBResponseException
from smbprotocol.file_info import FileRenameInformation
from smbprotocol.header import NtStatus
from smbprotocol.open import CreateOptions, FilePipePrinterAccessMask

# Zato
from zato.common.api import SMB
from zato.common.audit_log.api import AuditLog
from zato.common.file_transfer.api import Default_Verify_How, OutcomeUnknown
from zato.common.file_transfer.spool import Chunk_Size
from zato.common.pubsub.outgoing import OutgoingPublisher, OutgoingType
from zato.common.typing_ import cast_
from zato.common.util.logging_ import file_transfer_logger_name
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from smbprotocol.session import Session
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, callable_, iterator_, stranydict
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(file_transfer_logger_name)

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_smb_config_defaults:'dict[str, object]' = {
    'host': '',
    'port': SMB.DEFAULT.PORT,
    'username': '',
    'should_store_content': False,
    'verify_how': Default_Verify_How,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_smb_int_config_keys = ('port',)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_smb_bool_config_keys = ('should_store_content',)

# Config keys that must be strings but may arrive as integers from opaque storage
outconn_smb_string_config_keys = ('host', 'username', 'verify_how')

# How the source of a rename is shared with other handles - reading and writing, but not its deletion,
# which is what a rename of the same file through another handle requires
rename_share_access = 'rw'

# How long the server may leave the data of a request unacknowledged before the connection is closed, in milliseconds.
# The library waits for each response without a time limit, which means that without this setting an operation
# sent over a connection whose packets the network drops waits indefinitely.
unacknowledged_data_timeout_ms = 15000

# The operating systems that support the time limit on unacknowledged data
has_unacknowledged_data_timeout = hasattr(socket, 'TCP_USER_TIMEOUT')

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

        # The connections of this client only. The library otherwise keeps one connection per host and port
        # for the whole process, and closing this client would close it for every other client of the same server.
        self.connection_cache:'stranydict' = {}

        # Credentials given to each operation - the library registers and caches sessions on first use,
        # keyed by host, port and username, which means that callers never need to register anything themselves.
        self.conn_kwargs:'stranydict' = {
            'username': self.username,
            'password': self.password,
            'port': self.port,
            'connection_cache': self.connection_cache,
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

    def _register_session(self) -> 'Session':
        """ Returns the session of this client, establishing it first if there is none or its connection was closed.
        """
        out:'Session' = smbclient.register_session(self.host, **self.conn_kwargs)

        # A connection whose data the server does not acknowledge in time is closed, which ends each operation that waits on it
        if has_unacknowledged_data_timeout:
            sock = out.connection.transport._sock
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, unacknowledged_data_timeout_ms)

        return out

# ################################################################################################################################

    def _forget_share(self, unc_path:'str') -> 'None':
        """ Removes the cached connection to the share of a UNC path, so that the next operation connects to the share anew.
        """
        session = self._register_session()

        # The library keys its connections to shares by the server and the share name, e.g. \\host\share ..
        server, share = unc_path.lstrip('\\').split('\\')[:2]
        share_name = '\\\\{}\\{}'.format(server, share)

        # .. and the server no longer knows the connection, which is why it is only removed from the cache.
        for tree_id, tree in list(session.tree_connect_table.items()):
            if tree.share_name == share_name:
                del session.tree_connect_table[tree_id]

# ################################################################################################################################

    @contextmanager
    def _share_access(self, unc_path:'str') -> 'iterator_[None]':
        """ Runs one operation on the share of a UNC path. The library keeps its connection to a share even after
        the server deleted the share, e.g. because it was removed and created again, and every later operation fails.
        """
        _ = self._register_session()

        try:
            yield

        except SMBOSError as e:

            # The connection to a deleted share is removed, so that the next operation connects to the share again ..
            if e.ntstatus == NtStatus.STATUS_NETWORK_NAME_DELETED:
                self._forget_share(unc_path)

            # .. and the caller receives the error in each case.
            raise

# ################################################################################################################################

    def ping(self) -> 'None':

        # Establish or reuse a session - this runs the full protocol negotiation
        # and the NTLM or Kerberos authentication with the remote server ..
        session = self._register_session()

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
        smbclient.delete_session(self.host, port=self.port, connection_cache=self.connection_cache)

# ################################################################################################################################

    def zato_delete_impl(self) -> 'None':
        self.close()

# ################################################################################################################################

    def stat(self, remote_path:'str') -> 'any_':

        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            out = smbclient.stat(unc_path, **self.conn_kwargs)

        return out

# ################################################################################################################################

    def exists(self, remote_path:'str') -> 'bool':

        unc_path = self.to_unc(remote_path)

        # The path exists only if the remote server can tell us anything about it
        try:
            with self._share_access(unc_path):
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
        with self._share_access(unc_path):
            for entry in smbclient.scandir(unc_path, **self.conn_kwargs):
                out.append(entry)

        return out

# ################################################################################################################################

    def read_chunks(self, remote_path:'str', callback:'callable_') -> 'None':
        """ Reads a remote file, handing each chunk of its bytes to the callback as soon as it arrives.
        """
        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            with smbclient.open_file(unc_path, mode='rb', **self.conn_kwargs) as remote_file:
                while chunk := remote_file.read(Chunk_Size):
                    callback(chunk)

# ################################################################################################################################

    def read(self, remote_path:'str') -> 'bytes':

        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            with smbclient.open_file(unc_path, mode='rb', **self.conn_kwargs) as remote_file:
                out = remote_file.read()

        return out

# ################################################################################################################################

    def write(self, remote_path:'str', data:'bytes') -> 'None':

        buffer = BytesIO(data)
        self.write_from_file(remote_path, buffer)

# ################################################################################################################################

    def write_from_file(self, remote_path:'str', source_file:'any_') -> 'None':
        """ Stores the bytes of a local file object, sending them one chunk at a time.
        """
        unc_path = self.to_unc(remote_path)

        # Writing always overwrites, which is why any existing file is deleted first ..
        if self.exists(remote_path):
            self.remove(remote_path)

        # .. and the file is now created anew - note that the 'x' mode maps to the FILE_CREATE disposition,
        # which, unlike the overwrite-if dispositions, is handled correctly by all the SMB server implementations.
        with self._share_access(unc_path):
            with smbclient.open_file(unc_path, mode='xb', **self.conn_kwargs) as remote_file:
                copyfileobj(source_file, remote_file, Chunk_Size)

# ################################################################################################################################

    def remove(self, remote_path:'str') -> 'None':

        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            smbclient.remove(unc_path, **self.conn_kwargs)

# ################################################################################################################################

    def rmdir(self, remote_path:'str') -> 'None':

        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            smbclient.rmdir(unc_path, **self.conn_kwargs)

# ################################################################################################################################

    def makedirs(self, remote_path:'str', exist_ok:'bool'=False) -> 'None':

        unc_path = self.to_unc(remote_path)

        with self._share_access(unc_path):
            smbclient.makedirs(unc_path, exist_ok=exist_ok, **self.conn_kwargs)

# ################################################################################################################################

    def rename(self, from_path:'str', to_path:'str') -> 'None':

        from_unc_path = self.to_unc(from_path)
        to_unc_path = self.to_unc(to_path)

        # The server receives the new name relative to the share, e.g. dir\file.txt ..
        target_name = to_unc_path.lstrip('\\').split('\\', 2)[2]

        # .. a rename always overwrites its target, and the source takes its place in a single operation,
        # .. which means that a reader of the target directory never finds an incomplete file under the target name ..
        rename_info = FileRenameInformation()
        rename_info['replace_if_exists'] = True
        rename_info['file_name'] = target_name

        with self._share_access(from_unc_path):

            # .. the source is opened for its deletion without sharing it, which means that of two concurrent renames
            # .. of one file, e.g. by two consumers that claim it, only one opens the file and the other one fails ..
            source = SMBRawIO(
                from_unc_path,
                mode='r',
                share_access=rename_share_access,
                desired_access=FilePipePrinterAccessMask.DELETE,
                create_options=CreateOptions.FILE_OPEN_REPARSE_POINT,
                **self.conn_kwargs,
            )

            # .. the file is renamed through that handle ..
            is_open = False

            try:
                with source:
                    is_open = True
                    with SMBFileTransaction(source) as transaction:
                        set_info(transaction, rename_info)

            # .. a status that the server returned means that it did not rename the file ..
            except (SMBOSError, SMBResponseException):
                raise

            # .. whereas a connection that failed once the handle was open leaves the rename possibly carried out.
            except (SMBException, OSError) as e:
                if is_open:
                    raise OutcomeUnknown(f'Rename of `{from_path}` to `{to_path}` not confirmed -> {e}') from e
                else:
                    raise

# ################################################################################################################################
# ################################################################################################################################

class OutconnSMBWrapper(Wrapper):
    """ Wraps a queue of connections to SMB.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = '{}:{}'.format(config.host, config.port)
        super(OutconnSMBWrapper, self).__init__(config, 'outgoing SMB', server)

        # Every file this connection moves is recorded through this object
        self.audit_log = AuditLog(server.name)

        # Whether the audited operations also keep the bytes of the files they moved -
        # connections created before the flag existed have no such key stored at all.
        if 'should_store_content' in config:
            self.should_store_content = config['should_store_content']
        else:
            self.should_store_content = False

        # A connection without the setting checks the size.
        if not (verify_how := config.get('verify_how')):
            verify_how = Default_Verify_How

        self.verify_how = verify_how

        # What a guaranteed delivery to this connection goes through. It is built from the connection's
        # id rather than its name because that is what a rename leaves alone.
        self.publisher = OutgoingPublisher(server, OutgoingType.SMB, config.id)

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
