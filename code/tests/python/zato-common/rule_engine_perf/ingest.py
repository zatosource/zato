# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from threading import Thread
from time import monotonic, sleep

# humanize
from humanize import intcomma

# Local
from common import Floors, Full_Buffer_Sleep_Seconds, Ingest_Decision_Count, Ingest_Submitter_Count, Measurement, \
    percentile, PerfDatabase
from zato.common.rule_engine.sql import CapturePolicy, RuleSQLBackend
from zato.common.rule_engine.sql.errors import DecisionBufferFullError
from seeding import count_decision_rows, delete_all_rows
from traffic import build_decision, create_rulesets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import float_list, measurement_list
    from zato.common.rule_engine.sql import DecisionBatchWriter
    from zato.common.rule_engine.sql.data import strlist

    DecisionBatchWriter = DecisionBatchWriter
    float_list = float_list
    measurement_list = measurement_list
    strlist = strlist

    fired_count_dict = dict[str, int]
    thread_list = list[Thread]

# ################################################################################################################################
# ################################################################################################################################

# The day every ingested decision occurs on - one day keeps the rollup verification exact and simple.
Ingest_Base_Time = datetime(2026, 7, 1)

# How much of successful traffic keeps its full story - a production capture dial.
Ingest_Success_Capture_Percent = 10

# The latency percentiles the scenario reports.
Percentile_50 = 0.50
Percentile_95 = 0.95
Percentile_99 = 0.99

# How many milliseconds one second has.
Ms_Per_Second = 1000.0

# ################################################################################################################################
# ################################################################################################################################

class _SubmitterState:
    """ What one submitter thread produces - its accepted-submit latencies and its fired-rule totals.
    """

    def __init__(self) -> 'None':
        self.latencies:'float_list' = []
        self.admin_fired:'fired_count_dict' = {}
        self.clinical_fired:'fired_count_dict' = {}

# ################################################################################################################################
# ################################################################################################################################

def _count_fired(counts:'fired_count_dict', fired_rule_ids:'strlist') -> 'None':
    """ Adds one decision's fired rules to a submitter's running totals.
    """
    for rule_id in fired_rule_ids:
        if rule_id in counts:
            counts[rule_id] += 1
        else:
            counts[rule_id] = 1

# ################################################################################################################################

def _submit_share(
    writer:'DecisionBatchWriter',
    ruleset_ids:'tuple[int, int]',
    first_index:'int',
    last_index:'int',
    state:'_SubmitterState',
    ) -> 'None':
    """ What one submitter thread runs - its share of the measured decisions, each submitted
    with backpressure, retrying while the writer's bounded buffer reports saturation.
    """
    for index in range(first_index, last_index):

        # The occurred-at hour spreads over the day while every decision stays in one rollup bucket.
        occurred_at = Ingest_Base_Time.replace(hour=index % 24)
        decision = build_decision(index, ruleset_ids, occurred_at, 'ingest')

        # Submit with backpressure - saturation is the writer's documented contract, not an error here ..
        submit_start = monotonic()

        while True:
            try:
                writer.submit(decision)
                break
            except DecisionBufferFullError:
                sleep(Full_Buffer_Sleep_Seconds)

        submit_end = monotonic()
        state.latencies.append(submit_end - submit_start)

        # .. and keep exact per-rule totals for the zero-loss verification.
        if index % 2 == 0:
            _count_fired(state.admin_fired, decision.fired_rule_ids)
        else:
            _count_fired(state.clinical_fired, decision.fired_rule_ids)

# ################################################################################################################################

def _merge_counts(target:'fired_count_dict', source:'fired_count_dict') -> 'None':
    """ Folds one submitter's fired-rule totals into the combined expectation.
    """
    for rule_id, fired_count in source.items():
        if rule_id in target:
            target[rule_id] += fired_count
        else:
            target[rule_id] = fired_count

# ################################################################################################################################

def _rollup_totals(backend:'RuleSQLBackend', ruleset_id:'int') -> 'fired_count_dict':
    """ Sums the persisted daily firing counters of one ruleset by rule.
    """
    out:'fired_count_dict' = {}
    points = backend.reporting.daily_rule_counts(ruleset_id=ruleset_id)

    for point in points:
        if point.rule_id in out:
            out[point.rule_id] += point.firing_count
        else:
            out[point.rule_id] = point.firing_count

    return out

