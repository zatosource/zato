# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass, dict_field, list_field
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import timedelta
    from zato.common.typing_ import datetime, dtnone, intnone, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerTokenConfig(Model):
    sec_def_name:'str'
    username:'str'
    password:'str'
    scopes:'str'
    grant_type:'str'
    extra_fields:'stranydict'
    auth_server_url:'str'
    client_id_field:'str'
    client_secret_field:'str'

    # How the client proves its identity at the token endpoint - a client secret or a signed JWT
    client_auth_method:'str' = ''

    # Private key JWT - the PEM key the assertion is signed with, its algorithm and its key ID
    private_key:'str' = ''
    jwt_algorithm:'str' = ''
    key_id:'str' = ''

    # Private key JWT - the aud claim when it is not the auth endpoint, and the certificate the thumbprints come from
    assertion_audience:'str' = ''
    certificate:'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerTokenInfo(Model):
    creation_time: 'datetime'
    sec_def_name: 'str'
    token:'str'
    token_type:'str'
    expires_in:'timedelta | None'
    expires_in_sec:'intnone'
    expiration_time:'dtnone'
    scopes:'str' = ''
    username:'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerTokenInfoResult(Model):
    info: 'BearerTokenInfo'
    is_cache_hit: 'bool'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerTokenVerifyConfig(Model):
    """ Everything needed to verify an inbound bearer token against one security definition.
    """
    security_id:'int' = 0
    sec_def_name:'str' = ''

    # Static mode - the exact token the caller must present
    static_token:'str' = ''

    # JWT mode - what the token must have been issued with
    issuer:'str' = ''
    jwks_url:'str' = ''
    audience:'str' = ''

    # JWT mode - claim name to required value pairs, all of which must match
    claims:'stranydict' = dict_field()

    # JWT mode - the claim whose value names the caller, e.g. sub, email or oid
    identity_claim:'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerTokenVerifyResult(Model):
    """ The outcome of checking one inbound bearer token against one security definition.
    When the token is accepted, claims are the verified ones. When it is refused, reason says
    why and claims carry whatever could be read from the token without trusting it.
    """
    is_ok:'bool' = False
    reason:'str' = ''
    claim:'str' = ''
    claims:'stranydict' = dict_field()
    claims_matched:'strlist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BearerAuthInfo(Model):
    """ What a bearer token check against a channel's security groups established about the caller.
    On success security_id names the definition that matched and identity is the resolved caller.
    On refusal reason says why, and identity, issuer and client are filled in as far as they could be read.
    """
    is_ok:'bool' = False
    security_id:'int' = 0
    sec_def_name:'str' = ''
    identity_claim:'str' = ''
    identity:'str' = ''
    reason:'str' = ''
    claim:'str' = ''
    claims:'stranydict' = dict_field()
    claims_matched:'strlist' = list_field()
    is_jwt:'bool' = False

# ################################################################################################################################
# ################################################################################################################################

class BearerRefusalReason:
    """ Why an inbound bearer token or a request without one was turned away.
    """
    No_Credentials = 'no_credentials'
    Malformed = 'malformed'
    Unsupported_Algorithm = 'unsupported_algorithm'
    Unknown_Key = 'unknown_key'
    Expired = 'expired'
    Wrong_Issuer = 'wrong_issuer'
    Wrong_Audience = 'wrong_audience'
    Bad_Signature = 'bad_signature'
    Claim_Missing = 'claim_missing'
    Claim_Mismatch = 'claim_mismatch'
    No_Definition_Matched = 'no_definition_matched'

# ################################################################################################################################
# ################################################################################################################################
