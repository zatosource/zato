# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, MetaData, \
    String, Table, Text, UniqueConstraint

# ################################################################################################################################
# ################################################################################################################################

metadata = MetaData()

_boolean_type     = Boolean()
_datetime_type    = DateTime()
_integer_type     = Integer()
_string_14_type   = String(14)
_string_64_type   = String(64)
_string_191_type  = String(191)
_string_1000_type = String(1000)
_text_type        = Text()

# ################################################################################################################################
# ################################################################################################################################

_definition_id              = Column('id', _integer_type, primary_key=True, autoincrement=True)
_definition_cluster_id      = Column('cluster_id', _integer_type, nullable=False)
_definition_parent_foreign  = ForeignKey('rule_definition.id', ondelete='RESTRICT')
_definition_parent_id       = Column('parent_id', _integer_type, _definition_parent_foreign, nullable=True)
_definition_parent_key      = Column('parent_key', _integer_type, nullable=False)
_definition_name            = Column('name', _string_191_type, nullable=False)
_definition_object_type     = Column('object_type', _string_64_type, nullable=False)
_definition_current_version = Column('current_version', _integer_type, nullable=False)
_definition_live_version    = Column('live_version', _integer_type, nullable=True)
_definition_is_active       = Column('is_active', _boolean_type, nullable=False)
_definition_created_at      = Column('created_at', _datetime_type, nullable=False)
_definition_updated_at      = Column('updated_at', _datetime_type, nullable=False)
_definition_document        = Column('document', _text_type, nullable=False)
_definition_unique_name     = UniqueConstraint(
    'cluster_id',
    'parent_key',
    'object_type',
    'name',
    name='rd_uq_name',
)
_definition_current_check = CheckConstraint('current_version >= 1', name='rd_ck_current_version')
_definition_parent_check  = CheckConstraint('parent_key >= 0', name='rd_ck_parent_key')

rule_definition_table = Table(
    'rule_definition',
    metadata,
    _definition_id,
    _definition_cluster_id,
    _definition_parent_id,
    _definition_parent_key,
    _definition_name,
    _definition_object_type,
    _definition_current_version,
    _definition_live_version,
    _definition_is_active,
    _definition_created_at,
    _definition_updated_at,
    _definition_document,
    _definition_unique_name,
    _definition_current_check,
    _definition_parent_check,
)

_ = Index('rd_parent', rule_definition_table.c.cluster_id, rule_definition_table.c.parent_id)
_ = Index(
    'rd_type',
    rule_definition_table.c.cluster_id,
    rule_definition_table.c.object_type,
    rule_definition_table.c.is_active,
)
_ = Index('rd_updated', rule_definition_table.c.cluster_id, rule_definition_table.c.updated_at)

# ################################################################################################################################

_version_id                 = Column('id', _integer_type, primary_key=True, autoincrement=True)
_version_definition_foreign = ForeignKey('rule_definition.id', ondelete='RESTRICT')
_version_definition_id      = Column('definition_id', _integer_type, _version_definition_foreign, nullable=False)
_version_number             = Column('version', _integer_type, nullable=False)
_version_author             = Column('author', _string_191_type, nullable=False)
_version_comment            = Column('comment', _string_1000_type, nullable=False)
_version_created_at         = Column('created_at', _datetime_type, nullable=False)
_version_document           = Column('document', _text_type, nullable=False)
_version_unique_number      = UniqueConstraint('definition_id', 'version', name='rv_uq_version')
_version_number_check       = CheckConstraint('version >= 1', name='rv_ck_version')
_version_comment_check      = CheckConstraint('length(trim(comment)) > 0', name='rv_ck_comment')

rule_version_table = Table(
    'rule_version',
    metadata,
    _version_id,
    _version_definition_id,
    _version_number,
    _version_author,
    _version_comment,
    _version_created_at,
    _version_document,
    _version_unique_number,
    _version_number_check,
    _version_comment_check,
)

_ = Index('rv_created', rule_version_table.c.definition_id, rule_version_table.c.created_at)

# ################################################################################################################################

_event_id                 = Column('id', _integer_type, primary_key=True, autoincrement=True)
_event_cluster_id         = Column('cluster_id', _integer_type, nullable=False)
_event_definition_foreign = ForeignKey('rule_definition.id', ondelete='RESTRICT')
_event_definition_id      = Column('definition_id', _integer_type, _event_definition_foreign, nullable=False)
_event_version            = Column('version', _integer_type, nullable=True)
_event_type               = Column('event_type', _string_64_type, nullable=False)
_event_actor              = Column('actor', _string_191_type, nullable=False)
_event_subject_id         = Column('subject_id', _string_191_type, nullable=True)
_event_bucket_start       = Column('bucket_start', _datetime_type, nullable=True)
_event_count              = Column('event_count', _integer_type, nullable=True)
_event_created_at         = Column('created_at', _datetime_type, nullable=False)
_event_payload            = Column('payload', _text_type, nullable=True)
_event_count_check        = CheckConstraint('event_count IS NULL OR event_count > 0', name='re_ck_count')

