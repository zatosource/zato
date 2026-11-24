# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Make the sibling modules of this directory importable no matter where pytest runs from.
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.test.zato_database import zato_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env() -> 'any_':
    """ Points the audit database at a new PostgreSQL database so every test
    runs on its own isolated database.
    """
    with zato_database_engine():
        yield

# ################################################################################################################################
# ################################################################################################################################
