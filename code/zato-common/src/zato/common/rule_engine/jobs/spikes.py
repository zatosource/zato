# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
from datetime import timedelta
from logging import getLogger

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.store import raise_alert
from zato.common.audit_log.api import get_audit_engine
from zato.common.rule_engine.jobs.common import build_backend, configure_job
from zato.common.rule_engine.sql import DecisionFilter
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Event_Type_Decisions_Spiked, \
    Hour_Bucket_Format, System_Actor
from zato.common.rule_engine.sql.time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime

    from zato.common.rule_engine.sql import RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The current hour's count next to the typical hourly count.
count_pair:TypeAlias = tuple[int, int]

# ################################################################################################################################
# ################################################################################################################################

# The current hour spikes when it exceeds this many times the typical hourly count.
Spike_Multiplier = 5.0

# Below this many decisions in the current hour, nothing counts as a spike no matter the typical rate.
Spike_Minimum_Count = 100

# How many trailing hours establish what is typical for a ruleset.
Spike_Window_Hours = 24

# One continuing spike produces one event, not one per sweep - as long as sweeps
# keep observing it within this window of the previous observation.
Spike_Dedup_Window_Seconds = 3600

# How the deduplicating alert store files these findings.
Spike_Finding_Kind   = 'decision-spike'
Spike_Finding_Source = 'rule-engine'

# How many rulesets one sweep examines at most.
Max_Rulesets = 10_000

# ################################################################################################################################
# ################################################################################################################################

def _spike_counts(backend:'RuleSQLBackend', ruleset_id:'int', now:'datetime') -> 'count_pair':
    """ Returns the current hour's decision count and the typical hourly count of the trailing window.
    """
    # One indexed group-by covers the trailing window plus the current hour ..
    start_time = now - timedelta(hours=Spike_Window_Hours + 1)
    filters = DecisionFilter(ruleset_id=ruleset_id, start_time=start_time)
    points = backend.reporting.hourly_counts(filters)

    # .. split the buckets into the current hour and its history ..
    current_bucket = now.strftime(Hour_Bucket_Format)
    current_count = 0
    history_total = 0

    for point in points:
        if point.key == current_bucket:
            current_count = point.item_count
        else:
            history_total += point.item_count

    # .. silent hours have no bucket rows at all, so the typical rate
    # .. divides by the full window and not just by the buckets returned.
    typical_count = history_total // Spike_Window_Hours

    return current_count, typical_count

# ################################################################################################################################

def run_spike_sweep(backend:'RuleSQLBackend', now:'datetime | None' = None) -> 'int':
    """ Examines every ruleset's hourly decision counts and appends one spike event
    per newly detected spike, returning how many events were appended.
    """
    out = 0

    if now is None:
        now = utc_now()

    # The deduplicating alert store remembers spikes across sweeps ..
    audit_engine = get_audit_engine()

    # .. and every active ruleset is examined the same way.
    definitions = backend.definitions.list(object_type=Definition_Type_Ruleset, limit=Max_Rulesets)

    for definition in definitions:
        current_count, typical_count = _spike_counts(backend, definition.id, now)

        # Quiet hours never spike, no matter how quiet the history was ..
        if current_count < Spike_Minimum_Count:
            continue

        # .. and busy hours spike only when they dwarf the typical rate.
        threshold = Spike_Multiplier * typical_count
        if current_count <= threshold:
            continue

        # A spike was found - dedup decides whether it is a new one ..
        message = f"'{definition.name}' decided {current_count:,} times in the last hour " + \
            f'against a typical {typical_count:,}.'
        finding = new_finding(Spike_Finding_Kind, Spike_Finding_Source, definition.name, message)
        rule = new_rule(
            f'rule-engine.spike.{definition.name}',
            Spike_Finding_Kind,
            dedup_window_seconds=Spike_Dedup_Window_Seconds,
        )
        raise_result = raise_alert(audit_engine, rule, finding, now)

        # .. a continuing spike was already announced, only a new one becomes an event
        # .. for the notify loop to deliver.
        if raise_result.is_new:
            payload = {
                'hour':    now.strftime(Hour_Bucket_Format),
                'count':   current_count,
                'typical': typical_count,
            }
            _ = backend.events.append(
                definition_id=definition.id,
                version=None,
                event_type=Event_Type_Decisions_Spiked,
                actor=System_Actor,
                payload=payload,
            )

            logger.info('Decision spike on `%s` -> %d against a typical %d',
                definition.name, current_count, typical_count)
            out += 1

    return out

# ################################################################################################################################

def main() -> 'None':
    """ The spike alert sweep - one pass over every ruleset's hourly counts and exit.
    """
    # Set up the argument parser ..
    parser = argparse.ArgumentParser(description='Zato rule engine spike alerts - hourly decision count thresholds')

    _ = parser.add_argument(
        '--env-file', default='',
        help='Path to a file with environment variables to use')

    args = parser.parse_args()

    # .. prepare logging and the environment ..
    configure_job(args.env_file)

    # .. open the shared rule engine database ..
    backend = build_backend()

    # .. and run the one sweep.
    spike_count = run_spike_sweep(backend)
    suffix = 'spike' if spike_count == 1 else 'spikes'
    logger.info('Spike sweep complete -> %d new %s', spike_count, suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
