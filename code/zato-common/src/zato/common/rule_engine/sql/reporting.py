# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import case, func, select

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Event_Type_Rule_Fired_Daily
from .data import count_point_list, decision_record_list, CountPoint, DecisionFilter, rule_fire_point_list, \
    RuleFirePoint, strlist, strset
from .database import SessionFactory
from .decisions import normalize_utc
from .document import deserialize_document, deserialize_string_list
from .errors import InvalidStoreInputError
from .records import decision_record
from .reporting_common import add_count, apply_filters, bucket_split_dict, BucketSplit, count_points, \
    count_total_dict, DecisionAggregates, ForensicResult, In_Named_Bucket, Outside_Named_Bucket
from .schema import rule_decision_table, rule_event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime

    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

class RuleReporting:
    """ Portable aggregate, drill-down and forensic queries over promoted columns.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def list_decisions(self, filters:'DecisionFilter', *, limit:'int' = 100) -> 'decision_record_list':
        """ Lists individual decision headers and retained stories using keyset pagination.
        """
        # Reject an unusable page size ..
        if limit < 1:
            raise InvalidStoreInputError('Decision list limit must be at least 1')

        # .. apply only promoted-column filters ..
        query = select(rule_decision_table)
        query = apply_filters(query, filters)
        decision_id_descending = rule_decision_table.c.id.desc()
        query = query.order_by(decision_id_descending)
        query = query.limit(limit)
        session = self._session_factory()

        # .. load the requested page ..
        try:
            result = session.execute(query)
            out:'decision_record_list' = []

            for row in result:
                record = decision_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def decision_count(self, filters:'DecisionFilter') -> 'int':
        """ How many decisions one selection holds - one number, over promoted columns alone.

        This is what tells a rename how much traffic addresses the ruleset it is about to rename,
        so the count is answered by the database rather than by loading the rows.
        """
        # Count the selection itself, without grouping it by anything ..
        decision_count = func.count(rule_decision_table.c.id)
        query = select(decision_count)
        query = apply_filters(query, filters)
        session = self._session_factory()

        # .. read the single row a count always answers with ..
        try:
            result = session.execute(query)
            out = result.scalar_one()

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def outcome_counts(self, filters:'DecisionFilter') -> 'count_point_list':
        """ Counts decisions by outcome using only promoted columns.
        """
        # Build a portable grouped count over the promoted outcome ..
        decision_count = func.count(rule_decision_table.c.id)
        query = select(rule_decision_table.c.outcome, decision_count)
        query = apply_filters(query, filters)
        query = query.group_by(rule_decision_table.c.outcome)
        query = query.order_by(rule_decision_table.c.outcome)
        session = self._session_factory()
        out:'count_point_list' = []

        # .. turn each SQL group into one typed result ..
        try:
            for row in session.execute(query):
                key = row[0]
                item_count = row[1]
                point = CountPoint(key, item_count)
                out.append(point)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def version_counts(self, filters:'DecisionFilter') -> 'count_point_list':
        """ Counts decisions by rules version using only promoted columns.
        """
        # Build a portable grouped count over the promoted rules version ..
        decision_count = func.count(rule_decision_table.c.id)
        query = select(rule_decision_table.c.rules_version, decision_count)
        query = apply_filters(query, filters)
        query = query.group_by(rule_decision_table.c.rules_version)
        query = query.order_by(rule_decision_table.c.rules_version)
        session = self._session_factory()
        out:'count_point_list' = []

        # .. turn each SQL group into one typed result ..
        try:
            for row in session.execute(query):
                key = row[0]
                item_count = row[1]
                point = CountPoint(key, item_count)
                out.append(point)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def hourly_counts(self, filters:'DecisionFilter') -> 'count_point_list':
        """ Counts decisions by their write-time UTC hour bucket using portable GROUP BY SQL.
        """
        # Group on the write-time bucket rather than a database-specific date function ..
        decision_count = func.count(rule_decision_table.c.id)
        query = select(rule_decision_table.c.time_bucket, decision_count)
        query = apply_filters(query, filters)
        query = query.group_by(rule_decision_table.c.time_bucket)
        query = query.order_by(rule_decision_table.c.time_bucket)
        session = self._session_factory()
        out:'count_point_list' = []

        # .. turn each SQL group into one typed result ..
        try:
            for row in session.execute(query):
                key = row[0]
                item_count = row[1]
                point = CountPoint(key, item_count)
                out.append(point)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def aggregates(self, filters:'DecisionFilter') -> 'DecisionAggregates':
        """ Every chart aggregate of one selection in one scan, rolled up by key afterwards.

        Outcome, version and hourly counts all summarise the same rows, so they come from one
        grouped query rather than one scan each, and the average duration is the weighted mean
        of the same groups - the database sees the selection once per request.
        """
        # Group on all three reporting keys at once, carrying enough to average durations ..
        decision_count = func.count(rule_decision_table.c.id)
        duration_total = func.sum(rule_decision_table.c.duration_ms)
        duration_count = func.count(rule_decision_table.c.duration_ms)

        query = select(
            rule_decision_table.c.outcome,
            rule_decision_table.c.rules_version,
            rule_decision_table.c.time_bucket,
            decision_count,
            duration_total,
            duration_count,
        )
        query = apply_filters(query, filters)
        query = query.group_by(
            rule_decision_table.c.outcome,
            rule_decision_table.c.rules_version,
            rule_decision_table.c.time_bucket,
        )
        session = self._session_factory()

        # .. one row per key combination, which each reporting key then sums over ..
        outcome_totals:'count_total_dict' = {}
        version_totals:'count_total_dict' = {}
        hourly_totals:'count_total_dict' = {}

        # .. a decision with no recorded duration is left out of the average, the way SQL AVG does ..
        duration_sum = 0.0
        durations_seen = 0

        try:
            for row in session.execute(query):
                outcome = row[0]
                rules_version = row[1]
                time_bucket = row[2]
                item_count = row[3]
                group_duration_total = row[4]
                group_duration_count = row[5]

                add_count(outcome_totals, outcome, item_count)
                add_count(version_totals, rules_version, item_count)
                add_count(hourly_totals, time_bucket, item_count)

                # .. a group whose every decision lacks a duration sums to NULL, not to zero.
                if group_duration_total is not None:
                    duration_sum += float(group_duration_total)
                    durations_seen += group_duration_count

        # .. and release the read-only session.
        finally:
            session.close()

        has_durations = durations_seen > 0

        if has_durations:
            average_duration_ms = duration_sum / durations_seen
        else:
            average_duration_ms = 0.0

        out = DecisionAggregates(
            outcomes=count_points(outcome_totals),
            versions=count_points(version_totals),
            hourly=count_points(hourly_totals),
            average_duration_ms=average_duration_ms,
        )
        return out

# ################################################################################################################################

    def bucket_counts_by_ruleset(self, *, start_time:'datetime', bucket:'str') -> 'bucket_split_dict':
        """ Per ruleset, how many decisions landed in one hour bucket and how many elsewhere in a window.

        The spike sweep needs both numbers for every ruleset, and asking per ruleset would run one
        query per ruleset - one grouped scan answers for all of them.
        """
        # Split each ruleset's window into the named bucket and everything else ..
        bucket_condition = rule_decision_table.c.time_bucket == bucket
        is_bucket = case((bucket_condition, In_Named_Bucket), else_=Outside_Named_Bucket)
        decision_count = func.count(rule_decision_table.c.id)

        query = select(rule_decision_table.c.ruleset_id, is_bucket, decision_count)
        cluster_condition = rule_decision_table.c.cluster_id == default_cluster_id
        window_condition = rule_decision_table.c.occurred_at >= normalize_utc(start_time)
        query = query.where(cluster_condition)
        query = query.where(window_condition)
        query = query.group_by(rule_decision_table.c.ruleset_id, is_bucket)
        session = self._session_factory()

        # Our response to produce
        out:'bucket_split_dict' = {}

        # .. each ruleset contributes at most one row per side of the split ..
        try:
            for row in session.execute(query):
                ruleset_id = row[0]
                is_named_bucket = row[1]
                item_count = row[2]

                if ruleset_id not in out:
                    out[ruleset_id] = BucketSplit()

                split = out[ruleset_id]

                if is_named_bucket == In_Named_Bucket:
                    split.bucket_count = item_count
                else:
                    split.other_count = item_count

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def average_duration_ms(self, filters:'DecisionFilter') -> 'float':
        """ Returns the average duration over the selected promoted decision headers.
        """
        # Average the promoted duration after applying the same drill-down filters ..
        average_duration = func.avg(rule_decision_table.c.duration_ms)
        query = select(average_duration)
        query = apply_filters(query, filters)
        session = self._session_factory()

        # .. map an empty selection to its natural reporting value ..
        try:
            result = session.execute(query)
            value = result.scalar_one()
            if value is None:
                out = 0.0
            else:
                out = float(value)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def daily_rule_counts(
        self,
        *,
        ruleset_id:'int',
        start_time:'datetime | None' = None,
        end_time:'datetime | None' = None,
        rules_version:'int | None' = None,
        ) -> 'rule_fire_point_list':
        """ Sums append-only in-memory counter flushes into per-rule daily totals.
        """
        # Sum the append-only counter increments by stable rule id, day and rules version ..
        firing_count = func.sum(rule_event_table.c.event_count)
        query = select(
            rule_event_table.c.subject_id,
            rule_event_table.c.bucket_start,
            rule_event_table.c.version,
            firing_count,
        )
        cluster_condition = rule_event_table.c.cluster_id == default_cluster_id
        ruleset_condition = rule_event_table.c.definition_id == ruleset_id
        event_type_condition = rule_event_table.c.event_type == Event_Type_Rule_Fired_Daily
        query = query.where(cluster_condition)
        query = query.where(ruleset_condition)
        query = query.where(event_type_condition)

        # .. narrow the counters to the requested portable timestamp and version range ..
        if start_time is not None:
            start_time = normalize_utc(start_time)
            start_condition = rule_event_table.c.bucket_start >= start_time
            query = query.where(start_condition)

        if end_time is not None:
            end_time = normalize_utc(end_time)
            end_condition = rule_event_table.c.bucket_start < end_time
            query = query.where(end_condition)

        if rules_version is not None:
            version_condition = rule_event_table.c.version == rules_version
            query = query.where(version_condition)

        query = query.group_by(
            rule_event_table.c.subject_id,
            rule_event_table.c.bucket_start,
            rule_event_table.c.version,
        )
        query = query.order_by(
            rule_event_table.c.bucket_start,
            rule_event_table.c.subject_id,
            rule_event_table.c.version,
        )
        session = self._session_factory()
        out:'rule_fire_point_list' = []

        # .. turn each SQL group into one typed result ..
        try:
            for row in session.execute(query):
                rule_id = row[0]
                day_bucket = row[1]
                point_version = row[2]
                point_firing_count = row[3]
                point = RuleFirePoint(rule_id, day_bucket, point_version, point_firing_count)
                out.append(point)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def rules_that_never_fired(
        self,
        *,
        ruleset_id:'int',
        known_rule_ids:'strlist',
        start_time:'datetime | None' = None,
        end_time:'datetime | None' = None,
        rules_version:'int | None' = None,
        ) -> 'strlist':
        """ Returns known stable rule identifiers absent from the selected firing counters.
        """
        # Read the firing totals for the requested range ..
        points = self.daily_rule_counts(
            ruleset_id=ruleset_id,
            start_time=start_time,
            end_time=end_time,
            rules_version=rules_version,
        )
        fired_rule_ids:'strset' = set()

        # .. collect every rule that appeared in at least one daily bucket ..
        for point in points:
            fired_rule_ids.add(point.rule_id)

        out:'strlist' = []

        # .. and return the known identifiers absent from that set.
        for rule_id in known_rule_ids:
            if rule_id not in fired_rule_ids:
                out.append(rule_id)

        return out

# ################################################################################################################################

    def decisions_firing_rule(
        self,
        *,
        rule_id:'str',
        filters:'DecisionFilter',
        limit:'int' = 10_000,
        ) -> 'ForensicResult':
        """ Narrows by promoted version and time columns, then filters retained stories in application code.
        """
        # Narrow the candidate set in SQL using only promoted columns ..
        headers = self.list_decisions(filters, limit=limit)
        decisions:'decision_record_list' = []
        headers_without_payload = 0

        # .. inspect the compact promoted list when the escape hatch is enabled ..
        for header in headers:
            if header.fired_rule_ids is not None:
                fired_rule_ids = deserialize_string_list(header.fired_rule_ids)

            # .. otherwise inspect the retained full story ..
            elif header.has_payload:
                payload = cast_(str, header.payload)
                story = deserialize_document(payload)
                story_rule_ids = story['fired_rule_ids']
                fired_rule_ids = cast_(strlist, story_rule_ids)

            # .. and count sampled-out candidates whose fired rules cannot be recovered.
            else:
                headers_without_payload += 1
                continue

            if rule_id in fired_rule_ids:
                decisions.append(header)

        # .. and report both matches and the number of sampled-out stories, so the result is never overstated.
        scanned_count = len(headers)
        out = ForensicResult(
            decisions=decisions,
            scanned_count=scanned_count,
            headers_without_payload=headers_without_payload,
        )
        return out

# ################################################################################################################################
# ################################################################################################################################
