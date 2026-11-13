# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two nodes partitioned from each other while both reach the database. The nodes of the shared storage mode
# exchange nothing directly, so the active node keeps renewing its lease, the standby takes no part in serving,
# and no takeover takes place however long the partition lasts.

# stdlib
import logging
import time

# Zato
from ha_checks import check_scheduler, check_workload, watch_roles
from ha_faults import heal, partition
from postgresql_checks import check_active_server
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.partition')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the partition, in seconds
    Traffic_Seconds = 10

    # How long the partition lasts, many times the takeover time, in seconds
    Partition_Seconds = 90

    # The role of the standby
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

def test_partition_between_nodes(ha_pair:'HAEnvironment') -> 'None':
    """ While the nodes do not reach each other and both reach the database, the record keeps naming the active node
    at its generation, the nodes never serve at the same time, and nothing acknowledged is lost.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The nodes lose each other ..
    partition(active, [standby.ip])
    partition(standby, [active.ip])

    both_active = watch_roles(env, ModuleCtx.Partition_Seconds)
    assert not both_active, both_active

    # .. and nothing changes, since neither of them depends on the other.
    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    assert active.is_active(), active.read_role()

    report = standby.read_role()
    assert report is not None
    assert report['role'] == ModuleCtx.Standby_In_Sync, report

    heal(active)
    heal(standby)

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_active_server(env, active)

# ################################################################################################################################
# ################################################################################################################################
