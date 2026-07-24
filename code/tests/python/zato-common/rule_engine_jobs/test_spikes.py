# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from datetime import timedelta

# Zato
from zato.common.rule_engine.jobs.spikes import run_spike_sweep
from zato.common.rule_engine.sql.constants import Event_Type_Decisions_Spiked
from zato.common.rule_engine.sql.time_ import utc_now

# Test helpers
from jobs_test_data import create_ruleset, seed_decisions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _spike_events(backend:'any_', definition_id:'int') -> 'any_':
    """ Returns every spike event of one ruleset, newest first.
    """
    out = []

    events = backend.events.list(definition_id=definition_id)
    for event in events:
        if event.event_type == Event_Type_Decisions_Spiked:
            out.append(event)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_spike_appends_one_event(backend:'any_') -> 'None':
    """ An hour far above the typical rate produces exactly one spike event with both counts.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    # A typical rate of 10 per hour over the trailing day ..
    history_time = now - timedelta(hours=3)
    seed_decisions(backend, ruleset.id, occurred_at=history_time, count=240, decision_id_prefix='history')

    # .. and a current hour that dwarfs it.
    seed_decisions(backend, ruleset.id, occurred_at=now, count=600, decision_id_prefix='current')

    spike_count = run_spike_sweep(backend, now)
    assert spike_count == 1

    events = _spike_events(backend, ruleset.id)
    assert len(events) == 1

    payload = json.loads(events[0].payload)
    assert payload['count'] == 600
    assert payload['typical'] == 10

# ################################################################################################################################

def test_a_continuing_spike_is_deduplicated(backend:'any_') -> 'None':
    """ The same spike observed by a later sweep produces no second event.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    history_time = now - timedelta(hours=3)
    seed_decisions(backend, ruleset.id, occurred_at=history_time, count=240, decision_id_prefix='history')
    seed_decisions(backend, ruleset.id, occurred_at=now, count=600, decision_id_prefix='current')

    first_sweep = run_spike_sweep(backend, now)
    assert first_sweep == 1

    # Five minutes later the spike is still there - and still one event.
    later = now + timedelta(minutes=5)
    second_sweep = run_spike_sweep(backend, later)
    assert second_sweep == 0

    events = _spike_events(backend, ruleset.id)
    assert len(events) == 1

# ################################################################################################################################

def test_quiet_hours_never_spike(backend:'any_') -> 'None':
    """ Below the minimum count nothing spikes, no matter how quiet the history was.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    # Ninety decisions from nothing is unusual but below the floor.
    seed_decisions(backend, ruleset.id, occurred_at=now, count=90, decision_id_prefix='current')

    spike_count = run_spike_sweep(backend, now)
    assert spike_count == 0

    events = _spike_events(backend, ruleset.id)
    assert events == []

# ################################################################################################################################

def test_steady_traffic_never_spikes(backend:'any_') -> 'None':
    """ A busy hour within the multiplier of its typical rate is business as usual.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    # A typical rate of 100 per hour ..
    history_time = now - timedelta(hours=3)
    seed_decisions(backend, ruleset.id, occurred_at=history_time, count=2400, decision_id_prefix='history')

    # .. and a current hour three times that - busy, not a spike.
    seed_decisions(backend, ruleset.id, occurred_at=now, count=300, decision_id_prefix='current')

    spike_count = run_spike_sweep(backend, now)
    assert spike_count == 0

# ################################################################################################################################
# ################################################################################################################################
