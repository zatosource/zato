# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# pytest
import pytest

# Local
from zato.common.rule_engine.sql import CapturePolicy, CountPoint, DecisionAlreadyExistsError, DecisionFilter, DecisionWrite, \
    RecordNotFoundError, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.rule_engine.sql.data import anydict, decision_write_list, strlist

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

# ################################################################################################################################
# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend') -> 'int':
    """ Creates the ruleset that owns test decisions.
    """
    # Create one ruleset containing every stable rule identifier used below ..
    document = {'rules': [{'id': 'preferential-rate'}, {'id': 'insurance-required'}]}
    definition = backend.definitions.create(
        name='Preferential lending',
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment='Create the lending ruleset',
    )

    # .. and return its promoted database identity.
    out = definition.id
    return out

# ################################################################################################################################

def _decision(
    *,
    decision_id:'str',
    ruleset_id:'int',
    rules_version:'int',
    occurred_at:'datetime',
    business_key:'str',
    outcome:'str',
    is_error:'bool',
    duration_ms:'int',
    fired_rule_ids:'strlist',
    ) -> 'DecisionWrite':
    """ Builds one complete realistic decision.
    """
    # Build the complete retained story, deliberately without a fired_rule_ids key,
    # because the write path injects the canonical list from the promoted field ..
    story:'anydict' = {
        'input': {'customer.creditScore': 780, 'loan.amount': 200000},
        'output': {'loan.approved': outcome == 'approved'},
        'messages': ['Excellent credit rule evaluated.'],
    }

    # .. and pair it with the promoted decision header.
    out = DecisionWrite(
        decision_id=decision_id,
        ruleset_id=ruleset_id,
        rules_version=rules_version,
        occurred_at=occurred_at,
        business_key=business_key,
        outcome=outcome,
        is_error=is_error,
        duration_ms=duration_ms,
        story=story,
        fired_rule_ids=fired_rule_ids,
    )
    return out

# ################################################################################################################################

