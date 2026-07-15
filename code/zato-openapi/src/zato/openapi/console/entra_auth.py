# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os

# Zato - the console reuses the Dashboard's authentication modules as they are, so an environment
# configured for Entra ID once covers both applications with the same identity and the same groups.
from zato.admin.web.auth.common import auth_config, AuthType
from zato.admin.web.auth.entra import complete_auth_code_flow, EntraAuthError, get_authorize_url

# ################################################################################################################################
# ################################################################################################################################

# Everything is inherited from the Dashboard's Zato_Dashboard_Auth_* variables except the redirect URL,
# because Entra ID requires an exact redirect match per application.
Env_Redirect_URL = 'Zato_OpenAPI_Console_Auth_Entra_Redirect_URL'

if _console_redirect_url := os.environ.get(Env_Redirect_URL):
    auth_config.redirect_url = _console_redirect_url

# ################################################################################################################################
# ################################################################################################################################

# Re-exported for the console's views, so everything Entra-related comes from this one module
AuthType = AuthType
auth_config = auth_config
complete_auth_code_flow = complete_auth_code_flow
EntraAuthError = EntraAuthError
get_authorize_url = get_authorize_url

# ################################################################################################################################

def is_entra_enabled() -> 'bool':
    """ Whether the environment selects Entra ID for sign-ins - the console reads the same variable
    the Dashboard does, so configuring the authentication type once covers both applications.
    """
    out = auth_config.auth_type == AuthType.Entra
    return out

# ################################################################################################################################
# ################################################################################################################################
