# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one place that turns the ssl_* keys of an outgoing SQL connection configuration
# into the driver-level SSL connect arguments that PyMySQL and pg8000 accept.

# Zato
from zato.common.db_env import build_ssl_context_from_values
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

def _get_config_value(config:'any_', key:'str', default:'any_') -> 'any_':
    """ Returns one key from a connection configuration, using the default
    when the key is absent or empty - configurations written by older releases
    do not carry the newer keys at all.
    """
    value = config.get(key)

    # Missing and empty keys both mean the default is to be used.
    if value in (None, ''):
        value = default

    return value

# ################################################################################################################################

def get_ssl_values_from_config(config:'any_') -> 'stranydict':
    """ Normalizes the ssl_* keys of a connection configuration into a dict of values with the defaults filled in.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL is off unless requested explicitly and verification is on by default
    out['ssl']        = as_bool(_get_config_value(config, 'ssl', Default_SSL))
    out['ssl_verify'] = as_bool(_get_config_value(config, 'ssl_verify', Default_SSL_Verify))

    # The certificate paths are empty unless given
    out['ssl_ca_file']   = _get_config_value(config, 'ssl_ca_file', '')
    out['ssl_cert_file'] = _get_config_value(config, 'ssl_cert_file', '')
    out['ssl_key_file']  = _get_config_value(config, 'ssl_key_file', '')

    return out

# ################################################################################################################################

def get_ssl_connect_args(config:'any_', engine_name:'str') -> 'stranydict':
    """ Returns the driver-level SSL connect arguments for a connection configuration.
    When SSL is not enabled, the dict is empty, apart from PostgreSQL, for which TLS
    is turned off explicitly. PyMySQL accepts an ssl.SSLContext instance
    under the `ssl` keyword, pg8000 under `ssl_context`, and oracledb under `ssl_context`
    next to the TCPS protocol.
    """

    # Our response to produce
    out:'stranydict' = {}

    # Read the ssl_* keys with the defaults filled in ..
    values = get_ssl_values_from_config(config)

    # .. only MySQL, PostgreSQL and Oracle connections are configured through these keys -
    # .. other engines pass their SSL options through their own extra options ..
    is_mysql      = engine_name.startswith('mysql')
    is_oracle     = engine_name.startswith('oracle')
    is_postgresql = engine_name.startswith('postgres')

    # .. SSL is off unless requested explicitly, which pg8000 needs to be told about,
    # .. because without a context it attempts an unverified TLS connection first ..
    if not values['ssl']:
        if is_postgresql:
            out['ssl_context'] = False
        return out

    # .. Oracle needs the TCPS protocol next to its SSL context ..
    if is_oracle:
        out['protocol'] = 'tcps'
        out['ssl_context'] = build_ssl_context_from_values(values)
        return out

    # .. pg8000 takes the context under its own keyword ..
    if is_postgresql:
        out['ssl_context'] = build_ssl_context_from_values(values)
        return out

    if not is_mysql:
        return out

    # .. and PyMySQL takes it under the `ssl` keyword.
    out['ssl'] = build_ssl_context_from_values(values)

    return out

# ################################################################################################################################
# ################################################################################################################################
