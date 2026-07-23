# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Local
from zato.common.rule_engine.sql import InvalidStoreInputError, RuleDefinitionRecord, RuleSQLBackend, VersionConflictError
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Sentence_Rule, \
    Event_Type_Review_Commented
from zato.common.rule_engine.sql.data import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'
_ruleset_name = 'Loan approval'
_initial_comment = 'Create the first complete ruleset'

# ################################################################################################################################
# ################################################################################################################################

def _ruleset_document(minimum_score:'int') -> 'anydict':
    """ Returns one realistic complete ruleset document.
    """
    # Keep the stable rule identifier and regression scenario inside one complete document.
    out = {
        'rules': [
            {
                'id': 'excellent-credit',
                'if': {'customer.creditScore': {'at_least': minimum_score}},
                'then': {'loan.approved': True},
            }
        ],
        'test_set': {'scenario_ids': ['excellent-credit-approved']},
    }
    return out

# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend', name:'str' = _ruleset_name) -> 'RuleDefinitionRecord':
    """ Creates the common ruleset used by repository tests.
    """
    # Build the first complete document ..
    document = _ruleset_document(740)

    # .. and preserve it through the definition repository.
    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment=_initial_comment,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_create_definition_snapshot_and_events(backend:'RuleSQLBackend') -> 'None':
    """ A definition, first snapshot and history events commit together.
    """
    # Create one current definition ..
    definition = _create_ruleset(backend)

    # .. verify its promoted identity and current-version paths ..
    assert definition.name == _ruleset_name
    assert definition.current_version == 1
    assert definition.live_version is None
    assert definition.is_active is True

    # .. verify the current TEXT document round-trips without loss ..
    document = backend.definitions.get_document(definition.id)
    expected_document = _ruleset_document(740)
    assert document == expected_document

    # .. verify the first immutable snapshot is complete ..
    version = backend.versions.get(definition.id, 1)
    assert version.document == definition.document
    assert version.comment == _initial_comment

    # .. and verify both creation events are present.
    events = backend.events.list(definition_id=definition.id)
    event_types = set()

    for event in events:
        event_types.add(event.event_type)

    assert event_types == {'definition.created', 'version.created'}

# ################################################################################################################################

def test_definition_identity_search_parent_and_archive(backend:'RuleSQLBackend') -> 'None':
    """ Identity constraints, document search, parent paths and archival use promoted columns.
    """
    # Create a top-level ruleset and a child sentence rule ..
    definition = _create_ruleset(backend)
    child_document = {'conditions': [{'term': 'customer.creditScore', 'operator': 'at-least', 'value': 740}]}
    child = backend.definitions.create(
        name='Excellent credit',
        object_type=Definition_Type_Sentence_Rule,
        document=child_document,
        author=_author,
        comment='Add the excellent-credit sentence rule',
        parent_id=definition.id,
    )

    # .. locate the child by content rather than its name ..
    matches = backend.definitions.list(parent_id=definition.id, search_text='creditScore')
    assert matches == [child]

    # .. reject a duplicate identity under the same parent and type ..
    with pytest.raises(InvalidStoreInputError):
        _ = backend.definitions.create(
            name='Excellent credit',
            object_type=Definition_Type_Sentence_Rule,
            document=child_document,
            author=_author,
            comment='Attempt a duplicate sentence rule',
            parent_id=definition.id,
        )

    # .. archive without deleting the definition or its history ..
    backend.definitions.archive(definition_id=definition.id, actor='mark.b')
    archived = backend.definitions.get(definition.id)
    assert archived.is_active is False

    # .. and exclude the archived definition from the normal top-level list.
    active_definitions = backend.definitions.list()
    assert active_definitions == []

# ################################################################################################################################

def test_optimistic_versions_publish_and_restore(backend:'RuleSQLBackend') -> 'None':
    """ Edits are optimistic, publication is singular and restore adds a new linear snapshot.
    """
    # Create and publish the first snapshot ..
    definition = _create_ruleset(backend)
    first_live = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)
    assert first_live.version == 1

    # .. verify the one live pointer, the promoted definition column, follows publication ..
    live = backend.versions.get_live(definition.id)
    assert live.version == 1

    # .. create a second full snapshot using the expected current version ..
    second_document = _ruleset_document(720)
    second = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=second_document,
        author='mark.b',
        comment='Lower the minimum score after portfolio review',
    )
    assert second.version == 2

    # .. verify an unpublished edit never moves the live pointer ..
    live = backend.versions.get_live(definition.id)
    assert live.version == 1

    # .. reject a stale editor attempting to create the same next version ..
    with pytest.raises(VersionConflictError):
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=second_document,
            author='review.agent',
            comment='Attempt an edit from a stale version',
        )

    # .. publish the second snapshot and prove the one pointer moved ..
    second_live = backend.versions.publish(definition_id=definition.id, version=2, actor='mark.b')
    assert second_live.version == 2
    live = backend.versions.get_live(definition.id)
    assert live.version == 2

    # .. restore the first document as a new third snapshot rather than mutating history ..
    first_version = backend.versions.get(definition.id, 1)
    restored = backend.versions.restore(
        definition_id=definition.id,
        source_version=1,
        expected_current_version=2,
        actor=_author,
        comment='Restore the original threshold after regression review',
    )
    assert restored.version == 3
    assert restored.document == first_version.document

    # .. and verify the promoted current and live paths both point at the linear restore.
    current = backend.definitions.get(definition.id)
    assert current.current_version == 3
    assert current.live_version == 3
    live = backend.versions.get_live(definition.id)
    assert live.version == 3

# ################################################################################################################################

def test_mandatory_comment_and_generic_event(backend:'RuleSQLBackend') -> 'None':
    """ Every version has a reason and generic activity remains append-only.
    """
    # Create one definition ..
    definition = _create_ruleset(backend)
    document = _ruleset_document(700)

    # .. reject a version with no reason for the change ..
    with pytest.raises(InvalidStoreInputError):
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=_author,
            comment='',
        )

    # .. append a review comment through the generic event path ..
    payload = {'comment': 'The boundary case at 740 needs one more scenario.'}
    event = backend.events.append(
        definition_id=definition.id,
        version=1,
        event_type=Event_Type_Review_Commented,
        actor='risk.reviewer',
        payload=payload,
    )

    # .. and read the same immutable event from the parent feed.
    events = backend.events.list(definition_id=definition.id)
    assert events[0] == event

# ################################################################################################################################
# ################################################################################################################################
