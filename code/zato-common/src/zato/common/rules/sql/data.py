# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Any, NamedTuple

# typing-extensions
from typing_extensions import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime

    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

any_:TypeAlias = Any
anydict:TypeAlias = dict[str, any_]
dictlist:TypeAlias = list[anydict]
strlist:TypeAlias = list[str]
strset:TypeAlias = set[str]
intset:TypeAlias = set[int]
rowdict:TypeAlias = dict[str, any_]
rowlist:TypeAlias = list[rowdict]
decision_write_list:TypeAlias = list['DecisionWrite']
definition_record_list:TypeAlias = list['RuleDefinitionRecord']
event_record_list:TypeAlias = list['RuleEventRecord']
decision_record_list:TypeAlias = list['RuleDecisionRecord']
count_point_list:TypeAlias = list['CountPoint']
rule_fire_point_list:TypeAlias = list['RuleFirePoint']
reference_record_list:TypeAlias = list['RuleReferenceRecord']
follow_record_list:TypeAlias = list['RuleFollowRecord']
view_record_list:TypeAlias = list['RuleViewRecord']
recent_record_list:TypeAlias = list['RuleRecentRecord']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DecisionWrite:
    """ One complete decision handed to the persistence layer.
    """

    decision_id:    'str'
    ruleset_id:     'int'
    rules_version:  'int'
    occurred_at:    'datetime'
    business_key:   'str | None'
    outcome:        'str'
    is_error:       'bool'
    duration_ms:    'int'
    story:          'anydict'
    fired_rule_ids: 'strlist'

    def __init__(
        self,
        *,
        decision_id:'str',
        ruleset_id:'int',
        rules_version:'int',
        occurred_at:'datetime',
        business_key:'str | None',
        outcome:'str',
        is_error:'bool',
        duration_ms:'int',
        story:'anydict',
        fired_rule_ids:'strlist',
        ) -> 'None':

        self.decision_id    = decision_id
        self.ruleset_id     = ruleset_id
        self.rules_version  = rules_version
        self.occurred_at    = occurred_at
        self.business_key   = business_key
        self.outcome        = outcome
        self.is_error       = is_error
        self.duration_ms    = duration_ms
        self.story          = story
        self.fired_rule_ids = fired_rule_ids

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DecisionFilter:
    """ Promoted-column filters used by decision queries and drill-downs.
    """

    ruleset_id:    'int | None'
    start_time:    'datetime | None'
    end_time:      'datetime | None'
    business_key:  'str | None'
    outcome:       'str | None'
    rules_version: 'int | None'
    is_error:      'bool | None'
    before_id:     'int | None'

    def __init__(
        self,
        *,
        ruleset_id:'int | None' = None,
        start_time:'datetime | None' = None,
        end_time:'datetime | None' = None,
        business_key:'str | None' = None,
        outcome:'str | None' = None,
        rules_version:'int | None' = None,
        is_error:'bool | None' = None,
        before_id:'int | None' = None,
        ) -> 'None':

        self.ruleset_id    = ruleset_id
        self.start_time    = start_time
        self.end_time      = end_time
        self.business_key  = business_key
        self.outcome       = outcome
        self.rules_version = rules_version
        self.is_error      = is_error
        self.before_id     = before_id

# ################################################################################################################################
# ################################################################################################################################

class RuleDefinitionRecord(NamedTuple):
    """ One current rule-engine object.
    """

    id:              'int'
    cluster_id:      'int'
    parent_id:       'int | None'
    parent_key:      'int'
    name:            'str'
    object_type:     'str'
    current_version: 'int'
    live_version:    'int | None'
    is_active:       'bool'
    created_at:      'datetime'
    updated_at:      'datetime'
    document:        'str'

# ################################################################################################################################

class RuleVersionRecord(NamedTuple):
    """ One immutable full-document snapshot, the live pointer lives on the definition row.
    """

    id:            'int'
    definition_id: 'int'
    version:       'int'
    author:        'str'
    comment:       'str'
    created_at:    'datetime'
    document:      'str'

# ################################################################################################################################

class RuleEventRecord(NamedTuple):
    """ One append-only activity event or firing-counter increment.
    """

    id:            'int'
    cluster_id:    'int'
    definition_id: 'int'
    version:       'int | None'
    event_type:    'str'
    actor:         'str'
    subject_id:    'str | None'
    bucket_start:  'datetime | None'
    event_count:   'int | None'
    created_at:    'datetime'
    payload:       'str | None'

# ################################################################################################################################

class RuleDecisionRecord(NamedTuple):
    """ One promoted decision header with its optional retained story.
    """

    id:             'int'
    cluster_id:     'int'
    decision_id:    'str'
    ruleset_id:     'int'
    rules_version:  'int'
    occurred_at:    'datetime'
    time_bucket:    'str'
    business_key:   'str | None'
    outcome:        'str'
    is_error:       'bool'
    duration_ms:    'int'
    has_payload:    'bool'
    payload:        'str | None'
    fired_rule_ids: 'str | None'

# ################################################################################################################################

class RuleReferenceRecord(NamedTuple):
    """ One place where one stored rule references one vocabulary term.
    """

    id:            'int'
    cluster_id:    'int'
    definition_id: 'int'
    rule_name:     'str'
    term:          'str'
    block:         'str'
    role:          'str'

# ################################################################################################################################

class RuleFollowRecord(NamedTuple):
    """ One actor following one definition, with when they last looked at it.
    """

    id:            'int'
    cluster_id:    'int'
    definition_id: 'int'
    actor:         'str'
    created_at:    'datetime'
    last_seen_at:  'datetime'

# ################################################################################################################################

class RuleViewRecord(NamedTuple):
    """ One saved view - a named filter payload owned by one actor.
    """

    id:         'int'
    cluster_id: 'int'
    actor:      'str'
    name:       'str'
    payload:    'str'
    created_at: 'datetime'
    updated_at: 'datetime'

# ################################################################################################################################

class RuleRecentRecord(NamedTuple):
    """ One actor's most recent visit to one definition.
    """

    id:            'int'
    cluster_id:    'int'
    definition_id: 'int'
    actor:         'str'
    visited_at:    'datetime'

# ################################################################################################################################
# ################################################################################################################################

class CountPoint(NamedTuple):
    """ One grouped reporting result.
    """

    key:        'str | int'
    item_count: 'int'

# ################################################################################################################################

class RuleFirePoint(NamedTuple):
    """ One rule's firing count in one daily bucket.
    """

    rule_id:      'str'
    day_bucket:   'datetime'
    rules_version:'int | None'
    firing_count: 'int'

# ################################################################################################################################
# ################################################################################################################################
