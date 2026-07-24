# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.rule_engine.jobs.retention import run_retention
from zato.common.rule_engine.sql import DecisionFilter
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

def test_retention_deletes_only_expired_decisions(backend:'any_') -> 'None':
    """ Decisions past the window go, recent ones stay.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    # Three decisions well past the 90-day window and two fresh ones ..
    expired_time = now - timedelta(days=120)
    fresh_time = now - timedelta(days=5)

    seed_decisions(backend, ruleset.id, occurred_at=expired_time, count=3, decision_id_prefix='expired')
    seed_decisions(backend, ruleset.id, occurred_at=fresh_time, count=2, decision_id_prefix='fresh')

    # .. the sweep removes exactly the expired ones ..
    deleted_count = run_retention(backend, 90)
    assert deleted_count == 3

    # .. and the fresh ones remain readable.
    filters = DecisionFilter(ruleset_id=ruleset.id)
    remaining = backend.reporting.list_decisions(filters)
    assert len(remaining) == 2

# ################################################################################################################################

def test_retention_with_nothing_expired_deletes_nothing(backend:'any_') -> 'None':
    """ A sweep over fresh data is a clean no-op.
    """
    ruleset = create_ruleset(backend)
    now = utc_now()

    fresh_time = now - timedelta(days=5)
    seed_decisions(backend, ruleset.id, occurred_at=fresh_time, count=2, decision_id_prefix='fresh')

    deleted_count = run_retention(backend, 90)
    assert deleted_count == 0

# ################################################################################################################################
# ################################################################################################################################
