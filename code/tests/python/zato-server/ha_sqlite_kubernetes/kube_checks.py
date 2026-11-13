# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks of every run applied to a pair in Kubernetes, and the report of how long the Service listed no pod.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment, KubeNode
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite_kubernetes.checks')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before a fault, in seconds
    Traffic_Seconds = 15

    # How long the pair may take to recover once a fault is removed, in seconds, which includes pods that start again
    Recovery_Timeout = 600

# ################################################################################################################################
# ################################################################################################################################

def start_workload(env:'KubeEnvironment') -> 'Workload':
    """ Starts the shared workload against the Service of the pair and lets it run before a fault.
    """
    out = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    out.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    return out

# ################################################################################################################################

def get_pair(env:'KubeEnvironment') -> 'tuple[KubeNode, KubeNode]':
    """ Returns the active pod and its standby, each with the node it runs on.
    """
    active = env.get_active()
    assert active is not None, 'No active pod'

    standby = env.get_other(active)

    active.locate()
    standby.locate()

    out = (active, standby)
    return out

# ################################################################################################################################

def finish(env:'KubeEnvironment', workload:'Workload', fault_started:'float') -> 'KubeNode':
    """ Waits for the pair, reports how long the Service listed no pod after the fault and applies the checks of every run.
    """
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    for period_start, period_end in env.watcher.get_empty_periods_after(fault_started):
        logger.info('Service listed no pod for %.1fs, from %.3f', period_end - period_start, period_start)

    check_workload(cast_('any_', env), workload)

    _ = check_scheduler(cast_('any_', env), active)
    check_copies(cast_('any_', env), active)

    return active

# ################################################################################################################################
# ################################################################################################################################
