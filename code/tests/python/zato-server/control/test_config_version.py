# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from random import Random

# gevent
import gevent

# Zato
from zato.server.control.config_version import ConfigVersionGate

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intlist

    any_ = any_
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many schedules of receipts and reloads the randomized test runs
    Schedule_Count = 500

    # The highest configuration version that a schedule commits
    Version_Max = 12

    # How many copies of one event a schedule delivers at most
    Copies_Max = 3

    # How many reloads a schedule requests at most
    Reloads_Max = 3

# ################################################################################################################################
# ################################################################################################################################

class Recorder:
    """ Records the events that a gate applies.
    """
    def __init__(self) -> 'None':
        self.applied:'intlist' = []

    def apply(self, event:'any_') -> 'None':
        self.applied.append(event)

# ################################################################################################################################
# ################################################################################################################################

def test_events_received_out_of_order_are_applied_in_version_order() -> 'None':
    recorder = Recorder()
    gate = ConfigVersionGate(0, recorder.apply)

    # The events of versions 3 and 2 are held ..
    gate.receive(3, 3)
    gate.receive(2, 2)

    assert recorder.applied == []
    assert gate.version == 0

    # .. until the event of version 1 arrives.
    gate.receive(1, 1)

    assert recorder.applied == [1, 2, 3]
    assert gate.version == 3
    assert gate.held == {}

# ################################################################################################################################

def test_an_event_whose_version_is_in_effect_is_skipped() -> 'None':
    recorder = Recorder()
    gate = ConfigVersionGate(5, recorder.apply)

    # The initial load put version 5 in effect ..
    gate.receive(4, 4)
    gate.receive(5, 5)

    assert recorder.applied == []

    # .. and the relayed copy of an applied event is skipped.
    gate.receive(6, 6)
    gate.receive(6, 6)

    assert recorder.applied == [6]
    assert gate.held == {}

# ################################################################################################################################

def test_a_reload_puts_held_events_up_to_its_version_in_effect() -> 'None':
    recorder = Recorder()
    gate = ConfigVersionGate(0, recorder.apply)

    # The event of version 1 never arrives, because its worker terminated before it sent it ..
    gate.receive(2, 2)
    gate.receive(4, 4)

    assert recorder.applied == []

    # .. so the reload that follows the termination reads version 3 with the configuration ..
    gate.reload(3)

    # .. after which version 4 is the next one, and no event up to version 3 is applied twice.
    assert recorder.applied == [4]
    assert gate.version == 4
    assert gate.held == {}

    gate.receive(2, 2)
    gate.receive(3, 3)

    assert recorder.applied == [4]

# ################################################################################################################################

def test_events_received_while_one_is_applied_follow_it() -> 'None':
    applied:'intlist' = []
    gate:'ConfigVersionGate'

    def receive_meanwhile() -> 'None':
        gate.receive(2, 2)
        gate.receive(1, 1)

    # Applying the event of version 1 switches greenlets, and another greenlet receives the next event and a copy ..
    def apply(event:'int') -> 'None':
        if event == 1:
            greenlet = gevent.spawn(receive_meanwhile)
            greenlet.join()

        applied.append(event)

    gate = ConfigVersionGate(0, apply)
    gate.receive(1, 1)

    # .. and the events are applied one at a time, in order, each one once.
    assert applied == [1, 2]
    assert gate.version == 2
    assert gate.held == {}

# ################################################################################################################################

def _run_schedule(random:'Random') -> 'None':
    recorder = Recorder()
    gate = ConfigVersionGate(0, recorder.apply)

    # Each version is delivered between one and several times, in any order ..
    deliveries:'intlist' = []

    for version in range(1, ModuleCtx.Version_Max + 1):
        copy_count = random.randint(1, ModuleCtx.Copies_Max)
        deliveries.extend([version] * copy_count)

    random.shuffle(deliveries)

    # .. with reloads at random points, each reading a version committed by then ..
    reload_count = random.randint(0, ModuleCtx.Reloads_Max)
    reload_points:'intlist' = []

    for _ in range(reload_count):
        point = random.randint(0, len(deliveries))
        reload_points.append(point)

    reloaded_versions:'intlist' = []

    for index, version in enumerate(deliveries):
        if index in reload_points:
            reload_version = random.randint(gate.version, ModuleCtx.Version_Max)
            reloaded_versions.append(reload_version)
            gate.reload(reload_version)

        gate.receive(version, version)

    # .. every version is in effect at the end ..
    assert gate.version == ModuleCtx.Version_Max
    assert gate.held == {}

    # .. the applied events are in increasing order and each one is applied once ..
    for previous, current in zip(recorder.applied, recorder.applied[1:]):
        assert previous < current

    # .. and every version not applied by an event was put in effect by a reload.
    covered = max(reloaded_versions, default=0)

    for version in range(covered + 1, ModuleCtx.Version_Max + 1):
        assert version in recorder.applied

# ################################################################################################################################

def test_any_schedule_applies_every_version_once_in_order() -> 'None':
    for seed in range(ModuleCtx.Schedule_Count):
        random = Random(seed)
        _run_schedule(random)

# ################################################################################################################################
# ################################################################################################################################
