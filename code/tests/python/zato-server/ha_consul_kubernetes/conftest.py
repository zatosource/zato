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

_ha_consul_dir = os.path.join(_here, '..', 'ha_consul')
_ha_consul_dir = os.path.abspath(_ha_consul_dir)

_pubsub_faults_dir = os.path.join(_here, '..', '..', 'zato-common', 'pubsub_faults')
_pubsub_faults_dir = os.path.abspath(_pubsub_faults_dir)

sys.path.insert(0, _pubsub_faults_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, _ha_consul_dir)
sys.path.insert(0, _here)

# Zato
from ha_resume import pytest_runtest_protocol, pytest_runtest_teardown # noqa: F401
from kube_cluster import delete_cluster
from kube_env import create_kube_session, ready_kube_pair, remove_kube_session
from kube_faults import restore_cluster
from nodes import Timers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def kube_session() -> 'any_':
    """ The cluster, the receivers, the quickstart environment of the pods and Consul, deleted at the end of the run,
    including a run that fails.
    """
    # A session that fails while it is created leaves no cluster behind ..
    try:
        session = create_kube_session()
    except Exception:
        delete_cluster()
        raise

    # .. and neither does a run that fails.
    try:
        yield session
    finally:
        remove_kube_session(session)

# ################################################################################################################################

@pytest.fixture
def kube_pair(kube_session:'any_', request:'any_') -> 'any_':
    """ A pair with the default timers that is ready, with every node of the cluster restored once the test completes.
    """
    try:
        with ready_kube_pair(kube_session, request.node.name, Timers()) as env:
            yield env
    finally:
        restore_cluster()

# ################################################################################################################################
# ################################################################################################################################
