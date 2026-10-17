# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A local demo server for file transfers - one process with three listeners on 127.0.0.1, plain FTP,
# explicit FTPS and SMB, each in a thread of its own. It runs as
#
#   python -m zato.common.demo.file_transfer_server --config <path>
#
# and reads everything it needs from that JSON file:
#
#   host, ftp_port, ftps_port, smb_port - where the three listeners bind
#   certificate_path                    - the PEM file with the FTPS certificate and its key
#   pid_file_path, log_file_path        - where the process records its pid and writes its log
#   ftp_users                           - a list of {username, password, home}
#   smb_shares                          - a list of {name, path}
#   smb_users                           - a list of {username, password}

# stdlib
import logging
import os
import signal
import sys
from argparse import ArgumentParser
from binascii import hexlify
from datetime import datetime, timedelta, timezone
from json import loads
from threading import Event, Thread

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# impacket
from impacket.ntlm import compute_lmhash, compute_nthash
from impacket.smbserver import SimpleSMBServer

# pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.ioloop import IOLoop
from pyftpdlib.servers import ThreadedFTPServer

# Zato
from zato.common.util.local_server import wait_until_accepting_connections, write_pid_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.demo.file_transfer_server')

# ################################################################################################################################
# ################################################################################################################################

# What the process is run as, which is also how its command line is recognized later on
Module_Name = 'zato.common.demo.file_transfer_server'

# The name of the PEM file the certificate and its key are written to
Certificate_File_Name = 'ftp-server.pem'

# The permissions each FTP user has over its home directory - everything pyftpdlib knows
_ftp_user_permissions = 'elradfmwMT'

# How many days the self-signed certificate stays valid for
_certificate_validity_days = 3650

# How many bits go into the certificate's private key
_certificate_key_bits = 2048

# The RSA public exponent for the certificate's private key
_certificate_public_exponent = 65537

# How long a listener may take to accept connections after it was started, in seconds
_listener_start_timeout = 10.0

# How long to wait for a listener's thread to end once it was told to stop, in seconds
_thread_join_timeout = 10.0

# How often the main thread looks whether it was told to stop, in seconds
_stop_check_interval = 1.0

# The libraries log every command of every session at this level otherwise
_library_loggers = ['pyftpdlib', 'impacket']

_log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# ################################################################################################################################
# ################################################################################################################################

def write_self_signed_certificate(directory:'str') -> 'str':
    """ Writes a self-signed certificate with its private key into one PEM file and returns its path.
    """

    # A key for the certificate to sign ..
    key = rsa.generate_private_key(public_exponent=_certificate_public_exponent, key_size=_certificate_key_bits)

    # .. the certificate names this machine and nothing else ..
    common_name = x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')
    subject = x509.Name([common_name])
    now = datetime.now(timezone.utc)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(subject)

    public_key = key.public_key()
    builder = builder.public_key(public_key)

    serial_number = x509.random_serial_number()
    builder = builder.serial_number(serial_number)

    expiry = now + timedelta(days=_certificate_validity_days)
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(expiry)

    algorithm = hashes.SHA256()
    certificate = builder.sign(key, algorithm)

    # .. and both the key and the certificate go into the one file pyftpdlib reads.
    no_encryption = serialization.NoEncryption()
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=no_encryption,
    )
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)

    out = os.path.join(directory, Certificate_File_Name)

    with open(out, 'wb') as pem_file:
        _ = pem_file.write(key_pem)
        _ = pem_file.write(certificate_pem)

    os.chmod(out, 0o600)

    return out

# ################################################################################################################################
# ################################################################################################################################

