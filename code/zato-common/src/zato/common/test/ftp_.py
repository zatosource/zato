# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from shutil import rmtree
from tempfile import mkdtemp
from threading import Thread
from time import sleep

# pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.ioloop import IOLoop
from pyftpdlib.servers import ThreadedFTPServer

# Zato
from zato.common.demo.file_transfer_server import write_self_signed_certificate
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

# How long a single probe connection may take, in seconds
_connect_timeout = 1.0

# Credentials for the test user
_default_username = 'zato_test_user'
_default_password = 'Test.FTP.Password.1'

# The permissions the test user has over the served directory - everything pyftpdlib knows
_user_permissions = 'elradfmwMT'

# ################################################################################################################################
# ################################################################################################################################

class FTPTestServer:
    """ Starts a private, non-root FTP server (pyftpdlib) on a random port for use in tests,
    speaking FTPS when built with use_ssl.
    """
    def __init__(self, use_ssl:'bool' = False) -> 'None':

        # A directory for the remote files that tests operate on - it is what the server serves
        self.files_dir = mkdtemp(prefix='zato-test-ftp-')

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()
        self.username = _default_username
        self.password = _default_password
        self.use_ssl = use_ssl

        # The certificate lives outside the served directory.
        if use_ssl:
            self.certificate_dir = mkdtemp(prefix='zato-test-ftp-tls-')
            self.certificate_path = write_self_signed_certificate(self.certificate_dir)
        else:
            self.certificate_dir = ''
            self.certificate_path = ''

        # The server object and its thread, both populated in .start.
        self.server:'ThreadedFTPServer | None' = None
        self.server_thread:'Thread | None' = None

# ################################################################################################################################

    def _wait_until_accepting_connections(self) -> 'None':

        # Keep trying until the server accepts connections or we run out of time.
        attempts = int(_start_timeout / _start_sleep_time)

        for _ in range(attempts):
            try:
                with socket.create_connection((self.host, self.port), timeout=_connect_timeout):
                    break
            except OSError:
                sleep(_start_sleep_time)
        else:
            # If we are here, the server never came up.
            raise Exception(f'FTP server did not start within {_start_timeout}s on {self.host}:{self.port}')

# ################################################################################################################################

    def _start_server(self) -> 'None':

        # The one test user may do everything over the served directory ..
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, self.files_dir, perm=_user_permissions)

        # .. each server gets a handler subclass of its own - the authorizer
        # .. and the certificate are class attributes ..
        if self.use_ssl:
            base_handler = TLS_FTPHandler
        else:
            base_handler = FTPHandler

        handler = type('ZatoTestFTPHandler', (base_handler,), {})
        handler.authorizer = authorizer

        # .. with SSL on, both the control and data channels are encrypted ..
        if self.use_ssl:
            handler.certfile = self.certificate_path

        # .. each session runs in its own thread - the private ioloop keeps this server
        # .. out of pyftpdlib's process-wide singleton loop, where a close issued by one
        # .. server could otherwise close sockets another server had just registered ..
        self.server = ThreadedFTPServer((self.host, self.port), handler, ioloop=IOLoop())

        # .. the blocking serve_forever loop runs in its own thread too ..
        self.server_thread = Thread(target=self.server.serve_forever, name='zato-test-ftp-server', daemon=True)
        self.server_thread.start()

        # .. and wait until it accepts connections.
        self._wait_until_accepting_connections()

# ################################################################################################################################

    def _stop_server(self) -> 'None':

        # Closing everything ends the serve_forever loop along with the listening socket ..
        if self.server:
            self.server.close_all()
            self.server = None

        # .. and then its thread has nothing left to do.
        if self.server_thread:
            self.server_thread.join(timeout=_start_timeout)
            self.server_thread = None

# ################################################################################################################################

    def start(self) -> 'None':

        self._start_server()

        logger.info('Test FTP server started on %s:%s (%s)', self.host, self.port, self.files_dir)

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Stops the server and starts it again on the same port, keeping the files it serves
        and dropping every session a client had open.
        """
        self._stop_server()
        self._start_server()

        logger.info('Test FTP server restarted on %s:%s (%s)', self.host, self.port, self.files_dir)

# ################################################################################################################################

    def pause(self) -> 'None':
        """ Stops the server without touching the directory it serves.
        """
        self._stop_server()

        logger.info('Test FTP server paused on %s:%s (%s)', self.host, self.port, self.files_dir)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Brings a paused server back on the same port, with the files it serves as they were.
        """
        self._start_server()

        logger.info('Test FTP server resumed on %s:%s (%s)', self.host, self.port, self.files_dir)

# ################################################################################################################################

    def stop(self) -> 'None':

        # Stop the server first ..
        self._stop_server()

        # .. and only then delete everything it used.
        rmtree(self.files_dir, ignore_errors=True)

        if self.certificate_dir:
            rmtree(self.certificate_dir, ignore_errors=True)

        logger.info('Test FTP server stopped (%s)', self.files_dir)

# ################################################################################################################################
# ################################################################################################################################
