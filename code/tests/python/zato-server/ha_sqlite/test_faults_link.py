# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Packet faults on the replication link - delay with jitter, loss, reordering, duplication, corruption and a bandwidth
# limit, each at every severity, in both directions between the nodes and on that link only. Each run reports
# the latency of the barrier and the acknowledgment rate, and total loss makes the active node mark the standby out.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
from ha_tools import degrade_link, get_netem, ModuleCtx as ToolsCtx, restore_link
from ha_traffic import get_percentile, TimedPublisher
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.faults_link')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the faults and under each severity, in seconds
    Traffic_Seconds = 10
    Window_Seconds = 30

    # The percentiles of the latency that each run reports
    Percentile_50 = 0.5
    Percentile_99 = 0.99

    # How long the pair may take to recover after a severity is removed, in seconds
    Recovery_Timeout = 300

    # How long the active node may take to mark the standby out at total loss, in seconds
    Mark_Out_Timeout = 60

    # The roles of the active node alone and of the standby in sync
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def degrade_replication_link(active:'Node', standby:'Node', netem:'str') -> 'None':
    degrade_link(active, [standby.ip], netem)
    degrade_link(standby, [active.ip], netem)

# ################################################################################################################################

def restore_replication_link(active:'Node', standby:'Node') -> 'None':
    restore_link(active)
    restore_link(standby)

# ################################################################################################################################

@pytest.mark.parametrize('kind', ToolsCtx.Packet_Faults)
def test_replication_link(ha_pair:'HAEnvironment', kind:'str') -> 'None':
    """ The pair acknowledges publications under each severity of a packet fault with one node active at a time,
    marks the standby out at total loss, and loses nothing.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # Each severity runs on its own and the pair recovers before the next one ..
    for severity in ToolsCtx.Severities:

        netem = get_netem(kind, severity)
        degrade_replication_link(active, standby, netem)

        started = time.time()
        both_active = watch_roles(env, ModuleCtx.Window_Seconds)
        ended = time.time()

        restore_replication_link(active, standby)
        workload.fault_windows.append((started, time.time()))

        assert not both_active, f'Two active nodes under {netem} -> {both_active}'

        latencies = publisher.get_latencies_between(started, ended)
        rate = len(latencies) / (ended - started)
        p50 = get_percentile(latencies, ModuleCtx.Percentile_50)
        p99 = get_percentile(latencies, ModuleCtx.Percentile_99)

        logger.info('%s %.0f%% -> %.1f acknowledgments/s, p50 %.3fs, p99 %.3fs', kind, severity * 100, rate, p50, p99)

        active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
        standby = env.get_other(active)

    # .. and total loss makes the active node continue alone.
    degrade_replication_link(active, standby, ToolsCtx.Total_Loss)
    started = time.time()

    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    restore_replication_link(active, standby)
    workload.fault_windows.append((started, time.time()))

    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Recovery_Timeout)

    publisher.stop()

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
