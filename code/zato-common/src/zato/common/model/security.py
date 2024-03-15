# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass
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
    cache_expiry: 'float'
    cache_hits: 'int' = 0

# ################################################################################################################################
# ################################################################################################################################
