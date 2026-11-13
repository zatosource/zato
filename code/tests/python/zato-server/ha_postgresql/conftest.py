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

_here = os.path.dirname(os.path.abspath(__file__))

_ha_consul_dir = os.path.join(_here, '..', 'ha_consul')
_ha_consul_dir = os.path.abspath(_ha_consul_dir)

_scheduler_failover_dir = os.path.join(_here, '..', 'scheduler_failover')
_scheduler_failover_dir = os.path.abspath(_scheduler_failover_dir)

_pubsub_faults_dir = os.path.join(_here, '..', '..', 'zato-common', 'pubsub_faults')
_pubsub_faults_dir = os.path.abspath(_pubsub_faults_dir)

sys.path.insert(0, _pubsub_faults_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, _ha_consul_dir)
sys.path.insert(0, _here)

# Zato
from ha_env import create_session, remove_session
from ha_resume import pytest_runtest_protocol # noqa: F401 # pyright: ignore[reportUnusedImport]
from ha_resume import pytest_runtest_teardown # noqa: F401 # pyright: ignore[reportUnusedImport]
from nodes import Timers
from postgresql_env import ready_pair

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def ha_session() -> 'any_':
    """ The network, the receivers and the quickstart environments of both nodes, which every test copies.
    """
    session = create_session()

    try:
        yield session
    finally:
        remove_session(session)

# ################################################################################################################################

@pytest.fixture
def ha_pair(ha_session:'any_', request:'any_') -> 'any_':
    """ A pair on PostgreSQL with the default timers that is ready.
    """
    with ready_pair(ha_session, request.node.name, Timers(), []) as env:
        yield env

# ################################################################################################################################
# ################################################################################################################################
