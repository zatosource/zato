# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one place that turns the ssl_* keys of an SQL connection configuration,
# e.g. the [odb] stanza of server.conf or the options of an outgoing SQL connection,
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
    """ Returns the driver-level SSL connect arguments for a connection configuration,
    an empty dict when SSL is not enabled. Both PyMySQL and pg8000 accept
    an ssl.SSLContext instance under the same `ssl` keyword.
    """

    # Our response to produce
    out:'stranydict' = {}

    # Read the ssl_* keys with the defaults filled in ..
    values = get_ssl_values_from_config(config)

    # .. SSL is off unless requested explicitly ..
    if not values['ssl']:
        return out

    # .. only MySQL and PostgreSQL connections are configured through these keys -
    # .. other engines pass their SSL options through their own extra options ..
    is_mysql      = engine_name.startswith('mysql')
    is_postgresql = engine_name.startswith('postgres')

    if not is_mysql:
        if not is_postgresql:
            return out

    # .. and both of their drivers accept the same SSL context under the same keyword.
    out['ssl'] = build_ssl_context_from_values(values)

    return out

# ################################################################################################################################

def get_psycopg2_ssl_connect_args(config:'any_') -> 'stranydict':
    """ Returns SSL connect arguments in the libpq format that psycopg2 accepts -
    the Dashboard connects to PostgreSQL through psycopg2 rather than pg8000.
    """

    # Our response to produce
    out:'stranydict' = {}

    # Read the ssl_* keys with the defaults filled in ..
    values = get_ssl_values_from_config(config)

    # .. SSL is off unless requested explicitly ..
    if not values['ssl']:
        return out

    # .. the server certificate and its hostname are verified unless turned off explicitly ..
    if values['ssl_verify']:
        out['sslmode'] = 'verify-full'
    else:
        out['sslmode'] = 'require'

    # .. the server certificate is verified against the given CA ..
    if ca_file := values['ssl_ca_file']:
        out['sslrootcert'] = ca_file

    # .. and a client certificate is only needed for mutual TLS.
    if cert_file := values['ssl_cert_file']:
        out['sslcert'] = cert_file
        out['sslkey']  = values['ssl_key_file']

    return out

# ################################################################################################################################
# ################################################################################################################################
