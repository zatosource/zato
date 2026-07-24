# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import json
import socket
import ssl
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from http.client import CREATED, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
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
    from zato.common.typing_ import anydict, dictlist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# How long the tokens the simulated Graph auth server issues remain valid, in seconds.
_token_lifetime = 3600

# How long the self-signed TLS certificate remains valid.
_certificate_lifetime_days = 2

# The URL path prefix of the Graph API the Teams simulator serves.
_api_prefix = '/v1.0'

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a TCP port that is free right now.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        _, port = sock.getsockname()

    return port

# ################################################################################################################################
# ################################################################################################################################

class SlackTestHandler(BaseHTTPRequestHandler):
    """ A local Slack Web API - chat.postMessage, auth.test and conversations.list over plain HTTP.
    """

    # The bot token this workspace accepts
    expected_token:'strnone' = None

    # Every chat.postMessage payload received so far
    messages:'dictlist' = []

    # What conversations.list answers with
    channel_names:'strlist' = []

    # Channels that report channel_not_found, for the failure-path tests
    broken_channels:'strlist' = []

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

# ################################################################################################################################

    def _read_json(self) -> 'anydict':
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Methods like auth.test arrive with no body at all.
        if body:
            out = json.loads(body)
        else:
            out = {}

        return out

# ################################################################################################################################

    def do_POST(self) -> 'None':

        # Every method call carries the bot token ..
        auth_header = self.headers.get('Authorization', '')
        expected_header = f'Bearer {self.expected_token}'

        if auth_header != expected_header:
            self._send_json(OK, {'ok': False, 'error': 'invalid_auth'})
            return

        # .. and dispatches on the method name in the path.
        if self.path == '/chat.postMessage':
            data = self._read_json()
            channel = data['channel']

            # A channel configured as broken reports the same error the real API would.
            if channel in self.broken_channels:
                self._send_json(OK, {'ok': False, 'error': 'channel_not_found'})
                return

            SlackTestHandler.messages.append(data)
            self._send_json(OK, {'ok': True, 'channel': channel})
            return

        if self.path == '/auth.test':
            self._send_json(OK, {'ok': True, 'team': 'Test Workspace'})
            return

        if self.path == '/conversations.list':
            channels = []
            for name in self.channel_names:
                channels.append({'name': name})

            self._send_json(OK, {'ok': True, 'channels': channels})
            return

        self._send_json(OK, {'ok': False, 'error': 'unknown_method'})

# ################################################################################################################################
# ################################################################################################################################

def start_slack_server(port:'int', token:'str', channel_names:'strlist') -> 'ThreadingHTTPServer':
    """ Starts the simulated Slack Web API in a background thread, over plain HTTP.
    """
    SlackTestHandler.expected_token = token
    SlackTestHandler.messages = []
    SlackTestHandler.channel_names = channel_names
    SlackTestHandler.broken_channels = []

    out = ThreadingHTTPServer(('127.0.0.1', port), SlackTestHandler)

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _make_tls_certificate() -> 'tuple':
    """ Generates a self-signed TLS certificate for 127.0.0.1 and returns paths to the certificate and its key.
    """

    # Generate the private key ..
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # .. it is self-signed so the subject and issuer are the same ..
    subject_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, '127.0.0.1')])

    # .. and it must be valid for the loopback address the simulator listens on ..
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
    certificate_directory = tempfile.mkdtemp(prefix='zato_rule_engine_jobs_tls_')

    certificate_path = Path(certificate_directory) / 'server.crt'
    private_key_path = Path(certificate_directory) / 'server.key'

    _ = certificate_path.write_bytes(certificate_pem)
    _ = private_key_path.write_bytes(private_key_pem)

    # .. and hand the paths back to our caller.
    return str(certificate_path), str(private_key_path)

# ################################################################################################################################
# ################################################################################################################################

