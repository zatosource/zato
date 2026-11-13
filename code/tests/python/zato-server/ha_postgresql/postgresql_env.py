# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the PostgreSQL suites. The session is the one of the Consul suite, and every test receives
# a new PostgreSQL cluster in place of Consul, which both nodes share as the pub/sub database and as the referee,
# both nodes started from a copy of the environments of the session and HAProxy in front of them.

# stdlib
import os
from contextlib import contextmanager

# Zato
from ha_authority import Authority
from ha_env import clear_receivers, new_nodes, start_pair, until_removed
from postgresql_cluster import PostgreSQLCluster
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node, NodeHook, Timers
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The file in which the server of a node records its pub/sub generation and its owner
    Server_Generation_File = 'pubsub-generation'

# ################################################################################################################################
# ################################################################################################################################

def get_cluster(env:'HAEnvironment') -> 'PostgreSQLCluster':
    out = cast_('PostgreSQLCluster', env.referee)
    return out

# ################################################################################################################################

def prepare_node(node:'Node', cluster:'PostgreSQLCluster', timers:'Timers') -> 'None':
    """ Fills in the environment of a node with the database of the cluster as its pub/sub database and its referee,
    which selects the shared storage mode.
    """
    node.prepare_common(timers)

    node.env['Zato_HA_Referee_Type'] = 'postgresql'
    node.env.update(cluster.node_env)

# ################################################################################################################################

def build_environment(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'HAEnvironment':
    """ Starts a new PostgreSQL cluster, both nodes from the environments of the session and HAProxy,
    without waiting for the pair.
    """
    authority = Authority(os.path.join(session.run_dir, 'authority'))

    cluster = PostgreSQLCluster(session.run_dir)
    cluster.start()

    node_list = new_nodes(session)

    for node in node_list:
        prepare_node(node, cluster, timers)

    out = start_pair(session, test_name, timers, hooks, authority, cluster, cluster.database, node_list)
    return out

# ################################################################################################################################

@contextmanager
def ready_pair(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'any_':
    """ A pair on PostgreSQL with the given timers and node hooks that is ready, removed when the test completes.
    """
    clear_receivers(session)
    env = build_environment(session, test_name, timers, hooks)

    with until_removed(env) as out:
        yield out

# ################################################################################################################################

def read_server_generation(node:'Node') -> 'tuple[int, str]':
    """ Returns the pub/sub generation and the owner that the server of a node recorded when it started.
    """
    path = node.db_path(ModuleCtx.Server_Generation_File)

    with open(path) as generation_file:
        value = generation_file.read()

    generation, owner = value.split('\n', 1)

    out = (int(generation), owner)
    return out

# ################################################################################################################################
# ################################################################################################################################
