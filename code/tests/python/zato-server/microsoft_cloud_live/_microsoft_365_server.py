# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import json
import os
import ssl
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from http.client import ACCEPTED, BAD_REQUEST, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# How long the tokens this server issues remain valid, in seconds.
_token_lifetime = 3600

# How long short-lived tokens remain valid, in seconds - these exercise the token renewal path.
_short_token_lifetime = 4

# How long the self-signed TLS certificate remains valid.
_certificate_lifetime_days = 2

# The URL path prefix of the Graph API this server simulates.
_api_prefix = '/v1.0'

# The ID of the default calendar each simulated mailbox has.
_default_calendar_id = 'calendar-main'

# ################################################################################################################################
# ################################################################################################################################

def _build_initial_users() -> 'list':
    """ Returns the directory users the simulated tenant starts with.
    """
    return [
        {
            'id': 'user-id-001',
            'displayName': 'Maria Garcia',
            'givenName': 'Maria',
            'surname': 'Garcia',
            'mail': 'maria.garcia@example.com',
            'userPrincipalName': 'maria.garcia@example.com',
            'businessPhones': [],
        },
        {
            'id': 'user-id-002',
            'displayName': 'James Wilson',
            'givenName': 'James',
            'surname': 'Wilson',
            'mail': 'james.wilson@example.com',
            'userPrincipalName': 'james.wilson@example.com',
            'businessPhones': [],
        },
    ]

# ################################################################################################################################

def _build_initial_events() -> 'list':
    """ Returns the calendar events the simulated default calendar starts with.
    """
    return [
        {
            'id': 'event-id-001',
            'subject': 'Quarterly planning',
            'isAllDay': False,
            'start': {'dateTime': '2026-07-15T09:00:00', 'timeZone': 'UTC'},
            'end': {'dateTime': '2026-07-15T10:30:00', 'timeZone': 'UTC'},
            'body': {'contentType': 'html', 'content': 'Planning for the next quarter'},
            'attendees': [],
        },
        {
            'id': 'event-id-002',
            'subject': 'Customer onboarding call',
            'isAllDay': False,
            'start': {'dateTime': '2026-07-16T14:00:00', 'timeZone': 'UTC'},
            'end': {'dateTime': '2026-07-16T15:00:00', 'timeZone': 'UTC'},
            'body': {'contentType': 'html', 'content': 'Walking a new customer through the setup'},
            'attendees': [],
        },
    ]

# ################################################################################################################################
# ################################################################################################################################

def _make_tls_certificate() -> 'tuple':
    """ Generates a self-signed TLS certificate for 127.0.0.1 and returns paths to the certificate and its key.
    """

    # Generate the private key ..
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # .. describe who the certificate is for - it is self-signed so the subject and issuer are the same ..
    subject_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, '127.0.0.1')])

    # .. the certificate must be valid for the loopback address the test server listens on ..
    alternative_names = x509.SubjectAlternativeName([
        x509.DNSName('localhost'),
        x509.IPAddress(ipaddress.IPv4Address('127.0.0.1')),
    ])

    now = datetime.now(timezone.utc)
    not_valid_after = now + timedelta(days=_certificate_lifetime_days)

    # .. build and sign the certificate ..
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject_name)
    builder = builder.issuer_name(subject_name)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(not_valid_after)
    builder = builder.add_extension(alternative_names, critical=False)

    certificate = builder.sign(private_key, hashes.SHA256())

    # .. serialize both to PEM ..
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    private_key_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    # .. write them out to a temporary directory ..
    certificate_directory = tempfile.mkdtemp(prefix='zato_microsoft_cloud_tls_')

    certificate_path = os.path.join(certificate_directory, 'server.crt')
    private_key_path = os.path.join(certificate_directory, 'server.key')

    with open(certificate_path, 'wb') as certificate_file:
        _ = certificate_file.write(certificate_pem)

    with open(private_key_path, 'wb') as private_key_file:
        _ = private_key_file.write(private_key_pem)

    # .. and hand the paths back to our caller.
    return certificate_path, private_key_path

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365TestHandler(BaseHTTPRequestHandler):

    # Credentials the token endpoint accepts
    expected_tenant_id:'strnone' = None
    expected_client_id:'strnone' = None
    expected_client_secret:'strnone' = None

    # A client that is issued short-lived tokens, used to exercise the token renewal path
    short_lived_client_id:'strnone' = None

    # The port this server listens on, used to build the URLs in the OpenID configuration
    port = 0

    # All the tokens issued so far, mapped to when they expire
    valid_tokens:'anydict' = {}

    # How many tokens were issued to each client ID
    issued_token_counts:'anydict' = {}

    # The state of the simulated tenant
    users:'list' = []
    events:'list' = []

    # Payloads that the sendMail endpoint received
    sent_messages:'list' = []

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    @classmethod
    def invalidate_tokens(class_) -> 'None':
        """ Makes all the previously issued tokens invalid, which forces clients to obtain new ones.
        """
        class_.valid_tokens = {}

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

