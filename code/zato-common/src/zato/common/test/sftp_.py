# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from tempfile import mkdtemp

# Zato
from zato.common.sftp_local import LocalSFTPServer
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The passphrase protecting the encrypted client key - it is used as the connection's password in tests
Default_Key_Passphrase = 'Test.SFTP.Passphrase.1'

# ################################################################################################################################
# ################################################################################################################################

class SFTPTestServer(LocalSFTPServer):
    """ Starts a private, non-root SSH server with an SFTP subsystem on a random port for use in tests.
    """
    def __init__(self) -> 'None':

        # Everything the server needs lives in a temporary directory, and it listens on a free port
        base_dir = mkdtemp(prefix='zato-test-sftp-')
        port = get_free_port()

        super().__init__(base_dir, port)

        # A directory for the remote files that tests operate on, always through absolute paths
        self.files_dir = os.path.join(self.base_dir, 'files')
        os.mkdir(self.files_dir)

        # The passphrase of the encrypted client key
        self.password = Default_Key_Passphrase

        # The second client key, protected with self.password
        self.client_key_encrypted_path = os.path.join(self.base_dir, 'client_key_encrypted')

# ################################################################################################################################

    def get_client_key_paths(self) -> 'strlist':

        out = super().get_client_key_paths()
        out.append(self.client_key_encrypted_path)

        return out

# ################################################################################################################################

    def ensure_keys(self) -> 'None':

        # The host key and the plain client key come from the base class ..
        super().ensure_keys()

        # .. and the second client key is protected with a passphrase.
        self._ensure_key(self.client_key_encrypted_path, self.password)

# ################################################################################################################################

    def start(self) -> 'None':

        self.prepare()
        self.start_process()

        logger.info('Test SSH server started on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Stops the server and starts it again on the same port, with the same keys and the same files.
        """
        self.stop_process()
        self.start_process()

        logger.info('Test SSH server restarted on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def pause(self) -> 'None':
        """ Takes the server away without touching anything it uses, which is how a test asks
        for a server that cannot be reached for a while. Nothing else may be assumed about
        the state of what the server serves - resume brings it back exactly as it was.
        """
        self.stop_process()

        logger.info('Test SSH server paused on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Brings a paused server back on the same port, with the same keys and the same files.
        """
        self.start_process()

        logger.info('Test SSH server resumed on %s:%s (%s)', self.host, self.port, self.base_dir)

# ################################################################################################################################

    def stop(self) -> 'None':

        super().stop()

        logger.info('Test SSH server stopped (%s)', self.base_dir)

# ################################################################################################################################
# ################################################################################################################################
