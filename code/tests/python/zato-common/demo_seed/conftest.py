# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.db_env.database import dispose_database_engine
from zato.common.test.zato_database import isolated_database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env() -> 'any_':
    """ Points the Zato database at a new PostgreSQL database for each test, so that every test
    runs on its own isolated database.
    """
    with isolated_database_env() as env:
        try:
            yield env
        finally:
            dispose_database_engine()

# ################################################################################################################################
# ################################################################################################################################
