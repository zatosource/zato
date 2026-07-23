# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

# SQLAlchemy
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.defaults import default_cluster_id

# Local
from .constants import Default_Retention_Chunk_Size, Default_Success_Capture_Percent, Hour_Bucket_Format, \
    Maximum_Capture_Percent, Minimum_Capture_Percent
from .data import decision_write_list, DecisionWrite, intset, rowdict, rowlist, RuleDecisionRecord, strlist, strset
from .database import SessionFactory
from .document import serialize_document, serialize_string_list
from .errors import DecisionAlreadyExistsError, InvalidStoreInputError, RecordNotFoundError, RuleSQLStoreError
from .records import decision_record
from .schema import rule_decision_table, rule_definition_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CapturePolicy:
    """ Controls which successful decisions retain their full story and whether fired rule identifiers are promoted.
    """

    success_percent:     'int'
    store_fired_rule_ids:'bool'

    def __init__(
        self,
        success_percent:'int' = Default_Success_Capture_Percent,
        store_fired_rule_ids:'bool' = False,
        ) -> 'None':

        # Ensure the configured percentage fits the complete sampling range ..
        if success_percent < Minimum_Capture_Percent:
            message = f'Success capture percentage cannot be below {Minimum_Capture_Percent}'
            raise InvalidStoreInputError(message)

        # .. reject values above the range too ..
        if success_percent > Maximum_Capture_Percent:
            message = f'Success capture percentage cannot exceed {Maximum_Capture_Percent}'
            raise InvalidStoreInputError(message)

        # .. and retain the validated policy.
        self.success_percent      = success_percent
        self.store_fired_rule_ids = store_fired_rule_ids

# ################################################################################################################################

    def keeps_story(self, decision:'DecisionWrite') -> 'bool':
        """ Returns whether this decision keeps its full story.
        """
        # Always retain errors because they are the decisions most likely to be investigated ..
        if decision.is_error:
            out = True

        # .. retain every successful story when full capture is configured ..
        elif self.success_percent == Maximum_Capture_Percent:
            out = True

        # .. retain no successful stories when header-only capture is configured ..
        elif self.success_percent == Minimum_Capture_Percent:
            out = False

        # .. otherwise derive a stable sample from the decision id, so retries always receive the same answer.
        else:
            decision_id = decision.decision_id.encode('utf-8')
            digest_builder = hashlib.sha256(decision_id)
            digest = digest_builder.digest()
            digest_prefix = digest[:8]
            sample = int.from_bytes(digest_prefix, 'big')
            sample_percent = sample % Maximum_Capture_Percent
            out = sample_percent < self.success_percent

        return out

# ################################################################################################################################
# ################################################################################################################################

def normalize_utc(value:'datetime') -> 'datetime':
    """ Converts a datetime to timezone-neutral UTC for portable storage.
    """
    # Convert an aware value to UTC and strip its timezone metadata ..
    if value.tzinfo:
        value = value.astimezone(timezone.utc)
        out = value.replace(tzinfo=None)

    # .. while a naive value is already the database representation used by this layer.
    else:
        out = value

    return out

# ################################################################################################################################