rule_event_table = Table(
    'rule_event',
    metadata,
    _event_id,
    _event_cluster_id,
    _event_definition_id,
    _event_version,
    _event_type,
    _event_actor,
    _event_subject_id,
    _event_bucket_start,
    _event_count,
    _event_created_at,
    _event_payload,
    _event_count_check,
)

_ = Index('re_feed', rule_event_table.c.cluster_id, rule_event_table.c.created_at, rule_event_table.c.id)
_ = Index('re_parent', rule_event_table.c.definition_id, rule_event_table.c.created_at, rule_event_table.c.id)
_ = Index(
    're_rollup',
    rule_event_table.c.definition_id,
    rule_event_table.c.event_type,
    rule_event_table.c.bucket_start,
    rule_event_table.c.subject_id,
)

# ################################################################################################################################

_decision_id                 = Column('id', _integer_type, primary_key=True, autoincrement=True)
_decision_cluster_id         = Column('cluster_id', _integer_type, nullable=False)
_decision_external_id        = Column('decision_id', _string_191_type, nullable=False)
_decision_ruleset_foreign    = ForeignKey('rule_definition.id', ondelete='RESTRICT')
_decision_ruleset_id         = Column('ruleset_id', _integer_type, _decision_ruleset_foreign, nullable=False)
_decision_rules_version      = Column('rules_version', _integer_type, nullable=False)
_decision_occurred_at        = Column('occurred_at', _datetime_type, nullable=False)
_decision_time_bucket        = Column('time_bucket', _string_14_type, nullable=False)
_decision_business_key       = Column('business_key', _string_191_type, nullable=True)
_decision_outcome            = Column('outcome', _string_191_type, nullable=False)
_decision_is_error           = Column('is_error', _boolean_type, nullable=False)
_decision_duration_ms        = Column('duration_ms', _integer_type, nullable=False)
_decision_has_payload        = Column('has_payload', _boolean_type, nullable=False)
_decision_payload            = Column('payload', _text_type, nullable=True)
_decision_fired_rule_ids     = Column('fired_rule_ids', _text_type, nullable=True)
_decision_unique_external_id = UniqueConstraint('cluster_id', 'decision_id', name='rdec_uq_decision')
_decision_version_check      = CheckConstraint('rules_version >= 1', name='rdec_ck_version')
_decision_duration_check     = CheckConstraint('duration_ms >= 0', name='rdec_ck_duration')

rule_decision_table = Table(
    'rule_decision',
    metadata,
    _decision_id,
    _decision_cluster_id,
    _decision_external_id,
    _decision_ruleset_id,
    _decision_rules_version,
    _decision_occurred_at,
    _decision_time_bucket,
    _decision_business_key,
    _decision_outcome,
    _decision_is_error,
    _decision_duration_ms,
    _decision_has_payload,
    _decision_payload,
    _decision_fired_rule_ids,
    _decision_unique_external_id,
    _decision_version_check,
    _decision_duration_check,
)

_ = Index('rdec_time', rule_decision_table.c.cluster_id, rule_decision_table.c.occurred_at, rule_decision_table.c.id)
_ = Index(
    'rdec_business',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.business_key,
    rule_decision_table.c.occurred_at,
)
_ = Index(
    'rdec_outcome',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.ruleset_id,
    rule_decision_table.c.outcome,
    rule_decision_table.c.occurred_at,
)
_ = Index(
    'rdec_version',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.ruleset_id,
    rule_decision_table.c.rules_version,
    rule_decision_table.c.occurred_at,
)
_ = Index(
    'rdec_error',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.is_error,
    rule_decision_table.c.occurred_at,
)
_ = Index(
    'rdec_ruleset_time',
    rule_decision_table.c.ruleset_id,
    rule_decision_table.c.occurred_at,
    rule_decision_table.c.id,
)
_ = Index(
    'rdec_bucket',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.ruleset_id,
    rule_decision_table.c.time_bucket,
    rule_decision_table.c.outcome,
)
_ = Index(
    'rdec_duration',
    rule_decision_table.c.cluster_id,
    rule_decision_table.c.ruleset_id,
    rule_decision_table.c.duration_ms,
)

# ################################################################################################################################
# ################################################################################################################################
