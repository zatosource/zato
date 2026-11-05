# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Item 15.14 - faults that run together - several faults at their own levels at the same time, a fault during
# a failover of the database, and a fault during the drain of a backlog.

# gevent
from gevent import sleep, spawn

# Zato
from faults import Fault
from zato.common.test.pubsub_replication import kill_primary, promote_standby

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from traffic import Traffic
    from zato.common.test.pubsub_replication import ReplicatedDatabase
    from zato.common.typing_ import anylist

    faultlevel  = tuple[Fault, int]
    faultlevels = list[faultlevel]

# ################################################################################################################################
# ################################################################################################################################

class CombinedFault(Fault):
    """ Several faults, each at its own level, applied and removed together.
    """

    def __init__(self, name:'str', parts:'faultlevels') -> 'None':
        self.name = name
        self.parts = parts

        for fault, _ in parts:
            self.min_duration = max(self.min_duration, fault.min_duration)

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        for fault, _ in self.parts:
            fault.start_baseline()

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        for fault, _ in self.parts:
            fault.end_baseline()

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        for fault, part_level in self.parts:
            fault.apply(part_level)

# ################################################################################################################################

    def remove(self) -> 'None':
        for fault, _ in reversed(self.parts):
            fault.remove()

# ################################################################################################################################
# ################################################################################################################################

class FailoverFault(Fault):
    """ A fault applied to the standby, after which the primary ends at once and the standby is promoted under the fault.
    """

    def __init__(self, name:'str', database:'ReplicatedDatabase', fault:'Fault', level:'int') -> 'None':
        self.name = name
        self.database = database
        self.fault = fault
        self.level = level

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self.fault.start_baseline()

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        self.fault.end_baseline()

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self.fault.apply(self.level)
        kill_primary(self.database)
        _ = promote_standby(self.database)

# ################################################################################################################################

    def remove(self) -> 'None':
        self.fault.remove()

# ################################################################################################################################
# ################################################################################################################################

class BacklogDrainFault(Fault):
    """ The pull partners stop for the first part of the fault, which builds a backlog, and resume for the rest of it,
    during which the backlog drains under another fault.
    """

    def __init__(self, name:'str', traffic:'Traffic', fault:'Fault', level:'int', backlog_seconds:'float') -> 'None':
        self.name = name
        self.traffic = traffic
        self.fault = fault
        self.level = level
        self.backlog_seconds = backlog_seconds
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self.fault.start_baseline()

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        self.fault.end_baseline()

# ################################################################################################################################

    def _resume_partners(self) -> 'None':
        for sub_key in self.traffic.partner_sub_keys:
            self.traffic.paused_sub_keys.discard(sub_key)

# ################################################################################################################################

    def _resume_under_fault(self) -> 'None':
        sleep(self.backlog_seconds)
        self.fault.apply(self.level)
        self._resume_partners()

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self.traffic.paused_sub_keys.update(self.traffic.partner_sub_keys)

        greenlet = spawn(self._resume_under_fault)
        self._greenlets.append(greenlet)

# ################################################################################################################################

    def remove(self) -> 'None':

        for greenlet in self._greenlets:
            greenlet.kill()

        self._greenlets = []
        self._resume_partners()
        self.fault.remove()

# ################################################################################################################################
# ################################################################################################################################
