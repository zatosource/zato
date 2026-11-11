# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rejoin of a standby under traffic - through the backup, the frames after it and the admission. A crash
# of either node in each of the three phases leaves a pair that recovers, with nothing acknowledged lost.
#
# Each phase is held until the crash. The link from the active node to the joining node is slowed down
# to a rate at which the backup of the current databases lasts a known time, and the frames written meanwhile
# reach the joining node over the same link during the catch-up. The admission is held by a referee
# that the active node cannot reach, after the link is fast again.

# stdlib
import logging
import os
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from ha_tools import change_link, degrade_links, restore_link
from topology import ModuleCtx as TopologyCtx
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

    # How long the traffic runs before the rejoin, in seconds
    Traffic_Seconds = 15

    # How often the active node is asked for its report while the test waits for a phase, in seconds
    Phase_Poll_Interval = 0.02

    # How long the test waits for a phase, in seconds
    Phase_Timeout = 180

    # How long the active node may take to mark the standby out, in seconds
    Mark_Out_Timeout = 60

    # How long the pair may take to recover after the crash, in seconds
    Recovery_Timeout = 300

    # The roles of the active node alone and of the active node with its standby in sync
    Active_Solo = ['ActiveSolo']
    Active_Replicated = 'ActiveReplicated'

    # The databases of a backup, each sent as its file and its log
    Database_Files = ['pubsub.db', 'common.db', 'audit.db']
    WAL_Suffix = '-wal'

    # How long the backup of the current databases lasts over the slowed link, in seconds
    Backup_Seconds = 60

    # The units of the rate of the slowed link
    Bits_Per_Byte = 8
    Bits_Per_Kbit = 1000

    # The bands of the link of the active node - to the joining node and to the referee
    Joining_Band = 1
    Referee_Band = 2

    # The parameters of netem that leave the packets unchanged and that drop every packet
    Unchanged_Netem = 'delay 0ms'
    Total_Loss = 'loss 100%'

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

def _wait_for_phase(active:'Node', phase:'str') -> 'None':
    """ Waits until the rejoin reaches the given phase.
    """
    deadline = time.monotonic() + ModuleCtx.Phase_Timeout

    while time.monotonic() < deadline:
        report = active.read_role()

        if report is not None:

            if _is_in_phase(report, phase):
                logger.info('Rejoin in its %s', phase)
                return

            if report['role'] == ModuleCtx.Active_Replicated:
                raise Exception(f'The rejoin completed before its {phase}')

        time.sleep(ModuleCtx.Phase_Poll_Interval)

    raise Exception(f'No rejoin in its {phase} within {ModuleCtx.Phase_Timeout}s')

# ################################################################################################################################

def _get_backup_netem(active:'Node') -> 'str':
    """ Returns the rate of the link at which the backup of the current databases of the active node lasts
    the configured time. Each log is sent only up to its end, so the backup may take less than that, never more.
    """
    total = 0

    for file_name in ModuleCtx.Database_Files:
        path = active.db_path(file_name)
        total += os.path.getsize(path)

        wal_path = path + ModuleCtx.WAL_Suffix
        if os.path.exists(wal_path):
            total += os.path.getsize(wal_path)

    kbit = total * ModuleCtx.Bits_Per_Byte // (ModuleCtx.Backup_Seconds * ModuleCtx.Bits_Per_Kbit)

    out = f'rate {kbit}kbit'
    return out

# ################################################################################################################################

def _crash_during(env:'HAEnvironment', phase:'str', side:'str') -> 'tuple[Node, float]':
    """ Takes the standby out, resumes it, holds its rejoin in the given phase and crashes one node there,
    and returns the node that crashed and the time of the crash.
    """
    active = env.get_active()
    assert active is not None, 'No active node'

    joining = env.get_other(active)

    joining.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The backup is slowed down, which also keeps the frames written in the meantime behind it ..
    netems = [
        ([joining.ip], _get_backup_netem(active)),
        ([TopologyCtx.Consul_IP], ModuleCtx.Unchanged_Netem),
    ]
    degrade_links(active, netems)

    joining.resume()
    _wait_for_phase(active, phase=ModuleCtx.Phase_Backup)

    # .. the active node read the address of the joining node before its backup began,
    # and from here on, it does not reach the referee that confirms an admission ..
    if phase == ModuleCtx.Phase_Admission:
        change_link(active, ModuleCtx.Referee_Band, ModuleCtx.Total_Loss)

    if phase != ModuleCtx.Phase_Backup:
        _wait_for_phase(active, phase=ModuleCtx.Phase_Catch_Up)

    # .. the backlog reaches the joining node over a fast link again, and the admission waits for the referee ..
    if phase == ModuleCtx.Phase_Admission:
        change_link(active, ModuleCtx.Joining_Band, ModuleCtx.Unchanged_Netem)
        _wait_for_phase(active, phase=ModuleCtx.Phase_Admission)

    if side == ModuleCtx.Side_Joining:
        crashed = joining
    else:
        crashed = active

    crashed_at = time.time()
    crashed.kill()

    logger.info('Killed %s during the %s', crashed.node_name, phase)

    # .. and the links are restored once the crash is done, unless the active node itself crashed,
    # since a container that starts again has a network of its own.
    if crashed is joining:
        restore_link(active)

    out = (crashed, crashed_at)
    return out

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