class TeamsGraphTestHandler(BaseHTTPRequestHandler):
    """ A local Microsoft Graph - the OAuth token endpoint plus teams, channels and channel messages, over TLS.
    """

    # Credentials the token endpoint accepts
    expected_tenant_id:'strnone' = None
    expected_client_id:'strnone' = None
    expected_client_secret:'strnone' = None

    # The port this server listens on, used to build the URLs in the OpenID configuration
    port = 0

    # All the tokens issued so far, mapped to when they expire
    valid_tokens:'anydict' = {}

    # The simulated tenant's teams - each entry is {'id', 'displayName', 'channels': [{'id', 'displayName'}]}
    teams:'dictlist' = []

    # Every channel message received so far
    messages:'dictlist' = []

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

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

        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1]

        if token not in self.valid_tokens:
            return False

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

        # Reject requests whose credentials do not match ..
        if client_id != self.expected_client_id:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client', 'error_description': 'Unknown client ID'})
            return

        if client_secret != self.expected_client_secret:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client', 'error_description': 'Invalid client secret'})
            return

        # .. otherwise, issue a new token with an expiration time.
        token = 'token.' + CryptoManager.generate_hex_string()

        now = time.time()
        TeamsGraphTestHandler.valid_tokens[token] = now + _token_lifetime

        self._send_json(OK, {
            'token_type': 'Bearer',
            'expires_in': _token_lifetime,
            'ext_expires_in': _token_lifetime,
            'access_token': token,
        })

# ################################################################################################################################

    def _filtered(self, items:'dictlist', query:'str') -> 'dictlist':
        """ Applies an optional Graph-style displayName filter to a list of objects.
        """
        parameters = parse_qs(query)
        filter_values = parameters.get('$filter')

        # No filter returns everything ..
        if not filter_values:
            return items

        # .. a filter like "displayName eq 'Pricing'" keeps only the matching names.
        filter_text = filter_values[0]
        wanted_name = filter_text.split("'")[1]

        out = []
        for item in items:
            if item['displayName'] == wanted_name:
                out.append(item)

        return out

# ################################################################################################################################

    def _handle_graph_request(self, method:'str', path:'str', query:'str') -> 'None':
        """ The Graph API - teams, their channels and channel messages.
        The path is everything after the /v1.0 prefix.
        """
        segments = []

        for segment in path.split('/'):
            if segment:
                segments.append(segment)

        segment_count = len(segments)

        # GET /teams - list or filter the tenant's teams
        if segment_count == 1:
            if segments[0] == 'teams':
                if method == 'GET':
                    teams = []
                    for team in self.teams:
                        teams.append({'id': team['id'], 'displayName': team['displayName']})

                    matched = self._filtered(teams, query)
                    self._send_json(OK, {'value': matched})
                    return

        # Everything below is scoped to a single team
        if segment_count >= 3:
            if segments[0] == 'teams':
                team_id = segments[1]

                for team in self.teams:
                    if team['id'] == team_id:
                        break
                else:
                    self._send_json(NOT_FOUND, {'error': {'code': 'NotFound', 'message': f'No such team: {team_id}'}})
                    return

                # GET /teams/{team_id}/channels - list or filter the team's channels
                if segment_count == 3:
                    if segments[2] == 'channels':
                        if method == 'GET':
                            matched = self._filtered(team['channels'], query)
                            self._send_json(OK, {'value': matched})
                            return

                # POST /teams/{team_id}/channels/{channel_id}/messages - post a channel message
                if segment_count == 5:
                    if segments[2] == 'channels':
                        if segments[4] == 'messages':
                            if method == 'POST':
                                body = self._read_body()
                                payload = json.loads(body)

                                TeamsGraphTestHandler.messages.append({
                                    'team_id': team_id,
                                    'channel_id': segments[3],
                                    'payload': payload,
                                })

                                self._send_json(CREATED, {'id': 'message-id-001'})
                                return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(NOT_FOUND,
            {'error': {'code': 'ResourceNotFound', 'message': f'Unsupported request: {method} {self.path}'}})

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
            self._handle_graph_request(method, graph_path, parsed_path.query)
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

def start_teams_server(
    port:'int',
    tenant_id:'str',
    client_id:'str',
    client_secret:'str',
    teams:'dictlist',
    ) -> 'ThreadingHTTPServer':
    """ Starts the simulated Microsoft Graph in a background thread, over TLS -
    MSAL only accepts https authorities, so the clients turn certificate verification off.
    """
    TeamsGraphTestHandler.expected_tenant_id = tenant_id
    TeamsGraphTestHandler.expected_client_id = client_id
    TeamsGraphTestHandler.expected_client_secret = client_secret
    TeamsGraphTestHandler.port = port

    TeamsGraphTestHandler.valid_tokens = {}
    TeamsGraphTestHandler.teams = teams
    TeamsGraphTestHandler.messages = []

    out = ThreadingHTTPServer(('127.0.0.1', port), TeamsGraphTestHandler)

    certificate_path, private_key_path = _make_tls_certificate()

    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls_context.load_cert_chain(certificate_path, private_key_path)

    out.socket = tls_context.wrap_socket(out.socket, server_side=True)

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