def _reporting_decisions(ruleset_id:'int') -> 'decision_write_list':
    """ Returns four decisions spanning outcomes, versions and UTC hour buckets.
    """
    # Place the decisions across two UTC hours and two rules versions ..
    first_time = datetime(2026, 7, 20, 10, 15, tzinfo=timezone.utc)
    second_time = datetime(2026, 7, 20, 10, 45, tzinfo=timezone.utc)
    third_time = datetime(2026, 7, 20, 11, 5, tzinfo=timezone.utc)
    fourth_time = datetime(2026, 7, 20, 11, 35, tzinfo=timezone.utc)
    first_rule_ids = ['preferential-rate']
    second_rule_ids = ['preferential-rate', 'insurance-required']
    third_rule_ids = ['insurance-required']
    fourth_rule_ids:'strlist' = []

    first = _decision(
        decision_id='decision-approved-1001',
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=first_time,
        business_key='application-1001',
        outcome='approved',
        is_error=False,
        duration_ms=4,
        fired_rule_ids=first_rule_ids,
    )
    second = _decision(
        decision_id='decision-approved-1002',
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=second_time,
        business_key='application-1002',
        outcome='approved',
        is_error=False,
        duration_ms=6,
        fired_rule_ids=second_rule_ids,
    )
    third = _decision(
        decision_id='decision-declined-1003',
        ruleset_id=ruleset_id,
        rules_version=2,
        occurred_at=third_time,
        business_key='application-1003',
        outcome='declined',
        is_error=False,
        duration_ms=8,
        fired_rule_ids=third_rule_ids,
    )
    fourth = _decision(
        decision_id='decision-error-1004',
        ruleset_id=ruleset_id,
        rules_version=2,
        occurred_at=fourth_time,
        business_key='application-1004',
        outcome='error',
        is_error=True,
        duration_ms=10,
        fired_rule_ids=fourth_rule_ids,
    )

    # .. and return the complete population in insertion order.
    out = [first, second, third, fourth]
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_capture_policy_keeps_headers_and_every_error(backend:'RuleSQLBackend') -> 'None':
    """ Header-only capture still retains every decision header and every error story.
    """
    # Create one success and one error under a zero-percent success policy ..
    ruleset_id = _create_ruleset(backend)
    occurred_at = datetime(2026, 7, 20, 9, 30, tzinfo=timezone.utc)
    success_rule_ids = ['preferential-rate']
    error_rule_ids:'strlist' = []
    success = _decision(
        decision_id='decision-approved-header-only',
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=occurred_at,
        business_key='application-header-only',
        outcome='approved',
        is_error=False,
        duration_ms=5,
        fired_rule_ids=success_rule_ids,
    )
    error = _decision(
        decision_id='decision-error-full-story',
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=occurred_at,
        business_key='application-error-story',
        outcome='error',
        is_error=True,
        duration_ms=7,
        fired_rule_ids=error_rule_ids,
    )
    capture_policy = CapturePolicy(success_percent=0, store_fired_rule_ids=True)
    decisions = [success, error]
    inserted_count = backend.decisions.insert_batch(decisions, capture_policy)

    # .. verify that both promoted headers exist ..
    assert inserted_count == 2
    success_record = backend.decisions.get(success.decision_id)
    error_record = backend.decisions.get(error.decision_id)

    # .. verify that the success story was sampled out ..
    assert success_record.has_payload is False
    assert success_record.payload is None
    assert success_record.fired_rule_ids is not None

    # .. and verify that the error story was retained regardless of the dial.
    assert error_record.has_payload is True
    assert error_record.payload is not None

    # .. recover a sampled-out decision through the optional compact fired-rule column ..
    filters = DecisionFilter(ruleset_id=ruleset_id)
    forensic = backend.reporting.decisions_firing_rule(rule_id='preferential-rate', filters=filters)
    assert forensic.headers_without_payload == 0
    assert forensic.decisions == [success_record]

    # A duplicate mandatory decision id is an explicit domain error.
    duplicate_decisions = [success]
    with pytest.raises(DecisionAlreadyExistsError):
        _ = backend.decisions.insert_batch(duplicate_decisions, capture_policy)

# ################################################################################################################################

def test_missing_ruleset_is_named_not_mislabeled(backend:'RuleSQLBackend') -> 'None':
    """ A batch referencing a ruleset the database does not know names the ruleset, never a duplicate.
    """
    # Build one decision against a ruleset id that does not exist ..
    occurred_at = datetime(2026, 7, 20, 9, 30, tzinfo=timezone.utc)
    fired_rule_ids = ['preferential-rate']
    decision = _decision(
        decision_id='decision-missing-ruleset',
        ruleset_id=987654,
        rules_version=1,
        occurred_at=occurred_at,
        business_key='application-missing-ruleset',
        outcome='approved',
        is_error=False,
        duration_ms=5,
        fired_rule_ids=fired_rule_ids,
    )
    capture_policy = CapturePolicy()
    decisions = [decision]

    # .. and verify the integrity failure is diagnosed as the missing ruleset it is.
    with pytest.raises(RecordNotFoundError):
        _ = backend.decisions.insert_batch(decisions, capture_policy)

# ################################################################################################################################

def test_forensics_read_injected_story_rule_ids(backend:'RuleSQLBackend') -> 'None':
    """ Stored stories always carry the canonical fired-rule list even when producers omit it.
    """
    # Insert one full-capture decision whose input story has no fired_rule_ids key ..
    ruleset_id = _create_ruleset(backend)
    occurred_at = datetime(2026, 7, 20, 9, 30, tzinfo=timezone.utc)
    fired_rule_ids = ['preferential-rate']
    decision = _decision(
        decision_id='decision-injected-story',
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=occurred_at,
        business_key='application-injected-story',
        outcome='approved',
        is_error=False,
        duration_ms=5,
        fired_rule_ids=fired_rule_ids,
    )
    capture_policy = CapturePolicy()
    decisions = [decision]
    _ = backend.decisions.insert_batch(decisions, capture_policy)

    # .. and verify the story-path forensic search still finds it through the injected list.
    filters = DecisionFilter(ruleset_id=ruleset_id)
    forensic = backend.reporting.decisions_firing_rule(rule_id='preferential-rate', filters=filters)
    assert forensic.headers_without_payload == 0
    assert len(forensic.decisions) == 1
    assert forensic.decisions[0].decision_id == 'decision-injected-story'

