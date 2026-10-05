# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
from base64 import urlsafe_b64encode
from hashlib import sha256
from html import unescape
from http.client import CONFLICT, CREATED, FOUND, NO_CONTENT, OK, SEE_OTHER
from typing import NamedTuple
from urllib.parse import parse_qs, urlsplit

# Requests
import requests

# Zato - test helpers
from keycloak_ import _admin_headers, _get_client_internal_id, _http_timeout, Audience_Main, get_issuer, get_token_url, \
    Keycloak_Base_URL, Realm_Main

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlistnone, strnone, strtuple

# ################################################################################################################################
# ################################################################################################################################

# The claim a person is named by in the tokens Keycloak issues and the claim their groups travel in
Claim_Username = 'preferred_username'
Claim_Groups   = 'groups'

# The group whose members a gateway lets in
Group_Billing_Agents = 'billing-agents'

# A person in the group and a person in no group at all
User_Member   = 'maria.johnson'
User_Outsider = 'john.smith'

Password_Member   = 'zato-test-password-maria'
Password_Outsider = 'zato-test-password-john'

# The client scope every client of the realm receives - it carries the audience and the groups claim,
# so a client registered dynamically issues the same tokens as one provisioned here
Client_Scope_MCP = 'zato-mcp'

# The scope a login asks for - an OpenID Connect request needs this one to be there
Scope_OpenID = 'openid'

# How long short-lived access tokens last, in seconds
Short_Login_Token_Lifespan = 1

# The registration policies a realm applies to anonymous dynamic registration that would keep
# a client registering from a test process out, by provider ID
_open_registration_policies = ('trusted-hosts', 'consent-required')

_registration_policy_type = 'org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy'
_registration_policy_subtype = 'anonymous'

# What the login page's form looks like, which is what a browserless login posts to
_login_form_pattern = re.compile(r'<form[^>]*id="kc-form-login"[^>]*>')
_form_action_pattern = re.compile(r'action="([^"]+)"')

# How many random bytes a PKCE verifier is made of
_verifier_bytes = 32

# ################################################################################################################################
# ################################################################################################################################

class PublicClient(NamedTuple):
    """ One public client of the realm, standing in for one MCP client product - its ID and
    the exact redirect URI that product's documentation names.
    """
    client_id: 'str'
    redirect_uri: 'str'
    token_lifespan: 'int' = 0

# ################################################################################################################################

# One public client per MCP client product, each with the redirect URI its documentation names
Client_VSCode      = PublicClient('zato-test-vscode', 'http://127.0.0.1:33418/')
Client_Cursor      = PublicClient('zato-test-cursor', 'http://localhost:8787/callback')
Client_Claude_Code = PublicClient('zato-test-claude-code', 'http://localhost:8080/callback')
Client_Claude_AI   = PublicClient('zato-test-claude-ai', 'https://claude.ai/api/mcp/auth_callback')

# A public client whose tokens expire almost immediately, for expiry tests of a signed-in person
Client_Short_Lived_Login = PublicClient('zato-test-login-short-lived', 'http://localhost:8080/callback',
    Short_Login_Token_Lifespan)

Public_Clients = (Client_VSCode, Client_Cursor, Client_Claude_Code, Client_Claude_AI, Client_Short_Lived_Login)

# ################################################################################################################################
# ################################################################################################################################

def get_authorize_url(realm:'str'=Realm_Main) -> 'str':
    issuer = get_issuer(realm)

    out = f'{issuer}/protocol/openid-connect/auth'
    return out

# ################################################################################################################################

def get_registration_url(realm:'str'=Realm_Main) -> 'str':
    issuer = get_issuer(realm)

    out = f'{issuer}/clients-registrations/openid-connect'
    return out

# ################################################################################################################################

def get_authorization_server_metadata_url(realm:'str'=Realm_Main) -> 'str':
    issuer = get_issuer(realm)

    out = f'{issuer}/.well-known/openid-configuration'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _admin_url(realm:'str', path:'str') -> 'str':
    out = f'{Keycloak_Base_URL}/admin/realms/{realm}/{path}'
    return out

# ################################################################################################################################

def _ensure_created(response:'any_', what:'str') -> 'None':
    """ Anything other than created-or-already-there is an actual error.
    """
    if response.status_code not in (CREATED, CONFLICT):
        raise Exception(f'Could not create {what} -> {response.status_code} -> {response.text}')

