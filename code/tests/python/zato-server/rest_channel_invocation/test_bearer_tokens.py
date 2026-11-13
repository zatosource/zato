# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels secured with bearer token definitions - static tokens and JWTs verified against a JWKS document.

# stdlib
import time
from http.client import OK

# Zato
from channel_definitions import Credentials, Paths, Security
from channel_suite import assert_unauthorized
from channel_tokens import new_foreign_key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from channel_suite import Suite
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_challenge = 'Bearer'
_subject = 'mary.johnson'

# ################################################################################################################################
# ################################################################################################################################

def _bearer(token:'str') -> 'strdict':
    out = {'Authorization': f'Bearer {token}'}
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_static_token(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Bearer_Static, _bearer(Credentials.Static_Token))

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.Bearer_Static
    assert security['type'] == 'oauth'

# ################################################################################################################################

def test_static_token_rejected(client:'ChannelClient') -> 'None':
    assert_unauthorized(client.get(Paths.Bearer_Static, _bearer('wrong-static-token')), _challenge)
    assert_unauthorized(client.get(Paths.Bearer_Static), _challenge)
    assert_unauthorized(client.get(Paths.Bearer_Static, {'Authorization': Credentials.Static_Token}), _challenge)

# ################################################################################################################################

def test_jwt(suite:'Suite') -> 'None':
    token = suite.provider.new_token(_subject)
    response = suite.client.get(Paths.Bearer_JWT, _bearer(token))

    assert response.status == OK
    security = response.json()['channel']['security']

    assert security['name'] == Security.Bearer_JWT
    assert security['type'] == 'oauth'
    assert security['username'] == 'test.channel.jwt.client'

# ################################################################################################################################

def test_jwt_expired(suite:'Suite') -> 'None':
    now = int(time.time())
    token = suite.provider.new_token(_subject, iat=now - 7200, exp=now - 3600)

    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

# ################################################################################################################################

def test_jwt_wrong_audience(suite:'Suite') -> 'None':
    token = suite.provider.new_token(_subject, aud='api.orders.example.com')
    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

# ################################################################################################################################

def test_jwt_wrong_issuer(suite:'Suite') -> 'None':
    token = suite.provider.new_token(_subject, iss='https://idp.example.org/other')
    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

# ################################################################################################################################

def test_jwt_wrong_signature(suite:'Suite') -> 'None':
    provider = suite.provider
    claims = provider.get_claims(_subject)

    # A key the JWKS document does not publish, under the identifier of the one it does ..
    token = provider.sign(claims, key=new_foreign_key())
    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

    # .. and a valid token with its signature altered.
    token = provider.new_token(_subject)
    header, payload, signature = token.split('.')
    altered = signature[:-4] + ('AAAA' if signature[-4:] != 'AAAA' else 'BBBB')

    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(f'{header}.{payload}.{altered}')), _challenge)

# ################################################################################################################################

def test_jwt_unknown_key_id(suite:'Suite') -> 'None':
    provider = suite.provider
    token = provider.sign(provider.get_claims(_subject), key_id='test.key.unknown')

    assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

# ################################################################################################################################

def test_jwt_malformed(suite:'Suite') -> 'None':

    for token in ('not-a-jwt', 'a.b.c', ''):
        assert_unauthorized(suite.client.get(Paths.Bearer_JWT, _bearer(token)), _challenge)

# ################################################################################################################################

def test_jwt_claims_matched(suite:'Suite') -> 'None':
    provider = suite.provider
    client = suite.client

    token = provider.new_token(_subject, **{Credentials.JWT_Claim_Name: Credentials.JWT_Claim_Value})
    response = client.get(Paths.Bearer_JWT_Claims, _bearer(token))

    assert response.status == OK
    assert response.json()['channel']['security']['name'] == Security.Bearer_JWT_Claims

# ################################################################################################################################

def test_jwt_claims_not_matched(suite:'Suite') -> 'None':
    provider = suite.provider
    client = suite.client

    token = provider.new_token(_subject, **{Credentials.JWT_Claim_Name: 'sales'})
    assert_unauthorized(client.get(Paths.Bearer_JWT_Claims, _bearer(token)), _challenge)

    token = provider.new_token(_subject)
    assert_unauthorized(client.get(Paths.Bearer_JWT_Claims, _bearer(token)), _challenge)

# ################################################################################################################################
# ################################################################################################################################
