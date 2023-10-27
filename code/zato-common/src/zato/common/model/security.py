# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import timedelta
    from zato.common.typing_ import dtnone, intnone, stranydict

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
    token:'str'
    token_type:'str'
    expires_in:'timedelta | None'
    expires_in_sec:'intnone'
    expiration_time:'dtnone'
    scopes:'str' = ''
    username:'str' = ''

# ################################################################################################################################
# ################################################################################################################################
