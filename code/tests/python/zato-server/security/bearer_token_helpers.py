# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric import rsa

# PyJWT
from jwt import encode as jwt_encode
from jwt.algorithms import RSAAlgorithm

# Zato
from zato.common.bearer_token_verifier import BearerTokenVerifier
from zato.common.model.security import BearerTokenVerifyConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

_rsa_public_exponent = 65537
_rsa_key_size = 2048

Issuer   = 'https://idp.example.com/realms/test'
Audience = 'test-audience'
JWKS_URL = 'https://idp.example.com/realms/test/protocol/openid-connect/certs'

Signing_Key_ID = 'test-signing-key'
Rotated_Key_ID = 'test-rotated-key'

Algorithm = 'RS256'

# How many seconds into the future test tokens expire by default
_default_expires_in = 300

# The signing key all happy-path tokens use
Signing_Key = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)

# A second key that stands in for a rotated IdP key
Rotated_Key = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)

# A key that is never published in any JWKS document - tokens signed with it must be rejected
Unpublished_Key = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)

# ################################################################################################################################
# ################################################################################################################################

def make_jwk(key:'any_', key_id:'str') -> 'stranydict':
    """ Returns a JWKS entry for the public part of the given RSA key.
    """
    public_key = key.public_key()

    out = RSAAlgorithm.to_jwk(public_key, as_dict=True)
    out['kid'] = key_id
    out['use'] = 'sig'
    out['alg'] = Algorithm

    return out

# ################################################################################################################################

def make_token(
    key:'any_',
    key_id:'strnone'=Signing_Key_ID,
    issuer:'str'=Issuer,
    audience:'str'=Audience,
    expires_in:'int'=_default_expires_in,
    extra_claims:'stranydict | None'=None,
    ) -> 'str':
    """ Returns a signed JWT with the given parameters.
    """
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(seconds=expires_in)

    claims:'stranydict' = {
        'iss': issuer,
        'aud': audience,
        'exp': expiry,
        'iat': now,
    }

    if extra_claims:
        claims.update(extra_claims)

    headers:'stranydict' = {}

    if key_id:
        headers['kid'] = key_id

    out = jwt_encode(claims, key, algorithm=Algorithm, headers=headers)
    return out

# ################################################################################################################################
# ################################################################################################################################

class FakeCache:
    """ A minimal stand-in for CacheAPI - only the get and set methods the verifier uses.
    """
    def __init__(self) -> 'None':
        self.data:'stranydict' = {}
        self.set_calls:'anylist' = []

    def get(self, key:'str') -> 'any_':
        return self.data.get(key)

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.data[key] = value
        self.set_calls.append((key, value, expiry))

# ################################################################################################################################
# ################################################################################################################################

class TestVerifier(BearerTokenVerifier):
    """ A verifier whose JWKS fetches are served from a configurable document instead of HTTP.
    """

    # This is not a test case for pytest to collect
    __test__ = False

    def __init__(self, cache:'any_', jwks_document:'stranydict') -> 'None':
        super().__init__(cache)
        self.jwks_document = jwks_document
        self.fetch_count = 0

    def _fetch_jwks_document(self, jwks_url:'str') -> 'stranydict':
        self.fetch_count += 1
        return self.jwks_document

# ################################################################################################################################
# ################################################################################################################################

def make_config(
    static_token:'str'='',
    issuer:'str'=Issuer,
    audience:'str'=Audience,
    claims:'stranydict | None'=None,
    ) -> 'BearerTokenVerifyConfig':
    """ Returns a verification config for the tests.
    """
    out = BearerTokenVerifyConfig()

    out.security_id = 123
    out.sec_def_name = 'test.bearer.def'
    out.static_token = static_token
    out.issuer = issuer
    out.jwks_url = JWKS_URL
    out.audience = audience
    out.claims = claims or {}

    return out

# ################################################################################################################################

def make_verifier(keys:'anylist | None'=None) -> 'TestVerifier':
    """ Returns a test verifier whose JWKS document contains the given keys.
    """
    if keys is None:
        keys = [make_jwk(Signing_Key, Signing_Key_ID)]

    out = TestVerifier(FakeCache(), {'keys': keys})
    return out

# ################################################################################################################################
# ################################################################################################################################
