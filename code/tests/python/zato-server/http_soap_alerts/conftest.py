# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.odb.model import HTTPSOAP, SecurityBase, Service
from zato.common.test.config_database import config_database_engine
from zato.common.test.direct_sql.seed import seed_config_objects

# The test doubles live next to the tests and are imported flat
sys.path.insert(0, os.path.dirname(__file__))

# Test support
from http_soap_stub import Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_
    any_ = any_
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session_factory(tmp_path:'Path') -> 'any_':
    """ A sessionmaker over a fresh SQLite database file with the tables the services touch.
    """
    tables = [
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]

    with config_database_engine(tmp_path, tables) as engine:
        factory = sessionmaker(bind=engine)

        session = factory()
        seed_config_objects(session, [Service(None, Service_Name, True, 'orders.OrdersGet', False)])
        session.commit()
        session.close()

        yield factory

# ################################################################################################################################
# ################################################################################################################################
