# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from time import monotonic

# humanize
from humanize import intcomma

# Local
from common import Batch_Count, Batch_Size, Floors, Measurement, PerfDatabase
from zato.common.rules.sql import CapturePolicy, RuleSQLBackend
from seeding import count_decision_rows, delete_all_rows
from traffic import build_decision, create_rulesets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import measurement_list
    from zato.common.rules.sql.data import decision_write_list

    decision_write_list = decision_write_list
    measurement_list = measurement_list

# ################################################################################################################################
# ################################################################################################################################

# The day every batched decision occurs on.
Batch_Base_Time = datetime(2026, 7, 2)

# How much of successful traffic keeps its full story - the same production dial the ingest uses.
Batch_Success_Capture_Percent = 10

# ################################################################################################################################
# ################################################################################################################################

def run_batch_scenario(backend:'RuleSQLBackend', database:'PerfDatabase', floors:'Floors') -> 'measurement_list':
    """ The synchronous path - one caller inserting realistic batches through insert_batch,
    without the background writer, must clear the same decisions-per-second claim.
    """
    total_count = Batch_Count * Batch_Size
    print(f'Batch: {Batch_Count} batches of {Batch_Size} decisions', flush=True)

    # Start from empty tables with freshly created rulesets ..
    delete_all_rows(database)
    ruleset_ids = create_rulesets(backend)
    capture_policy = CapturePolicy(success_percent=Batch_Success_Capture_Percent, store_fired_rule_ids=True)

    # .. build every batch before the measured window, the scenario measures the store, not generation ..
    batches:'list[decision_write_list]' = []

    for batch_index in range(Batch_Count):
        batch:'decision_write_list' = []

        for position in range(Batch_Size):
            index = batch_index * Batch_Size + position
            occurred_at = Batch_Base_Time.replace(hour=index % 24)
            decision = build_decision(index, ruleset_ids, occurred_at, 'batch')
            batch.append(decision)

        batches.append(batch)

    # .. insert every batch, each one its own transaction ..
    start = monotonic()

    for batch in batches:
        _ = backend.decisions.insert_batch(batch, capture_policy)

    now = monotonic()
    elapsed = now - start

    # .. the rate must clear the batch floor ..
    rate = total_count / elapsed
    floor = floors.min_batch_rate
    assert rate >= floor, f'Batch insert rate too low: {intcomma(int(rate))}/s, floor {floor}/s'

    # .. and every row must be durably present.
    row_count = count_decision_rows(backend.session_factory)
    assert row_count == total_count, f'Expected {intcomma(total_count)} rows, found {intcomma(row_count)}'

    print(f'Batch: {intcomma(int(rate))} decisions/s in {elapsed:.2f}s', flush=True)

    out = [
        Measurement('Batch insert decisions/s', intcomma(int(rate)), f'>= {floor}/s'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################
