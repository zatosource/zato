# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The long runs - one hour of takeovers every four minutes, each followed by a rejoin, and one hour of steady traffic.
# Both runs report every minute, stop when the root file system runs out of space, and end with the checks of every run,
# the bounds of the resources and the WAL, and the replication lag at zero.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies, check_no_runs_while_replaced, check_publications_stored, check_scheduler, \
    check_workload
from ha_soak import get_bound_violations, MinuteReporter, wait_for_zero_lag
from ha_takeover import ModuleCtx as TakeoverCtx, take_over
from ha_traffic import TimedPublisher
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

logger = logging.getLogger('zato.test.ha_consul.long_runs')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long each run lasts and how often the active node is replaced, in seconds
    Duration_Seconds = 60 * 60
    Switch_Interval_Seconds = 4 * 60

    # How often a run checks whether it must stop, in seconds
    Check_Interval = 1.0

    # How long the pair may take to recover, in seconds
    Recovery_Timeout = 300

# ################################################################################################################################
# ################################################################################################################################

def _wait_until(reporter:'MinuteReporter', deadline:'float') -> 'None':
    """ Waits until the given monotonic time, stopping the run if the reporter requires it.
    """
    while time.monotonic() < deadline:
        reporter.check()
        time.sleep(ModuleCtx.Check_Interval)

# ################################################################################################################################

def _start(env:'HAEnvironment') -> 'tuple[Workload, TimedPublisher, MinuteReporter]':
    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    reporter = MinuteReporter(env, workload, publisher)
    reporter.start()

    out = (workload, publisher, reporter)
    return out

# ################################################################################################################################

def _finish(env:'HAEnvironment', workload:'Workload', publisher:'TimedPublisher', reporter:'MinuteReporter') -> 'Node':
    """ Stops the traffic and the reports and applies the checks of every run, the bounds and the replication lag.
    """
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    publisher.stop()
    reporter.stop()

    violations = get_bound_violations(reporter.reports)
    assert not violations, violations

    check_workload(env, workload)
    check_publications_stored(active, publisher.get_msg_ids())

    wait_for_zero_lag(active)

    _ = check_scheduler(env, active)
    check_copies(env, active)

    return active

# ################################################################################################################################
# ################################################################################################################################

def test_repeated_failover(ha_pair:'HAEnvironment') -> 'None':
    """ The active node fails every four minutes for one hour with each fault of the takeover suite in turn,
    and its standby takes over each time while the former active node joins again.
    """
    env = ha_pair
    workload, publisher, reporter = _start(env)

    # Each replaced node with the time it was replaced and the time it became active again.
    replacements:'list[tuple[Node, float]]' = []
    reactivations:'dict[int, float]' = {}

    switch_count = ModuleCtx.Duration_Seconds // ModuleCtx.Switch_Interval_Seconds - 1
    started = time.monotonic()

    for index in range(switch_count):
        _wait_until(reporter, started + (index + 1) * ModuleCtx.Switch_Interval_Seconds)

        fault = TakeoverCtx.Faults[index % len(TakeoverCtx.Faults)]

        active = env.get_active()
        assert active is not None, 'No active node'

        reporter.add_event(f'{fault} of {active.node_name}')
        logger.info('Switch %d of %d - %s of %s', index + 1, switch_count, fault, active.node_name)

        new_active, old_active, takeover_time = take_over(env, fault, workload)

        # The node that takes over was itself replaced in an earlier switch, and that period ends now.
        for replacement_index, (replaced, _) in enumerate(replacements):
            if replaced is new_active and replacement_index not in reactivations:
                reactivations[replacement_index] = takeover_time

        replacements.append((old_active, takeover_time))

    _wait_until(reporter, started + ModuleCtx.Duration_Seconds)

    _ = _finish(env, workload, publisher, reporter)

    for replacement_index, (replaced, boundary) in enumerate(replacements):

        # A node that never became active again was replaced until the end of the run.
        if replacement_index in reactivations:
            reactivated = reactivations[replacement_index]
        else:
            reactivated = time.time()

        check_no_runs_while_replaced(env, replaced, boundary, reactivated)

# ################################################################################################################################

def test_soak(ha_pair:'HAEnvironment') -> 'None':
    """ One hour of steady traffic, with the resources of both containers and the WAL of each database within
    their bounds and the replication lag at zero once the traffic stops.
    """
    env = ha_pair
    workload, publisher, reporter = _start(env)

    _wait_until(reporter, time.monotonic() + ModuleCtx.Duration_Seconds)

    _ = _finish(env, workload, publisher, reporter)

# ################################################################################################################################
# ################################################################################################################################