def decision_to_row(decision:'DecisionWrite', capture_policy:'CapturePolicy') -> 'rowdict':
    """ Converts a decision into one promoted header row with optional TEXT columns.
    """
    # Validate every required promoted field before any database work begins ..
    if not decision.decision_id:
        raise InvalidStoreInputError('Decision id is required')

    if not decision.outcome:
        raise InvalidStoreInputError('Decision outcome is required')

    if decision.rules_version < 1:
        raise InvalidStoreInputError('Rules version must be at least 1')

    if decision.duration_ms < 0:
        raise InvalidStoreInputError('Decision duration cannot be negative')

    # .. derive the portable UTC hour used by reporting ..
    occurred_at = normalize_utc(decision.occurred_at)
    time_bucket = occurred_at.strftime(Hour_Bucket_Format)
    has_payload = capture_policy.keeps_story(decision)

    # .. apply the capture dial to the complete story, always injecting the canonical fired-rule
    # .. list from the promoted field, so the stored copy can never diverge from what actually fired ..
    if has_payload:
        story = dict(decision.story)
        story['fired_rule_ids'] = decision.fired_rule_ids
        payload = serialize_document(story)
    else:
        payload = None

    # .. promote the compact fired-rule list only when explicitly configured ..
    if capture_policy.store_fired_rule_ids:
        fired_rule_ids = serialize_string_list(decision.fired_rule_ids)
    else:
        fired_rule_ids = None

    # .. and produce the one row that represents this decision.
    out = {
        'cluster_id':     default_cluster_id,
        'decision_id':    decision.decision_id,
        'ruleset_id':     decision.ruleset_id,
        'rules_version':  decision.rules_version,
        'occurred_at':    occurred_at,
        'time_bucket':    time_bucket,
        'business_key':   decision.business_key,
        'outcome':        decision.outcome,
        'is_error':       decision.is_error,
        'duration_ms':    decision.duration_ms,
        'has_payload':    has_payload,
        'payload':        payload,
        'fired_rule_ids': fired_rule_ids,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def find_existing_decision_ids(session:'Session', decision_ids:'strlist') -> 'strset':
    """ Returns which of the given external identifiers already exist in the decision log.
    """
    # Ask for exactly the identifiers under suspicion ..
    query = select(rule_decision_table.c.decision_id)
    cluster_condition = rule_decision_table.c.cluster_id == default_cluster_id
    id_condition = rule_decision_table.c.decision_id.in_(decision_ids)
    query = query.where(cluster_condition)
    query = query.where(id_condition)

    # .. and collect the ones the log already contains.
    out:'strset' = set()

    for row in session.execute(query):
        out.add(row[0])

    return out

# ################################################################################################################################

def diagnose_decision_integrity_error(session:'Session', decisions:'decision_write_list') -> 'RuleSQLStoreError':
    """ Explains a batch integrity failure, naming duplicate decision ids first and missing rulesets second.
    """
    # Collect both identifier populations from the failed batch ..
    decision_ids:'strlist' = []
    ruleset_ids:'intset' = set()

    for decision in decisions:
        decision_ids.append(decision.decision_id)
        ruleset_ids.add(decision.ruleset_id)

    # .. name any decision the log already contains ..
    existing = find_existing_decision_ids(session, decision_ids)

    if existing:
        existing_sorted = sorted(existing)
        existing_text = ', '.join(existing_sorted)
        out = DecisionAlreadyExistsError(f'Decision ids already exist in the decision log -> {existing_text}')
        return out

    # .. otherwise check which referenced rulesets the definitions table contains ..
    query = select(rule_definition_table.c.id)
    ruleset_condition = rule_definition_table.c.id.in_(ruleset_ids)
    query = query.where(ruleset_condition)
    found_ruleset_ids:'intset' = set()

    for row in session.execute(query):
        found_ruleset_ids.add(row[0])

    # .. name any ruleset the batch references but the database does not know ..
    missing_ruleset_ids = ruleset_ids - found_ruleset_ids

    if missing_ruleset_ids:
        missing_sorted = sorted(missing_ruleset_ids)
        missing_texts:'strlist' = []

        for ruleset_id in missing_sorted:
            missing_texts.append(f'{ruleset_id}')

        missing_text = ', '.join(missing_texts)
        out = RecordNotFoundError(f'No such rulesets referenced by decisions -> {missing_text}')
        return out

    # .. and admit an unrecognized violation rather than mislabeling it.
    out = InvalidStoreInputError('A decision batch violated database integrity')
    return out

# ################################################################################################################################
# ################################################################################################################################

class DecisionStore:
    """ Synchronous decision-log writes, lookups and timestamp retention.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def insert_batch(self, decisions:'decision_write_list', capture_policy:'CapturePolicy') -> 'int':
        """ Inserts one decision row per evaluation in a single multi-row statement.
        """
        # Convert every decision before opening a transaction, so invalid input writes nothing ..
        rows:'rowlist' = []
        seen_decision_ids:'strset' = set()

        for decision in decisions:

            # .. reject a batch that duplicates its own decision ids before touching the database ..
            if decision.decision_id in seen_decision_ids:
                message = f'Duplicate decision id within one batch -> {decision.decision_id}'
                raise DecisionAlreadyExistsError(message)

            seen_decision_ids.add(decision.decision_id)
            row = decision_to_row(decision, capture_policy)
            rows.append(row)

        # .. make an empty flush a successful no-op ..
        if not rows:
            out = 0
            return out

        # .. insert the whole batch in one transaction ..
        session = self._session_factory()

        try:
            with session.begin():
                statement = insert(rule_decision_table)
                _ = session.execute(statement, rows)

        # .. diagnose an integrity failure honestly, as duplicates or a missing ruleset, never a guess ..
        except IntegrityError as e:
            diagnosis_session = self._session_factory()

            try:
                error = diagnose_decision_integrity_error(diagnosis_session, decisions)
            finally:
                diagnosis_session.close()

            raise error from e

        # .. and always release the session.
        finally:
            session.close()

        out = len(rows)
        return out

# ################################################################################################################################

    def get(self, decision_id:'str') -> 'RuleDecisionRecord':
        """ Returns one decision by its external identifier.
        """
        # Query by the externally visible decision id ..
        session = self._session_factory()

        try:
            query = select(rule_decision_table)
            cluster_condition = rule_decision_table.c.cluster_id == default_cluster_id
            decision_condition = rule_decision_table.c.decision_id == decision_id
            query = query.where(cluster_condition)
            query = query.where(decision_condition)
            result = session.execute(query)
            row = result.one_or_none()

            # .. return the matching header and story when found ..
            if row:
                out = decision_record(row)

            # .. or name the missing decision directly.
            else:
                message = f'No such decision -> {decision_id}'
                raise RecordNotFoundError(message)

        # Release the read-only session in either case.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def delete_before(
        self,
        cutoff:'datetime',
        chunk_size:'int' = Default_Retention_Chunk_Size,
        ) -> 'int':
        """ Deletes expired decisions in bounded chunks using only the indexed timestamp.
        """
        if chunk_size < 1:
            raise InvalidStoreInputError('Retention chunk size must be at least 1')

        cutoff = normalize_utc(cutoff)

        # Our count of deleted decision rows.
        out = 0

        # Select one bounded group of expired identifiers at a time ..
        while True:
            session = self._session_factory()

            try:
                with session.begin():
                    query = select(rule_decision_table.c.id)
                    cluster_condition = rule_decision_table.c.cluster_id == default_cluster_id
                    cutoff_condition = rule_decision_table.c.occurred_at < cutoff
                    query = query.where(cluster_condition)
                    query = query.where(cutoff_condition)
                    query = query.order_by(rule_decision_table.c.id)
                    query = query.limit(chunk_size)

                    result = session.execute(query)
                    scalars = result.scalars()
                    decision_ids = scalars.all()

                    # .. stop when the indexed timestamp finds no more expired rows ..
                    if not decision_ids:
                        break

                    # .. delete exactly the selected group in the same transaction ..
                    statement = delete(rule_decision_table)
                    id_condition = rule_decision_table.c.id.in_(decision_ids)
                    statement = statement.where(id_condition)
                    _ = session.execute(statement)

                    # .. and add its size to the total.
                    deleted_count = len(decision_ids)
                    out += deleted_count

            # Release each chunk's session before selecting the next one.
            finally:
                session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################
