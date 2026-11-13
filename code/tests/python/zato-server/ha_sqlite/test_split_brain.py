# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Attempts at a split brain - the two nodes are partitioned from each other while both reach the API server, with timers
# under which the active node attempts its mark-out and the standby its takeover at nearly the same moment.
# The referee accepts one of the two, and only that node acknowledges anything afterwards.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_env import ready_pair
from ha_checks import check_copies
from ha_faults import heal, partition
from ha_traffic import TimedPublisher
from nodes import Timers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.split_brain')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The mark-out and takeover times of each attempt, in seconds, the takeover always the longer one
    Timer_Settings = [
        (3.0, 3.05),
        (3.0, 3.2),
        (2.0, 2.01),
    ]

    # How long the traffic runs before the partition and how long the partition lasts, in seconds
    Traffic_Seconds = 10
    Partition_Seconds = 90

    # How long the node that remains may take to serve requests again, in seconds
    Settle_Timeout = 120

    # How long the pair may take to form again once the partition is healed, in seconds
    Rejoin_Timeout = 300

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('timer_setting', ModuleCtx.Timer_Settings)
def test_split_brain(ha_session:'HASession', request:'any_', timer_setting:'tuple[float, float]') -> 'None':
    """ With both nodes acting at once, the referee names one active node, and the other acknowledges
    no publication from the moment of the partition onwards.
    """
    timers = Timers()
    timers.mark_out, timers.takeover = timer_setting

    with ready_pair(ha_session, request.node.name, timers, []) as env:

        # Each node receives its own traffic, so that each acknowledgment names the node that gave it ..
        publishers:'dict[str, TimedPublisher]' = {}

        for node in env.node_list:
            publisher = TimedPublisher(node.server_url, env.publisher_username, env.publisher_password)
            publisher.start()
            publishers[node.node_name] = publisher

        time.sleep(ModuleCtx.Traffic_Seconds)

        # .. the nodes lose each other while both reach the API server, from the moment the rules of the first node
        # are in place, since they drop the packets in both directions ..
        node_a, node_b = env.node_list

        partition(node_a, [node_b.ip])
        partitioned_at = time.time()

        partition(node_b, [node_a.ip])

        time.sleep(ModuleCtx.Partition_Seconds)

        # .. the referee named one of them ..
        record = env.referee.read_record()
        assert record is not None

        winner = env.get_node(record['active_node'])
        loser = env.get_other(winner)

        _ = winner.wait_until_server_up(ModuleCtx.Settle_Timeout)

        # .. and the other one acknowledged nothing since the partition.
        for publisher in publishers.values():
            publisher.stop()

        late = publishers[loser.node_name].get_acknowledged_between(partitioned_at, time.time())
        assert not late, f'{loser.node_name} acknowledged after the partition -> {late}'

        assert not loser.is_active(), loser.read_role()

        # Once the partition is healed, the other node joins again.
        heal(node_a)
        heal(node_b)

        _ = loser.wait_for_role(['StandbyInSync'], ModuleCtx.Rejoin_Timeout)
        env.point_database_at(winner)

        check_copies(env, winner)

# ################################################################################################################################
# ################################################################################################################################
