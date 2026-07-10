# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import shutil
import ssl
import threading
import time
from http.client import BAD_REQUEST, FOUND, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps
from urllib.parse import parse_qsl, urlencode, urlsplit

# cryptography
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# PyJWT
import jwt
from jwt.algorithms import RSAAlgorithm

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from certs import build_tls_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdict, stranydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TokenErrorMode:
    """ The failure modes the token endpoint can simulate.
    """
    Expired_Code = 'expired_code'
    Bad_Signature = 'bad_signature'
    Wrong_Audience = 'wrong_audience'
    Missing_Groups = 'missing_groups'

# ################################################################################################################################

class AuthorizeErrorMode:
    """ The failure modes the authorize endpoint can simulate.
    """

    # The user has no session with Microsoft and a silent sign-in is not possible
    Login_Required = 'login_required'

# ################################################################################################################################
# ################################################################################################################################

# How long the issued tokens claim to live
_token_expires_in = 3600

# The key ID the JWKS document publishes
_signing_key_id = 'entra-test-signing-key'

# RSA parameters for the generated signing keys
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# The algorithm the ID tokens are signed with
_id_token_algorithm = 'RS256'

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ A threading HTTP server simulating the Microsoft identity platform - OIDC discovery,
    the authorize and token endpoints and the JWKS document, with configurable failure modes.
    """
    daemon_threads = True

    def __init__(self, tenant_id:'str', client_id:'str', client_secret:'str', *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        # The signing key ID tokens are normally signed with ..
        self.signing_key = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)

        # .. and a second key, never published in the JWKS, for the bad-signature mode.
        self.unpublished_key = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)

        # The user the server signs in
        self.user_principal_name = ''
        self.user_display_name = ''
        self.user_groups:'strlist' = []

        # Failure modes - None means the flow succeeds
        self.authorize_error:'strnone' = None
        self.token_error:'strnone' = None

        # Codes the authorize endpoint has issued, each carrying its request's nonce
        self.issued_codes:'stranydict' = {}

        # Every request the server has received
        self.recorded_requests:'anylist' = []
        self.last_request:'anydict | None' = None

        # Filled in when the server starts, once the ephemeral port is known
        self.base_address = ''

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Clears the failure modes, the issued codes and the recorded requests - each test starts clean.
        """
        self.authorize_error = None
        self.token_error = None
        self.issued_codes.clear()
        self.recorded_requests.clear()
        self.last_request = None

# ################################################################################################################################

    @property
    def issuer(self) -> 'str':
        out = f'{self.base_address}/{self.tenant_id}/v2.0'
        return out

# ################################################################################################################################

    def get_discovery_document(self) -> 'anydict':
        """ Returns the OIDC discovery document, the way the real platform publishes it per tenant.
        """
        out = {
            'issuer': self.issuer,
            'authorization_endpoint': f'{self.base_address}/{self.tenant_id}/oauth2/v2.0/authorize',
            'token_endpoint': f'{self.base_address}/{self.tenant_id}/oauth2/v2.0/token',
            'jwks_uri': f'{self.base_address}/{self.tenant_id}/discovery/v2.0/keys',
            'response_types_supported': ['code', 'id_token', 'code id_token', 'id_token token'],
            'response_modes_supported': ['query', 'fragment', 'form_post'],
            'subject_types_supported': ['pairwise'],
            'id_token_signing_alg_values_supported': [_id_token_algorithm],
            'scopes_supported': ['openid', 'profile', 'email', 'offline_access'],
            'token_endpoint_auth_methods_supported': ['client_secret_post', 'client_secret_basic'],
        }
        return out

# ################################################################################################################################

    def get_jwks_document(self) -> 'anydict':
        """ Returns the JWKS document with the public part of the signing key.
        """
        public_key = self.signing_key.public_key()
        key = RSAAlgorithm.to_jwk(public_key, as_dict=True)

        key['kid'] = _signing_key_id
        key['use'] = 'sig'
        key['alg'] = _id_token_algorithm

        out = {'keys': [key]}
        return out

# ################################################################################################################################

    def issue_code(self, nonce:'str') -> 'str':
        """ Issues an authorization code, remembering the nonce the authorize request carried.
        """
        code = 'code-' + CryptoManager.generate_hex_string()
        self.issued_codes[code] = {'nonce': nonce}

        out = code
        return out