class DemoFileTransferServer:
    """ The three listeners of the demo server, started and stopped together.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.host = config['host']

        # The servers and the threads they run in, populated in .start
        self.ftp_servers:'anylist' = []
        self.smb_server:'SimpleSMBServer | None' = None
        self.threads:'anylist' = []

# ################################################################################################################################

    def _build_authorizer(self) -> 'DummyAuthorizer':
        """ The FTP users, each with full permissions over its own home directory.
        """
        out = DummyAuthorizer()

        for user in self.config['ftp_users']:
            out.add_user(user['username'], user['password'], user['home'], perm=_ftp_user_permissions)

        return out

# ################################################################################################################################

    def _start_ftp_listener(self, port:'int', use_tls:'bool', authorizer:'DummyAuthorizer') -> 'None':

        # Each listener gets a handler subclass of its own - the authorizer and the certificate are class attributes ..
        if use_tls:
            base_handler = TLS_FTPHandler
            handler_name = 'ZatoDemoFTPSHandler'
        else:
            base_handler = FTPHandler
            handler_name = 'ZatoDemoFTPHandler'

        handler = type(handler_name, (base_handler,), {})
        handler.authorizer = authorizer

        # .. explicit FTPS refuses a login over a cleartext control channel and a transfer over a cleartext data channel ..
        if use_tls:
            tls_handler = handler
            tls_handler.certfile = self.config['certificate_path']
            tls_handler.tls_control_required = True
            tls_handler.tls_data_required = True

        # .. each listener has a private ioloop, so closing one of them never touches sockets of the other ..
        ioloop = IOLoop()
        server = ThreadedFTPServer((self.host, port), handler, ioloop=ioloop)
        self.ftp_servers.append(server)

        # .. the blocking serve_forever loop runs in a thread of its own ..
        thread = Thread(target=server.serve_forever, name=f'zato-demo-ftp-{port}', daemon=True)
        thread.start()
        self.threads.append(thread)

        # .. and the listener is ready once it accepts connections.
        wait_until_accepting_connections(port, self.host, _listener_start_timeout)

# ################################################################################################################################

    def _start_smb_listener(self) -> 'None':

        port = self.config['smb_port']

        # Build the server object ..
        self.smb_server = SimpleSMBServer(listenAddress=self.host, listenPort=port)

        # .. expose each share, backed by its directory ..
        for share in self.config['smb_shares']:
            self.smb_server.addShare(share['name'], share['path'], share['name'])

        # .. modern clients speak SMB2 or newer only ..
        self.smb_server.setSMB2Support(True)

        # .. per-connection threads must not block the shutdown if a client still has a session open ..
        self.smb_server.getServer().daemon_threads = True

        # .. users are authenticated against LM and NT hashes rather than plain-text passwords ..
        for user in self.config['smb_users']:

            password = user['password']

            lmhash = compute_lmhash(password)
            lmhash = hexlify(lmhash).decode('ascii')

            nthash = compute_nthash(password)
            nthash = hexlify(nthash).decode('ascii')

            self.smb_server.addCredential(user['username'], 0, lmhash, nthash)

        # .. serve_forever blocks, hence the server runs in its own thread ..
        thread = Thread(target=self.smb_server.start, name='zato-demo-smb', daemon=True)
        thread.start()
        self.threads.append(thread)

        # .. and the listener is ready once it accepts connections.
        wait_until_accepting_connections(port, self.host, _listener_start_timeout)

# ################################################################################################################################

    def start(self) -> 'None':

        # Both FTP listeners share the same users ..
        authorizer = self._build_authorizer()

        self._start_ftp_listener(self.config['ftp_port'], False, authorizer)
        self._start_ftp_listener(self.config['ftps_port'], True, authorizer)

        # .. and SMB has users of its own.
        self._start_smb_listener()

        logger.info('Demo file transfer server listening on %s - FTP %s, FTPS %s, SMB %s', self.host,
            self.config['ftp_port'], self.config['ftps_port'], self.config['smb_port'])

# ################################################################################################################################

    def stop(self) -> 'None':

        # Closing everything ends each FTP serve_forever loop along with its listening socket ..
        for server in self.ftp_servers:
            server.close_all()

        self.ftp_servers = []

        # .. shutdown ends the SMB serve_forever loop and stop closes its listening socket ..
        if self.smb_server:
            self.smb_server.getServer().shutdown()
            self.smb_server.stop()
            self.smb_server = None

        # .. and then the threads have nothing left to do.
        for thread in self.threads:
            thread.join(timeout=_thread_join_timeout)

        self.threads = []

        logger.info('Demo file transfer server stopped')

# ################################################################################################################################
# ################################################################################################################################

def _set_up_logging(log_file_path:'str') -> 'None':

    logging.basicConfig(filename=log_file_path, level=logging.INFO, format=_log_format)

    for name in _library_loggers:
        library_logger = logging.getLogger(name)
        library_logger.setLevel(logging.WARNING)

# ################################################################################################################################

def main() -> 'None':

    parser = ArgumentParser(description='A local demo server with FTP, FTPS and SMB listeners')
    _ = parser.add_argument('--config', required=True, help='Path to the JSON configuration file')

    args = parser.parse_args()

    with open(args.config, encoding='utf8') as config_file:
        data = config_file.read()

    config = loads(data)
    pid_file_path = config['pid_file_path']

    _set_up_logging(config['log_file_path'])

    # SIGTERM and SIGINT both mean that the process is to stop ..
    stop_event = Event()

    def _on_signal(signal_number:'int', frame:'any_') -> 'None':
        stop_event.set()

    _ = signal.signal(signal.SIGTERM, _on_signal)
    _ = signal.signal(signal.SIGINT, _on_signal)

    # .. start all the listeners ..
    server = DemoFileTransferServer(config)
    server.start()

    # .. record the pid only once everything listens ..
    pid = os.getpid()
    write_pid_file(pid_file_path, pid)

    # .. wait until told to stop ..
    while not stop_event.wait(_stop_check_interval):
        pass

    # .. and leave nothing behind.
    server.stop()

    if os.path.exists(pid_file_path):
        os.remove(pid_file_path)

    sys.exit(0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
