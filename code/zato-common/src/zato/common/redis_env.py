# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Environment-configured Redis connections - the connection details live in a family
# of environment variables, e.g. Zato_Redis_*, defaulting to a plain localhost server.
# This module reads such variables and builds Redis clients out of them, including
# SSL/TLS connections with optional client certificates.

# stdlib
import os
import ssl

# Redis
from redis import Redis

# Zato
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The prefix of the environment variables configuring the default Redis connection
Env_Prefix = 'Zato_Redis_'

# What is used when the corresponding variable is not set
Default_Host = 'localhost'
Default_Port = 6379
Default_DB   = 0

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

class EnvRedisConfig:
    """ Describes one environment-configured Redis connection - the environment variables selecting it.
    """

    def __init__(self, *, env_prefix:'str') -> 'None':

        self.env_prefix = env_prefix

        # The full names of the environment variables selecting and configuring the connection
        self.env_host     = f'{env_prefix}Host'
        self.env_port     = f'{env_prefix}Port'
        self.env_db       = f'{env_prefix}DB'
        self.env_username = f'{env_prefix}Username'
        self.env_password = f'{env_prefix}Password'

        # The full names of the environment variables configuring SSL/TLS
        self.env_ssl           = f'{env_prefix}SSL'
        self.env_ssl_ca_file   = f'{env_prefix}SSL_CA_File'
        self.env_ssl_cert_file = f'{env_prefix}SSL_Cert_File'
        self.env_ssl_key_file  = f'{env_prefix}SSL_Key_File'
        self.env_ssl_verify    = f'{env_prefix}SSL_Verify'

# ################################################################################################################################
# ################################################################################################################################

# How the default Redis connection is selected and configured through the environment
_env_config = EnvRedisConfig(env_prefix=Env_Prefix)

# ################################################################################################################################

def get_redis_values(config:'EnvRedisConfig'=_env_config) -> 'stranydict':
    """ Reads this connection's environment variables into a dict of connection values,
    filling in the defaults for anything that is not set.
    """

    # Our response to produce
    out:'stranydict' = {}

    out['host']     = os.environ.get(config.env_host, Default_Host)
    out['username'] = os.environ.get(config.env_username, '')
    out['password'] = os.environ.get(config.env_password, '')

    # The port and the database number are integers with well-known defaults ..
    if port := os.environ.get(config.env_port, ''):
        out['port'] = int(port)
    else:
        out['port'] = Default_Port

    if db := os.environ.get(config.env_db, ''):
        out['db'] = int(db)
    else:
        out['db'] = Default_DB

    # .. SSL is off unless requested explicitly ..
    if ssl_enabled := os.environ.get(config.env_ssl, ''):
        out['ssl'] = as_bool(ssl_enabled)
    else:
        out['ssl'] = Default_SSL

    # .. the server certificate is verified by default when SSL is on ..
    if verify := os.environ.get(config.env_ssl_verify, ''):
        out['ssl_verify'] = as_bool(verify)
    else:
        out['ssl_verify'] = Default_SSL_Verify

    # .. and the certificate paths are empty unless given.
    out['ssl_ca_file']   = os.environ.get(config.env_ssl_ca_file, '')
    out['ssl_cert_file'] = os.environ.get(config.env_ssl_cert_file, '')
    out['ssl_key_file']  = os.environ.get(config.env_ssl_key_file, '')

    return out

# ################################################################################################################################

def get_redis_conn_from_values(values:'stranydict') -> 'Redis':
    """ Builds a Redis client out of a dict of connection values, e.g. one returned by get_redis_values.
    """

    # The basic connection parameters are always present ..
    connect_args:'stranydict' = {
        'host': values['host'],
        'port': values['port'],
        'db':   values['db'],
    }

    # .. credentials are only passed if they were given ..
    if username := values['username']:
        connect_args['username'] = username

    if password := values['password']:
        connect_args['password'] = password

    # .. and so is the whole SSL/TLS configuration ..
    if values['ssl']:
        connect_args['ssl'] = True

        if ca_file := values['ssl_ca_file']:
            connect_args['ssl_ca_certs'] = ca_file

        # .. a client certificate is only needed for mutual TLS ..
        if cert_file := values['ssl_cert_file']:
            connect_args['ssl_certfile'] = cert_file
            connect_args['ssl_keyfile']  = values['ssl_key_file']

        # .. and verification can be turned off explicitly.
        if not values['ssl_verify']:
            connect_args['ssl_cert_reqs'] = ssl.CERT_NONE
            connect_args['ssl_check_hostname'] = False

    out = Redis(**connect_args)

    return out

# ################################################################################################################################

def get_redis_conn(config:'EnvRedisConfig'=_env_config) -> 'Redis':
    """ Returns a Redis client for an environment-configured connection.
    Which server is used comes from the environment variables named after
    this connection's prefix, defaulting to a plain localhost server.
    """
    values = get_redis_values(config)

    out = get_redis_conn_from_values(values)
    return out

# ################################################################################################################################
# ################################################################################################################################
