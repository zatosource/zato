# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class PortalAuthType:
    """ The kinds of credentials callers sign in to the API portal with. Basic Auth covers every username
    and password pair - Dashboard users, Basic Auth definitions and the client IDs and secrets of Bearer tokens.
    Bearer token covers the tokens themselves, static ones and JWTs, verified the way inbound REST channels verify them.
    """
    Basic_Auth   = 'basic_auth'
    API_Key      = 'apikey'
    Bearer_Token = 'bearer_token'

# ################################################################################################################################
# ################################################################################################################################
