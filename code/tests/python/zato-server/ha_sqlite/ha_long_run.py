# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The traffic and the takeovers of the long runs, shared by the long runs of every referee. Each run publishes paced
# traffic, reports every minute and stops at the first minute that exceeds a bound.

# stdlib
import logging
import time

# Zato
from ha_checks import check_no_runs_while_replaced
from ha_soak import MinuteReporter
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

logger = logging.getLogger('zato.test.ha_consul.long_run')

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

    # How long each of the eight publishers of the workload and the timed publisher wait after each publication,
    # in seconds, which paces the traffic at about fifty messages a second, the rate that the puller and the push
    # subscriber each sustained under an unpaced load, so that the pair runs near its capacity without
    # a backlog that grows over the hour
    Workload_Publish_Interval = 0.1
    Timed_Publish_Interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

class Replacement:
    """ A node that a takeover replaced, the time it was replaced and the time it became active again, if it did.
    """

    def __init__(self, node:'Node', replaced_at:'float') -> 'None':
        self.node = node
        self.replaced_at = replaced_at
        self.reactivated_at:'float | None' = None

# ################################################################################################################################
# ################################################################################################################################

def wait_until(reporter:'MinuteReporter', deadline:'float') -> 'None':
    """ Waits until the given monotonic time, stopping the run if the reporter requires it.
    """
    while time.monotonic() < deadline:
        reporter.check()
        time.sleep(ModuleCtx.Check_Interval)

# ################################################################################################################################

def start_traffic(env:'HAEnvironment') -> 'tuple[Workload, TimedPublisher, MinuteReporter]':
    """ Starts the paced traffic of a long run through HAProxy and its reports.
    """
    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]), ModuleCtx.Workload_Publish_Interval)
    workload.start()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password,
        ModuleCtx.Timed_Publish_Interval)
    publisher.start()

    reporter = MinuteReporter(env, workload, publisher)
    reporter.start()

    out = (workload, publisher, reporter)
    return out

# ################################################################################################################################

def stop_traffic(env:'HAEnvironment', publisher:'TimedPublisher', reporter:'MinuteReporter') -> 'Node':
    """ Waits for the pair to recover, stops the timed publisher and the reports, and returns the active node.
    """
    out = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    publisher.stop()
    reporter.stop()

    return out

# ################################################################################################################################

def run_repeated_failover(env:'HAEnvironment', workload:'Workload', reporter:'MinuteReporter') -> 'list[Replacement]':
    """ Replaces the active node every four minutes for one hour with each fault of the takeover suite in turn,
    and returns each replacement.
    """
    out:'list[Replacement]' = []

    switch_count = ModuleCtx.Duration_Seconds // ModuleCtx.Switch_Interval_Seconds - 1
    started = time.monotonic()

    for index in range(switch_count):
        wait_until(reporter, started + (index + 1) * ModuleCtx.Switch_Interval_Seconds)

        fault = TakeoverCtx.Faults[index % len(TakeoverCtx.Faults)]

        active = env.get_active()
        assert active is not None, 'No active node'

        reporter.add_event(f'{fault} of {active.node_name}')
        logger.info('Switch %d of %d - %s of %s', index + 1, switch_count, fault, active.node_name)

        new_active, old_active, takeover_time = take_over(env, fault, workload)

        # The node that takes over was itself replaced in an earlier switch, and that period ends now.
        for replacement in out:
            if replacement.node is new_active:
                if replacement.reactivated_at is None:
                    replacement.reactivated_at = takeover_time

        out.append(Replacement(old_active, takeover_time))

    wait_until(reporter, started + ModuleCtx.Duration_Seconds)

    return out

# ################################################################################################################################

def check_replacements(env:'HAEnvironment', replacements:'list[Replacement]') -> 'None':
    """ Checks that no replaced node began a scheduler run until it became active again.
    """
    for replacement in replacements:

        # A node that never became active again was replaced until the end of the run.
        if replacement.reactivated_at is None:
            reactivated = time.time()
        else:
            reactivated = replacement.reactivated_at

        check_no_runs_while_replaced(env, replacement.node, replacement.replaced_at, reactivated)

# ################################################################################################################################
# ################################################################################################################################
