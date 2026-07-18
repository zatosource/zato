# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one place that builds Redis clients for the server - the connection details live
# in the [redis] section of server.conf and this module normalizes such a section into
# a dict of connection values and builds Redis clients out of it, including SSL/TLS
# connections with optional client certificates.

# stdlib
import ssl

# Redis
from redis import Redis

# Zato
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# What is used when the corresponding key is not set
Default_Host = 'localhost'
Default_Port = 6379
Default_DB   = 0

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

def _get_section_value(section:'any_', key:'str', default:'any_') -> 'any_':
    """ Returns one key from a [redis] configuration section, falling back to the default
    when the key is absent or empty - sections written by older releases do not carry
    the newer keys at all.
    """
    value = section.get(key)

    if value is None or value == '':
        value = default

    return value

# ################################################################################################################################

def get_redis_values_from_section(section:'any_') -> 'stranydict':
    """ Normalizes a [redis] configuration section, e.g. fs_server_config.redis or the section
    read from server.conf on disk, into a dict of connection values with defaults filled in.
    """

    # Our response to produce
    out:'stranydict' = {}

    out['host']     = _get_section_value(section, 'host', Default_Host)
    out['username'] = _get_section_value(section, 'username', '')
    out['password'] = _get_section_value(section, 'password', '')

    # The display details live in the same section
    out['display_name'] = _get_section_value(section, 'name', '')
    out['description']  = _get_section_value(section, 'description', '')

    # The port and the database number may arrive as strings from a config file
    port = _get_section_value(section, 'port', Default_Port)
    db   = _get_section_value(section, 'db', Default_DB)

    out['port'] = int(port)
    out['db']   = int(db)

    # SSL is off unless requested explicitly and verification is on by default
    out['ssl']        = as_bool(_get_section_value(section, 'ssl', Default_SSL))
    out['ssl_verify'] = as_bool(_get_section_value(section, 'ssl_verify', Default_SSL_Verify))

    # The certificate paths are empty unless given
    out['ssl_ca_file']   = _get_section_value(section, 'ssl_ca_file', '')
    out['ssl_cert_file'] = _get_section_value(section, 'ssl_cert_file', '')
    out['ssl_key_file']  = _get_section_value(section, 'ssl_key_file', '')

    return out

# ################################################################################################################################

def build_redis_connect_args(values:'stranydict', *, decode_responses:'bool'=False) -> 'stranydict':
    """ Turns a dict of connection values into the keyword arguments a Redis client accepts.
    """

    # The basic connection parameters are always present ..
    out:'stranydict' = {
        'host': values['host'],
        'port': values['port'],
        'db':   values['db'],
    }

    # .. callers that exchange text rather than bytes ask for decoded responses ..
    if decode_responses:
        out['decode_responses'] = True

    # .. credentials are only passed if they were given ..
    if username := values['username']:
        out['username'] = username

    if password := values['password']:
        out['password'] = password

    # .. and so is the whole SSL/TLS configuration ..
    if values['ssl']:
        out['ssl'] = True

        if ca_file := values['ssl_ca_file']:
            out['ssl_ca_certs'] = ca_file

        # .. a client certificate is only needed for mutual TLS ..
        if cert_file := values['ssl_cert_file']:
            out['ssl_certfile'] = cert_file
            out['ssl_keyfile']  = values['ssl_key_file']

        # .. and verification can be turned off explicitly.
        if not values['ssl_verify']:
            out['ssl_cert_reqs'] = ssl.CERT_NONE
            out['ssl_check_hostname'] = False

    return out

# ################################################################################################################################

def get_redis_conn_from_values(values:'stranydict', *, decode_responses:'bool'=False) -> 'Redis':
    """ Builds a Redis client out of a dict of connection values,
    e.g. one returned by get_redis_values_from_section.
    """
    connect_args = build_redis_connect_args(values, decode_responses=decode_responses)

    out = Redis(**connect_args)
    return out

# ################################################################################################################################
# ################################################################################################################################
