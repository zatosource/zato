# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.db_env.database_env import DatabaseEnv

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import strnone

    Engine = Engine
    Iterator = Iterator

# ################################################################################################################################
# ################################################################################################################################

def _restore(name:'str', value:'strnone') -> 'None':
    """ Gives an environment variable back the value it had before a test changed it.
    """
    if value is None:
        _ = os.environ.pop(name, None)
    else:
        os.environ[name] = value

# ################################################################################################################################

@contextmanager
def file_database_engine(directory:'str | os.PathLike[str]') -> 'Iterator[Engine]':
    """ Points the Zato database at a SQLite file in a directory and yields its engine from the engine factory,
    with the settings, the schemas and the hooks that every server process uses, then disposes of the engine.
    """
    previous_type = os.environ.get(DatabaseEnv.Env_Type)
    previous_path = os.environ.get(DatabaseEnv.Env_Path)

    os.environ[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
    os.environ[DatabaseEnv.Env_Path] = os.path.join(directory, DatabaseEnv.File_Name)

    try:
        yield get_database_engine()
    finally:
        dispose_database_engine()
        _restore(DatabaseEnv.Env_Type, previous_type)
        _restore(DatabaseEnv.Env_Path, previous_path)

# ################################################################################################################################
# ################################################################################################################################
