# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.db_env.common import Default_SSL, Default_SSL_Verify, Default_Type, EnvDBConfig, get_env_values, \
    Type_MySQL, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    build_ssl_context_from_values, set_sqlite_busy_timeout
from zato.common.db_env.engine import dispose_env_engine, get_env_engine, get_sqlite_file_engine

# ################################################################################################################################
# ################################################################################################################################

# The public names of this package - re-exported here so callers keep importing from zato.common.db_env
__all__ = [
    'build_connect_args_from_values', 'build_engine_url_from_values', 'build_ssl_context_from_values',
    'dispose_env_engine', 'get_env_engine',
    'get_env_values', 'get_sqlite_file_engine', 'set_sqlite_busy_timeout', 'Default_SSL', 'Default_SSL_Verify',
    'Default_Type', 'EnvDBConfig', 'Type_MySQL', 'Type_PostgreSQL', 'Type_SQLite',
]

# ################################################################################################################################
# ################################################################################################################################
