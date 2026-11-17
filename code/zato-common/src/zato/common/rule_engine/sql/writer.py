# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import insert, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.typing_ import cast_

# Local
from .constants import Day_Bucket_Format, Default_Commit_Max_Decisions, Event_Type_Rule_Fired_Daily, System_Actor
from .data import decision_write_list, DecisionWrite, rowdict, rowlist
from .database import SessionFactory
from .decisions import CapturePolicy, decision_to_row, find_existing_decision_ids, normalize_utc
from .errors import InvalidStoreInputError
from .schema import rule_decision_table, rule_event_table
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

# How much of a group commit's capacity each decision takes - the capacity is counted in decisions
_decision_weight = 1

# ################################################################################################################################
# ################################################################################################################################

class _RollupKey(NamedTuple):
    """ One in-memory firing counter coordinate.
    """

    ruleset_id:    'int'
    rules_version: 'int'
    day_bucket:    'datetime'
    rule_id:       'str'

# ################################################################################################################################

class _PendingDecision:
    """ One decision of a group commit, with the failure that its caller receives if it alone could not be written.
    """

    def __init__(self, decision:'DecisionWrite') -> 'None':
        self.decision = decision
        self.error:'Exception | None' = None

# ################################################################################################################################

pending_decision_list:TypeAlias = list[_PendingDecision]
rollup_count_dict:TypeAlias = dict[_RollupKey, int]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DecisionWriterConfig:
    """ How many decisions one group commit writes at most.
    """

    commit_max_decisions: 'int'

    def __init__(self, *, commit_max_decisions:'int' = Default_Commit_Max_Decisions) -> 'None':

        # A commit admits at least the decision of the caller that runs it
        if commit_max_decisions < 1:
            raise InvalidStoreInputError('Decision writer commit size must be at least 1')

        self.commit_max_decisions = commit_max_decisions

# ################################################################################################################################
# ################################################################################################################################

class DecisionBatchWriter:
    """ Writes the decisions of concurrent callers in shared transactions, together with their firing counters.
    Each caller returns only once the transaction with its decision is committed, and an exception
    from that transaction reaches each caller whose decision was part of it.
    """

    def __init__(
        self,
        session_factory:'SessionFactory',
        capture_policy:'CapturePolicy',
        config:'DecisionWriterConfig',
        ) -> 'None':

        self._session_factory = session_factory
        self._capture_policy  = capture_policy

        # The decisions of concurrent callers share their commits
        self._commit_queue = CommitQueue(
            write_batch=self._flush,
            max_weight=config.commit_max_decisions,
        )

# ################################################################################################################################

    def submit(self, decision:'DecisionWrite') -> 'None':
        """ Writes one decision and returns once the transaction that holds it is committed.
        """
        pending = _PendingDecision(decision)
        self._commit_queue.write(pending, weight=_decision_weight, is_urgent=False)

        # The transaction committed, but this one decision could not be written in it
        if pending.error is not None:
            raise pending.error

# ################################################################################################################################

    def _day_bucket(self, occurred_at:'datetime') -> 'datetime':
        """ Returns the UTC start of the decision's daily firing-counter bucket.
        """
        # Normalize the decision timestamp ..
        occurred_at = normalize_utc(occurred_at)

        # .. format the portable day ..
        day_text = occurred_at.strftime(Day_Bucket_Format)

        # .. and parse its midnight boundary without database-specific date functions.
        out = datetime.strptime(day_text, Day_Bucket_Format)
        return out

# ################################################################################################################################

    def _rollup_counts(self, decisions:'decision_write_list') -> 'rollup_count_dict':
        """ Aggregates every fired rule in memory by ruleset, version and UTC day.
        """
        rollup_counts:'rollup_count_dict' = {}

        for decision in decisions:
            day_bucket = self._day_bucket(decision.occurred_at)

            for rule_id in decision.fired_rule_ids:
                key = _RollupKey(decision.ruleset_id, decision.rules_version, day_bucket, rule_id)

                if key in rollup_counts:
                    rollup_counts[key] += 1
                else:
                    rollup_counts[key] = 1

        return rollup_counts

