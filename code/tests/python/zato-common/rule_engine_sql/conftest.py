# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from pathlib import Path
from typing import Generator

# The shared test documents live in a local lib directory with flat imports.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, 'lib'))

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.engine import Engine

# typing-extensions
from typing_extensions import TypeAlias

# Local
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database_engine(tmp_path:'Path') -> 'engine_generator':
    """ Creates one isolated test-managed SQL database.
    """
    with file_database_engine(tmp_path) as engine:
        yield engine

# ################################################################################################################################

@pytest.fixture
def backend(database_engine:'Engine') -> 'RuleSQLBackend':
    """ Returns the complete backend over the isolated test database.
    """
    out = RuleSQLBackend.from_engine(database_engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
