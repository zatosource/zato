# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of a failed active node by its standby under traffic, on the database both nodes share - the active node
# is stopped gracefully, killed, frozen, or cut off from the standby and the database together. The standby takes over
# once the lease is not renewed, the former active node is fenced when it resumes, runs nothing afterwards and joins
# again as the standby, and the database accepts the writes of the server of the new active node.

# stdlib
import logging

# pytest
import pytest

# Zato
from ha_checks import check_no_runs_after, check_scheduler, check_workload
from ha_takeover import ModuleCtx, take_over
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

logger = logging.getLogger('zato.test.ha_postgresql.takeover')

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_takeover(ha_pair:'HAEnvironment', fault:'str') -> 'None':
    """ The standby takes over from an active node that failed under traffic, no acknowledged publication is lost,
    every repeated push was in flight during the fault, no scheduler slot runs twice, the former active node runs
    no job after the takeover, and the database accepts the writes of the server of the new active node.
    """
    env = ha_pair

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    new_active, old_active, takeover_time = take_over(env, fault, workload)

    check_workload(env, workload)
    check_no_runs_after(env, old_active, takeover_time)

    # An active node that fails leaves the claim it committed before the run began without a run.
    _ = check_scheduler(env, new_active, ModuleCtx.Unrun_Claims_After_Takeover)
    check_active_server(env, new_active)

# ################################################################################################################################
# ################################################################################################################################
