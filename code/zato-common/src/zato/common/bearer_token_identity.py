# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.model.security import BearerAuthInfo
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The auth block says this when the caller presented a JWT
Auth_Type_Bearer_JWT = 'bearer_jwt'

# The auth block says this when the caller presented a static bearer token
Auth_Type_Bearer_Static = 'bearer_static'

# The auth block says this when no bearer token was presented at all
Auth_Type_None = 'none'

# Which token claims name the OAuth client the person signed in through, in order of preference
_client_claims = ('azp', 'client_id')

# Which token claims carry the granted scopes, in order of preference
_scope_claims = ('scp', 'scope')

# The separator between a definition name and the claim value in a resolved identity
Identity_Separator = '/'

# Where the HTTP channel leaves what the bearer check established, accepted or refused,
# for the service behind the channel to read
Auth_Info_Key = 'zato.sec.bearer.auth_info'

# Where the HTTP channel leaves the resolved identity of the caller, whatever the credential type
Identity_Key = 'zato.sec.identity'

# ################################################################################################################################
# ################################################################################################################################

def resolve_identity(sec_def_name:'str', identity_claim:'str', claims:'stranydict') -> 'str':
    """ Returns the caller's identity - the definition name alone, or the definition name
    and the value of the identity claim when the definition names one and the token carries it.
    """
    out = sec_def_name

    if identity_claim:
        if identity_claim in claims:
            value = claims[identity_claim]
            out = f'{sec_def_name}{Identity_Separator}{value}'

    return out

# ################################################################################################################################

def _first_claim(claims:'stranydict', names:'tuple[str, ...]') -> 'any_':
    """ Returns the value of the first of the given claims that the token carries, or an empty string.
    """
    out = ''

    for name in names:
        if name in claims:
            out = claims[name]
            break

    return out

# ################################################################################################################################

def _scopes_as_list(value:'any_') -> 'list[str]':
    """ Scopes arrive either as a space-separated string or as a list - this returns a list either way.
    """
    out:'list[str]' = []

    if isinstance(value, str):
        out.extend(value.split())
    elif isinstance(value, list):
        for item in value:
            out.append(str(item))

    return out

# ################################################################################################################################

def build_auth_block(info:'BearerAuthInfo') -> 'stranydict':
    """ Builds the fixed-key auth document that every MCP audit event carries.
    Only the named fields are copied out of the token so that nothing incidental lands in the log.
    """
    claims = info.claims

    if info.is_jwt:
        auth_type = Auth_Type_Bearer_JWT
    elif info.sec_def_name:
        auth_type = Auth_Type_Bearer_Static
    else:
        auth_type = Auth_Type_None

    # The identity in the block is the raw claim value - the definition is a field of its own
    identity = ''
    if info.identity_claim:
        if info.identity_claim in claims:
            identity = str(claims[info.identity_claim])

    out:'stranydict' = {
        'type': auth_type,
        'definition': info.sec_def_name,
        'identity': identity,
        'issuer': claims.get('iss', ''),
        'audience': claims.get('aud', ''),
        'client': _first_claim(claims, _client_claims),
        'scopes': _scopes_as_list(_first_claim(claims, _scope_claims)),
        'token_id': claims.get('jti', ''),
        'expires_at': claims.get('exp', 0),
        'claims_matched': list(info.claims_matched),
    }

    if not info.is_ok:
        out['reason'] = info.reason
        out['claim'] = info.claim

    return out

# ################################################################################################################################
# ################################################################################################################################
