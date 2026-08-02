# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK, UNAUTHORIZED

# cryptography
from cryptography.hazmat.primitives.asymmetric import rsa

# PyJWT
import jwt as pyjwt

# Requests
import requests

# Zato
from zato.common.bearer_token_verifier import JWKS_Fetch_Interval

# Zato - test helpers
import keycloak_

from conftest import build_config_yaml, run_enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Timeout for HTTP requests to the server under test, in seconds
_http_timeout = 30

# How much longer than the token lifespan to wait before using an expired token, in seconds
_expiry_wait_extra = 1.5

# How long to wait after key rotation for Keycloak to publish the new key, in seconds
_rotation_settle_seconds = 1

# How long the server may take to pick up a rotated key, in seconds. The verifier fetches one JWKS
# URL at most once per JWKS_Fetch_Interval, so a key rotated to right after a fetch only becomes
# visible once that interval has passed, with a margin for the fetch itself.
_rotation_pickup_timeout = JWKS_Fetch_Interval + 15

# How often to retry while waiting for a rotated key to be picked up, in seconds
_rotation_poll_interval = 2

# ################################################################################################################################
# ################################################################################################################################

def _get(url:'str', token:'str') -> 'any_':
    """ Invokes a channel with the given bearer token.
    """
    headers = {'Authorization': f'Bearer {token}'}

    out = requests.get(url, headers=headers, timeout=_http_timeout)
    return out

# ################################################################################################################################

def _get_until_ok(url:'str', client_id:'str', secret:'str', timeout:'int') -> 'any_':
    """ Invokes a channel with a freshly issued token until it answers 200 or the timeout expires,
    returning the last response either way.
    """
    deadline = time.monotonic() + timeout

    while True:

        token = keycloak_.get_token(client_id, secret)
        response = _get(url, token)

        # The channel accepted the token, so there is nothing left to wait for ..
        if response.status_code == OK:
            return response

        # .. and once the deadline has passed the last response is what the caller asserts on.
        if time.monotonic() >= deadline:
            return response

        time.sleep(_rotation_poll_interval)

# ################################################################################################################################

def _assert_unauthorized(response:'any_') -> 'None':
    """ Asserts that a response is a 401 with the RFC 6750 Bearer challenge.
    """
    assert response.status_code == UNAUTHORIZED, f'Expected 401, got {response.status_code} -> {response.text}'

    challenge = response.headers['WWW-Authenticate']
    assert challenge == 'Bearer', f'Expected a Bearer challenge, got {challenge}'

# ################################################################################################################################
# ################################################################################################################################

def test_static_happy_path(zato_server:'stranydict') -> 'None':

    static_token = zato_server['static_token']
    response = _get(zato_server['static_url'], static_token)

    assert response.status_code == OK, response.text

# ################################################################################################################################

def test_static_wrong_token(zato_server:'stranydict') -> 'None':

    response = _get(zato_server['static_url'], 'this-is-not-the-configured-token')

    _assert_unauthorized(response)

# ################################################################################################################################

def test_static_missing_header(zato_server:'stranydict') -> 'None':

    response = requests.get(zato_server['static_url'], timeout=_http_timeout)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_happy_path(zato_server:'stranydict') -> 'None':

    token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
    response = _get(zato_server['jwt_url'], token)

    assert response.status_code == OK, response.text

# ################################################################################################################################

def test_jwt_wrong_audience(zato_server:'stranydict') -> 'None':

    token = keycloak_.get_token(keycloak_.Client_Wrong_Audience, keycloak_.Secret_Wrong_Audience)
    response = _get(zato_server['jwt_url'], token)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_wrong_issuer(zato_server:'stranydict') -> 'None':

    # This token comes from the second realm, so its issuer does not match the definition
    token = keycloak_.get_token(keycloak_.Client_Other_Realm, keycloak_.Secret_Other_Realm, realm=keycloak_.Realm_Other)
    response = _get(zato_server['jwt_url'], token)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_claim_mismatch(zato_server:'stranydict') -> 'None':

    # This token carries department=Sales while the definition requires Accounting
    token = keycloak_.get_token(keycloak_.Client_Sales, keycloak_.Secret_Sales)
    response = _get(zato_server['jwt_url'], token)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_expired(zato_server:'stranydict') -> 'None':

    # This token expires almost immediately, so waiting past its lifespan makes it invalid
    token = keycloak_.get_token(keycloak_.Client_Short_Lived, keycloak_.Secret_Short_Lived)
    time.sleep(keycloak_.Short_Token_Lifespan + _expiry_wait_extra)

    response = _get(zato_server['jwt_url'], token)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_bad_signature(zato_server:'stranydict') -> 'None':

    # A tampered payload makes the signature invalid while the key ID stays known
    token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
    header, payload, signature = token.split('.')

    # Reversing the signature guarantees it no longer matches the payload
    tampered = f'{header}.{payload}.{signature[::-1]}'

    response = _get(zato_server['jwt_url'], tampered)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_unknown_signing_key(zato_server:'stranydict') -> 'None':

    # A token signed by a key the IdP never published must be rejected
    # even though all its claims look right
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    now = int(time.time())

    claims = {
        'iss': keycloak_.get_issuer(),
        'aud': keycloak_.Audience_Main,
        'exp': now + 300,
        'iat': now,
        keycloak_.Claim_Department: keycloak_.Department_Accounting,
    }

    token = pyjwt.encode(claims, private_key, algorithm='RS256', headers={'kid': 'test-unpublished-key'})

    response = _get(zato_server['jwt_url'], token)

    _assert_unauthorized(response)

# ################################################################################################################################

def test_jwt_key_rotation(zato_server:'stranydict') -> 'None':

    # A new realm key means new tokens carry a key ID the server has never cached, which must
    # trigger a JWKS refetch rather than a permanent rejection - the refetch is held back until
    # the interval that follows the previous fetch has passed.
    keycloak_.rotate_keys()
    time.sleep(_rotation_settle_seconds)

    response = _get_until_ok(
        zato_server['jwt_url'],
        keycloak_.Client_Accounting,
        keycloak_.Secret_Accounting,
        _rotation_pickup_timeout,
    )

    assert response.status_code == OK, response.text

# ################################################################################################################################

def test_definition_edit_propagates(zato_server:'stranydict') -> 'None':

    server_directory = zato_server['server_directory']

    try:
        # Redeploy the JWT definition so it now requires department=Sales ..
        config_yaml = build_config_yaml(department=keycloak_.Department_Sales)
        run_enmasse(server_directory, config_yaml)

        # .. an Accounting token no longer matches ..
        token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
        response = _get(zato_server['jwt_url'], token)
        _assert_unauthorized(response)

        # .. while a Sales one now does - all without a server restart. Keys rotated by the test
        # .. before this one may still be waiting for the JWKS fetch interval to pass.
        response = _get_until_ok(
            zato_server['jwt_url'],
            keycloak_.Client_Sales,
            keycloak_.Secret_Sales,
            _rotation_pickup_timeout,
        )
        assert response.status_code == OK, response.text

    finally:
        # Restore the original claim filter for any tests that follow
        config_yaml = build_config_yaml()
        run_enmasse(server_directory, config_yaml)

# ################################################################################################################################
# ################################################################################################################################
