# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite file that the server of a queue delivery suite keeps its pub/sub database in.

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.db_env.database_env import DatabaseEnv

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

SQLite_File_Name = 'zato.db'

# ################################################################################################################################
# ################################################################################################################################

def get_db_path(data_directory:'str') -> 'str':
    """ The SQLite file of a session's own, in its data directory.
    """
    out = os.path.join(data_directory, SQLite_File_Name)
    return out

# ################################################################################################################################

@contextmanager
def pubsub_path_env(db_path:'str') -> 'envgen':
    """ Points Zato_Database_Path at one SQLite file for as long as the context is open.
    """
    old_path = os.environ.get(DatabaseEnv.Env_Path)
    os.environ[DatabaseEnv.Env_Path] = db_path

    try:
        yield
    finally:
        if old_path is None:
            _ = os.environ.pop(DatabaseEnv.Env_Path, None)
        else:
            os.environ[DatabaseEnv.Env_Path] = old_path

# ################################################################################################################################
# ################################################################################################################################
