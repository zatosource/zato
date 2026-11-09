# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rejoin of a standby under traffic - through the backup, the frames after it and the admission. A crash
# of either node in each of the three phases leaves a pair that recovers, with nothing acknowledged lost.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_, anydict

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.rejoin')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The phases of a rejoin, as the active node reports them
    Phase_Backup    = 'backup'
    Phase_Catch_Up  = 'catch-up'
    Phase_Admission = 'admission'

    # The node that crashes
    Side_Joining = 'joining'
    Side_Active  = 'active'

    # The states of the link on the active node
    Link_Joining   = 'Joining'
    Link_Caught_Up = 'CaughtUp'

    # How long the traffic runs before each attempt, in seconds
    Traffic_Seconds = 15

    # How many times the standby is taken out and resumed until the crash finds the rejoin in the phase it needs
    Max_Attempts = 10

    # How often the active node is asked for its report while the test waits for a phase, in seconds
    Phase_Poll_Interval = 0.02

    # How long the test waits for a phase in one attempt, in seconds
    Phase_Timeout = 120

    # How long the active node may take to mark the standby out, in seconds
    Mark_Out_Timeout = 60

    # How long the pair may take to recover after the crash, in seconds
    Recovery_Timeout = 300

    # The roles of the active node alone and of the standby in sync
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _is_in_phase(report:'anydict', phase:'str') -> 'bool':
    """ Tells whether the report of the active node shows its rejoining standby in the given phase. The backup
    is confirmed only once it is complete, so a rejoin with no confirmed position is still in its backup.
    """
    if phase == ModuleCtx.Phase_Admission:
        out = report['link'] == ModuleCtx.Link_Caught_Up or report['admitting']
        return out

    if report['link'] != ModuleCtx.Link_Joining:
        return False

    has_confirmed = False

    for database in report['databases']:
        if database['confirmed']['frame'] > 0:
            has_confirmed = True

    if phase == ModuleCtx.Phase_Backup:
        out = not has_confirmed
    else:
        out = has_confirmed

    return out

# ################################################################################################################################

def _wait_for_phase(active:'Node', phase:'str') -> 'bool':
    """ Waits until the rejoin reaches the given phase and returns whether it did before it completed.
    """
    deadline = time.monotonic() + ModuleCtx.Phase_Timeout

    while time.monotonic() < deadline:
        report = active.read_role()

        if report is not None:

            if _is_in_phase(report, phase):
                return True

            # The rejoin completed without the test seeing the phase.
            if report['role'] == 'ActiveReplicated':
                return False

        time.sleep(ModuleCtx.Phase_Poll_Interval)

    return False

# ################################################################################################################################

def _crash_during(env:'HAEnvironment', phase:'str', side:'str') -> 'tuple[Node, float]':
    """ Takes the standby out and resumes it until a crash finds its rejoin in the given phase, and returns
    the node that crashed and the time of the crash.
    """
    for attempt in range(ModuleCtx.Max_Attempts):

        active = env.get_active()
        assert active is not None, 'No active node'

        joining = env.get_other(active)

        joining.kill()
        _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

        time.sleep(ModuleCtx.Traffic_Seconds)
        joining.resume()

        if _wait_for_phase(active, phase):

            if side == ModuleCtx.Side_Joining:
                crashed = joining
            else:
                crashed = active

            crashed_at = time.time()
            crashed.kill()

            logger.info('Killed %s during the %s, attempt %d', crashed.node_name, phase, attempt)

            out = (crashed, crashed_at)
            return out

        logger.info('Rejoin passed the %s unseen, attempt %d', phase, attempt)
        _ = joining.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Recovery_Timeout)

    raise Exception(f'No rejoin seen in its {phase} in {ModuleCtx.Max_Attempts} attempts')

# ################################################################################################################################

@pytest.mark.parametrize('side', [ModuleCtx.Side_Joining, ModuleCtx.Side_Active])
@pytest.mark.parametrize('phase', [ModuleCtx.Phase_Backup, ModuleCtx.Phase_Catch_Up, ModuleCtx.Phase_Admission])
def test_crash_during_rejoin(ha_pair:'HAEnvironment', phase:'str', side:'str') -> 'None':
    """ A crash of the joining node or of the active node during the rejoin leaves a pair that forms again
    once the crashed node starts, with nothing acknowledged lost and both copies equal.
    """
    env = ha_pair

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    crashed, crashed_at = _crash_during(env, phase, side)

    time.sleep(ModuleCtx.Traffic_Seconds)
    crashed.resume()

    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((crashed_at, time.time()))

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
