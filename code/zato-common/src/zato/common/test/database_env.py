# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment variables that select the Zato database in tests. A test points the database at a SQLite file
# of its own, and the engine of the database is keyed by these variables, so each such file has its own engine.

# Zato
from zato.common.db_env.common import Type_SQLite
from zato.common.db_env.database import database_config

# ################################################################################################################################
# ################################################################################################################################

class DatabaseEnv:

    # The variable with the type of the database
    Env_Type = database_config.env_type

    # The variable with the path to the SQLite file of the database
    Env_Path = database_config.env_path

    # The type of a database kept in a SQLite file
    Type_SQLite = Type_SQLite

    # The name of the SQLite file of the database
    File_Name = database_config.sqlite_file_name

# ################################################################################################################################
# ################################################################################################################################
