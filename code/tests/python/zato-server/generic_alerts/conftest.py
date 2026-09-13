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
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnClient, GenericConnSec, Job, SecurityBase, Service
from zato.server.service.internal.generic import connection as connection_module

# The test doubles live next to the tests and are imported flat
sys.path.insert(0, os.path.dirname(__file__))

# Test support
from generic_stub import Cluster_Id, Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _no_config_audit(*args:'any_', **kwargs:'any_') -> 'None':
    """ The config audit trail is written to the audit log database, which these tests do not have - what they
    check is what the services store and publish.
    """

# ################################################################################################################################

@pytest.fixture(autouse=True)
def without_config_audit(monkeypatch:'any_') -> 'None':
    monkeypatch.setattr(connection_module, 'record_service_config_change', _no_config_audit)

# ################################################################################################################################

@pytest.fixture
def session_factory() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the services touch - the connections
    themselves, the rows a deletion cascades to and the scheduler jobs their health checks link to.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        SecurityBase.__table__,
        GenericConn.__table__,
        GenericConnSec.__table__,
        GenericConnClient.__table__,
        Job.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    factory = sessionmaker(bind=engine)

    session = factory()
    cluster = Cluster(Cluster_Id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.add(Service(None, Service_Name, True, 'zato.server.service.internal.connection.HealthCheckRun', True, cluster))
    session.commit()
    session.close()

    return factory

# ################################################################################################################################
# ################################################################################################################################
