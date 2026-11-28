# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from exactly_once.batch import run_conflict_isolated_in_batch_scenario, run_lease_after_ack_in_batch_scenario, \
    run_strict_duplicate_isolated_in_batch_scenario, run_two_leases_in_batch_scenario
from exactly_once.copies import run_concurrent_copies_scenario
from exactly_once.pull import run_ack_with_publications_scenario, run_concluded_with_other_publications_scenario, \
    run_concluded_with_same_publications_scenario, run_different_content_scenario, run_lease_ran_out_scenario, \
    run_repeated_call_scenario, run_stale_attempt_scenario
from exactly_once.push import run_announced_after_commit_scenario, run_atomic_rollback_scenario, \
    run_batch_committed_twice_scenario, run_conflicting_id_in_scope_scenario, run_cycle_rollback_scenario, \
    run_repeat_in_batch_scenario
from exactly_once.retention import run_deduplication_window_scenario, run_different_content_after_removal_scenario, \
    run_removed_by_expiry_scenario, run_window_after_over_cap_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# The prefix and the suffix of the name of each scenario function
_scenario_prefix = 'run_'
_scenario_suffix = '_scenario'

# The scenarios of the backend, each run against PostgreSQL
Scenarios = [
    run_atomic_rollback_scenario,
    run_cycle_rollback_scenario,
    run_repeat_in_batch_scenario,
    run_batch_committed_twice_scenario,
    run_announced_after_commit_scenario,
    run_conflicting_id_in_scope_scenario,
    run_ack_with_publications_scenario,
    run_stale_attempt_scenario,
    run_repeated_call_scenario,
    run_concluded_with_other_publications_scenario,
    run_concluded_with_same_publications_scenario,
    run_different_content_scenario,
    run_removed_by_expiry_scenario,
    run_lease_ran_out_scenario,
    run_concurrent_copies_scenario,
    run_deduplication_window_scenario,
    run_window_after_over_cap_scenario,
    run_different_content_after_removal_scenario,
    run_conflict_isolated_in_batch_scenario,
    run_strict_duplicate_isolated_in_batch_scenario,
    run_lease_after_ack_in_batch_scenario,
    run_two_leases_in_batch_scenario,
]

# ################################################################################################################################
# ################################################################################################################################

def get_scenario_id(scenario:'callable_') -> 'str':
    """ Returns the name of a scenario without the prefix and the suffix of its function.
    """
    out = scenario.__name__
    out = out.removeprefix(_scenario_prefix)
    out = out.removesuffix(_scenario_suffix)

    return out

# ################################################################################################################################
# ################################################################################################################################
