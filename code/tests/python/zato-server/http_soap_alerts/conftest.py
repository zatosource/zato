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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.odb.model import Base, HTTPSOAP, SecurityBase, Service

# The test doubles live next to the tests and are imported flat
sys.path.insert(0, os.path.dirname(__file__))

# Test support
from http_soap_stub import Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session_factory() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the services touch.
    """
    engine = create_engine('sqlite://')

    tables = [
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(Service(None, Service_Name, True, 'orders.OrdersGet', False))
    session.commit()
    session.close()

    yield factory

    engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
