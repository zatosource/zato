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

_scheduler_failover_dir = os.path.join(_here, '..', 'scheduler_failover')
_scheduler_failover_dir = os.path.abspath(_scheduler_failover_dir)

_pubsub_faults_dir = os.path.join(_here, '..', '..', 'zato-common', 'pubsub_faults')
_pubsub_faults_dir = os.path.abspath(_pubsub_faults_dir)

sys.path.insert(0, _pubsub_faults_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, _here)

# Zato
from ha_env import create_session, remove_session
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown
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
    """ The network, the referee and the receivers, which every test shares.
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

@pytest.fixture
def ha_production_pair(ha_session:'any_', request:'any_') -> 'any_':
    """ A pair on PostgreSQL with the settings of a production installation that is ready.
    """
    timers = Timers()
    timers.is_production = True

    with ready_pair(ha_session, request.node.name, timers, []) as env:
        yield env

# ################################################################################################################################
# ################################################################################################################################
