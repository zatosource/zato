# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from failover import docker, read_generation, wait_for_generation, wait_until_up
from pubsub_exactly_once.database import postgresql_only
from pubsub_exactly_once.harness import new_keys, stage_batch, verify
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import count_invocations, release
from zato.common.test.pubsub_database import pubsub_db_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_exactly_once_takeover.server_pair import ServerPair

# ################################################################################################################################
# ################################################################################################################################

# How many input messages each test publishes
_batch_count = 10

# How long the standby may take to take over the database once its container started, in seconds
_takeover_timeout = 180

# ################################################################################################################################
# ################################################################################################################################

@postgresql_only
def test_frozen_server_on_postgresql(server_pair:'ServerPair') -> 'None':
    """ The active server is frozen while its relay holds the last key of a batch, the standby takes over and
    delivers the batch, and the frozen server resumes and finishes the held key, whose commit is rejected.
    The database holds each output once.
    """
    pair = server_pair

    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    generation = read_generation(pair.database)

    # The relay of the active server holds the last key of a batch ..
    TestConfig.base_url = pair.active.base_url
    stage_batch(keys)

    # .. the server is frozen and the standby takes over ..
    _ = docker('pause', pair.active.container_name)

    _ = docker('start', pair.standby.container_name)
    _ = wait_until_up(pair.standby)
    _ = wait_for_generation(pair.database, generation + 1, _takeover_timeout)

    # .. and the frozen server resumes and finishes the held key.
    _ = docker('unpause', pair.active.container_name)
    release(last_key)

    with pubsub_db_env(pair.database.env):
        _ = verify(prefix, keys)

    assert count_invocations(last_key) >= 2

# ################################################################################################################################
# ################################################################################################################################
