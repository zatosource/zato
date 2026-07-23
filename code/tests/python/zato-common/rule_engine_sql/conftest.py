# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path
from typing import Generator

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.engine import Engine

# typing-extensions
from typing_extensions import TypeAlias

# Local
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database_engine(tmp_path:'Path') -> 'engine_generator':
    """ Creates one isolated test-managed SQL database.
    """
    # Build a file-backed database that the background writer thread can share ..
    database_path = tmp_path / 'rule-engine.sqlite'
    database_url = f'sqlite:///{database_path}'
    connection_options = {'check_same_thread': False}
    engine = create_database_engine(database_url, connect_args=connection_options)

    # .. create only the rule-engine tables ..
    create_schema(engine)

    # .. hand the engine to the test ..
    yield engine

    # .. and release its test-managed connection pool.
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def backend(database_engine:'Engine') -> 'RuleSQLBackend':
    """ Returns the complete backend over the isolated test database.
    """
    out = RuleSQLBackend.from_engine(database_engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
