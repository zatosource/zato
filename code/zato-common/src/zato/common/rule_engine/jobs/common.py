# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# Zato
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Default_DB_URL, Env_DB_URL
from zato.common.util.env import populate_environment_from_file

# ################################################################################################################################
# ################################################################################################################################

# SQLite connections travel between the pooled sessions of one process, hence the flag.
_sqlite_connect_args = {'check_same_thread': False}

# The shared format every rule engine job logs in.
_log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'

# ################################################################################################################################
# ################################################################################################################################

def configure_job(env_file:'str') -> 'None':
    """ Everything a job process needs before touching the database - logging and environment variables.
    """
    # Every job logs the same way ..
    logging.basicConfig(level=logging.INFO, format=_log_format)

    # .. and reads its Zato_* variables from the environment file when one was given.
    if env_file:
        _ = populate_environment_from_file(env_file)

# ################################################################################################################################

def build_backend() -> 'RuleSQLBackend':
    """ Opens the same rule engine database the dashboard uses and returns the typed SQL facade over it.
    """
    # The URL is the same one the dashboard keeps its tables under ..
    if url := os.environ.get(Env_DB_URL):
        pass
    else:
        url = Default_DB_URL

    # .. SQLite connections have to be usable across threads ..
    if url.startswith('sqlite'):
        engine = create_database_engine(url, connect_args=_sqlite_connect_args)
    else:
        engine = create_database_engine(url)

    # .. the tables come into being on first run and every later call is a no-op.
    create_schema(engine)

    out = RuleSQLBackend.from_engine(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
