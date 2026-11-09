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

_scheduler_failover_dir = os.path.join(os.path.dirname(__file__), '..', 'scheduler_failover')
_scheduler_failover_dir = os.path.abspath(_scheduler_failover_dir)

_pubsub_faults_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'pubsub_faults')
_pubsub_faults_dir = os.path.abspath(_pubsub_faults_dir)

sys.path.insert(0, _pubsub_faults_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, os.path.dirname(__file__))

# Zato
from ha_env import create_session, ready_pair, remove_session
from nodes import Timers

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
    """ A pair with the default timers that is ready.
    """
    with ready_pair(ha_session, request.node.name, Timers(), []) as env:
        yield env

# ################################################################################################################################
# ################################################################################################################################
