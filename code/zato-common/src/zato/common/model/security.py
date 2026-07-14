# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass, dict_field
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import datetime, dtnone, intnone, stranydict, timedelta

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

# ################################################################################################################################
# ################################################################################################################################
