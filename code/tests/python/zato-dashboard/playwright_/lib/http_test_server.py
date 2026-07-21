# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import ssl
import tempfile
import threading
import time
from base64 import b64decode
from datetime import datetime, timedelta, timezone
from http.client import OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# What the server responds with when a path has no explicit configuration
_Default_Response_Status = OK
_Default_Response_Body   = '{"result": "ok"}'

# All responses carry this content type
_Default_Content_Type = 'application/json'

# How long to wait for expected requests to arrive
_Request_Wait_Timeout = 10

# How long to sleep between polling attempts while waiting for requests
_Request_Poll_Interval = 0.2

# How long the self-signed certificate of the HTTPS variant remains valid
_Certificate_Valid_Days = 7

# The RSA key size for the self-signed certificate
_Certificate_Key_Size = 2048

# The public exponent for the RSA key above
_Certificate_Public_Exponent = 65537

# ################################################################################################################################
# ################################################################################################################################

class _RecordingHandler(BaseHTTPRequestHandler):
    """ Records every incoming request on the server object and responds according to per-path configuration.
    """

    protocol_version = 'HTTP/1.1'

    def _handle(self) -> 'None':

        # The server object carries the recorded requests and the response configuration
        server:'any_' = self.server

        # Split the raw path into its path and query string parts ..
        parts = urlsplit(self.path)
        path = parts.path
        query = dict(parse_qsl(parts.query))

        # .. read the body if one was sent ..
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            body_bytes = self.rfile.read(content_length)
            body = body_bytes.decode('utf-8')
        else:
            body = ''

        # .. record the request so tests can assert on it ..
        record = {
            'method': self.command,
            'path': path,
            'query': query,
            'headers': dict(self.headers.items()),
            'body': body,
        }

        # Subclasses may enrich the record, e.g. with the authenticated principal
        record.update(self._get_extra_record_fields())

        server.recorded_requests.append(record)

        # .. use the per-path configuration if there is one, defaulting otherwise ..
        if config := server.path_config.get(path):
            response_config = config
        else:
            response_config = server.default_config

        # .. an optional delay simulates a slow backend for timeout tests ..
        if response_config['delay']:
            time.sleep(response_config['delay'])

        # .. and send the response back.
        response_body = response_config['body'].encode('utf-8')
        body_length = len(response_body)

        self.send_response(response_config['status'])
        self.send_header('Content-Type', _Default_Content_Type)
        self.send_header('Content-Length', str(body_length))
        self.end_headers()

        # HEAD responses must not carry a body
        if self.command != 'HEAD':
            _ = self.wfile.write(response_body)

# ################################################################################################################################

    do_GET     = _handle
    do_POST    = _handle
    do_PUT     = _handle
    do_PATCH   = _handle
    do_DELETE  = _handle
    do_HEAD    = _handle
    do_OPTIONS = _handle

