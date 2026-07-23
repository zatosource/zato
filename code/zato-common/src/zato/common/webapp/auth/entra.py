# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.contrib.auth import login as django_login

# msal
from msal import ConfidentialClientApplication

# PyJWT
import jwt

# requests
import requests

# Zato
from zato.common.typing_ import cast_
from zato.common.webapp.auth.config import auth_config, provision_user

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EntraAuthError(Exception):
    """ Raised when an Entra ID sign-in attempt cannot be completed.
    """

# ################################################################################################################################
# ################################################################################################################################

# Keys the flow details wait under in the Django session between the redirect and the callback
_flow_session_key = 'zato_entra_flow'
_next_session_key = 'zato_entra_next'

# The backend name Django stores in the session for users logged in through Entra ID
_django_backend = 'django.contrib.auth.backends.ModelBackend'

# The ID token signing algorithm Entra ID uses
_id_token_algorithm = 'RS256'

# No extra scopes are needed - MSAL always requests openid, profile and offline_access itself
_scopes = []

# ################################################################################################################################
# ################################################################################################################################

# The MSAL application, built once, when the first sign-in starts
_msal_app = None

# The ID token signing keys, fetched from the authority's JWKS endpoint and cached by key ID
_signing_keys:'stranydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def _get_authority_url() -> 'str':
    """ Returns the full authority URL, i.e. the base address plus the tenant.
    """
    out = f'{auth_config.authority_url}/{auth_config.tenant_id}'
    return out

# ################################################################################################################################

def _get_msal_app() -> 'ConfidentialClientApplication':
    """ Returns the MSAL application, building it on first use.
    """
    global _msal_app

    if _msal_app is None:

        authority_url = _get_authority_url()

        # Instance discovery is skipped because the authority comes from trusted configuration,
        # which also lets tests point MSAL at a local authority.
        _msal_app = ConfidentialClientApplication(
            auth_config.client_id,
            client_credential=auth_config.client_secret,
            authority=authority_url,
            instance_discovery=False,
        )

    out = _msal_app
    return out

# ################################################################################################################################

def get_authorize_url(req:'any_', next_path:'str') -> 'str':
    """ Starts a new Entra ID sign-in flow and returns the Microsoft authorize URL to redirect the browser to.
    """
    app = _get_msal_app()

    # MSAL generates the state, the nonce and the PKCE values for this flow ..
    flow = app.initiate_auth_code_flow(_scopes, redirect_uri=auth_config.redirect_url)

    # .. both the flow and the post-login path wait in the session for the callback ..
    req.session[_flow_session_key] = flow
    req.session[_next_session_key] = next_path

    # .. and the browser can go to Microsoft now.
    out = cast_('str', flow['auth_uri'])
    return out

# ################################################################################################################################

def _get_signing_key(key_id:'str') -> 'any_':
    """ Returns the public key of the given key ID, fetched from the authority's JWKS endpoint and cached.
    """

    # An unknown key ID triggers a fetch - this also picks up rolled-over keys ..
    if key_id not in _signing_keys:

        authority_url = _get_authority_url()
        discovery_url = f'{authority_url}/v2.0/.well-known/openid-configuration'

        discovery_response = requests.get(discovery_url)
        discovery = discovery_response.json()

        jwks_response = requests.get(discovery['jwks_uri'])
        jwks = jwks_response.json()

        for key in jwks['keys']:
            key_object = jwt.PyJWK(key)
            _signing_keys[key['kid']] = key_object.key

    # .. a key ID the authority does not publish means the token cannot be trusted.
    if key_id not in _signing_keys:
        raise EntraAuthError(f'ID token signed with an unknown key `{key_id}`')

    out = _signing_keys[key_id]
    return out

# ################################################################################################################################

def _verify_id_token(id_token:'str') -> 'None':
    """ Verifies the ID token's signature, audience, issuer and expiration against the authority's published keys.
    MSAL validates the claims but relies on TLS for the signature, which this check confirms explicitly.
    """
    header = jwt.get_unverified_header(id_token)
    signing_key = _get_signing_key(header['kid'])

    # The v2.0 issuer is the authority URL plus the version suffix.
    authority_url = _get_authority_url()
    issuer_url = f'{authority_url}/v2.0'

    try:
        _ = jwt.decode(
            id_token,
            key=signing_key,
            algorithms=[_id_token_algorithm],
            audience=auth_config.client_id,
            issuer=issuer_url,
        )
    except jwt.PyJWTError as e:
        raise EntraAuthError(f'ID token validation error -> {e}')

# ################################################################################################################################

def complete_auth_code_flow(req:'any_') -> 'any_':
    """ Completes the Entra ID part of a sign-in - exchanges the code for tokens, verifies the ID token
    and checks group membership. Returns the username, the display name and the path to redirect to
    afterwards - what to do with the authenticated identity is up to the caller.
    """

    # Without a flow in the session the response cannot be matched to any sign-in attempt ..
    if _flow_session_key not in req.session:
        raise EntraAuthError('No sign-in attempt is in progress')

    flow = req.session.pop(_flow_session_key)
    next_path = req.session.pop(_next_session_key)

    app = _get_msal_app()

    # .. exchange the code for tokens - MSAL checks the state, the nonce and the ID token claims here ..
    try:
        result = app.acquire_token_by_auth_code_flow(flow, req.GET.dict())
    except (RuntimeError, ValueError) as e:
        raise EntraAuthError(f'Sign-in error -> {e}')

    # .. the authority reported an error, e.g. the code expired or a silent sign-in was not possible ..
    if 'error' in result:
        error = result['error']
        if 'error_description' in result:
            error = result['error_description']
        raise EntraAuthError(f'Sign-in error -> {error}')

    # .. the signature check complements MSAL's claim validation ..
    _verify_id_token(result['id_token'])

    claims = result['id_token_claims']

    # .. group claims are required because access cannot be decided without them ..
    if 'groups' not in claims:
        raise EntraAuthError('No groups claim in the ID token - the app registration must emit group claims')

    groups = set(claims['groups'])
    allowed_groups = set(auth_config.group_admin)

    # .. membership in any of the configured groups grants access ..
    matched_allowed = groups & allowed_groups
    if not matched_allowed:
        raise EntraAuthError('User is not a member of any allowed group')

    username = claims['preferred_username']
    display_name = claims['name']

    return username, display_name, next_path

# ################################################################################################################################

def handle_callback(req:'any_') -> 'str':
    """ Completes an Entra ID sign-in - exchanges the code for tokens, checks group membership,
    provisions the Django user and logs the person in. Returns the path to redirect to afterwards.
    """
    username, display_name, next_path = complete_auth_code_flow(req)

    # The Django user comes into being or is refreshed now ..
    user = provision_user(username, display_name)

    # .. and the session starts.
    django_login(req, user, backend=_django_backend)

    logger.info('User `%s` logged in through Entra ID', username)

    out = next_path
    return out

# ################################################################################################################################
# ################################################################################################################################
