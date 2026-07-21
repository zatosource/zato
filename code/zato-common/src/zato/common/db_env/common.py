# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Environment-configured SQLAlchemy engines - the audit log and the analytics store
# both live in their own database selected through a family of environment variables,
# e.g. Zato_Audit_Log_DB_* or Zato_Analytics_DB_*, defaulting to an SQLite file.
# This package builds and caches such engines so each store only declares its
# environment prefix, its default SQLite file name and its schema.

# stdlib
import os

# Zato
from zato.common.defaults import default_env_base_dir
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from zato.common.typing_ import stranydict

    # Dummy assignments to satisfy type checkers
    MetaData = MetaData

# ################################################################################################################################
# ################################################################################################################################

# Recognized database types
Type_SQLite     = 'sqlite'
Type_MySQL      = 'mysql'
Type_PostgreSQL = 'postgresql'
Type_Oracle     = 'oracle'

# What is used when the type variable is not set
Default_Type = Type_SQLite

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

class EnvDBConfig:
    """ Describes one environment-configured database - the environment variables
    selecting it, its default SQLite file name and the schema it needs.
    """

    def __init__(self, *, env_prefix:'str', sqlite_file_name:'str', metadata:'MetaData', needs_pool:'bool'=False) -> 'None':

        self.env_prefix = env_prefix
        self.sqlite_file_name = sqlite_file_name
        self.metadata = metadata

        # Whether SQLite connections are pooled - SQLAlchemy's default for file-based SQLite
        # is no pooling at all, which makes every transaction open and close the database file,
        # and each close checkpoints the WAL, costing more than ten milliseconds. Stores with
        # many small transactions, such as pub/sub, need a real pool instead.
        self.needs_pool = needs_pool

        # The full names of the environment variables selecting and configuring the database
        self.env_type     = f'{env_prefix}Type'
        self.env_host     = f'{env_prefix}Host'
        self.env_port     = f'{env_prefix}Port'
        self.env_username = f'{env_prefix}Username'
        self.env_password = f'{env_prefix}Password'
        self.env_name     = f'{env_prefix}Name'

        # The full names of the environment variables configuring SSL/TLS
        self.env_ssl           = f'{env_prefix}SSL'
        self.env_ssl_ca_file   = f'{env_prefix}SSL_CA_File'
        self.env_ssl_cert_file = f'{env_prefix}SSL_Cert_File'
        self.env_ssl_key_file  = f'{env_prefix}SSL_Key_File'
        self.env_ssl_verify    = f'{env_prefix}SSL_Verify'

# ################################################################################################################################

    def get_sqlite_path(self) -> 'str':
        """ Returns the full path to the default SQLite file of this database.
        """
        out = os.path.join(default_env_base_dir, self.sqlite_file_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_env_values(config:'EnvDBConfig') -> 'stranydict':
    """ Reads this database's environment variables into a dict of connection values,
    filling in the defaults for anything that is not set.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The type has a well-known default ..
    if db_type := os.environ.get(config.env_type, ''):
        out['type'] = db_type
    else:
        out['type'] = Default_Type

    # .. the SQLite file path defaults to this store's shared file ..
    if name := os.environ.get(config.env_name, ''):
        out['name'] = name
    elif out['type'] == Type_SQLite:
        out['name'] = config.get_sqlite_path()
    else:
        out['name'] = ''

    # .. the network location and credentials are empty unless given ..
    out['host']     = os.environ.get(config.env_host, '')
    out['port']     = os.environ.get(config.env_port, '')
    out['username'] = os.environ.get(config.env_username, '')
    out['password'] = os.environ.get(config.env_password, '')

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
# ################################################################################################################################
