# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep, spawn

# Zato
from zato.server.config_gate import ChangeGate

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class GateUnderTest:
    """ A gate whose marks and changes are recorded in the order in which they happened.
    """

    def __init__(self) -> 'None':
        self.history:'anylist' = []
        self.gate = ChangeGate(self.send_mark)

    def send_mark(self, slot:'int', cid:'str') -> 'None':
        self.history.append(('mark', slot, cid))

    def change(self, name:'str') -> 'None':
        self.history.append(('change-start', name))
        sleep(0.01)
        self.history.append(('change-end', name))

    def run_change(self, name:'str') -> 'None':
        _ = self.gate.run(self.change, name)

# ################################################################################################################################
# ################################################################################################################################

def test_a_load_request_waits_for_the_change_in_progress() -> 'None':
    test = GateUnderTest()

    change = spawn(test.run_change, 'first')
    sleep(0)

    request = spawn(test.gate.request_load, 1, 'load-1')
    _ = change.join()
    _ = request.join()

    assert test.history == [('change-start', 'first'), ('change-end', 'first'), ('mark', 1, 'load-1')]

# ################################################################################################################################

def test_a_change_waits_for_every_load_in_progress() -> 'None':
    test = GateUnderTest()

    test.gate.request_load(0, 'load-0')
    test.gate.request_load(1, 'load-1')

    change = spawn(test.run_change, 'after-loads')
    sleep(0.02)

    assert test.history == [('mark', 0, 'load-0'), ('mark', 1, 'load-1')]

    test.gate.on_load_done(0, 'load-0')
    sleep(0.02)

    assert ('change-start', 'after-loads') not in test.history

    test.gate.on_load_done(1, 'load-1')
    _ = change.join()

    assert test.history[-2:] == [('change-start', 'after-loads'), ('change-end', 'after-loads')]

# ################################################################################################################################

def test_a_load_report_of_another_request_changes_nothing() -> 'None':
    test = GateUnderTest()

    test.gate.request_load(0, 'load-new')
    test.gate.on_load_done(0, 'load-old')

    assert test.gate.loading == {0: 'load-new'}
    assert not test.gate.idle.is_set()

# ################################################################################################################################

def test_a_terminated_worker_releases_its_load_and_its_request() -> 'None':
    test = GateUnderTest()

    test.gate.request_load(0, 'load-0')

    change = spawn(test.run_change, 'blocked')
    sleep(0)

    # The worker of slot 1 asks while the change waits for the load of slot 0, and terminates before its mark ..
    request = spawn(test.gate.request_load, 1, 'load-1')
    sleep(0)

    test.gate.on_worker_gone(1)

    # .. and the worker of slot 0 terminates during its load, after which the change runs and no mark follows.
    test.gate.on_worker_gone(0)

    _ = change.join()
    _ = request.join()

    assert test.history == [('mark', 0, 'load-0'), ('change-start', 'blocked'), ('change-end', 'blocked')]
    assert test.gate.loading == {}
    assert test.gate.pending == {}

# ################################################################################################################################

def test_the_loads_of_a_previous_config_process_hold_the_changes() -> 'None':
    test = GateUnderTest()

    test.gate.set_loading({2: 'load-2'})

    change = spawn(test.run_change, 'after-takeover')
    sleep(0.02)

    assert test.history == []

    test.gate.on_load_done(2, 'load-2')
    _ = change.join()

    assert test.history == [('change-start', 'after-takeover'), ('change-end', 'after-takeover')]

# ################################################################################################################################

def test_a_change_runs_its_nested_changes_without_waiting() -> 'None':
    test = GateUnderTest()

    def outer() -> 'None':
        test.history.append(('outer', 'start'))
        test.run_change('inner')
        test.history.append(('outer', 'end'))

    _ = test.gate.run(outer)

    assert test.history == [('outer', 'start'), ('change-start', 'inner'), ('change-end', 'inner'), ('outer', 'end')]

# ################################################################################################################################
# ################################################################################################################################
