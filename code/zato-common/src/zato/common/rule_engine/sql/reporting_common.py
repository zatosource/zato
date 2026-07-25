# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.defaults import default_cluster_id

# Local
from .data import any_, count_point_list, decision_record_list, CountPoint, DecisionFilter
from .decisions import normalize_utc
from .schema import rule_decision_table

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DecisionAggregates:
    """ Every aggregate the decision log's charts need, gathered in one pass over one selection.
    """

    outcomes:            'count_point_list'
    versions:            'count_point_list'
    hourly:              'count_point_list'
    average_duration_ms: 'float'

    def __init__(
        self,
        *,
        outcomes:'count_point_list',
        versions:'count_point_list',
        hourly:'count_point_list',
        average_duration_ms:'float',
        ) -> 'None':

        self.outcomes            = outcomes
        self.versions            = versions
        self.hourly              = hourly
        self.average_duration_ms = average_duration_ms

# ################################################################################################################################

@dataclass(init=False)
class BucketSplit:
    """ How many decisions one ruleset made in one hour bucket and how many in the rest of a window.
    """

    bucket_count: 'int'
    other_count:  'int'

    def __init__(self) -> 'None':

        # A ruleset that decided nothing on one side of the split has no row for that side,
        # so both numbers start at zero and only the sides the database reported are filled in.
        self.bucket_count = 0
        self.other_count  = 0

# ################################################################################################################################

@dataclass(init=False)
class ForensicResult:
    """ Decisions whose retained stories name one rule, plus the number of headers whose stories were not captured.
    """

    decisions:              'decision_record_list'
    scanned_count:          'int'
    headers_without_payload:'int'

    def __init__(
        self,
        *,
        decisions:'decision_record_list',
        scanned_count:'int',
        headers_without_payload:'int',
        ) -> 'None':

        self.decisions               = decisions
        self.scanned_count           = scanned_count
        self.headers_without_payload = headers_without_payload

# ################################################################################################################################
# ################################################################################################################################

bucket_split_dict:TypeAlias = dict[int, BucketSplit]

# One reporting key's running totals, keyed the way its CountPoint keys are.
count_total_dict:TypeAlias = dict['str | int', int]

# How a grouped scan labels which side of a bucket split one of its rows belongs to.
In_Named_Bucket      = 1
Outside_Named_Bucket = 0

# ################################################################################################################################
# ################################################################################################################################

def add_count(totals:'count_total_dict', key:'str | int', item_count:'int') -> 'None':
    """ Adds one grouped count to a reporting key's running total.
    """
    if key in totals:
        totals[key] += item_count
    else:
        totals[key] = item_count

# ################################################################################################################################

def count_points(totals:'count_total_dict') -> 'count_point_list':
    """ Turns one reporting key's running totals into typed points, in key order.
    """

    # Our response to produce
    out:'count_point_list' = []

    # Reporting keys come back sorted, the way a single grouped query with an ORDER BY would.
    for key in sorted(totals):
        point = CountPoint(key, totals[key])
        out.append(point)

    return out

# ################################################################################################################################
# ################################################################################################################################

def apply_filters(query:'any_', filters:'DecisionFilter') -> 'any_':
    """ Adds promoted-column filters to a decision query.
    """
    # Every query stays inside the one Zato cluster ..
    cluster_condition = rule_decision_table.c.cluster_id == default_cluster_id
    query = query.where(cluster_condition)

    # .. then each supplied promoted-column filter narrows the same SQL statement.
    if filters.ruleset_id is not None:
        ruleset_condition = rule_decision_table.c.ruleset_id == filters.ruleset_id
        query = query.where(ruleset_condition)

    if filters.start_time is not None:
        start_time = normalize_utc(filters.start_time)
        start_condition = rule_decision_table.c.occurred_at >= start_time
        query = query.where(start_condition)

    if filters.end_time is not None:
        end_time = normalize_utc(filters.end_time)
        end_condition = rule_decision_table.c.occurred_at < end_time
        query = query.where(end_condition)

    if filters.business_key is not None:
        business_condition = rule_decision_table.c.business_key == filters.business_key
        query = query.where(business_condition)

    if filters.outcome is not None:
        outcome_condition = rule_decision_table.c.outcome == filters.outcome
        query = query.where(outcome_condition)

    if filters.rules_version is not None:
        version_condition = rule_decision_table.c.rules_version == filters.rules_version
        query = query.where(version_condition)

    if filters.is_error is not None:
        error_condition = rule_decision_table.c.is_error == filters.is_error
        query = query.where(error_condition)

    if filters.before_id is not None:
        id_condition = rule_decision_table.c.id < filters.before_id
        query = query.where(id_condition)

    return query

# ################################################################################################################################
# ################################################################################################################################
