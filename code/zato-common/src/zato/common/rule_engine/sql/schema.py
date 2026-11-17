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
_string_64_type   = String(64)
_string_191_type  = String(191)
_string_1000_type = String(1000)
_text_type        = Text()

# ################################################################################################################################
# ################################################################################################################################

_definition_id              = Column('id', _integer_type, primary_key=True, autoincrement=True)
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

_ = Index('rd_parent', rule_definition_table.c.parent_id)
_ = Index(
    'rd_type',
    rule_definition_table.c.object_type,
    rule_definition_table.c.is_active,
)

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

# ################################################################################################################################
# ################################################################################################################################
