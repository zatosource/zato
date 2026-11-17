# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

# Local
from zato.common.rule_engine.sql import CapturePolicy, DecisionFilter, DecisionWrite, DecisionWriterConfig, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Event_Type_Rule_Fired_Daily
from zato.common.rule_engine.sql.data import anydict, strlist
from zato.common.rule_engine.sql.schema import rule_event_table

# ################################################################################################################################
# ################################################################################################################################

def _rollup_row_count(backend:'RuleSQLBackend') -> 'int':
    """ Counts the physical firing-counter rows, proving storage stays bounded by rules, not traffic.
    """
    session = backend.session_factory()

    try:
        row_count = func.count(rule_event_table.c.id)
        query = select(row_count)
        type_condition = rule_event_table.c.event_type == Event_Type_Rule_Fired_Daily
        query = query.where(type_condition)
        result = session.execute(query)
        out = result.scalar_one()
    finally:
        session.close()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend') -> 'int':
    """ Creates the ruleset that owns the written decisions.
    """
    # Create one ruleset containing both fired and deliberately unfired stable identifiers ..
    document = {'rules': [{'id': 'preferential-rate'}, {'id': 'insurance-required'}, {'id': 'manual-review'}]}
    definition = backend.definitions.create(
        name='Lending decisions',
        object_type=Definition_Type_Ruleset,
        document=document,
        author='anna.k',
        comment='Create the decision writer ruleset',
    )

    # .. and return its promoted database identity.
    out = definition.id
    return out

# ################################################################################################################################

def _decision(
    *,
    decision_id:'str',
    ruleset_id:'int',
    occurred_at:'datetime',
    fired_rule_ids:'strlist',
    ) -> 'DecisionWrite':
    """ Builds one complete decision for the writer.
    """
    # Build the complete retained story ..
    story:'anydict' = {
        'input': {'customer.creditScore': 780},
        'output': {'loan.approved': True},
        'fired_rule_ids': fired_rule_ids,
        'messages': ['The lending decision completed.'],
    }
    # .. and pair it with the promoted decision header.
    out = DecisionWrite(
        decision_id=decision_id,
        ruleset_id=ruleset_id,
        rules_version=1,
        occurred_at=occurred_at,
        business_key=decision_id,
        outcome='approved',
        is_error=False,
        duration_ms=5,
        story=story,
        fired_rule_ids=fired_rule_ids,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_writer_batches_headers_and_daily_rule_counts(backend:'RuleSQLBackend') -> 'None':
    """ The writer commits decision rows together with bounded per-rule daily increments.
    """
    # Build three decisions whose firing counts overlap ..
    ruleset_id = _create_ruleset(backend)
    occurred_at = datetime(2026, 7, 21, 14, 30, tzinfo=timezone.utc)
    first_rule_ids = ['preferential-rate']
    second_rule_ids = ['preferential-rate', 'insurance-required']
    third_rule_ids = ['insurance-required']
    first = _decision(
        decision_id='decision-2001',
        ruleset_id=ruleset_id,
        occurred_at=occurred_at,
        fired_rule_ids=first_rule_ids,
    )
    second = _decision(
        decision_id='decision-2002',
        ruleset_id=ruleset_id,
        occurred_at=occurred_at,
        fired_rule_ids=second_rule_ids,
    )
    third = _decision(
        decision_id='decision-2003',
        ruleset_id=ruleset_id,
        occurred_at=occurred_at,
        fired_rule_ids=third_rule_ids,
    )

    # .. each submit returns once its decision is committed ..
    config = DecisionWriterConfig(commit_max_decisions=2)
    capture_policy = CapturePolicy()
    writer = backend.decision_writer(capture_policy=capture_policy, config=config)
    writer.submit(first)
    writer.submit(second)
    writer.submit(third)

    # .. verify one persisted header per decision ..
    filters = DecisionFilter(ruleset_id=ruleset_id)
    decisions = backend.reporting.list_decisions(filters)
    decision_count = len(decisions)
    assert decision_count == 3

    # .. verify the upserted increments aggregate into exact daily totals ..
    points = backend.reporting.daily_rule_counts(ruleset_id=ruleset_id)
    assert len(points) == 2
    assert points[0].rule_id == 'insurance-required'
    assert points[0].firing_count == 2
    assert points[1].rule_id == 'preferential-rate'
    assert points[1].firing_count == 2

    # .. verify counter storage is one physical row per rule, day and version, despite two
    # .. separate commits having incremented the insurance-required counter ..
    rollup_row_count = _rollup_row_count(backend)
    assert rollup_row_count == 2

    # .. and verify never-fired reporting uses the same counters.
    known_rule_ids = ['preferential-rate', 'insurance-required', 'manual-review']
    never_fired = backend.reporting.rules_that_never_fired(
        ruleset_id=ruleset_id,
        known_rule_ids=known_rule_ids,
    )
    assert never_fired == ['manual-review']

# ################################################################################################################################

def test_writer_skips_duplicates_without_stopping(backend:'RuleSQLBackend') -> 'None':
    """ A duplicate decision id is skipped without an error and every other decision is committed.
    """
    # Build a decision and a distinct one for the same ruleset ..
    config = DecisionWriterConfig(commit_max_decisions=2)
    capture_policy = CapturePolicy()
    writer = backend.decision_writer(capture_policy=capture_policy, config=config)
    ruleset_id = _create_ruleset(backend)
    occurred_at = datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc)
    fired_rule_ids = ['preferential-rate']
    decision = _decision(
        decision_id='decision-duplicate',
        ruleset_id=ruleset_id,
        occurred_at=occurred_at,
        fired_rule_ids=fired_rule_ids,
    )
    other_rule_ids = ['insurance-required']
    other = _decision(
        decision_id='decision-distinct',
        ruleset_id=ruleset_id,
        occurred_at=occurred_at,
        fired_rule_ids=other_rule_ids,
    )

    # .. submit the same decision id twice, alongside the distinct decision, a duplicate being a skip and not a failure ..
    writer.submit(decision)
    writer.submit(decision)
    writer.submit(other)

    # .. verify each distinct decision landed exactly once ..
    filters = DecisionFilter(ruleset_id=ruleset_id)
    decisions = backend.reporting.list_decisions(filters)
    decision_count = len(decisions)
    assert decision_count == 2

    # .. and verify the skipped duplicate was not counted in the firing rollups.
    points = backend.reporting.daily_rule_counts(ruleset_id=ruleset_id)
    assert len(points) == 2
    assert points[0].rule_id == 'insurance-required'
    assert points[0].firing_count == 1
    assert points[1].rule_id == 'preferential-rate'
    assert points[1].firing_count == 1

# ################################################################################################################################

def test_writer_surfaces_structural_failures(backend:'RuleSQLBackend') -> 'None':
    """ A missing ruleset is a structural failure that reaches the caller of the decision, never a silent skip.
    """
    # Submit one decision against a ruleset id that does not exist ..
    config = DecisionWriterConfig(commit_max_decisions=1)
    capture_policy = CapturePolicy()
    writer = backend.decision_writer(capture_policy=capture_policy, config=config)
    occurred_at = datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc)
    fired_rule_ids = ['preferential-rate']
    decision = _decision(
        decision_id='decision-structural',
        ruleset_id=987654,
        occurred_at=occurred_at,
        fired_rule_ids=fired_rule_ids,
    )

    # .. and verify the referential failure reaches the caller.
    with pytest.raises(IntegrityError):
        writer.submit(decision)

# ################################################################################################################################
# ################################################################################################################################
