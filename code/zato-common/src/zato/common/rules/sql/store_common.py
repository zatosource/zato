# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import insert, select

# Zato
from zato.common.defaults import default_cluster_id

# Local
from .constants import Root_Parent_Key
from .data import anydict, RuleDefinitionRecord, RuleEventRecord, RuleVersionRecord
from .document import serialize_document
from .errors import InvalidStoreInputError, RecordNotFoundError
from .records import definition_record, version_record
from .schema import rule_definition_table, rule_event_table, rule_version_table
from .time_ import utc_now

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

def payload_text(payload:'anydict | None') -> 'str | None':
    """ Serializes an optional event payload.
    """
    # Preserve the distinction between no payload and an empty JSON document ..
    if payload is None:
        out = None

    # .. while every supplied payload receives the same canonical encoding as rule documents.
    else:
        out = serialize_document(payload)

    return out

# ################################################################################################################################

def get_definition(session:'Session', definition_id:'int') -> 'RuleDefinitionRecord':
    """ Returns one definition in the caller's transaction.
    """
    # Query inside the one Zato cluster ..
    query = select(rule_definition_table)
    cluster_condition = rule_definition_table.c.cluster_id == default_cluster_id
    id_condition = rule_definition_table.c.id == definition_id
    query = query.where(cluster_condition)
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

def add_event(
    session:'Session',
    *,
    definition_id:'int',
    version:'int | None',
    event_type:'str',
    actor:'str',
    payload:'anydict | None',
    ) -> 'RuleEventRecord':
    """ Appends one event inside the caller's transaction.
    """
    # Build every promoted event field ..
    created_at = utc_now()
    event_payload = payload_text(payload)
    values = {
        'cluster_id':    default_cluster_id,
        'definition_id': definition_id,
        'version':       version,
        'event_type':    event_type,
        'actor':         actor,
        'subject_id':    None,
        'bucket_start':  None,
        'event_count':   None,
        'created_at':    created_at,
        'payload':       event_payload,
    }

    # .. append the event in the caller's transaction ..
    statement = insert(rule_event_table)
    result = session.execute(statement, values)
    primary_key = result.inserted_primary_key
    event_id = primary_key[0]

    # .. and build the detached record from the values just written, avoiding a redundant re-read.
    out = RuleEventRecord(
        id=event_id,
        cluster_id=default_cluster_id,
        definition_id=definition_id,
        version=version,
        event_type=event_type,
        actor=actor,
        subject_id=None,
        bucket_start=None,
        event_count=None,
        created_at=created_at,
        payload=event_payload,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
