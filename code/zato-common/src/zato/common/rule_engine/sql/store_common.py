# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Local
from .constants import Root_Parent_Key
from .data import RuleDefinitionRecord, RuleVersionRecord
from .errors import InvalidStoreInputError, RecordNotFoundError
from .records import definition_record, version_record
from .schema import rule_definition_table, rule_version_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

def require_text(value:'str', label:'str') -> 'None':
    """ Rejects a missing required text value.
    """
    stripped_value = value.strip()
    if not stripped_value:
        message = f'{label} is required'
        raise InvalidStoreInputError(message)

# ################################################################################################################################

def parent_key(parent_id:'int | None') -> 'int':
    """ Returns the non-null parent key used by the portable uniqueness constraint.
    """
    # Represent a top-level object with the reserved root key ..
    if parent_id is None:
        out = Root_Parent_Key

    # .. while a child uses its real parent id.
    else:
        out = parent_id

    return out

# ################################################################################################################################

def get_definition(session:'Session', definition_id:'int') -> 'RuleDefinitionRecord':
    """ Returns one definition in the caller's transaction.
    """
    # Query the definition by its id ..
    query = select(rule_definition_table)
    id_condition = rule_definition_table.c.id == definition_id
    query = query.where(id_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. return the definition when found ..
    if row:
        out = definition_record(row)

    # .. or name the missing id directly.
    else:
        message = f'No such rule definition -> {definition_id}'
        raise RecordNotFoundError(message)

    return out

# ################################################################################################################################

def get_version(session:'Session', definition_id:'int', version:'int') -> 'RuleVersionRecord':
    """ Returns one immutable version in the caller's transaction.
    """
    # Query the composite definition and version identity ..
    query = select(rule_version_table)
    definition_condition = rule_version_table.c.definition_id == definition_id
    version_condition = rule_version_table.c.version == version
    query = query.where(definition_condition)
    query = query.where(version_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. return the snapshot when found ..
    if row:
        out = version_record(row)

    # .. or name both missing coordinates directly.
    else:
        message = f'No version {version} of rule definition {definition_id}'
        raise RecordNotFoundError(message)

    return out

# ################################################################################################################################
# ################################################################################################################################
