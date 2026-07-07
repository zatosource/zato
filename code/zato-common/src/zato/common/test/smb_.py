# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from binascii import hexlify
from logging import getLogger
from shutil import rmtree
from tempfile import mkdtemp
from threading import Thread
from time import sleep

# impacket
from impacket.ntlm import compute_lmhash, compute_nthash
from impacket.smbserver import SimpleSMBServer

# Zato
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the server to start accepting connections, in seconds
_start_timeout = 10.0

# How long to sleep between connection attempts while waiting for the server, in seconds
_start_sleep_time = 0.1

# Credentials for the test user
Default_Username = 'zato_test_user'
Default_Password = 'Test.SMB.Password.1'

# The name of the only share the server exposes
Default_Share_Name = 'zato_test_share'

# ################################################################################################################################
# ################################################################################################################################

class SMBTestServer:
    """ Starts a private, non-root SMB server (impacket's SimpleSMBServer) on a random port for use in tests.
    """
    def __init__(self) -> 'None':

        # A directory for the remote files that tests operate on - it backs the server's only share
        self.files_dir = mkdtemp(prefix='zato-test-smb-')

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()
        self.username = Default_Username
        self.password = Default_Password
        self.share_name = Default_Share_Name

        # The server object and its thread, both populated in .start
        self.server = None # type: SimpleSMBServer | None
        self.server_thread = None # type: Thread | None

# ################################################################################################################################

    def _wait_until_accepting_connections(self) -> 'None':

        # Keep trying until the server accepts connections or we run out of time
        attempts = int(_start_timeout / _start_sleep_time)

        for _ in range(attempts):
            try:
                with socket.create_connection((self.host, self.port), timeout=1.0):
                    return
            except OSError:
                sleep(_start_sleep_time)

        # If we are here, the server never came up
        raise Exception('SMB server did not start within {}s on {}:{}'.format(_start_timeout, self.host, self.port))

# ################################################################################################################################

    def start(self) -> 'None':

        # Build the server object ..
        self.server = SimpleSMBServer(listenAddress=self.host, listenPort=self.port)

        # .. expose one share backed by our temporary directory ..
        self.server.addShare(self.share_name, self.files_dir, 'Zato test share')

        # .. modern clients speak SMB2 or newer only ..
        self.server.setSMB2Support(True)

        # .. per-connection threads must not block the server's shutdown if a client
        # .. still has a session open when the test suite finishes ..
        self.server.getServer().daemon_threads = True

        # .. the server authenticates users against LM and NT hashes rather than plain-text passwords ..
        lmhash = hexlify(compute_lmhash(self.password)).decode('ascii')
        nthash = hexlify(compute_nthash(self.password)).decode('ascii')
        self.server.addCredential(self.username, 0, lmhash, nthash)

        # .. serve_forever blocks, hence the server runs in its own thread ..
        self.server_thread = Thread(target=self.server.start, name='zato-test-smb-server', daemon=True)
        self.server_thread.start()

        # .. and wait until it accepts connections.
        self._wait_until_accepting_connections()

        logger.info('Test SMB server started on %s:%s (%s)', self.host, self.port, self.files_dir)

# ################################################################################################################################

    def stop(self) -> 'None':

        # Stop the server first - shutdown ends the serve_forever loop and stop closes the listening socket ..
        if self.server:
            self.server.getServer().shutdown()
            self.server.stop()
            self.server = None

        # .. wait for its thread to finish ..
        if self.server_thread:
            self.server_thread.join(timeout=_start_timeout)
            self.server_thread = None

        # .. and only then delete everything it used.
        rmtree(self.files_dir, ignore_errors=True)

        logger.info('Test SMB server stopped (%s)', self.files_dir)

# ################################################################################################################################
# ################################################################################################################################
