# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.rule_engine.sql import InvalidStoreInputError, RecordNotFoundError
from zato.common.rule_engine.sql.constants import Event_Type_Version_Created, Event_Type_Version_Published

# Test helpers
from jobs_test_data import Author, create_ruleset

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_actor = 'sarah.p'
_target = 'pricing-rules'

# ################################################################################################################################
# ################################################################################################################################

def test_add_and_list_destinations(backend:'any_') -> 'None':
    """ A new destination lists back with its identity and a clean delivery status.
    """
    ruleset = create_ruleset(backend)

    record = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='slack',
        target=_target,
        actor=_actor,
    )
    assert record.kind == 'slack'
    assert record.target == _target
    assert record.is_active is True
    assert record.last_status is None
    assert record.last_error is None
    assert record.last_delivery_at is None
    assert record.created_by == _actor

    listed = backend.notifications.list_destinations(definition_id=ruleset.id)
    assert len(listed) == 1
    assert listed[0].id == record.id

# ################################################################################################################################

def test_new_destination_cursor_starts_at_the_end_of_the_feed(backend:'any_') -> 'None':
    """ A destination only hears about changes made after it was added.
    """
    # Creating the ruleset appends creation and version events ..
    ruleset = create_ruleset(backend)
    events = backend.events.list(definition_id=ruleset.id)
    newest_event_id = events[0].id

    # .. so the new destination's cursor is already past all of them.
    record = backend.notifications.add_destination(
        definition_id=ruleset.id,
        kind='slack',
        target=_target,
        actor=_actor,
    )
    assert record.cursor_id >= newest_event_id

# ################################################################################################################################

def test_duplicate_destination_is_rejected(backend:'any_') -> 'None':
    """ The same channel cannot be added to the same ruleset twice.
    """
    ruleset = create_ruleset(backend)

    _ = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_target, actor=_actor)

    with pytest.raises(InvalidStoreInputError):
        _ = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_target, actor=_actor)

# ################################################################################################################################

def test_delete_destination(backend:'any_') -> 'None':
    """ A deleted destination is gone, deleting it again is an error worth reporting.
    """
    ruleset = create_ruleset(backend)
    record = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_target, actor=_actor)

    backend.notifications.delete_destination(record.id)

    listed = backend.notifications.list_destinations(definition_id=ruleset.id)
    assert listed == []

    with pytest.raises(RecordNotFoundError):
        backend.notifications.delete_destination(record.id)

# ################################################################################################################################

def test_delivery_status_transitions(backend:'any_') -> 'None':
    """ Delivered moves the cursor and clears errors, failed keeps the cursor and records the error.
    """
    ruleset = create_ruleset(backend)
    record = backend.notifications.add_destination(definition_id=ruleset.id, kind='slack', target=_target, actor=_actor)

    # A failure keeps the cursor where it was and surfaces the error ..
    backend.notifications.mark_failed(record.id, 'channel_not_found')
    failed = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert failed.last_status == 'error'
    assert failed.last_error == 'channel_not_found'
    assert failed.cursor_id == record.cursor_id
    assert failed.last_delivery_at is None

    # .. while a delivery moves the cursor and wipes the error away.
    delivered_event_id = record.cursor_id + 10
    backend.notifications.mark_delivered(record.id, delivered_event_id)
    delivered = backend.notifications.list_destinations(definition_id=ruleset.id)[0]
    assert delivered.last_status == 'delivered'
    assert delivered.last_error is None
    assert delivered.cursor_id == delivered_event_id
    assert delivered.last_delivery_at is not None

# ################################################################################################################################

def test_list_since_reads_forward_with_type_filter(backend:'any_') -> 'None':
    """ Forward reads return only newer events of the wanted types, oldest first.
    """
    ruleset = create_ruleset(backend)

    # A publication event lands past the creation events ..
    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    # .. reading everything from the start sees both event kinds in feed order ..
    all_events = backend.events.list_since(since_id=0, definition_id=ruleset.id)
    event_ids = []
    for event in all_events:
        event_ids.append(event.id)

    assert event_ids == sorted(event_ids)

    # .. while the type filter narrows the read to publications only ..
    published = backend.events.list_since(
        since_id=0,
        definition_id=ruleset.id,
        event_types=[Event_Type_Version_Published],
    )
    assert len(published) == 1

    # .. and a cursor past the publication sees nothing new.
    nothing = backend.events.list_since(
        since_id=published[0].id,
        definition_id=ruleset.id,
        event_types=[Event_Type_Version_Published, Event_Type_Version_Created],
    )
    assert nothing == []

# ################################################################################################################################

def test_job_cursor_roundtrip(backend:'any_') -> 'None':
    """ A named job cursor starts at zero, moves and stays where it was put.
    """
    assert backend.notifications.get_job_cursor('advisory-runs') == 0

    backend.notifications.set_job_cursor('advisory-runs', 17)
    assert backend.notifications.get_job_cursor('advisory-runs') == 17

    backend.notifications.set_job_cursor('advisory-runs', 42)
    assert backend.notifications.get_job_cursor('advisory-runs') == 42

# ################################################################################################################################
# ################################################################################################################################
