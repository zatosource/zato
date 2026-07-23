# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# Zato
from zato.common.util.api import asbool
from zato.common.util.env import get_list_from_environment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

class AuthType:
    """ The dashboard authentication types Zato_Dashboard_Auth_Type can select.
    """
    Built_In = 'built-in'
    Entra = 'entra'

# ################################################################################################################################
# ################################################################################################################################

# Environment variables the dashboard authentication is configured through
_auth_type_env     = 'Zato_Dashboard_Auth_Type'
_tenant_id_env     = 'Zato_Dashboard_Auth_Entra_Tenant_Id'
_client_id_env     = 'Zato_Dashboard_Auth_Entra_Client_Id'
_client_secret_env = 'Zato_Dashboard_Auth_Entra_Client_Secret'
_redirect_url_env  = 'Zato_Dashboard_Auth_Entra_Redirect_URL'
_group_admin_env   = 'Zato_Dashboard_Auth_Entra_Group_Admin'
_auto_login_env    = 'Zato_Dashboard_Auth_Entra_Auto_Login'
_authority_url_env = 'Zato_Dashboard_Auth_Entra_Authority_URL'

# Defaults applied when the environment does not set a value
_default_auth_type     = AuthType.Built_In
_default_auto_login    = 'false'
_default_authority_url = 'https://login.microsoftonline.com'
_default_entra_value   = ''

# The separator group lists use in the environment
_group_list_separator = ','

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AuthConfig:
    """ The dashboard authentication configuration, read from environment variables.
    """

    # Which authentication type is in use
    auth_type: 'str'

    # Entra ID connection details
    tenant_id:     'str'
    client_id:     'str'
    client_secret: 'str'
    redirect_url:  'str'
    authority_url: 'str'

    # Entra ID group object IDs deciding access
    group_admin: 'strlist'

    # Whether a GET on the login page goes straight to Microsoft
    auto_login: 'bool'

# ################################################################################################################################
# ################################################################################################################################

def _get_from_environment(key:'str', default:'str') -> 'str':
    """ Returns the environment variable's value or the given default when it is not set.
    """
    if value := os.environ.get(key):
        out = value
    else:
        out = default

    return out

# ################################################################################################################################

def build_auth_config() -> 'AuthConfig':
    """ Reads the dashboard authentication configuration from environment variables.
    """

    # Our response to produce
    out = AuthConfig()

    # The overall authentication type first ..
    out.auth_type = _get_from_environment(_auth_type_env, _default_auth_type)

    # .. the scalar Entra ID values next ..
    out.tenant_id     = _get_from_environment(_tenant_id_env, _default_entra_value)
    out.client_id     = _get_from_environment(_client_id_env, _default_entra_value)
    out.client_secret = _get_from_environment(_client_secret_env, _default_entra_value)
    out.redirect_url  = _get_from_environment(_redirect_url_env, _default_entra_value)
    out.authority_url = _get_from_environment(_authority_url_env, _default_authority_url)

    # .. the group list ..
    out.group_admin = get_list_from_environment(_group_admin_env, _group_list_separator)

    # .. and the auto-login flag.
    auto_login = _get_from_environment(_auto_login_env, _default_auto_login)
    out.auto_login = asbool(auto_login)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The configuration is read once, when this module is first imported
auth_config = build_auth_config()

# ################################################################################################################################
# ################################################################################################################################

def provision_user(username:'str', display_name:'str') -> 'any_':
    """ Creates or updates a Django user for a person authenticated by an external identity provider.
    Such accounts never keep a local password.
    """
    # Imported here so that applications without Django's auth models, such as the OpenAPI console,
    # can still import this module for its configuration.
    from django.contrib.auth.models import User
    from django.core.exceptions import ObjectDoesNotExist

    # Find the user or start a new one - external accounts cannot log in with a local password ..
    try:
        user:'any_' = User.objects.get(username=username)
    except ObjectDoesNotExist:
        user = User(username=username)
        user.set_unusable_password()

    # .. the display name splits into the first and last name ..
    first_name, _, last_name = display_name.partition(' ')
    user.first_name = first_name
    user.last_name = last_name

    user.is_staff = True
    user.is_superuser = True

    # .. and the user is ready now.
    user.save()

    out = user
    return out

# ################################################################################################################################
# ################################################################################################################################