# ################################################################################################################################

def _ensure_group(admin_token:'str', realm:'str', name:'str') -> 'str':
    """ Creates a group if there is none of that name yet and returns its internal ID.
    """
    headers = _admin_headers(admin_token)

    response = requests.post(_admin_url(realm, 'groups'), json={'name': name}, headers=headers, timeout=_http_timeout)
    _ensure_created(response, f'group `{name}`')

    response = requests.get(_admin_url(realm, 'groups'), params={'search': name, 'exact': 'true'},
        headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not look up group `{name}` -> {response.status_code} -> {response.text}')

    for item in response.json():
        if item['name'] == name:
            out = item['id']
            return out

    raise Exception(f'Group `{name}` not found after creation')

# ################################################################################################################################

def _ensure_user(admin_token:'str', realm:'str', username:'str', password:'str', group_id:'strnone') -> 'None':
    """ Creates a person with a set password and a complete profile, in the given group when there is one.
    """
    headers = _admin_headers(admin_token)

    first_name, last_name = username.split('.')

    response = requests.post(_admin_url(realm, 'users'), json={
        'username': username,
        'enabled': True,
        'emailVerified': True,
        'firstName': first_name.capitalize(),
        'lastName': last_name.capitalize(),
        'email': f'{username}@example.com',
        'credentials': [{'type': 'password', 'value': password, 'temporary': False}],
    }, headers=headers, timeout=_http_timeout)
    _ensure_created(response, f'user `{username}`')

    if not group_id:
        return

    response = requests.get(_admin_url(realm, 'users'), params={'username': username, 'exact': 'true'},
        headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not look up user `{username}` -> {response.status_code} -> {response.text}')

    items = response.json()

    if not items:
        raise Exception(f'User `{username}` not found after creation')

    first = items[0]
    user_id = first['id']

    response = requests.put(_admin_url(realm, f'users/{user_id}/groups/{group_id}'), headers=headers,
        timeout=_http_timeout)

    if response.status_code != NO_CONTENT:
        raise Exception(f'Could not add `{username}` to its group -> {response.status_code} -> {response.text}')

# ################################################################################################################################

def _find_client_scope_id(admin_token:'str', realm:'str', name:'str') -> 'strnone':
    headers = _admin_headers(admin_token)

    response = requests.get(_admin_url(realm, 'client-scopes'), headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not list client scopes -> {response.status_code} -> {response.text}')

    for item in response.json():
        if item['name'] == name:
            out = item['id']
            return out

    return None

# ################################################################################################################################

def _ensure_client_scope(admin_token:'str', realm:'str') -> 'str':
    """ Creates the client scope that puts the audience and the groups claim into every access token
    of the realm, makes it a default of the realm and returns its internal ID.
    """
    headers = _admin_headers(admin_token)

    scope_id = _find_client_scope_id(admin_token, realm, Client_Scope_MCP)

    if not scope_id:

        response = requests.post(_admin_url(realm, 'client-scopes'), json={
            'name': Client_Scope_MCP,
            'protocol': 'openid-connect',
            'attributes': {
                'include.in.token.scope': 'false',
                'display.on.consent.screen': 'false',
            },
            'protocolMappers': [
                {
                    'name': f'{Client_Scope_MCP}-audience',
                    'protocol': 'openid-connect',
                    'protocolMapper': 'oidc-audience-mapper',
                    'config': {
                        'included.custom.audience': Audience_Main,
                        'access.token.claim': 'true',
                        'id.token.claim': 'false',
                    },
                },
                {
                    'name': f'{Client_Scope_MCP}-groups',
                    'protocol': 'openid-connect',
                    'protocolMapper': 'oidc-group-membership-mapper',
                    'config': {
                        'claim.name': Claim_Groups,
                        'full.path': 'false',
                        'access.token.claim': 'true',
                        'id.token.claim': 'true',
                        'userinfo.token.claim': 'true',
                    },
                },
            ],
        }, headers=headers, timeout=_http_timeout)
        _ensure_created(response, f'client scope `{Client_Scope_MCP}`')

        scope_id = _find_client_scope_id(admin_token, realm, Client_Scope_MCP)

        if not scope_id:
            raise Exception(f'Client scope `{Client_Scope_MCP}` not found after creation')

    # Every client created from now on, a dynamically registered one included, receives the scope
    response = requests.put(_admin_url(realm, f'default-default-client-scopes/{scope_id}'), headers=headers,
        timeout=_http_timeout)

    if response.status_code not in (NO_CONTENT, CONFLICT):
        raise Exception(f'Could not make `{Client_Scope_MCP}` a realm default -> {response.status_code} -> {response.text}')

    out = scope_id
    return out

# ################################################################################################################################

def _ensure_public_client(admin_token:'str', realm:'str', client:'PublicClient', scope_id:'str') -> 'None':
    """ Creates a public client with the authorization code flow, PKCE required and exactly one redirect URI.
    """
    headers = _admin_headers(admin_token)

    internal_id = _get_client_internal_id(admin_token, realm, client.client_id)

    if not internal_id:

        attributes:'stranydict' = {'pkce.code.challenge.method': 'S256'}

        if client.token_lifespan:
            attributes['access.token.lifespan'] = str(client.token_lifespan)

        response = requests.post(_admin_url(realm, 'clients'), json={
            'clientId': client.client_id,
            'protocol': 'openid-connect',
            'publicClient': True,
            'standardFlowEnabled': True,
            'directAccessGrantsEnabled': False,
            'serviceAccountsEnabled': False,
            'redirectUris': [client.redirect_uri],
            'attributes': attributes,
        }, headers=headers, timeout=_http_timeout)

        if response.status_code != CREATED:
            raise Exception(f'Could not create client `{client.client_id}` -> {response.status_code} -> {response.text}')

        internal_id = _get_client_internal_id(admin_token, realm, client.client_id)

        if not internal_id:
            raise Exception(f'Client `{client.client_id}` not found after creation')

    # The scope is attached outright rather than left to the realm default, so a client created before
    # the scope existed carries it too
    response = requests.put(_admin_url(realm, f'clients/{internal_id}/default-client-scopes/{scope_id}'),
        headers=headers, timeout=_http_timeout)

    if response.status_code not in (NO_CONTENT, CONFLICT):
        raise Exception(f'Could not attach `{Client_Scope_MCP}` to `{client.client_id}` -> {response.status_code}')

# ################################################################################################################################

def _open_dynamic_registration(admin_token:'str', realm:'str') -> 'None':
    """ Removes the anonymous registration policies that would turn a registering test process away.
    """
    headers = _admin_headers(admin_token)

    response = requests.get(_admin_url(realm, 'components'), params={'type': _registration_policy_type},
        headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not list registration policies -> {response.status_code} -> {response.text}')

    for item in response.json():

        if item.get('subType') != _registration_policy_subtype:
            continue

        if item.get('providerId') not in _open_registration_policies:
            continue

        component_id = item['id']
        response = requests.delete(_admin_url(realm, f'components/{component_id}'), headers=headers,
            timeout=_http_timeout)

        if response.status_code != NO_CONTENT:
            raise Exception(f'Could not remove policy `{item["providerId"]}` -> {response.status_code} -> {response.text}')

# ################################################################################################################################
# ################################################################################################################################

def provision_oauth_login(admin_token:'str', realm:'str'=Realm_Main) -> 'None':
    """ Creates everything a sign-in of a person needs - the group, the two people, the client scope with the
    audience and the groups claim, one public client per MCP client product, and a realm open to dynamic
    registration. Safe to run repeatedly.
    """
    group_id = _ensure_group(admin_token, realm, Group_Billing_Agents)

    _ensure_user(admin_token, realm, User_Member, Password_Member, group_id)
    _ensure_user(admin_token, realm, User_Outsider, Password_Outsider, None)

    scope_id = _ensure_client_scope(admin_token, realm)

    for client in Public_Clients:
        _ensure_public_client(admin_token, realm, client, scope_id)

    _open_dynamic_registration(admin_token, realm)

# ################################################################################################################################
# ################################################################################################################################

def _build_pkce_pair() -> 'strtuple':
    """ A verifier and the S256 challenge made of it, both without base64 padding.
    """
    verifier = urlsafe_b64encode(os.urandom(_verifier_bytes)).rstrip(b'=').decode()

    digest = sha256(verifier.encode()).digest()
    challenge = urlsafe_b64encode(digest).rstrip(b'=').decode()

    out = (verifier, challenge)
    return out

# ################################################################################################################################

def _find_login_form_action(page:'str') -> 'str':
    """ The address the login page's form posts to.
    """
    form_match = _login_form_pattern.search(page)

    if not form_match:
        raise Exception(f'No login form in the page received -> {page[:500]}')

    action_match = _form_action_pattern.search(form_match.group(0))

    if not action_match:
        raise Exception(f'The login form has no action -> {form_match.group(0)}')

    out = unescape(action_match.group(1))
    return out

# ################################################################################################################################

def _build_cookie_header(response:'any_') -> 'str':
    """ Every cookie a response set, as one Cookie header value.
    """
    pairs:'anylist' = []

    for cookie in response.cookies:
        pairs.append(f'{cookie.name}={cookie.value}')

    out = '; '.join(pairs)
    return out

# ################################################################################################################################

def _read_code_from_redirect(response:'any_', username:'str') -> 'str':
    """ The authorization code the redirect back to the client carries. The redirect is never followed,
    so the client's address only ever needs to be registered, not reachable.
    """
    if response.status_code not in (FOUND, SEE_OTHER):
        raise Exception(f'Sign-in of `{username}` did not redirect -> {response.status_code} -> {response.text[:500]}')

    location = response.headers['Location']
    query = parse_qs(urlsplit(location).query)

    codes = query.get('code')

    if not codes:
        raise Exception(f'No authorization code in the redirect -> {location}')

    out = codes[0]
    return out

# ################################################################################################################################

def get_user_token(
    client_id:'str',
    redirect_uri:'str',
    username:'str',
    password:'str',
    realm:'str'=Realm_Main,
    scopes:'strlistnone'=None,
    resource:'strnone'=None,
    ) -> 'str':
    """ Signs a person in through the authorization code flow with PKCE without a browser - the login page
    is fetched, its form is posted, the code is read from the redirect and exchanged with the verifier.
    Returns the access token. A resource, when given, travels with both requests as RFC 8707 has it.
    """
    verifier, challenge = _build_pkce_pair()

    if scopes is None:
        scopes = [Scope_OpenID]

    authorize_params:'anydict' = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'state': urlsafe_b64encode(os.urandom(16)).rstrip(b'=').decode(),
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
    }

    token_params:'anydict' = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code_verifier': verifier,
    }

    if resource:
        authorize_params['resource'] = resource
        token_params['resource'] = resource

    response = requests.get(get_authorize_url(realm), params=authorize_params, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not open the login page -> {response.status_code} -> {response.text[:500]}')

    action = _find_login_form_action(response.text)

    # The form post carries the cookies the login page set. A browser treats localhost as a secure context
    # and sends them over plain HTTP, so they are carried by hand rather than left to a cookie jar.
    cookie_header = _build_cookie_header(response)

    response = requests.post(action, data={
        'username': username,
        'password': password,
        'credentialId': '',
    }, headers={'Cookie': cookie_header}, allow_redirects=False, timeout=_http_timeout)

    token_params['code'] = _read_code_from_redirect(response, username)

    response = requests.post(get_token_url(realm), data=token_params, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not exchange the code of `{username}` -> {response.status_code} -> {response.text}')

    data = response.json()

    out = data['access_token']
    return out

# ################################################################################################################################
# ################################################################################################################################

def read_registration_endpoint(realm:'str'=Realm_Main) -> 'str':
    """ The registration endpoint the authorization server's metadata names.
    """
    response = requests.get(get_authorization_server_metadata_url(realm), timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not read the authorization server metadata -> {response.status_code} -> {response.text}')

    metadata = response.json()

    out = metadata['registration_endpoint']
    return out

# ################################################################################################################################

def register_client(client_name:'str', redirect_uris:'anylist', realm:'str'=Realm_Main) -> 'str':
    """ Registers a public client dynamically, the way a product with no pre-registered client does,
    and returns the client ID the authorization server assigned.
    """
    registration_endpoint = read_registration_endpoint(realm)

    response = requests.post(registration_endpoint, json={
        'client_name': client_name,
        'redirect_uris': redirect_uris,
        'token_endpoint_auth_method': 'none',
        'grant_types': ['authorization_code', 'refresh_token'],
        'response_types': ['code'],
    }, timeout=_http_timeout)

    if response.status_code != CREATED:
        raise Exception(f'Could not register `{client_name}` -> {response.status_code} -> {response.text}')

    data = response.json()

    out = data['client_id']
    return out

# ################################################################################################################################
# ################################################################################################################################
