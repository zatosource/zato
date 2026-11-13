# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the suite with three Consul servers. The session is the one of the pair suite, and every test
# receives a new cluster in place of the one Consul server, with each node pointed at the server on its own host.

# stdlib
import os
from contextlib import contextmanager

# Zato
from consul_multi_cluster import ConsulCluster
from ha_authority import Authority
from ha_env import clear_receivers, new_nodes, start_pair, until_removed
from zato.common.test.pubsub_database import PubSubDatabase, PubSubDBMode
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import NodeHook, Timers
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def get_cluster(env:'HAEnvironment') -> 'ConsulCluster':
    out = cast_('ConsulCluster', env.referee)
    return out

# ################################################################################################################################

def build_environment(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'HAEnvironment':
    """ Starts a new Consul cluster, both nodes from the environments of the session and HAProxy,
    without waiting for the pair.
    """
    authority = Authority(os.path.join(session.run_dir, 'authority'))

    cluster = ConsulCluster(authority, session.run_dir)
    cluster.start()
    cluster.create_node_token()

    node_list = new_nodes(session)

    for node, server in zip(node_list, cluster.servers):
        node.prepare(authority, cluster, timers)
        node.env['Zato_HA_Consul_Address'] = server.address

    database = PubSubDatabase(PubSubDBMode.SQLite)

    out = start_pair(session, test_name, timers, hooks, authority, cluster, database, node_list)
    return out

# ################################################################################################################################

@contextmanager
def ready_pair(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'any_':
    """ A pair on three Consul servers with the given timers and node hooks that is ready, removed when the test completes.
    """
    clear_receivers(session)
    env = build_environment(session, test_name, timers, hooks)

    with until_removed(env) as out:
        yield out

# ################################################################################################################################
# ################################################################################################################################
