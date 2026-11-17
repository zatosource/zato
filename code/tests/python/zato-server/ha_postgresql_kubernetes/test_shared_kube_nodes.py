# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the worker node of the active pod of the SQLite suites, run against a pair on PostgreSQL through
# the fixtures of this directory. A partitioned node reaches neither the other zone nor the zone of the database.
# The stop of the node covers each fault that ends the node, and the partition covers the loss of the database.

# pytest
import pytest

# Zato
from test_kube_nodes import ModuleCtx as NodesCtx, test_node_fault as run_node_fault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the worker node of the active pod
    Faults = [NodesCtx.Fault_Stop, NodesCtx.Fault_Partition]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_node_fault(kube_pair:'KubeEnvironment', partition_replaces_active:'bool', fault:'str') -> 'None':
    """ The worker node of the active pod fails under traffic, as in the SQLite suite.
    """
    run_node_fault(kube_pair, partition_replaces_active, fault)

# ################################################################################################################################
# ################################################################################################################################
