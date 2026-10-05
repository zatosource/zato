# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from threading import Thread
from urllib.parse import parse_qs

# PyJWT
import jwt

# Zato
from zato.common.api import OAuth
from zato.common.bearer_token import BearerTokenManager
from zato.common.private_key_jwt import get_public_key_pem, load_private_key
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The client ID every test definition uses
Client_ID = 'test-client-id'

# The client secret of client secret definitions
Client_Secret = 'test-client-secret'

# The access token the fake endpoint hands out, followed by a counter so each token is distinct
Token_Prefix = 'test-access-token-'

# How long each token the fake endpoint hands out is valid for
Token_Expires_In = 3600

# ################################################################################################################################
# ################################################################################################################################

class TokenRequest:
    """ One token request the fake endpoint received, decoded from form data or JSON.
    """
    def __init__(self, body:'stranydict', headers:'stranydict') -> 'None':
        self.body = body
        self.headers = headers

# ################################################################################################################################
# ################################################################################################################################

class FakeTokenEndpoint:
    """ An in-process OAuth token endpoint - it accepts a client secret or a signed client assertion,
    verifies the assertion against the public keys it was given and remembers every request it saw.
    """

    def __init__(self) -> 'None':
        self.requests:'list[TokenRequest]' = []
        self.seen_jti:'set[str]' = set()
        self.token_counter = 0

        # Public keys by kid - an assertion whose kid is not here, or that has no kid, uses the default key
        self.public_keys:'dict[str, str]' = {}
        self.default_public_key = ''
        self.algorithms:'strlist' = list(OAuth.JWT_Algorithms)

        # What the aud claim of each assertion must be - the token URL unless a test says otherwise
        self.expected_audience = ''

        endpoint = self
        tokens = self._handle_token_request

        class Handler(BaseHTTPRequestHandler):

            def do_POST(self) -> 'None':
                length = int(self.headers['Content-Length'])
                raw = self.rfile.read(length).decode('utf8')
                content_type = self.headers['Content-Type']

                if content_type.startswith('application/json'):
                    body = loads(raw)
                else:
                    parsed = parse_qs(raw)
                    body = {}
                    for key, value in parsed.items():
                        body[key] = value[0]

                headers = {}
                for key, value in self.headers.items():
                    headers[key] = value

                endpoint.requests.append(TokenRequest(body, headers))
                status, response = tokens(body)

                payload = dumps(response).encode('utf8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                _ = self.wfile.write(payload)

            def log_message(self, format:'str', *args:'any_') -> 'None':
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

        self.port = self.server.server_address[1]
        self.url = f'http://127.0.0.1:{self.port}/oauth2/token'

# ################################################################################################################################

    def start(self) -> 'None':
        self.thread.start()

    def stop(self) -> 'None':
        self.server.shutdown()
        self.server.server_close()

# ################################################################################################################################

    def register_private_key(self, private_key_pem:'str', key_id:'str'='') -> 'None':
        """ Registers the public half of a private key, under its kid if given, as the default key otherwise.
        """
        key = load_private_key(private_key_pem)
        public_key_pem = get_public_key_pem(key)

        if key_id:
            self.public_keys[key_id] = public_key_pem
        else:
            self.default_public_key = public_key_pem

# ################################################################################################################################

    def _error(self, error:'str', description:'str') -> 'tuple[int, anydict]':
        out = 400, {'error': error, 'error_description': description}
        return out

# ################################################################################################################################

    def _next_token(self) -> 'anydict':
        self.token_counter += 1
        out = {
            'access_token': Token_Prefix + str(self.token_counter),
            'token_type': 'Bearer',
            'expires_in': Token_Expires_In,
        }
        return out

# ################################################################################################################################

    def _verify_assertion(self, assertion:'str') -> 'tuple[int, anydict] | None':
        """ Verifies a client assertion the way an authorization server does, returning an error response if it fails.
        """
        header = jwt.get_unverified_header(assertion)
        key_id = header.get('kid', '')

        if key_id:
            public_key = self.public_keys.get(key_id)
            if not public_key:
                return self._error('invalid_client', f'Unknown key ID `{key_id}`')
        else:
            public_key = self.default_public_key
            if not public_key:
                return self._error('invalid_client', 'No key registered for this client')

        audience = self.expected_audience
        if not audience:
            audience = self.url

        try:
            claims = jwt.decode(assertion, public_key, algorithms=self.algorithms, audience=audience)
        except jwt.PyJWTError as e:
            return self._error('invalid_client', f'Assertion rejected -> {e}')

        if claims['iss'] != Client_ID:
            return self._error('invalid_client', 'Issuer is not the client ID')

        if claims['sub'] != Client_ID:
            return self._error('invalid_client', 'Subject is not the client ID')

        jti = claims['jti']
        if jti in self.seen_jti:
            return self._error('invalid_client', f'Assertion replayed -> jti `{jti}`')
        self.seen_jti.add(jti)

        return None

# ################################################################################################################################

    def _handle_token_request(self, body:'stranydict') -> 'tuple[int, anydict]':

        if body.get('grant_type') != OAuth.Default.Grant_Type:
            return self._error('unsupported_grant_type', 'Only client_credentials is supported')

        if body.get('client_id') != Client_ID:
            return self._error('invalid_client', 'Unknown client')

        # A signed assertion takes precedence - a client that sends one must not send a secret as well
        if 'client_assertion' in body:

            if body.get('client_assertion_type') != OAuth.Assertion_Type:
                return self._error('invalid_request', 'Wrong client_assertion_type')

            if 'client_secret' in body:
                return self._error('invalid_request', 'Both a client secret and an assertion were sent')

            error = self._verify_assertion(body['client_assertion'])
            if error:
                return error

        else:
            if body.get('client_secret') != Client_Secret:
                return self._error('invalid_client', 'Wrong client secret')

        out = 200, self._next_token()
        return out

# ################################################################################################################################
# ################################################################################################################################

class FakeCache:
    """ The subset of the server's cache API the token manager uses.
    """
    def __init__(self) -> 'None':
        self.data:'anydict' = {}
        self.expiries:'dict[str, int]' = {}

    def get(self, key:'str') -> 'any_':
        out = self.data.get(key)
        return out

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.data[key] = value
        self.expiries[key] = expiry

# ################################################################################################################################

class FakeConfigManager:
    def __init__(self) -> 'None':
        self.cache_api = FakeCache()

# ################################################################################################################################

class FakeServer:
    """ The subset of a server the token manager uses - its cache and its ability to decrypt a stored key.
    """
    def __init__(self) -> 'None':
        self.security_facade = None
        self.config_manager = FakeConfigManager()
        self.decrypt_calls = 0

    def decrypt(self, data:'str') -> 'str':
        self.decrypt_calls += 1
        return data

# ################################################################################################################################
# ################################################################################################################################

def make_manager() -> 'tuple[BearerTokenManager, FakeServer]':
    """ Returns a token manager bound to a fake server.
    """
    server = FakeServer()
    manager = BearerTokenManager(cast_('any_', server))
    out = manager, server
    return out

# ################################################################################################################################

def make_sec_def(endpoint:'FakeTokenEndpoint', name:'str'='test.bearer.def', **extra:'any_') -> 'stranydict':
    """ Returns a client secret definition pointed at the fake endpoint, with any field overridden by the caller.
    """
    out:'stranydict' = {
        'name': name,
        'username': Client_ID,
        'password': Client_Secret,
        'auth_server_url': endpoint.url,
        'client_id_field': OAuth.Default.Client_ID_Field,
        'client_secret_field': OAuth.Default.Client_Secret_Field,
        'grant_type': OAuth.Default.Grant_Type,
        'scopes': '',
        'extra_fields': '',
        'data_format': 'form',
    }
    out.update(extra)
    return out

# ################################################################################################################################

def make_private_key_jwt_sec_def(
    endpoint:'FakeTokenEndpoint',
    private_key_pem:'str',
    jwt_algorithm:'str'=OAuth.Default.JWT_Algorithm,
    key_id:'str'='',
    name:'str'='test.bearer.private.key.jwt',
    **extra:'any_',
) -> 'stranydict':
    """ Returns a private key JWT definition pointed at the fake endpoint - it has no usable client secret at all.
    """
    out = make_sec_def(
        endpoint,
        name=name,
        password='',
        client_auth_method=OAuth.Client_Auth_Method.Private_Key_JWT,
        private_key=private_key_pem,
        jwt_algorithm=jwt_algorithm,
        key_id=key_id,
        **extra,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
