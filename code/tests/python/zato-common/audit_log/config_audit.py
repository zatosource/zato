# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, \
    AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.config_audit import build_change_summary, is_secret_field, mask_secrets, \
    record_config_change, record_view_event, ConfigScope, Secret_Mask

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-config-audit-server'

# The people making and viewing changes in this scenario
_actor           = 'alice'
_effective_actor = 'zato.admin'
_viewer          = 'bob'

# The object the config changes are about
_object_type = 'channel-rest'
_object_name = 'config.test.channel'

# ################################################################################################################################
# ################################################################################################################################

def _get_event_row(event_id:'int') -> 'anydict':
    """ Returns one event row as a dict.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.id == event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    out = dict(row._mapping)
    return out

# ################################################################################################################################

def _get_attr_map(event_id:'int') -> 'anydict':
    """ Returns the attributes of one event as a dict of name to (value, value_number).
    """
    engine = get_audit_engine()

    query = select(event_attr_table)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            mapping = row._mapping
            out[mapping['name']] = (mapping['value'], mapping['value_number'])

    return out

# ################################################################################################################################

def _search_by_attr(name:'str', value:'str') -> 'anylist':
    """ Returns the ids of the events carrying one attribute value.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.event_id)
    query = query.where(event_attr_table.c.name == name)
    query = query.where(event_attr_table.c.value == value)
    query = query.order_by(event_attr_table.c.event_id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_masking_checks() -> 'None':
    """ Confirms secret fields are recognized and masked in change summaries.
    """

    # The match is case-insensitive
    assert is_secret_field('password')
    assert is_secret_field('Password')
    assert is_secret_field('api_key')
    assert not is_secret_field('address')

    masked = mask_secrets({'address': 'example.com', 'password': 'abc'})
    assert masked == {'address': 'example.com', 'password': Secret_Mask}, masked

# ################################################################################################################################

def _run_summary_checks() -> 'None':
    """ Confirms the before/after summary carries only the fields that differ,
    with additions, removals and secrets each handled correctly.
    """

    before = {
        'address': 'example.com',
        'timeout': 30,
        'password': 'old-secret',
        'removed_field': 'going-away',
    }

    after = {
        'address': 'example.com',
        'timeout': 60,
        'password': 'new-secret',
        'added_field': 'brand-new',
    }

    summary = build_change_summary(before, after)

    # The unchanged address stays out, the changed and removed fields are in before ..
    assert summary['before'] == {
        'timeout': 30,
        'password': Secret_Mask,
        'removed_field': 'going-away',
    }, summary

    # .. and the changed and added fields are in after, secrets masked on both sides.
    assert summary['after'] == {
        'timeout': 60,
        'password': Secret_Mask,
        'added_field': 'brand-new',
    }, summary

# ################################################################################################################################

def _run_config_change_checks(audit_log:'AuditLog') -> 'None':
    """ Writes the full create-edit-delete sequence and confirms what is stored -
    the summary, the scope and both identities, all of them searchable.
    """

    # A creation has an empty before ..
    create_id = record_config_change(
        audit_log,
        action=AuditEvent.Config_Created,
        object_type=_object_type,
        object_name=_object_name,
        actor=_actor,
        cid='cid-config-create',
        after={'address': 'example.com', 'password': 'abc'},
    )

    row = _get_event_row(create_id)
    assert row['source'] == AuditSource.Config
    assert row['event_type'] == AuditEvent.Config_Created
    assert row['object_name'] == _object_name
    assert row['outcome'] == AuditOutcome.OK

    summary = loads(row['data'])
    assert summary['before'] == {}, summary
    assert summary['after'] == {'address': 'example.com', 'password': Secret_Mask}, summary
    assert summary['object_type'] == _object_type

    # .. with no escalation the effective actor is the original one ..
    attr_map = _get_attr_map(create_id)
    assert attr_map['actor'][0] == _actor
    assert attr_map['effective_actor'][0] == _actor
    assert attr_map['scope'][0] == ConfigScope.Persistent
    assert attr_map['object_type'][0] == _object_type

    # .. an edit run under escalation records both identities ..
    edit_id = record_config_change(
        audit_log,
        action=AuditEvent.Config_Edited,
        object_type=_object_type,
        object_name=_object_name,
        actor=_actor,
        cid='cid-config-edit',
        effective_actor=_effective_actor,
        before={'address': 'example.com', 'password': 'abc'},
        after={'address': 'example.net', 'password': 'abc'},
    )

    attr_map = _get_attr_map(edit_id)
    assert attr_map['actor'][0] == _actor
    assert attr_map['effective_actor'][0] == _effective_actor

    # .. the summary carries only the changed field, the unchanged secret stays out ..
    summary = loads(_get_event_row(edit_id)['data'])
    assert summary['before'] == {'address': 'example.com'}, summary
    assert summary['after'] == {'address': 'example.net'}, summary

    # .. a runtime-only change is marked ephemeral ..
    suspend_id = record_config_change(
        audit_log,
        action=AuditEvent.Config_Edited,
        object_type=_object_type,
        object_name=_object_name,
        actor=_actor,
        cid='cid-config-suspend',
        scope=ConfigScope.Ephemeral,
        before={'is_active': True},
        after={'is_active': False},
    )

    attr_map = _get_attr_map(suspend_id)
    assert attr_map['scope'][0] == ConfigScope.Ephemeral

    # .. a deletion has an empty after ..
    delete_id = record_config_change(
        audit_log,
        action=AuditEvent.Config_Deleted,
        object_type=_object_type,
        object_name=_object_name,
        actor=_actor,
        cid='cid-config-delete',
        before={'address': 'example.net'},
    )

    summary = loads(_get_event_row(delete_id)['data'])
    assert summary['before'] == {'address': 'example.net'}, summary
    assert summary['after'] == {}, summary

    # .. and "everything this person changed" is one attribute query.
    changed_by_actor = _search_by_attr('actor', _actor)
    assert changed_by_actor == [create_id, edit_id, suspend_id, delete_id], changed_by_actor

# ################################################################################################################################

def _run_view_event_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms opening a message body writes a view event - who, which event,
    from which screen - searchable from both ends.
    """

    # The event whose body is about to be viewed
    viewed_id = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Received, 'config.test.mllp',
        cid='cid-view-target', outcome=AuditOutcome.OK)

    view_id = record_view_event(
        audit_log,
        actor=_viewer,
        viewed_event_id=viewed_id,
        screen='details-overlay',
        cid='cid-view-1',
    )

    row = _get_event_row(view_id)
    assert row['source'] == AuditSource.Config
    assert row['event_type'] == AuditEvent.Content_Viewed
    assert row['object_name'] == 'details-overlay'

    # The viewer and the viewed event are both searchable ..
    attr_map = _get_attr_map(view_id)
    assert attr_map['actor'][0] == _viewer
    assert attr_map['screen'][0] == 'details-overlay'

    # .. the viewed event id is numeric so it can join against the event table ..
    assert float(attr_map['viewed_event_id'][1]) == float(viewed_id)

    # .. and "who looked at this message" is one attribute query.
    viewers = _search_by_attr('actor', _viewer)
    assert viewers == [view_id], viewers

# ################################################################################################################################
# ################################################################################################################################

def run_config_audit_scenario() -> 'None':
    """ The config-audit scenario every backend must pass: secret masking,
    before/after summaries of only what changed, the create-edit-delete sequence
    with scope and dual identity, and view-access logging.
    """
    delete_all_events()

    audit_log = AuditLog(_server_name)

    _run_masking_checks()
    _run_summary_checks()
    _run_config_change_checks(audit_log)
    _run_view_event_checks(audit_log)

# ################################################################################################################################
# ################################################################################################################################
