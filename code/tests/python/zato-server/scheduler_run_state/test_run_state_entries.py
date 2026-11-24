# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import SCHEDULER
from zato.common.common_db.store import SharedObjectStore
from zato.common.test.zato_database import zato_database_engine
from zato.server.scheduler_.run_state import ModuleCtx as RunStateCtx, SchedulerRunState

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict, callable_, callnone, intnone

    anydict = anydict
    callable_ = callable_
    callnone = callnone
    Engine = Engine
    intnone = intnone

    storegen = Iterator['_InterleavedStore']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Job_Name = 'test.run_state.job'

    First_Slot = '2026-11-14T10:00:00+00:00'
    Second_Slot = '2026-11-14T10:01:00+00:00'

    First_Entry = '1763114400000-0'
    Second_Entry = '1763114460000-0'
    Forced_Entry = '1763114430000-0'

# ################################################################################################################################
# ################################################################################################################################

class _InterleavedStore(SharedObjectStore):
    """ A store that runs one write of another server before the next compare-and-set of the run state.
    """
    def __init__(self, engine:'Engine') -> 'None':
        super().__init__()
        self._engine = engine
        self.before_next_write:'callnone' = None

    def compare_and_set(self, object_type:'str', name:'str', data:'anydict', version:'intnone') -> 'bool':

        if self.before_next_write is not None:
            other_write = self.before_next_write
            self.before_next_write = None
            other_write()

        out = super().compare_and_set(object_type, name, data, version)
        return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def store() -> 'storegen':
    with zato_database_engine() as engine:
        yield _InterleavedStore(engine)

# ################################################################################################################################

def _get_data(store:'SharedObjectStore') -> 'anydict':
    item = store.get(RunStateCtx.Object_Type, ModuleCtx.Job_Name)
    assert item is not None

    out = item.data
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_firing_delivered_again_after_its_worker_terminated_runs(store:'_InterleavedStore') -> 'None':
    run_state = SchedulerRunState(store)

    # A worker claims a slot and terminates before the run returns ..
    first = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    assert first.is_claimed

    # .. and its replacement claims the same entry again, which runs the slot in place of the lost run.
    again = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    assert again.is_claimed

    data = _get_data(store)
    assert data[RunStateCtx.Key_Run_Count] == 2
    assert data[RunStateCtx.Key_Claimed_By] == ModuleCtx.First_Entry

# ################################################################################################################################

def test_a_firing_delivered_again_after_its_run_returned_is_skipped(store:'_InterleavedStore') -> 'None':
    run_state = SchedulerRunState(store)

    # The run of the entry returns and releases its record ..
    _ = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    assert run_state.release(ModuleCtx.Job_Name, ModuleCtx.First_Entry)

    # .. so the same entry, delivered again because its worker terminated before the xack, is skipped.
    again = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    assert not again.is_claimed
    assert again.outcome == SCHEDULER.OUTCOME.SKIPPED_ALREADY_RUN

    data = _get_data(store)
    assert data[RunStateCtx.Key_Last_Slot] == ModuleCtx.First_Slot
    assert data[RunStateCtx.Key_Run_Count] == 1
    assert data[RunStateCtx.Key_Claimed_By] is None

# ################################################################################################################################

def test_an_entry_of_a_superseded_slot_is_skipped_and_releases_nothing(store:'_InterleavedStore') -> 'None':
    run_state = SchedulerRunState(store)

    # The entry of one slot is claimed, then the entry of the next slot ..
    _ = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    _ = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.Second_Slot, ModuleCtx.Second_Entry)

    # .. after which the first entry delivered again is skipped ..
    again = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    assert again.outcome == SCHEDULER.OUTCOME.SKIPPED_ALREADY_RUN

    # .. and the return of its run leaves the record of the second entry in place.
    assert not run_state.release(ModuleCtx.Job_Name, ModuleCtx.First_Entry)

    data = _get_data(store)
    assert data[RunStateCtx.Key_Last_Slot] == ModuleCtx.Second_Slot
    assert data[RunStateCtx.Key_Claimed_By] == ModuleCtx.Second_Entry

# ################################################################################################################################

def test_a_forced_run_keeps_the_record_and_a_release_retries_after_it(store:'_InterleavedStore') -> 'None':
    run_state = SchedulerRunState(store)

    _ = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    # A forced run counts itself and leaves the record of the scheduled entry ..
    forced = run_state.claim(ModuleCtx.Job_Name, '', ModuleCtx.Forced_Entry)
    assert forced.is_claimed
    assert _get_data(store)[RunStateCtx.Key_Claimed_By] == ModuleCtx.First_Entry

    # .. another forced run changes the run state between the read and the write of the release ..
    def run_forced() -> 'None':
        _ = run_state.claim(ModuleCtx.Job_Name, '', ModuleCtx.Forced_Entry)

    store.before_next_write = run_forced

    # .. and the release reads the state again and clears the record.
    assert run_state.release(ModuleCtx.Job_Name, ModuleCtx.First_Entry)

    data = _get_data(store)
    assert data[RunStateCtx.Key_Last_Slot] == ModuleCtx.First_Slot
    assert data[RunStateCtx.Key_Run_Count] == 3
    assert data[RunStateCtx.Key_Claimed_By] is None

# ################################################################################################################################

def test_a_run_state_written_before_the_records(store:'_InterleavedStore') -> 'None':
    run_state = SchedulerRunState(store)

    previous = {
        RunStateCtx.Key_Last_Slot: ModuleCtx.First_Slot,
        RunStateCtx.Key_Run_Count: 5,
    }
    assert store.compare_and_set(RunStateCtx.Object_Type, ModuleCtx.Job_Name, previous, None)

    # The slot that the previous server claimed is skipped, and nothing is released ..
    again = run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    assert again.outcome == SCHEDULER.OUTCOME.SKIPPED_ALREADY_RUN
    assert not run_state.release(ModuleCtx.Job_Name, ModuleCtx.First_Entry)

    # .. while a forced run and the next slot are claimed.
    assert run_state.claim(ModuleCtx.Job_Name, '', ModuleCtx.Forced_Entry).is_claimed
    assert run_state.claim(ModuleCtx.Job_Name, ModuleCtx.Second_Slot, ModuleCtx.Second_Entry).is_claimed

    data = _get_data(store)
    assert data[RunStateCtx.Key_Last_Slot] == ModuleCtx.Second_Slot
    assert data[RunStateCtx.Key_Run_Count] == 7
    assert data[RunStateCtx.Key_Claimed_By] == ModuleCtx.Second_Entry

# ################################################################################################################################
# ################################################################################################################################
