# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.db_env.database import get_database_engine
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.util.env import populate_environment_from_file

# ################################################################################################################################
# ################################################################################################################################

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
    """ Returns the typed SQL facade over the rule engine tables of the Zato database.
    """
    engine = get_database_engine()
    out = RuleSQLBackend.from_engine(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
