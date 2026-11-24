# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import copy
import os
import sys

# pytest
import pytest

_here = os.path.dirname(os.path.abspath(__file__))

_scheduler_failover_dir = os.path.join(_here, '..', 'scheduler_failover')
_scheduler_failover_dir = os.path.abspath(_scheduler_failover_dir)

_ha_postgresql_dir = os.path.join(_here, '..', 'ha_postgresql')
_ha_postgresql_dir = os.path.abspath(_ha_postgresql_dir)

_pubsub_faults_dir = os.path.join(_here, '..', '..', 'zato-common', 'pubsub_faults')
_pubsub_faults_dir = os.path.abspath(_pubsub_faults_dir)

sys.path.insert(0, _pubsub_faults_dir)
sys.path.insert(0, _scheduler_failover_dir)
sys.path.insert(0, _ha_postgresql_dir)
sys.path.insert(0, _here)

# Zato
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown
from kube_cluster import delete_cluster, kubectl, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx, ready_kube_pair, remove_kube_session
from kube_faults import restore_cluster
from kube_local_postgresql import is_local_backend, start_local_backend, use_local_backend
from kube_postgresql import create_postgresql_session
from nodes import Timers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeSession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def kube_session() -> 'any_':
    """ The cluster, the receivers, the referee and PostgreSQL, deleted at the end of the run,
    including a run that fails.
    """
    # A session that fails while it is created leaves no cluster behind ..
    try:
        session = create_postgresql_session()
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

@pytest.fixture(scope='module')
def local_session(kube_session:'KubeSession') -> 'any_':
    """ The session with the local build as the Zato database of the pods. A session that already runs on the local
    build is used as it is, and any other one receives a local cluster for the tests of the module.
    """
    if is_local_backend():
        yield kube_session
        return

    backend = start_local_backend()

    out = copy.copy(kube_session)
    out.placeholders = dict(kube_session.placeholders)
    use_local_backend(out, backend)

    try:
        yield out
    finally:
        _ = kubectl('delete', 'statefulset', EnvCtx.StatefulSet_Name, '-n', ClusterCtx.Namespace, '--ignore-not-found',
            '--wait=true')
        backend.remove_service()
        backend.stop()

# ################################################################################################################################

@pytest.fixture
def local_pair(local_session:'KubeSession', request:'any_') -> 'any_':
    """ A pair on the local build that is ready, with every node of the cluster restored once the test completes.
    """
    try:
        with ready_kube_pair(local_session, request.node.name, Timers()) as env:
            yield env
    finally:
        restore_cluster()

# ################################################################################################################################
# ################################################################################################################################