# ################################################################################################################################

def run_ingest_scenario(backend:'RuleSQLBackend', database:'PerfDatabase', floors:'Floors') -> 'measurement_list':
    """ The headline: concurrent submitters push the measured decisions through the live asynchronous
    writer, the rate must clear the decisions-per-second floor, and afterwards every decision is
    durably present with rollups exact to the generated traffic - zero silent loss under concurrency.
    """
    print(f'Ingest: {intcomma(Ingest_Decision_Count)} decisions, {Ingest_Submitter_Count} submitters', flush=True)

    # Start from empty tables with freshly created rulesets ..
    delete_all_rows(database)
    ruleset_ids = create_rulesets(backend)

    # .. the writer runs with a production capture dial ..
    capture_policy = CapturePolicy(success_percent=Ingest_Success_Capture_Percent, store_fired_rule_ids=True)
    writer = backend.decision_writer(capture_policy=capture_policy)
    writer.start()

    # .. each submitter gets an equal share of the measured decisions ..
    share = Ingest_Decision_Count // Ingest_Submitter_Count
    states:'list[_SubmitterState]' = []
    threads:'thread_list' = []

    for submitter_index in range(Ingest_Submitter_Count):
        first_index = submitter_index * share
        last_index = first_index + share
        state = _SubmitterState()
        states.append(state)
        thread = Thread(target=_submit_share, args=(writer, ruleset_ids, first_index, last_index, state))
        threads.append(thread)

    # .. the measured window runs from the first submit to the durable close ..
    start = monotonic()

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    writer.close()

    now = monotonic()
    elapsed = now - start

    # .. the rate must clear the headline floor ..
    rate = Ingest_Decision_Count / elapsed
    floor = floors.min_decision_rate
    assert rate >= floor, f'Ingest rate too low: {intcomma(int(rate))}/s, floor {floor}/s'

    # .. every decision must be durably present ..
    row_count = count_decision_rows(backend.session_factory)
    assert row_count == Ingest_Decision_Count, f'Expected {intcomma(Ingest_Decision_Count)} rows, found {intcomma(row_count)}'

    # .. and the persisted rollups must match the generated traffic exactly.
    expected_admin:'fired_count_dict' = {}
    expected_clinical:'fired_count_dict' = {}
    all_latencies:'float_list' = []

    for state in states:
        _merge_counts(expected_admin, state.admin_fired)
        _merge_counts(expected_clinical, state.clinical_fired)
        all_latencies.extend(state.latencies)

    persisted_admin = _rollup_totals(backend, ruleset_ids[0])
    persisted_clinical = _rollup_totals(backend, ruleset_ids[1])
    assert persisted_admin == expected_admin, 'Administrative rollups diverge from the generated traffic'
    assert persisted_clinical == expected_clinical, 'Clinical rollups diverge from the generated traffic'

    # Report the throughput, its secondary fired-rules reading and the submit latency percentiles.
    fired_total = 0

    for fired_count in expected_admin.values():
        fired_total += fired_count

    for fired_count in expected_clinical.values():
        fired_total += fired_count

    fired_rate = fired_total / elapsed
    all_latencies.sort()
    p50 = percentile(all_latencies, Percentile_50) * Ms_Per_Second
    p95 = percentile(all_latencies, Percentile_95) * Ms_Per_Second
    p99 = percentile(all_latencies, Percentile_99) * Ms_Per_Second

    print(f'Ingest: {intcomma(int(rate))} decisions/s, {intcomma(int(fired_rate))} fired rules/s in {elapsed:.2f}s', flush=True)

    out = [
        Measurement('Ingest decisions/s', intcomma(int(rate)), f'>= {floor}/s'),
        Measurement('Ingest fired rules/s', intcomma(int(fired_rate)), 'reported'),
        Measurement('Ingest submit p50/p95/p99 ms', f'{p50:.2f} / {p95:.2f} / {p99:.2f}', 'reported'),
        Measurement('Ingest rows persisted', intcomma(row_count), f'== {intcomma(Ingest_Decision_Count)}'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################
