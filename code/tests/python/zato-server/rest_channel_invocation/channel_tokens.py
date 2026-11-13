# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An identity provider for JWTs - an RSA key pair, a JWKS document with its public key
# served over HTTP, and tokens signed with its private key.

# stdlib
import json
import time
from http.client import NOT_FOUND, OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

# cryptography
from cryptography.hazmat.primitives.asymmetric import rsa

# PyJWT
import jwt as pyjwt
from jwt.algorithms import RSAAlgorithm

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_public_exponent = 65537
_key_size = 2048
_algorithm = 'RS256'
_jwks_path = '/jwks.json'
_host = '127.0.0.1'

# How long a token is valid for by default, in seconds
Token_Lifetime = 3600

# ################################################################################################################################
# ################################################################################################################################

class IdentityProvider:
    """ Signs JWTs and serves the JWKS document that verifies them.
    """

    def __init__(self) -> 'None':
        self.private_key = rsa.generate_private_key(public_exponent=_public_exponent, key_size=_key_size)
        self.key_id = 'test.key.' + CryptoManager.generate_hex_string()
        self.issuer = 'https://idp.example.com/' + CryptoManager.generate_hex_string()
        self.audience = 'api.customers.example.com'

        self.http_server:'any_' = None
        self.jwks_url = ''

        public_jwk = RSAAlgorithm.to_jwk(self.private_key.public_key(), as_dict=True)
        public_jwk['kid'] = self.key_id
        public_jwk['use'] = 'sig'
        public_jwk['alg'] = _algorithm

        self.jwks_document = json.dumps({'keys': [public_jwk]}).encode('utf-8')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts serving the JWKS document on a free port in a thread of its own.
        """
        document = self.jwks_document

        class _Handler(BaseHTTPRequestHandler):

            def do_GET(self) -> 'None':
                if self.path == _jwks_path:
                    self.send_response(OK)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(document)))
                    self.end_headers()
                    _ = self.wfile.write(document)
                else:
                    self.send_response(NOT_FOUND)
                    self.send_header('Content-Length', '0')
                    self.end_headers()

            def log_message(self, *args:'any_') -> 'None':
                pass

        self.http_server = ThreadingHTTPServer((_host, 0), _Handler)
        port = self.http_server.server_address[1]
        self.jwks_url = f'http://{_host}:{port}{_jwks_path}'

        thread = Thread(target=self.http_server.serve_forever, daemon=True)
        thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            self.http_server = None

# ################################################################################################################################

    def get_claims(self, subject:'str', **extra:'any_') -> 'anydict':
        """ Returns the claims of a token that is valid for this provider's issuer and audience.
        """
        now = int(time.time())

        out:'anydict' = {
            'iss': self.issuer,
            'aud': self.audience,
            'sub': subject,
            'iat': now,
            'exp': now + Token_Lifetime,
        }

        out.update(extra)
        return out

# ################################################################################################################################

    def sign(self, claims:'anydict', key:'any_' = None, key_id:'str' = '') -> 'str':
        """ Signs the claims with the provider's key, or with the key given.
        """
        if key is None:
            key = self.private_key

        if not key_id:
            key_id = self.key_id

        out = pyjwt.encode(claims, key, algorithm=_algorithm, headers={'kid': key_id})
        return out

# ################################################################################################################################

    def new_token(self, subject:'str', **extra:'any_') -> 'str':
        """ Returns a valid token for the given subject.
        """
        claims = self.get_claims(subject, **extra)
        out = self.sign(claims)
        return out

# ################################################################################################################################
# ################################################################################################################################

def new_foreign_key() -> 'any_':
    """ Returns an RSA private key that no JWKS document of the suite publishes.
    """
    out = rsa.generate_private_key(public_exponent=_public_exponent, key_size=_key_size)
    return out

# ################################################################################################################################
# ################################################################################################################################
