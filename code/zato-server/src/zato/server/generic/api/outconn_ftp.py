# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from ftplib import error_perm, FTP, FTP_TLS
from io import BytesIO
from logging import getLogger
from ssl import create_default_context, CERT_NONE
from traceback import format_exc

# Zato
from zato.common.api import FTP as CommonFTP
from zato.common.audit_log.api import AuditLog
from zato.common.pubsub.outgoing import OutgoingPublisher, OutgoingType
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import anylist, stranydict
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many seconds to wait for the control connection to be established
_connect_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
Outconn_FTP_Config_Defaults:'stranydict' = {
    'host': '',
    'port': CommonFTP.DEFAULT.PORT,
    'username': '',
    'use_ssl': False,
    'should_store_content': False,
}

# Config keys that must be integers but may arrive as strings from opaque storage
Outconn_FTP_Int_Config_Keys = ('port',)

# Config keys that must be booleans but may arrive as strings from opaque storage
Outconn_FTP_Bool_Config_Keys = ('use_ssl', 'should_store_content')

# Config keys that must be strings but may arrive as integers from opaque storage
Outconn_FTP_String_Config_Keys = ('host', 'username')

# ################################################################################################################################
# ################################################################################################################################

def parse_mlst_facts(facts_line:'str') -> 'stranydict':
    """ Turns one MLST or MLSD facts string, e.g. type=file;size=13;modify=20260820103000;, into a dict.
    """

    # Our response to produce
    out:'stranydict' = {}

    for item in facts_line.split(';'):
        if '=' in item:
            key, _, value = item.partition('=')
            out[key.lower()] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class FTPClient:
    """ Wraps access to remote FTP servers via the standard library's ftplib,
    using TLS for both the control and data connections when the connection has SSL enabled.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':

        self.config = config
        self.server = server

        self.id        = self.config.id        # type: int
        self.name      = self.config.name      # type: str
        self.is_active = self.config.is_active # type: bool

        self.host     = self.config.host     # type: str
        self.port     = self.config.port     # type: int
        self.username = self.config.username # type: str
        self.use_ssl  = self.config.use_ssl  # type: bool

        # The connection's password - it may be missing if the connection was created without one
        password = self.config.secret
        if password is None:
            password = ''
        self.password = password # type: str

        self.is_connected = True

# ################################################################################################################################

    def _connect(self) -> 'FTP':
        """ Opens a new control connection and logs in - each operation runs over its own connection.
        """

        # With SSL enabled, both the control and data connections are encrypted -
        # the certificate is not validated ..
        if self.use_ssl:
            tls_context = create_default_context()
            tls_context.check_hostname = False
            tls_context.verify_mode = CERT_NONE
            out = FTP_TLS(context=tls_context)
        else:
            out = FTP()

        # .. open the control connection ..
        _ = out.connect(self.host, self.port, timeout=_connect_timeout)

        # .. log in with the connection's credentials - with FTP_TLS, this secures the control channel first ..
        _ = out.login(self.username, self.password)

        # .. and with SSL on, the data connections are encrypted too.
        if self.use_ssl:
            tls_client = cast_('FTP_TLS', out)
            _ = tls_client.prot_p()

        return out

# ################################################################################################################################

    def _disconnect(self, ftp:'FTP') -> 'None':

        # A polite quit is attempted first but a server that already dropped the control
        # connection must not turn a completed operation into an error.
        try:
            _ = ftp.quit()
        except Exception:
            ftp.close()

# ################################################################################################################################

    def _exists_on(self, ftp:'FTP', remote_path:'str') -> 'bool':
        """ Whether the path exists, checked over an already established connection.
        """

        # The path exists only if the remote server can tell us anything about it.
        command = 'MLST ' + remote_path
        try:
            _ = ftp.sendcmd(command)
        except error_perm:
            out = False
        else:
            out = True

        return out

# ################################################################################################################################

    def ping(self) -> 'None':

        # Establish a connection, which runs the full login sequence with the remote server ..
        ftp = self._connect()

        # .. and send a no-op command to confirm that the server actually responds.
        try:
            _ = ftp.voidcmd('NOOP')
        finally:
            self._disconnect(ftp)

# ################################################################################################################################

    def connect(self) -> 'None':
        # We do not maintain long-running connections ourselves but we still ping the remote end
        # to make sure we are actually able to authenticate with it.
        self.ping()
        logger.info('FTP ping OK; name:`%s`, host:`%s`, port:`%s`', self.name, self.host, self.port)

# ################################################################################################################################

    def close(self) -> 'None':
        # There is nothing to close because each operation runs over its own connection.
        pass

# ################################################################################################################################

    def zato_delete_impl(self) -> 'None':
        self.close()

# ################################################################################################################################

    def stat(self, remote_path:'str') -> 'stranydict':
        """ Returns the MLST facts of a path, e.g. its type, size and modification time.
        """

        ftp = self._connect()

        command = 'MLST ' + remote_path
        try:
            response = ftp.sendcmd(command)
        finally:
            self._disconnect(ftp)

        # The response is multiline - the facts are on the line that begins with a space,
        # in the part that precedes the space separating them from the path itself.
        for line in response.splitlines():
            if line.startswith(' '):
                stripped = line.strip()
                parts = stripped.split(' ', 1)
                facts_line = parts[0]
                break
        else:
            raise Exception(f'No facts line in the MLST response -> `{response}`')

        out = parse_mlst_facts(facts_line)
        return out

# ################################################################################################################################

    def exists(self, remote_path:'str') -> 'bool':

        ftp = self._connect()

        try:
            out = self._exists_on(ftp, remote_path)
        finally:
            self._disconnect(ftp)

        return out

# ################################################################################################################################

    def scandir(self, remote_path:'str') -> 'anylist':
        """ Lists a directory, returning a list of (name, facts) tuples.
        """

        # Our response to produce
        out = []

        ftp = self._connect()

        try:
            entries = ftp.mlsd(remote_path)

            for name, facts in entries:

                # The directory itself and its parent are not part of its own contents.
                if facts['type'] in ('cdir', 'pdir'):
                    continue

                out.append((name, facts))

        finally:
            self._disconnect(ftp)

        return out

# ################################################################################################################################

    def read(self, remote_path:'str') -> 'bytes':

        buffer = BytesIO()

        ftp = self._connect()

        command = 'RETR ' + remote_path
        try:
            _ = ftp.retrbinary(command, buffer.write)
        finally:
            self._disconnect(ftp)

        out = buffer.getvalue()
        return out

# ################################################################################################################################

    def write(self, remote_path:'str', data:'bytes') -> 'None':

        ftp = self._connect()

        # A store always overwrites, which is what the STOR command does on its own.
        command = 'STOR ' + remote_path
        buffer = BytesIO(data)
        try:
            _ = ftp.storbinary(command, buffer)
        finally:
            self._disconnect(ftp)

# ################################################################################################################################

    def remove(self, remote_path:'str') -> 'None':

        ftp = self._connect()

        try:
            _ = ftp.delete(remote_path)
        finally:
            self._disconnect(ftp)

# ################################################################################################################################

    def rmdir(self, remote_path:'str') -> 'None':

        ftp = self._connect()

        try:
            _ = ftp.rmd(remote_path)
        finally:
            self._disconnect(ftp)

# ################################################################################################################################

    def makedirs(self, remote_path:'str', exist_ok:'bool' = False) -> 'None':

        ftp = self._connect()

        try:
            # Without exist_ok, a path that is already there is an error, same as with local file systems ..
            if not exist_ok:
                if self._exists_on(ftp, remote_path):
                    raise Exception(f'Path already exists -> `{remote_path}`')

            # .. and each component is now created in turn, skipping the ones that already exist.
            current = ''

            for part in remote_path.split('/'):

                if not part:
                    continue

                if current:
                    current = current + '/' + part
                else:
                    current = part

                try:
                    _ = ftp.mkd(current)
                except error_perm:
                    # The component may already exist, which is fine - anything else is a real error.
                    if not self._exists_on(ftp, current):
                        raise

        finally:
            self._disconnect(ftp)

# ################################################################################################################################

    def rename(self, from_path:'str', to_path:'str') -> 'None':

        ftp = self._connect()

        try:
            _ = ftp.rename(from_path, to_path)
        finally:
            self._disconnect(ftp)

# ################################################################################################################################
# ################################################################################################################################

class OutconnFTPWrapper(Wrapper):
    """ Wraps a queue of connections to FTP.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = f'{config.host}:{config.port}'
        super(OutconnFTPWrapper, self).__init__(config, 'outgoing FTP', server)

        # Every file this connection moves is recorded through this object.
        self.audit_log = AuditLog(server.name)

        # Whether the audited operations also keep the bytes of the files they moved -
        # the key may be absent in the stored config.
        if should_store_content := config.get('should_store_content'):
            self.should_store_content = should_store_content
        else:
            self.should_store_content = False

        # What a guaranteed delivery to this connection goes through. It is built from the connection's
        # id rather than its name because that is what a rename leaves alone.
        self.publisher = OutgoingPublisher(server, OutgoingType.FTP, config.id)

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('FTPClient', client)
            client.ping()

# ################################################################################################################################

    def add_client(self) -> 'None':
        try:
            conn = FTPClient(self.config, self.server)
        except Exception:
            exc = format_exc()
            logger.warning('FTP client could not be built `%s`', exc)
        else:
            _ = self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
