# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.db_env.engine import new_zato_engine
from zato.common.odb.model import Base

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine

    Engine = Engine
    Iterator = Iterator
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name of the file of the configuration database
    File_Name = 'config.db'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def config_database_engine(directory:'str | os.PathLike[str]', tables:'list[Table]') -> 'Iterator[Engine]':
    """ Yields an engine of a configuration database in a file of a directory, built by the engine factory
    with the settings of durability of every database of Zato, and with the given tables of the configuration model,
    then disposes of the engine.
    """
    db_path = os.path.join(directory, ModuleCtx.File_Name)
    engine = new_zato_engine(f'sqlite:///{db_path}')

    Base.metadata.create_all(engine, tables=tables)

    try:
        yield engine
    finally:
        engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
