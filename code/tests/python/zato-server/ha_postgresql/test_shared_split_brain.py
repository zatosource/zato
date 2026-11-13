# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Attempts at a split brain on the database both nodes share. The process of the active node is frozen while its server
# continues, so the lease is not renewed and the standby takes over, under timers with the takeover time close
# to the mark-out time. The former server acknowledges publications until the server of the new active node raises
# the pub/sub generation and nothing afterwards, and the new active node delivers what it acknowledged before.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_publications_stored
from ha_takeover import ModuleCtx as TakeoverCtx
from ha_traffic import TimedPublisher
from nodes import Timers
from postgresql_checks import check_active_server, read_active_server, wait_for_raised_generation
from postgresql_env import ready_pair
from topology import docker
from workload import wait_for_deliveries
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from nodes import Node
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.split_brain')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The mark-out and takeover times of each attempt, in seconds, the takeover always the longer one
    Timer_Settings = [
        (3.0, 3.05),
        (3.0, 3.2),
        (2.0, 2.01),
    ]

    # How long the traffic runs before the freeze and after the server of the new active node starts, in seconds
    Traffic_Seconds = 10

    # The signals that freeze and resume the process of a node, which its server does not receive
    Signal_Freeze = 'STOP'
    Signal_Resume = 'CONT'

# ################################################################################################################################
# ################################################################################################################################

def _signal_node(node:'Node', signal:'str') -> 'None':
    """ Sends a signal to the process of a node only, which is the main process of its container.
    """
    _ = docker('kill', '--signal', signal, node.container_name)

# ################################################################################################################################

@pytest.mark.parametrize('timer_setting', ModuleCtx.Timer_Settings)
def test_split_brain(ha_session:'HASession', request:'any_', timer_setting:'tuple[float, float]') -> 'None':
    """ With the former server acknowledging while the standby takes over, the record names the new active node,
    the former server acknowledges nothing sent after the new server raised the generation, and every publication
    that the former server acknowledged is in the database and delivered.
    """
    timers = Timers()
    timers.mark_out, timers.takeover = timer_setting

    with ready_pair(ha_session, request.node.name, timers, []) as env:

        old_active = env.get_active()
        assert old_active is not None, 'No active node'

        new_active = env.get_other(old_active)
        generation_before, _ = read_active_server(env)

        # The server of the active node receives traffic directly, so that each acknowledgment comes from it ..
        publisher = TimedPublisher(old_active.server_url, env.publisher_username, env.publisher_password)
        publisher.start()

        time.sleep(ModuleCtx.Traffic_Seconds)

        # .. its node stops renewing the lease while the server continues ..
        _signal_node(old_active, ModuleCtx.Signal_Freeze)

        # .. the standby takes over ..
        _ = new_active.wait_for_role(TakeoverCtx.Active_Roles, TakeoverCtx.Takeover_Timeout)
        taken_over_at = time.time()

        # .. and its server raises the generation, after which the former server acknowledges nothing.
        raised_at = wait_for_raised_generation(env, generation_before, TakeoverCtx.Server_Timeout)
        _ = new_active.wait_until_server_up(TakeoverCtx.Server_Timeout)

        time.sleep(ModuleCtx.Traffic_Seconds)
        publisher.stop()

        record = env.referee.read_record()
        assert record is not None
        assert record['active_node'] == new_active.node_name, record

        late = publisher.get_acknowledged_between(raised_at, time.time())
        assert not late, f'{old_active.node_name} acknowledged after the generation was raised -> {late}'

        # What the former server acknowledged after the takeover and before the raise is not lost.
        before_raise = publisher.get_acknowledged_between(taken_over_at, raised_at)
        assert before_raise, f'{old_active.node_name} acknowledged nothing between the takeover and the raise'

        acknowledged = publisher.get_msg_ids()
        check_publications_stored(env, new_active, acknowledged)
        _ = wait_for_deliveries(cast_('any_', env), acknowledged)

        # The former node resumes, is fenced and joins again as the standby.
        _signal_node(old_active, ModuleCtx.Signal_Resume)
        _ = old_active.wait_for_role(TakeoverCtx.Standby_In_Sync, TakeoverCtx.Rejoin_Timeout)

        logs = old_active.read_logs()
        assert TakeoverCtx.Fencing_Text in logs, f'{old_active.node_name} was not fenced'

        check_active_server(env, new_active)

# ################################################################################################################################
# ################################################################################################################################
