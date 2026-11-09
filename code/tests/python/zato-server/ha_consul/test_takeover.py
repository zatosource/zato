# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of a failed active node by its standby under traffic - the active node is stopped gracefully, killed,
# killed with its unsynced writes discarded, frozen, or cut off from the standby and Consul together. The standby takes over with a higher generation,
# the former active node is fenced when it resumes, runs nothing afterwards and joins again as the standby.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_no_runs_after, check_scheduler, check_workload
from ha_env import ready_pair
from ha_lazyfs import LazyFSHook
from ha_takeover import ModuleCtx, take_over
from nodes import Timers
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.takeover')

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_takeover(ha_pair:'HAEnvironment', fault:'str') -> 'None':
    """ The standby takes over from an active node that failed under traffic, no acknowledged publication is lost,
    every repeated push was in flight during the fault, no scheduler slot runs twice, the former active node runs
    no job after the takeover, and both copies are intact and equal once it joined again.
    """
    env = ha_pair

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    new_active, old_active, takeover_time = take_over(env, fault, workload)

    check_workload(env, workload)
    check_no_runs_after(env, old_active, takeover_time)

    _ = check_scheduler(env, new_active)
    check_copies(env, new_active)

# ################################################################################################################################

def test_takeover_with_lost_writes(ha_session:'HASession', request:'any_') -> 'None':
    """ The active node is killed and every write it did not sync is discarded, as on a host that lost its power.
    The standby takes over with nothing acknowledged lost, and the former active node joins again from a copy
    of the new active node, whatever its own files hold.
    """
    lazyfs = LazyFSHook()

    with ready_pair(ha_session, request.node.name, Timers(), [lazyfs]) as env:

        old_active = env.get_active()
        assert old_active is not None, 'No active node'

        new_active = env.get_other(old_active)

        workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
        workload.start()

        time.sleep(ModuleCtx.Traffic_Seconds)

        # The active node loses its power ..
        fault_started = time.time()
        old_active.kill()
        lazyfs.discard_unsynced(old_active)

        # .. its standby takes over ..
        _ = new_active.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
        takeover_time = time.time()

        _ = new_active.wait_until_server_up(ModuleCtx.Server_Timeout)
        env.point_database_at(new_active)

        time.sleep(ModuleCtx.Traffic_Seconds)

        # .. and the former active node starts again and joins as the standby.
        old_active.resume()
        workload.fault_windows.append((fault_started, time.time()))

        _ = old_active.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

        check_workload(env, workload)
        check_no_runs_after(env, old_active, takeover_time)

        _ = check_scheduler(env, new_active)
        check_copies(env, new_active)

# ################################################################################################################################
# ################################################################################################################################
