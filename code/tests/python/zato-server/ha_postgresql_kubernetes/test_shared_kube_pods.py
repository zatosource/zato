# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the active pod of the SQLite suites, run against a pair on PostgreSQL through the fixtures
# of this directory. The deletion and the freeze of the pod end the lease renewal as the faults of the node do,
# so the pair on PostgreSQL runs the kill of the server only.

# pytest
import pytest

# Zato
from test_kube_pods import ModuleCtx as PodsCtx, test_pod_fault as run_pod_fault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the active pod
    Faults = [PodsCtx.Fault_Kill_Server]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_pod_fault(kube_pair:'KubeEnvironment', fault:'str') -> 'None':
    """ The active pod fails under traffic, as in the SQLite suite.
    """
    run_pod_fault(kube_pair, fault)

# ################################################################################################################################
# ################################################################################################################################