# ################################################################################################################################

    def _upsert_rollups(self, session:'Session', rollup_counts:'rollup_count_dict') -> 'None':
        """ Adds each in-memory counter to its one daily row, so counter storage stays bounded
            by how many rules exist, never by traffic or by the flush cadence.
        """
        created_at = utc_now()

        for key, firing_count in rollup_counts.items():

            # Add the increment to the bucket's one existing row ..
            statement = update(rule_event_table)
            definition_condition = rule_event_table.c.definition_id == key.ruleset_id
            type_condition = rule_event_table.c.event_type == Event_Type_Rule_Fired_Daily
            bucket_condition = rule_event_table.c.bucket_start == key.day_bucket
            subject_condition = rule_event_table.c.subject_id == key.rule_id
            version_condition = rule_event_table.c.version == key.rules_version
            statement = statement.where(definition_condition)
            statement = statement.where(type_condition)
            statement = statement.where(bucket_condition)
            statement = statement.where(subject_condition)
            statement = statement.where(version_condition)
            incremented_count = rule_event_table.c.event_count + firing_count
            statement = statement.values(event_count=incremented_count)
            result = session.execute(statement)
            result = cast_(CursorResult, result)

            # .. and create that one row when this is the bucket's first increment.
            if result.rowcount == 0:
                event_row:'rowdict' = {
                    'definition_id': key.ruleset_id,
                    'version':       key.rules_version,
                    'event_type':    Event_Type_Rule_Fired_Daily,
                    'actor':         System_Actor,
                    'subject_id':    key.rule_id,
                    'bucket_start':  key.day_bucket,
                    'event_count':   firing_count,
                    'created_at':    created_at,
                    'payload':       None,
                }
                statement = insert(rule_event_table)
                _ = session.execute(statement, event_row)

# ################################################################################################################################

    def _flush_batch(self, decisions:'decision_write_list') -> 'None':
        """ Writes decisions and their firing increments in one transaction.
        """
        # Convert every decision before opening the transaction ..
        decision_rows:'rowlist' = []

        for decision in decisions:
            row = decision_to_row(decision, self._capture_policy)
            decision_rows.append(row)

        rollup_counts = self._rollup_counts(decisions)

        # .. and write them with their firing counters in one transaction.
        self._session_factory.write(self._insert_batch, decision_rows, rollup_counts)

# ################################################################################################################################

    def _insert_batch(self, session:'Session', decision_rows:'rowlist', rollup_counts:'rollup_count_dict') -> 'None':
        """ Persists one row per decision and folds the batch's firing counters into their daily rows in the same commit.
        """
        statement = insert(rule_decision_table)
        _ = session.execute(statement, decision_rows)

        self._upsert_rollups(session, rollup_counts)

# ################################################################################################################################

    def _is_duplicate(self, decision_id:'str') -> 'bool':
        """ Returns whether one decision id already exists in the log.
        """
        session = self._session_factory()

        try:
            decision_ids = [decision_id]
            existing = find_existing_decision_ids(session, decision_ids)
        finally:
            session.close()

        out = decision_id in existing
        return out

# ################################################################################################################################

    def _flush_each(self, pending_list:'pending_decision_list') -> 'None':
        """ Writes each decision with its firing increments in a transaction of its own. A decision whose id the log
        contains already is skipped, and any other failure is stored with the decision for its caller alone.
        """
        for pending in pending_list:

            # Write this one decision with its counters ..
            try:
                self._flush_batch([pending.decision])

            # .. skip a decision the log already holds, its row and its counters were committed before ..
            except IntegrityError as e:
                is_duplicate = self._is_duplicate(pending.decision.decision_id)

                # .. while a structural failure such as a missing ruleset reaches the caller of this decision.
                if not is_duplicate:
                    pending.error = e

# ################################################################################################################################

    def _flush(self, pending_list:'pending_decision_list') -> 'None':
        """ Writes the decisions of one group commit, one transaction for all of them, or one transaction per decision
        if any of them violates a constraint, so that a duplicate is skipped and the others are committed.
        """
        decisions:'decision_write_list' = []

        for pending in pending_list:
            decisions.append(pending.decision)

        try:
            self._flush_batch(decisions)
        except IntegrityError:
            self._flush_each(pending_list)

# ################################################################################################################################
# ################################################################################################################################
