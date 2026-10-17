# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import dataclass
from json import dumps as json_dumps, loads as json_loads

# cryptography
from cryptography.fernet import InvalidToken

# Zato
from zato.common.bearer_token_verifier import build_verify_config
from zato.common.crypto.api import is_string_equal
from zato.common.util.api import new_cid_server
from zato.common.webapp.auth.auth_type import ConsoleAuthType
from zato.common.webapp.auth.dashboard_users import is_dashboard_admin

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intset, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What the decrypted content of each session token begins with, which no other value encrypted with the same key does
    Session_Prefix = b'zato.openapi.console.session\n'

    # How long, in seconds, a session token remains valid after sign-in
    Session_TTL = 8 * 60 * 60

    # The name under which the bearer token verifier logs the console's token checks
    Bearer_Channel_Name = 'OpenAPI console'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConsoleCaller:
    """ A signed-in console user - a Dashboard admin, or the holder of credentials that the given security definitions accept.
    """
    is_admin: 'bool'
    auth_type: 'str'
    username: 'str'
    secret: 'str'
    security_ids: 'intset'

# ################################################################################################################################
# ################################################################################################################################

def _is_active_secret(config:'anydict', secret:'str') -> 'bool':
    """ Whether the given definition is active and its secret is the one the caller sent.
    """
    if not config['is_active']:
        return False

    # Definitions that use no secret have none in the database
    if config['password'] is None:
        return False

    out = is_string_equal(secret, config['password'])
    return out

# ################################################################################################################################

def validate_api_key(server:'ParallelServer', key:'str') -> 'intset':
    """ Returns the IDs of all the active API key definitions that have the given key.
    """
    out:'intset' = set()

    for sec_def in server.url_data.apikey_config.values():
        config = sec_def['config']

        if _is_active_secret(config, key):
            out.add(config['id'])

    return out

# ################################################################################################################################

def validate_bearer_token(server:'ParallelServer', token:'str') -> 'intset':
    """ Returns the IDs of all the active Bearer token definitions that accept the given token, static tokens and JWTs alike,
    as verified by the same verifier that inbound REST channels use.
    """
    url_data = server.url_data
    verifier = url_data.get_bearer_token_verifier()
    cid = new_cid_server()

    out:'intset' = set()

    for sec_def in url_data.oauth_config.values():
        config = sec_def['config']

        # Inactive definitions accept no token ..
        if not config['is_active']:
            continue

        # .. and an active one accepts it if the verifier returns its claims.
        verify_config = build_verify_config(config)
        claims = verifier.verify(cid, ModuleCtx.Bearer_Channel_Name, token, verify_config)

        if claims is not None:
            out.add(config['id'])

    return out

# ################################################################################################################################

def validate_credentials(server:'ParallelServer', username:'str', password:'str') -> 'intset':
    """ Returns the IDs of the active Basic Auth and Bearer token definitions that the username and password belong to.
    Bearer token callers sign in with the definition's client ID and its secret. Each type has at most one definition per username.
    """
    url_data = server.url_data

    out:'intset' = set()

    for config_dict in (url_data.basic_auth_config, url_data.oauth_config):
        for sec_def in config_dict.values():
            config = sec_def['config']

            # Definitions that use no username have none in the database
            if config['username'] is None:
                continue

            if _is_active_secret(config, password):
                if is_string_equal(username, config['username']):
                    out.add(config['id'])

    return out

# ################################################################################################################################

def resolve_security_ids(server:'ParallelServer', auth_type:'str', username:'str', secret:'str') -> 'intset':
    """ Returns the IDs of all the active security definitions that accept the given credentials.
    """
    if auth_type == ConsoleAuthType.API_Key:
        out = validate_api_key(server, secret)

    elif auth_type == ConsoleAuthType.Bearer_Token:
        out = validate_bearer_token(server, secret)

    else:
        out = validate_credentials(server, username, secret)

    return out

# ################################################################################################################################

def sign_in(server:'ParallelServer', fields:'anydict') -> 'strnone':
    """ Verifies the credentials that a console user signs in with and returns the session token
    that the console sends in their place afterwards, or None if the credentials are not valid.
    """
    auth_type = fields['auth_type']
    username = fields['username']
    secret = fields['password']

    # Dashboard users are the console's admins and sign in with a username and a password,
    # checked against the auth_user table in the same database that the server's ODB uses ..
    is_admin = False

    if auth_type == ConsoleAuthType.Basic_Auth:
        with closing(server.odb.session()) as session:
            is_admin = is_dashboard_admin(session, username, secret)

    # .. and every other caller has to have at least one security definition that accepts the credentials.
    if not is_admin:
        if not resolve_security_ids(server, auth_type, username, secret):
            return None

    payload = {
        'auth_type': auth_type,
        'username': username,
        'secret': secret,
        'is_admin': is_admin,
    }

    data = ModuleCtx.Session_Prefix + json_dumps(payload).encode('utf8')
    token = server.crypto_manager.secret_key.encrypt(data)

    out = token.decode('utf8')
    return out

# ################################################################################################################################

def resolve_session(server:'ParallelServer', session_token:'str') -> 'ConsoleCaller | None':
    """ Returns the caller that a session token was issued to, or None if the token is not valid,
    has expired, or the credentials it was issued for are no longer accepted by any security definition.
    """
    # A token that this server did not issue, or issued too long ago, identifies no one ..
    try:
        data = server.crypto_manager.secret_key.decrypt(session_token.encode('utf8'), ttl=ModuleCtx.Session_TTL)
    except InvalidToken:
        return None

    if not data.startswith(ModuleCtx.Session_Prefix):
        return None

    payload = json_loads(data[len(ModuleCtx.Session_Prefix):])

    out = ConsoleCaller()
    out.is_admin = payload['is_admin']
    out.auth_type = payload['auth_type']
    out.username = payload['username']
    out.secret = payload['secret']

    # .. an admin has access to every channel ..
    if out.is_admin:
        out.security_ids = set()
        return out

    # .. and each other caller has access through the definitions that accept the credentials at this moment,
    # which a check in memory establishes, whereas the password of a Dashboard user is verified at sign-in only.
    out.security_ids = resolve_security_ids(server, out.auth_type, out.username, out.secret)

    if not out.security_ids:
        return None

    return out

# ################################################################################################################################
# ################################################################################################################################
