# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from typing import NamedTuple

# humanize
from humanize import intcomma

# Local
from common import Floors, Measurement, PerfDatabase, Rollup_Day_Count, Rollup_Rule_Count, Seeded_Decision_Count
from zato.common.rules.sql import DecisionFilter, RuleSQLBackend
from seeding import delete_all_rows, seed_reporting_decisions, seed_rollups
from traffic import Admin_Rule_Ids, create_rulesets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import measurement_list
    from zato.common.rules.sql.data import strlist

    measurement_list = measurement_list
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The one drilled-down business key - an even index, so it belongs to the administrative ruleset.
Drill_Down_Business_Key = 'claim-0000200'

# The rule the forensic scan looks for and how many candidate headers it inspects.
Forensic_Rule_Id = 'in-network-provider'
Forensic_Limit   = 10_000

# The rules the never-fired report must name - no counter ever mentions them.
Never_Fired_Rule_Ids = ['annual-plan-review-due', 'welcome-visit-scheduled']

# ################################################################################################################################
# ################################################################################################################################

class ReportingState(NamedTuple):
    """ What the reporting scenario leaves behind for the retention sweep - the seeded log stays in place.
    """

    admin_id:    'int'
    clinical_id: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _known_rollup_rule_ids() -> 'strlist':
    """ Returns the stable identifiers of every administrative rule with a seeded counter,
    plus the two rules that never fired.
    """
    out:'strlist' = []
    rules_per_ruleset = Rollup_Rule_Count // 2
    catalog_size = len(Admin_Rule_Ids)

    for rule_index in range(rules_per_ruleset):
        base_rule_id = Admin_Rule_Ids[rule_index % catalog_size]
        out.append(f'{base_rule_id}-{rule_index:04d}')

    out.extend(Never_Fired_Rule_Ids)
    return out

# ################################################################################################################################

def run_reporting_scenario(
    backend:'RuleSQLBackend',
    database:'PerfDatabase',
    floors:'Floors',
    ) -> 'tuple[measurement_list, ReportingState]':
    """ The dashboard paths over the million-row log - every aggregate, the drill-down and the
    forensic scan answer under the ceiling, with ninety days of counters behind the trends.
    """
    print(f'Reporting: seeding {intcomma(Seeded_Decision_Count)} decision rows', flush=True)

    # Start from empty tables, then bulk-seed the measured volume ..
    delete_all_rows(database)
    ruleset_ids = create_rulesets(backend)

    decision_seconds = seed_reporting_decisions(database, ruleset_ids)
    rollup_seconds = seed_rollups(database, ruleset_ids)
    rollup_count = intcomma(Rollup_Rule_Count * Rollup_Day_Count)
    print(f'Reporting: decisions seeded in {decision_seconds:.2f}s, {rollup_count} rollup rows in {rollup_seconds:.2f}s', flush=True)

    ceiling = floors.max_report_query_seconds
    admin_id = ruleset_ids[0]
    filters = DecisionFilter(ruleset_id=admin_id)
    out:'measurement_list' = []

    # .. group the half-million administrative decisions by outcome ..
    start = monotonic()
    outcome_counts = backend.reporting.outcome_counts(filters)
    now = monotonic()
    elapsed = now - start

    outcome_count = len(outcome_counts)
    assert outcome_count == 4, f'Expected 4 outcomes, found {outcome_count}'
    assert elapsed <= ceiling, f'Outcome counts too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report outcome counts seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. group them by the write-time UTC hour ..
    start = monotonic()
    hourly_counts = backend.reporting.hourly_counts(filters)
    now = monotonic()
    elapsed = now - start

    assert hourly_counts, 'Expected hourly buckets'
    assert elapsed <= ceiling, f'Hourly counts too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report hourly counts seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. compare the version populations ..
    start = monotonic()
    version_counts = backend.reporting.version_counts(filters)
    now = monotonic()
    elapsed = now - start

    version_count = len(version_counts)
    assert version_count == 3, f'Expected 3 versions, found {version_count}'
    assert elapsed <= ceiling, f'Version counts too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report version counts seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. average the promoted duration column ..
    start = monotonic()
    _ = backend.reporting.average_duration_ms(filters)
    now = monotonic()
    elapsed = now - start

    assert elapsed <= ceiling, f'Average duration too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report average duration seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. sum ninety days of firing counters into the per-rule trend ..
    start = monotonic()
    fire_points = backend.reporting.daily_rule_counts(ruleset_id=admin_id)
    now = monotonic()
    elapsed = now - start

    assert fire_points, 'Expected daily firing counters'
    assert elapsed <= ceiling, f'Daily rule counts too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report daily rule counts seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. name the rules that never fired across the whole window ..
    known_rule_ids = _known_rollup_rule_ids()
    start = monotonic()
    never_fired = backend.reporting.rules_that_never_fired(ruleset_id=admin_id, known_rule_ids=known_rule_ids)
    now = monotonic()
    elapsed = now - start

    assert never_fired == Never_Fired_Rule_Ids, f'Unexpected never-fired rules -> {never_fired}'
    assert elapsed <= ceiling, f'Never-fired report too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report never-fired seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. drill one business-key aggregate down to its exact decision ..
    drill_filters = DecisionFilter(ruleset_id=admin_id, business_key=Drill_Down_Business_Key)
    start = monotonic()
    matches = backend.reporting.list_decisions(drill_filters)
    now = monotonic()
    elapsed = now - start

    match_count = len(matches)
    assert match_count == 1, f'Expected 1 drill-down match, found {match_count}'
    assert elapsed <= ceiling, f'Drill-down too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report drill-down seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    # .. and run the forensic scan - promoted columns narrow in SQL, stories are inspected in code.
    forensic_filters = DecisionFilter(ruleset_id=admin_id, rules_version=1)
    start = monotonic()
    forensic = backend.reporting.decisions_firing_rule(
        rule_id=Forensic_Rule_Id,
        filters=forensic_filters,
        limit=Forensic_Limit,
    )
    now = monotonic()
    elapsed = now - start

    assert forensic.decisions, 'The forensic scan found nothing'
    assert elapsed <= ceiling, f'Forensic scan too slow: {elapsed:.3f}s, ceiling {ceiling}s'
    out.append(Measurement('Report forensic scan seconds', f'{elapsed:.3f}', f'<= {ceiling}s'))

    print('Reporting: every query cleared its ceiling', flush=True)

    state = ReportingState(admin_id=admin_id, clinical_id=ruleset_ids[1])
    result = out, state
    return result

# ################################################################################################################################
# ################################################################################################################################
