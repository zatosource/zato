# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from time import monotonic

# humanize
from humanize import intcomma

# Local
from common import Floors, Measurement, Seeded_Decision_Count
from reporting_load import ReportingState
from zato.common.rules.sql import DecisionFilter, RuleSQLBackend
from seeding import count_decision_rows, Seed_Base_Time, Seed_Span_Hours

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import measurement_list

    measurement_list = measurement_list

# ################################################################################################################################
# ################################################################################################################################

# The retention boundary - everything in the older half of the seeded timeline expires.
Retention_Cutoff_Hours = Seed_Span_Hours // 2

# How many rows one retention chunk deletes.
Retention_Chunk_Size = 10_000

# ################################################################################################################################
# ################################################################################################################################

def _expected_deleted_count() -> 'int':
    """ Counts the seeded decisions that fall before the retention cutoff - the traffic spreads
    over the hourly buckets deterministically, so the expectation is exact.
    """
    per_bucket = Seeded_Decision_Count // Seed_Span_Hours
    remainder = Seeded_Decision_Count % Seed_Span_Hours

    out = 0

    for hour in range(Retention_Cutoff_Hours):
        bucket_count = per_bucket

        # The remainder of the division goes to the first buckets, one decision each.
        if hour < remainder:
            bucket_count += 1

        out += bucket_count

    return out

# ################################################################################################################################

def run_retention_scenario(backend:'RuleSQLBackend', floors:'Floors', state:'ReportingState') -> 'measurement_list':
    """ The retention sweep over the still-seeded million-row log - the older half expires in bounded
    chunks under the ceiling and reporting still answers correctly over what remains.
    """
    cutoff = Seed_Base_Time + timedelta(hours=Retention_Cutoff_Hours)
    expected_deleted = _expected_deleted_count()
    print(f'Retention: deleting {intcomma(expected_deleted)} rows before {cutoff}', flush=True)

    # Expire the older half in bounded chunks ..
    start = monotonic()
    deleted_count = backend.decisions.delete_before(cutoff, chunk_size=Retention_Chunk_Size)
    now = monotonic()
    retention_seconds = now - start

    # .. exactly the expired rows are gone, nothing more, nothing less ..
    assert deleted_count == expected_deleted, \
        f'Expected {intcomma(expected_deleted)} deletions, got {intcomma(deleted_count)}'

    remaining_count = count_decision_rows(backend.session_factory)
    expected_remaining = Seeded_Decision_Count - expected_deleted
    assert remaining_count == expected_remaining, \
        f'Expected {intcomma(expected_remaining)} remaining rows, found {intcomma(remaining_count)}'

    ceiling = floors.max_retention_seconds
    assert retention_seconds <= ceiling, f'Retention too slow: {retention_seconds:.2f}s, ceiling {ceiling}s'

    # .. and the dashboard still answers under its ceiling over what remains.
    filters = DecisionFilter(ruleset_id=state.admin_id)
    start = monotonic()
    outcome_counts = backend.reporting.outcome_counts(filters)
    now = monotonic()
    query_seconds = now - start

    assert outcome_counts, 'Expected outcomes after retention'
    query_ceiling = floors.max_report_query_seconds
    assert query_seconds <= query_ceiling, f'Post-retention query too slow: {query_seconds:.3f}s, ceiling {query_ceiling}s'

    print(f'Retention: {intcomma(deleted_count)} rows in {retention_seconds:.2f}s', flush=True)

    out = [
        Measurement('Retention sweep seconds', f'{retention_seconds:.2f}', f'<= {ceiling}s'),
        Measurement('Retention rows deleted', intcomma(deleted_count), f'== {intcomma(expected_deleted)}'),
        Measurement('Post-retention query seconds', f'{query_seconds:.3f}', f'<= {query_ceiling}s'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################