# ################################################################################################################################

    def _get_extra_record_fields(self) -> 'anydict':
        """ Extra fields subclasses may add to a recorded request.
        """
        return {}

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[http_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

class _RecordingServer(ThreadingHTTPServer):
    """ A threading HTTP server that carries the recorded requests and the per-path response configuration.
    """

    daemon_threads = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.recorded_requests:'anylist' = []
        self.path_config:'anydict' = {}

        self.default_config = {
            'status': _Default_Response_Status,
            'body': _Default_Response_Body,
            'delay': 0,
        }

# ################################################################################################################################
# ################################################################################################################################

class HTTPTestServer:
    """ A live HTTP server for outgoing REST connection tests. It records every request it receives
    and responds according to per-path configuration, which lets tests assert exactly what Zato sent.
    """

    def __init__(self) -> 'None':
        self.host = '127.0.0.1'
        self.port = 0
        self.scheme = 'http'
        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds the server to an ephemeral port and starts serving in a background thread.
        """

        # Bind to an ephemeral port ..
        self._httpd = _RecordingServer((self.host, 0), _RecordingHandler)

        # .. remember which port was assigned ..
        address = self._httpd.server_address
        self.port = address[1]

        # .. and serve in the background.
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[HTTPTestServer] started on %s://%s:%d', self.scheme, self.host, self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and closes its socket.
        """
        self._httpd.shutdown()
        self._httpd.server_close()

        logger.info('[HTTPTestServer] stopped on %s://%s:%d', self.scheme, self.host, self.port)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ The base address of the server, e.g. http://127.0.0.1:12345.
        """

        out = f'{self.scheme}://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        """ All requests recorded so far, each a dict of method, path, query, headers and body.
        """

        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################

    def clear_requests(self) -> 'None':
        """ Forgets all recorded requests.
        """
        self._httpd.recorded_requests.clear()

# ################################################################################################################################

    def set_response(
        self,
        path:'str',
        *,
        status:'int'=_Default_Response_Status,
        body:'str'=_Default_Response_Body,
        delay:'float'=0,
        ) -> 'None':
        """ Configures how the server responds to requests for the given path.
        """

        self._httpd.path_config[path] = {
            'status': status,
            'body': body,
            'delay': delay,
        }

# ################################################################################################################################

    def wait_for_request_count(self, count:'int', timeout:'float'=_Request_Wait_Timeout) -> 'anylist':
        """ Waits until at least the given number of requests has been recorded and returns them all.
        """

        deadline = time.monotonic() + timeout

        while True:
            recorded = self._httpd.recorded_requests
            recorded_count = len(recorded)

            # Stop as soon as enough requests arrived ..
            if recorded_count >= count:
                break

            # .. or when the deadline passes, in which case the caller's assertion fails with details.
            if time.monotonic() >= deadline:
                break

            time.sleep(_Request_Poll_Interval)

        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################
# ################################################################################################################################

def _build_self_signed_certificate(host:'str') -> 'tuple':
    """ Generates a self-signed certificate for the given host and returns paths
    to temporary files with the certificate and its private key.
    """

    # Generate the private key ..
    private_key = rsa.generate_private_key(
        public_exponent=_Certificate_Public_Exponent,
        key_size=_Certificate_Key_Size,
    )

    # .. build the certificate's subject, which is also its issuer since it is self-signed ..
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, host),
    ])

    now = datetime.now(timezone.utc)
    valid_until = now + timedelta(days=_Certificate_Valid_Days)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(subject)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(valid_until)

    # .. the host must also be present as a subject alternative name for TLS validation ..
    alternative_names = x509.SubjectAlternativeName([
        x509.DNSName(host),
    ])
    builder = builder.add_extension(alternative_names, critical=False)

    # .. sign the certificate with its own key ..
    certificate = builder.sign(private_key, hashes.SHA256())

    # .. serialize both to PEM ..
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    key_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    # .. and write them to temporary files for the SSL context to load.
    certificate_file = tempfile.NamedTemporaryFile(suffix='-cert.pem', delete=False)
    _ = certificate_file.write(certificate_pem)
    certificate_file.close()

    key_file = tempfile.NamedTemporaryFile(suffix='-key.pem', delete=False)
    _ = key_file.write(key_pem)
    key_file.close()

    out = certificate_file.name, key_file.name
    return out

# ################################################################################################################################
# ################################################################################################################################

class HTTPSTestServer(HTTPTestServer):
    """ The HTTPS variant of the recording test server, using a self-signed certificate
    generated at start, for validate_tls tests. With require_client_cert it turns into
    a mutual-TLS server backed by a full CA, for mTLS security definition tests.
    """

    def __init__(self, require_client_cert:'bool'=False) -> 'None':
        super().__init__()

        self.scheme = 'https'
        self.require_client_cert = require_client_cert

        # Set only in the mutual-TLS mode - the CA plus the server and client material.
        self.tls_material:'any_' = None

        # Set only in the plain HTTPS mode - the self-signed certificate and its key.
        self._certificate_path = ''
        self._key_path = ''

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the plain server first, then wraps its socket in TLS - with a fresh self-signed
        certificate by default or with CA-signed material and a mandatory client certificate
        in the mutual-TLS mode.
        """

        # Bind to an ephemeral port ..
        self._httpd = _RecordingServer((self.host, 0), _RecordingHandler)

        # .. remember which port was assigned ..
        address = self._httpd.server_address
        self.port = address[1]

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        if self.require_client_cert:

            # Imported here because the module lives in the shared SOAP test library,
            # which the suite's conftest puts on sys.path before any test runs.
            from certs import build_tls_material

            # Mutual TLS needs a full CA so the client certificate can chain up to it ..
            self.tls_material = build_tls_material(self.host)
            ssl_context.load_cert_chain(self.tls_material.server_certificate_path, self.tls_material.server_key_path)

            # .. and the client certificate is mandatory and pinned to that CA.
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(self.tls_material.ca_path)

        else:
            # Plain HTTPS only needs the self-signed certificate.
            self._certificate_path, self._key_path = _build_self_signed_certificate(self.host)
            ssl_context.load_cert_chain(self._certificate_path, self._key_path)

        # .. wrap the listening socket in TLS ..
        self._httpd.socket = ssl_context.wrap_socket(self._httpd.socket, server_side=True)

        # .. and serve in the background.
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[HTTPSTestServer] started on %s://%s:%d require_client_cert=%s',
            self.scheme, self.host, self.port, self.require_client_cert)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes the temporary certificate files.
        """
        super().stop()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)
        else:
            os.remove(self._certificate_path)
            os.remove(self._key_path)

# ################################################################################################################################
# ################################################################################################################################

class _SPNEGOHandler(_RecordingHandler):
    """ The accept side of the SPNEGO negotiation - a request without a Negotiate token
    receives the 401 challenge, a request with one has its token verified with GSSAPI
    against the server's service keytab.
    """

    # The authenticated client principal, set once the negotiation completes
    _spnego_principal = ''

    def _handle(self) -> 'None':

        server:'any_' = self.server

        # A client that has completed the negotiation carries its token in this header ..
        auth_header = self.headers.get('Authorization')

        if auth_header and auth_header.startswith('Negotiate '):

            # Imported here because the module is loaded lazily, only by suites that use it
            from gssapi.exceptions import GSSError

            # .. verify the token with the service credentials - a token that cannot
            # be verified, e.g. one minted against stale keys, counts as no token at all ..
            in_token = b64decode(auth_header[len('Negotiate '):])

            accept_context = server.build_accept_context()

            try:
                _ = accept_context.step(in_token)
            except GSSError:
                logger.info('[SPNEGOTestServer] token verification failed', exc_info=True)
            else:
                # .. a complete context means the client authenticated, so the request
                # is recorded with the principal and served as usual ..
                if accept_context.complete:
                    self._spnego_principal = str(accept_context.initiator_name)
                    super()._handle()
                    return

        # .. anything else receives the challenge that starts the negotiation.
        self._respond_with_challenge()

# ################################################################################################################################

    # The base class binds its verb handlers to its own _handle function directly,
    # which is why they are rebound here to the negotiating one.
    do_GET     = _handle
    do_POST    = _handle
    do_PUT     = _handle
    do_PATCH   = _handle
    do_DELETE  = _handle
    do_HEAD    = _handle
    do_OPTIONS = _handle

# ################################################################################################################################

    def _respond_with_challenge(self) -> 'None':
        """ Responds with the 401 challenge, draining the request body first so that
        the keep-alive connection stays usable for the client's retry.
        """
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            _ = self.rfile.read(content_length)

        self.send_response(UNAUTHORIZED)
        self.send_header('WWW-Authenticate', 'Negotiate')
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _get_extra_record_fields(self) -> 'anydict':
        out = {'spnego_principal': self._spnego_principal}
        return out

# ################################################################################################################################
# ################################################################################################################################

class SPNEGOTestServer(HTTPTestServer):
    """ The SPNEGO-protected variant of the recording test server - it performs the accept
    side of the negotiation with the given service principal and its keytab, so tests cover
    the full 401-negotiate-retry dance that outgoing connections perform.
    """

    def __init__(self, service_principal:'str', keytab_path:'str') -> 'None':
        super().__init__()

        self.service_principal = service_principal
        self.keytab_path = keytab_path

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds the server to an ephemeral port and starts serving in a background thread,
        with the SPNEGO handler in place of the plain recording one.
        """

        # Imported here because the underlying gssapi package needs system Kerberos
        # libraries which may be absent from installations that never run these tests.
        import gssapi

        service_principal = self.service_principal
        keytab_path = self.keytab_path

        # Each negotiation needs its own context, so the server object exposes a builder
        # instead of a single shared context.
        def build_accept_context() -> 'any_':
            name = gssapi.Name(service_principal, gssapi.NameType.hostbased_service)
            creds = gssapi.Credentials(name=name, store={'keytab': keytab_path}, usage='accept')

            out = gssapi.SecurityContext(creds=creds, usage='accept')
            return out

        # Bind to an ephemeral port ..
        self._httpd = _RecordingServer((self.host, 0), _SPNEGOHandler)
        self._httpd.build_accept_context = build_accept_context

        # .. remember which port was assigned ..
        address = self._httpd.server_address
        self.port = address[1]

        # .. and serve in the background.
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[SPNEGOTestServer] started on %s://%s:%d principal=%s',
            self.scheme, self.host, self.port, self.service_principal)

# ################################################################################################################################
# ################################################################################################################################