# ################################################################################################################################

    def _send_empty(self, status:'int') -> 'None':
        self.send_response(status)
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _read_body(self) -> 'bytes':
        content_length = int(self.headers.get('Content-Length', 0))
        out = self.rfile.read(content_length)
        return out

# ################################################################################################################################

    def _check_token(self) -> 'bool':
        """ Confirms the request carries a valid, non-expired bearer token.
        """
        auth_header = self.headers.get('Authorization', '')

        # No bearer token at all
        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1]

        # A token we never issued, e.g. one that was invalidated in the meantime
        if token not in self.valid_tokens:
            return False

        # A token that has already expired
        now = time.time()
        expiration_time = self.valid_tokens[token]
        if now >= expiration_time:
            return False

        return True

# ################################################################################################################################

    def _handle_openid_configuration_request(self) -> 'None':
        """ The OpenID discovery document MSAL downloads before it requests any tokens.
        """
        base_url = f'https://127.0.0.1:{self.port}/{self.expected_tenant_id}'

        self._send_json(OK, {
            'issuer': f'{base_url}/v2.0',
            'authorization_endpoint': f'{base_url}/oauth2/v2.0/authorize',
            'token_endpoint': f'{base_url}/oauth2/v2.0/token',
        })

# ################################################################################################################################

    def _handle_token_request(self) -> 'None':
        """ An Azure-AD-style OAuth2 token endpoint for the client credentials grant.
        """
        body = self._read_body()
        form_data = parse_qs(body.decode('utf-8'))

        client_id = form_data.get('client_id', [''])[0]
        client_secret = form_data.get('client_secret', [''])[0]

        # Both the main client and the short-lived one are recognized ..
        known_client_ids = {self.expected_client_id, self.short_lived_client_id}

        # .. reject requests whose credentials do not match ..
        if client_id not in known_client_ids:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client', 'error_description': 'Unknown client ID'})
            return

        if client_secret != self.expected_client_secret:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client', 'error_description': 'Invalid client secret'})
            return

        # .. the short-lived client gets tokens that expire almost immediately ..
        if client_id == self.short_lived_client_id:
            token_lifetime = _short_token_lifetime
        else:
            token_lifetime = _token_lifetime

        # .. otherwise, issue a new token with an expiration time ..
        token = 'token.' + CryptoManager.generate_hex_string()

        now = time.time()
        Microsoft365TestHandler.valid_tokens[token] = now + token_lifetime

        # .. keep track of how many tokens each client received ..
        token_count = Microsoft365TestHandler.issued_token_counts.get(client_id, 0)
        Microsoft365TestHandler.issued_token_counts[client_id] = token_count + 1

        self._send_json(OK, {
            'token_type': 'Bearer',
            'expires_in': token_lifetime,
            'ext_expires_in': token_lifetime,
            'access_token': token,
        })

