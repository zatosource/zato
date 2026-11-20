# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from nodes import Timers
from postgresql_cluster import ModuleCtx as ClusterCtx
from postgresql_env import get_cluster, ready_pair
from pubsub_exactly_once.database import postgresql_only
from pubsub_exactly_once.harness import new_keys, stage_batch, verify
from pubsub_exactly_once_takeover.ha_pair import ControlDirHook, get_cluster_env, get_control_dir
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import release
from zato.common.test.pubsub_database import pubsub_db_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_exactly_once_takeover.ha_pair')

# ################################################################################################################################
# ################################################################################################################################

# How many input messages each test publishes
_batch_count = 10

# How long the pair may take to serve again after a failover of its database, in seconds
_recovery_timeout = 180

# The standby that the primary replicates to synchronously
_synchronous_standby = ClusterCtx.Standby_Names[0]

# ################################################################################################################################
# ################################################################################################################################

@postgresql_only
def test_database_failover_on_postgresql(relay_ha_session:'HASession', request:'any_') -> 'None':
    """ The primary of the shared database fails while the relay of the active node holds the last key of a batch,
    and its synchronous standby is promoted. The promoted database holds each output once.
    """
    hook = ControlDirHook(get_control_dir(relay_ha_session))

    with ready_pair(relay_ha_session, request.node.name, Timers(), [hook]) as env:

        cluster = get_cluster(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        prefix, keys = new_keys(_batch_count)
        last_key = keys[-1]

        # The relay of the active node holds the last key of a batch ..
        TestConfig.base_url = active.server_url
        stage_batch(keys)

        # .. the primary fails and its synchronous standby is promoted ..
        cluster.kill(cluster.primary_name)
        _ = cluster.promote(_synchronous_standby)

        # .. the pair serves again on the promoted database ..
        serving = env.wait_for_pair(_recovery_timeout)
        logger.info('Node %s serves after the failover', serving.node_name)

        # .. and the held key is finished.
        release(last_key)

        with pubsub_db_env(get_cluster_env(cluster)):
            _ = verify(prefix, keys)

# ################################################################################################################################
# ################################################################################################################################
