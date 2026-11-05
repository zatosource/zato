# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Items 14.7 and 14.8 - the primary is promoted away during the production traffic of a soak, and failover and failback
# alternate at a fixed interval during it. Every acknowledged publication is delivered, the counts equal the raw rows
# after every switch and the resources of the process remain bounded.

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from faults import Fault, Total_Loss
from run import FaultRun
from runner import get_count_mismatches, get_duration
from zato.common.test.pubsub_replication import kill_primary, promote_standby, switch_primary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from traffic import Traffic
    from zato.common.test.pubsub_replication import ReplicatedDatabase
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# How long a managed service takes to detect the loss of its primary before it promotes the standby, in seconds.
_detection_seconds = 2

# How long publishing may take to resume after the primary is lost, in seconds, and how often it is checked.
_resume_timeout_seconds = 300
_resume_poll_seconds = 0.1

# How often failover and failback alternate, in seconds, unless Zato_Test_Failover_Interval_Seconds says otherwise.
_failover_interval_seconds = 600

# How often the loop of the switches checks whether it is to stop, in seconds.
_switch_poll_seconds = 1

# The minute after the warm-up, whose resources the last minute is compared with.
_baseline_minute = 5

# ################################################################################################################################
# ################################################################################################################################

class PromotionFault(Fault):
    """ The primary ends at once during the traffic and the standby is promoted once the service detects the loss.
    The fault measures how long publishing takes to resume.
    """

    def __init__(self, name:'str', database:'ReplicatedDatabase', traffic:'Traffic') -> 'None':
        self.name = name
        self.database = database
        self.traffic = traffic
        self.promote_seconds = 0.0
        self.resume_seconds = 0.0

# ################################################################################################################################

    def _count_acknowledged(self) -> 'int':
        with self.traffic.lock:
            out = self.traffic.acknowledged_partner_count
        return out

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        lost_at = monotonic()
        kill_primary(self.database)

        sleep(_detection_seconds)
        self.promote_seconds = promote_standby(self.database)

        # Publishing has resumed once a publication is acknowledged by the promoted server ..
        acknowledged = self._count_acknowledged()
        deadline = monotonic() + _resume_timeout_seconds

        while self._count_acknowledged() == acknowledged:
            assert monotonic() < deadline, f'Publishing did not resume within {_resume_timeout_seconds}s'
            sleep(_resume_poll_seconds)

        # .. which is measured from the moment the primary was lost.
        self.resume_seconds = round(monotonic() - lost_at, 1)

        print(f'{self.name} | promoted in {self.promote_seconds:.1f}s | publishing resumed after {self.resume_seconds}s',
            flush=True)

# ################################################################################################################################

    def remove(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class RepeatedFailoverFault(Fault):
    """ Failover and failback alternate at a fixed interval for as long as the fault lasts, and the counts
    are compared with the raw rows after every switch.
    """

    def __init__(self, name:'str', database:'ReplicatedDatabase', interval_seconds:'int') -> 'None':
        self.name = name
        self.database = database
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.switches:'anylist' = []
        self._greenlet:'any_' = None

# ################################################################################################################################

    def _switch_loop(self) -> 'None':
        next_switch = monotonic() + self.interval_seconds

        while self.is_running:

            # A switch, once started, completes before the loop checks whether it is to stop ..
            if monotonic() >= next_switch:
                promote_seconds = switch_primary(self.database)
                mismatches = get_count_mismatches(is_snapshot=True)

                self.switches.append((promote_seconds, mismatches))

                print(f'{self.name} | switch {len(self.switches)} | promoted in {promote_seconds:.1f}s | ' + \
                    f'count mismatches {len(mismatches)}', flush=True)

                next_switch = monotonic() + self.interval_seconds

            # .. and otherwise, it waits for the next one.
            sleep(_switch_poll_seconds)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self.is_running = True
        self._greenlet = spawn(self._switch_loop)

# ################################################################################################################################

    def remove(self) -> 'None':
        self.is_running = False

        if self._greenlet:
            _ = self._greenlet.get()
            self._greenlet = None

# ################################################################################################################################
# ################################################################################################################################

def test_failover_during_soak(failover_database:'ReplicatedDatabase') -> 'None':
    """ Item 14.7 - the primary is lost during the production traffic of a soak and the standby is promoted.
    The phases come from the Zato_Test_Fault_* variables, which a soak sets to its hours.
    """
    run = FaultRun('')

    fault = PromotionFault('failover-during-soak', failover_database, run.traffic)

    run.label = fault.name
    run.run(fault, Total_Loss)
    run.check()

    monitor = run.monitor
    assert monitor is not None
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)

# ################################################################################################################################

def test_repeated_failover(failover_database:'ReplicatedDatabase') -> 'None':
    """ Item 14.8 - failover and failback alternate every ten minutes during the production traffic of a soak,
    whose length the Zato_Test_Fault_Seconds variable sets.
    """
    interval_seconds = get_duration('Zato_Test_Failover_Interval_Seconds', _failover_interval_seconds)

    fault = RepeatedFailoverFault('repeated-failover', failover_database, interval_seconds)

    run = FaultRun(fault.name)
    run.run(fault, Total_Loss)
    run.check()

    assert fault.switches, 'No switch took place'

    for index, (_, mismatches) in enumerate(fault.switches, 1):
        assert not mismatches, (index, mismatches)

    monitor = run.monitor
    assert monitor is not None
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)

# ################################################################################################################################
# ################################################################################################################################