# ################################################################################################################################

    def _handle_graph_request(self, method:'str', path:'str') -> 'None':
        """ The Graph API - users, mailboxes and calendars.
        The path is everything after the /v1.0 prefix, e.g. /users/maria.garcia@example.com/sendMail.
        """
        segments = []

        for segment in path.split('/'):
            if segment:
                segments.append(segment)

        segment_count = len(segments)

        # GET /organization - the tenant's organization details, used by the direct REST call test
        if segment_count == 1:
            if segments[0] == 'organization':
                if method == 'GET':
                    self._send_json(OK, {'value': [{
                        'id': 'organization-id-001',
                        'displayName': 'Test Organization',
                    }]})
                    return

        # GET /users - list the directory users
        if segment_count == 1:
            if segments[0] == 'users':
                if method == 'GET':
                    self._send_json(OK, {'value': self.users})
                    return

        # Anything below this point is scoped to a single user
        if segment_count >= 3:
            if segments[0] == 'users':

                # POST /users/{email}/sendMail - send an email from the user's mailbox
                if segments[2] == 'sendMail':
                    if method == 'POST':
                        body = self._read_body()
                        payload = json.loads(body)

                        Microsoft365TestHandler.sent_messages.append({
                            'email_from': segments[1],
                            'payload': payload,
                        })

                        self._send_empty(ACCEPTED)
                        return

                # GET /users/{email}/calendar - the user's default calendar
                if segments[2] == 'calendar':
                    if method == 'GET':
                        self._send_json(OK, {
                            'id': _default_calendar_id,
                            'name': 'Calendar',
                            'canEdit': True,
                        })
                        return

                # GET /users/{email}/calendars/{calendar_id}/events - the calendar's events
                if segment_count == 5:
                    if segments[2] == 'calendars':
                        if segments[4] == 'events':
                            if method == 'GET':
                                self._send_json(OK, {'value': self.events})
                                return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_request(self, method:'str') -> 'None':

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # The OpenID discovery document requires no bearer token.
        openid_configuration_path = f'/{self.expected_tenant_id}/v2.0/.well-known/openid-configuration'
        if path == openid_configuration_path:
            if method == 'GET':
                self._handle_openid_configuration_request()
                return

        # Neither does the token endpoint - it is where tokens come from.
        token_path = f'/{self.expected_tenant_id}/oauth2/v2.0/token'
        if path == token_path:
            if method == 'POST':
                self._handle_token_request()
                return

        # Everything else is the Graph API which requires a valid token ..
        if not self._check_token():
            self._send_json(UNAUTHORIZED,
                {'error': {'code': 'InvalidAuthenticationToken', 'message': 'Access token is missing or invalid'}})
            return

        # .. dispatch anything under the Graph prefix.
        if path.startswith(_api_prefix):
            graph_path = path[len(_api_prefix):]
            self._handle_graph_request(method, graph_path)
            return

        # No handler matched the path.
        self._send_json(NOT_FOUND, {'error': {'code': 'ResourceNotFound', 'message': f'No such path: {path}'}})

# ################################################################################################################################

    def do_GET(self) -> 'None':
        self._handle_request('GET')

# ################################################################################################################################

    def do_POST(self) -> 'None':
        self._handle_request('POST')

# ################################################################################################################################
# ################################################################################################################################

def start_microsoft_365_server(
    port:'int',
    tenant_id:'str',
    client_id:'str',
    client_secret:'str',
    short_lived_client_id:'str',
    ) -> 'tuple':
    """ Starts the simulated Microsoft 365 cloud in a background thread, over TLS. Returns (server, thread).
    """
    Microsoft365TestHandler.expected_tenant_id = tenant_id
    Microsoft365TestHandler.expected_client_id = client_id
    Microsoft365TestHandler.expected_client_secret = client_secret
    Microsoft365TestHandler.short_lived_client_id = short_lived_client_id
    Microsoft365TestHandler.port = port

    Microsoft365TestHandler.valid_tokens = {}
    Microsoft365TestHandler.issued_token_counts = {}
    Microsoft365TestHandler.users = _build_initial_users()
    Microsoft365TestHandler.events = _build_initial_events()
    Microsoft365TestHandler.sent_messages = []

    server = ThreadingHTTPServer(('127.0.0.1', port), Microsoft365TestHandler)

    # MSAL only accepts https authorities, so the server must speak TLS,
    # which is why the clients turn certificate verification off in their configuration.
    certificate_path, private_key_path = _make_tls_certificate()

    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls_context.load_cert_chain(certificate_path, private_key_path)

    server.socket = tls_context.wrap_socket(server.socket, server_side=True)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