# ################################################################################################################################

    def build_id_token(self, nonce:'str') -> 'str':
        """ Builds an RS256-signed ID token for the configured user, honoring the active failure mode.
        """
        now = int(time.time())

        # The wrong-audience mode issues the token for another application ..
        if self.token_error == TokenErrorMode.Wrong_Audience:
            audience = 'another-application-' + CryptoManager.generate_hex_string()
        else:
            audience = self.client_id

        claims:'stranydict' = {
            'iss': self.issuer,
            'aud': audience,
            'iat': now,
            'nbf': now,
            'exp': now + _token_expires_in,
            'sub': 'subject-' + CryptoManager.generate_hex_string(),
            'oid': 'object-' + CryptoManager.generate_hex_string(),
            'tid': self.tenant_id,
            'ver': '2.0',
            'nonce': nonce,
            'preferred_username': self.user_principal_name,
            'name': self.user_display_name,
        }

        # .. the missing-groups mode leaves the groups claim out entirely ..
        if self.token_error != TokenErrorMode.Missing_Groups:
            claims['groups'] = self.user_groups

        # .. the bad-signature mode signs with a key the JWKS never published ..
        if self.token_error == TokenErrorMode.Bad_Signature:
            signing_key = self.unpublished_key
        else:
            signing_key = self.signing_key

        key_pem = signing_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

        out = jwt.encode(claims, key_pem, algorithm=_id_token_algorithm, headers={'kid': _signing_key_id})
        return out

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Parses each incoming request, records it, and routes it to the matching endpoint.
    """

    protocol_version = 'HTTP/1.1'

# ################################################################################################################################

    def _read_body(self) -> 'bytes':
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            out = self.rfile.read(length)
        else:
            out = b''
        return out

# ################################################################################################################################

    def _record(self, path:'str', params:'strdict', raw_body:'bytes') -> 'stranydict':
        """ Builds one request record tests can assert on.
        """
        record:'stranydict' = {
            'method': self.command,
            'path': path,
            'query': params,
            'raw_path': self.path,
            'headers': dict(self.headers.items()),
            'raw_body': raw_body,
            'form': None,
        }

        if raw_body:
            record['form'] = dict(parse_qsl(raw_body.decode('utf8'), keep_blank_values=True))

        return record

# ################################################################################################################################

    def _send_json(self, status:'int', payload:'anydict') -> 'None':
        body = dumps(payload).encode('utf8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        _ = self.wfile.write(body)

# ################################################################################################################################

    def _send_redirect(self, location:'str') -> 'None':
        self.send_response(FOUND)
        self.send_header('Location', location)
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _handle_authorize(self, params:'strdict') -> 'None':
        """ Plays the authorize endpoint - it either sends the browser back with a code,
        the way a silent SSO completion does, or reports that a sign-in is required.
        """
        server:'any_' = self.server

        redirect_uri = params['redirect_uri']
        state = params['state']

        # The application must be the one this server knows about ..
        if params['client_id'] != server.client_id:
            payload = {'error': 'unauthorized_client', 'error_description': 'Unknown client_id'}
            self._send_json(BAD_REQUEST, payload)
            return

        # .. a configured error goes back to the callback the way the real platform reports it ..
        if server.authorize_error == AuthorizeErrorMode.Login_Required:
            error_params = {
                'error': 'login_required',
                'error_description': 'AADSTS50058: A silent sign-in request was sent but no user is signed in.',
                'state': state,
            }
            encoded = urlencode(error_params)
            self._send_redirect(f'{redirect_uri}?{encoded}')
            return

        # .. otherwise the sign-in completes silently and a code travels back with the state.
        code = server.issue_code(params['nonce'])

        success_params = {
            'code': code,
            'state': state,
        }
        encoded = urlencode(success_params)
        self._send_redirect(f'{redirect_uri}?{encoded}')

# ################################################################################################################################

    def _handle_token(self, form:'strdict') -> 'None':
        """ Plays the token endpoint - an authorization code and the client secret in,
        a signed ID token out, unless a failure mode says otherwise.
        """
        server:'any_' = self.server

        # The grant must be an authorization code exchange ..
        if form['grant_type'] != 'authorization_code':
            payload = {'error': 'unsupported_grant_type', 'error_description': 'Only authorization_code is supported'}
            self._send_json(BAD_REQUEST, payload)
            return

        # .. the client must present the correct secret ..
        if form['client_secret'] != server.client_secret:
            payload = {'error': 'invalid_client', 'error_description': 'AADSTS7000215: Invalid client secret provided.'}
            self._send_json(UNAUTHORIZED, payload)
            return

        code = form['code']

        # .. the code must be one this server issued and it is single-use ..
        if code not in server.issued_codes:
            payload = {'error': 'invalid_grant', 'error_description': 'AADSTS70008: The provided grant is invalid.'}
            self._send_json(BAD_REQUEST, payload)
            return

        code_details = server.issued_codes.pop(code)

        # .. the expired-code mode rejects the exchange the way the real platform does ..
        if server.token_error == TokenErrorMode.Expired_Code:
            payload = {
                'error': 'invalid_grant',
                'error_description': 'AADSTS70008: The provided authorization code has expired.',
            }
            self._send_json(BAD_REQUEST, payload)
            return

        # .. and the tokens go out now.
        id_token = server.build_id_token(code_details['nonce'])
        access_token = 'access-' + CryptoManager.generate_hex_string()

        payload = {
            'token_type': 'Bearer',
            'scope': 'openid profile email',
            'expires_in': _token_expires_in,
            'ext_expires_in': _token_expires_in,
            'access_token': access_token,
            'id_token': id_token,
        }
        self._send_json(OK, payload)

# ################################################################################################################################

    def _handle(self) -> 'None':

        server:'any_' = self.server

        raw_body = self._read_body()

        split = urlsplit(self.path)
        path = split.path
        params = dict(parse_qsl(split.query, keep_blank_values=True))

        record = self._record(path, params, raw_body)

        server.recorded_requests.append(record)
        server.last_request = record

        discovery_path = f'/{server.tenant_id}/v2.0/.well-known/openid-configuration'
        authorize_path = f'/{server.tenant_id}/oauth2/v2.0/authorize'
        token_path = f'/{server.tenant_id}/oauth2/v2.0/token'
        keys_path = f'/{server.tenant_id}/discovery/v2.0/keys'

        if path == discovery_path:
            discovery = server.get_discovery_document()
            self._send_json(OK, discovery)

        elif path == authorize_path:
            self._handle_authorize(params)

        elif path == token_path:
            self._handle_token(record['form'])

        elif path == keys_path:
            jwks = server.get_jwks_document()
            self._send_json(OK, jwks)

        # .. anything else is not an endpoint this server serves.
        else:
            payload = {'error': 'not_found', 'error_description': f'No such path `{path}`'}
            self._send_json(NOT_FOUND, payload)

# ################################################################################################################################

    do_GET  = _handle
    do_POST = _handle

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[entra_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

class EntraTestServer:
    """ A live HTTPS server simulating Microsoft Entra ID for dashboard sign-in tests -
    OIDC discovery, silent-SSO authorize redirects, code-for-token exchanges with
    RS256-signed ID tokens, a JWKS document and configurable failure modes.
    """
    def __init__(self, tenant_id:'str', client_id:'str', client_secret:'str') -> 'None':
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        self.host = '127.0.0.1'
        self.port = 0

        self.tls_material:'any_' = None
        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves over TLS in a background thread -
        MSAL accepts https authorities only, so TLS is not optional here.
        """
        self._httpd = _Server(self.tenant_id, self.client_id, self.client_secret, (self.host, 0), _Handler)
        self.port = self._httpd.server_address[1]

        tls_material = build_tls_material(self.host)
        self.tls_material = tls_material

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(tls_material.server_certificate_path, tls_material.server_key_path)

        self._httpd.socket = ssl_context.wrap_socket(self._httpd.socket, server_side=True)

        # The discovery document and the issuer need the full base address.
        self._httpd.base_address = self.address

        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[EntraTestServer] started on %s', self.address)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes the temporary TLS material.
        """
        self._httpd.shutdown()
        self._httpd.server_close()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)

        logger.info('[EntraTestServer] stopped on %s', self.address)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'https://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    @property
    def ca_path(self) -> 'str':
        out = self.tls_material.ca_path
        return out

# ################################################################################################################################

    def set_user(self, user_principal_name:'str', display_name:'str', groups:'strlist') -> 'None':
        """ Configures the user the server signs in and the groups the ID token carries.
        """
        self._httpd.user_principal_name = user_principal_name
        self._httpd.user_display_name = display_name
        self._httpd.user_groups = groups

# ################################################################################################################################

    def set_authorize_error(self, mode:'str') -> 'None':
        self._httpd.authorize_error = mode

# ################################################################################################################################

    def set_token_error(self, mode:'str') -> 'None':
        self._httpd.token_error = mode

# ################################################################################################################################

    def reset(self) -> 'None':
        self._httpd.reset()

# ################################################################################################################################

    @property
    def last_request(self) -> 'anydict':
        out = self._httpd.last_request
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################
# ################################################################################################################################