# ################################################################################################################################

def test_promoted_reporting_drill_down_and_forensics(backend:'RuleSQLBackend') -> 'None':
    """ Aggregates use promoted columns and every number drills down to individual decisions.
    """
    # Insert one complete reporting set with promoted fired-rule identifiers ..
    ruleset_id = _create_ruleset(backend)
    decisions = _reporting_decisions(ruleset_id)
    capture_policy = CapturePolicy(success_percent=100, store_fired_rule_ids=True)
    inserted_count = backend.decisions.insert_batch(decisions, capture_policy)
    assert inserted_count == 4

    # .. group by outcome using portable SQL ..
    filters = DecisionFilter(ruleset_id=ruleset_id)
    outcome_counts = backend.reporting.outcome_counts(filters)
    expected_outcomes = [
        CountPoint('approved', 2),
        CountPoint('declined', 1),
        CountPoint('error', 1),
    ]
    assert outcome_counts == expected_outcomes

    # .. group by the write-time UTC bucket without a database date function ..
    hourly_counts = backend.reporting.hourly_counts(filters)
    expected_hours = [
        CountPoint('2026-07-20T10', 2),
        CountPoint('2026-07-20T11', 2),
    ]
    assert hourly_counts == expected_hours

    # .. compare version populations and duration from promoted headers only ..
    version_counts = backend.reporting.version_counts(filters)
    assert version_counts == [CountPoint(1, 2), CountPoint(2, 2)]
    average_duration = backend.reporting.average_duration_ms(filters)
    assert average_duration == 7.0

    # .. drill one business-key aggregate down to its exact decision ..
    business_filters = DecisionFilter(ruleset_id=ruleset_id, business_key='application-1003')
    matching_decisions = backend.reporting.list_decisions(business_filters)
    matching_count = len(matching_decisions)
    assert matching_count == 1
    assert matching_decisions[0].decision_id == 'decision-declined-1003'

    # .. narrow a rare rule investigation in SQL, then inspect retained stories in application code ..
    version_filters = DecisionFilter(ruleset_id=ruleset_id, rules_version=1)
    forensic = backend.reporting.decisions_firing_rule(
        rule_id='preferential-rate',
        filters=version_filters,
    )
    assert forensic.scanned_count == 2
    assert forensic.headers_without_payload == 0
    assert len(forensic.decisions) == 2

# ################################################################################################################################

def test_timestamp_retention_deletes_in_bounded_chunks(backend:'RuleSQLBackend') -> 'None':
    """ Retention deletes only rows older than the indexed cutoff and works across multiple chunks.
    """
    # Insert four decisions spanning two UTC hours ..
    ruleset_id = _create_ruleset(backend)
    decisions = _reporting_decisions(ruleset_id)
    capture_policy = CapturePolicy()
    _ = backend.decisions.insert_batch(decisions, capture_policy)

    # .. delete the first hour one row at a time ..
    cutoff = datetime(2026, 7, 20, 11, 0, tzinfo=timezone.utc)
    deleted_count = backend.decisions.delete_before(cutoff, chunk_size=1)
    assert deleted_count == 2

    # .. and verify every remaining row is on or after the cutoff.
    filters = DecisionFilter(ruleset_id=ruleset_id)
    remaining = backend.reporting.list_decisions(filters)
    assert len(remaining) == 2

    for decision in remaining:
        assert decision.occurred_at >= cutoff.replace(tzinfo=None)

# ################################################################################################################################
# ################################################################################################################################
