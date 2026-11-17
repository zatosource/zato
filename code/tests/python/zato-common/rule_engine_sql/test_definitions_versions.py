# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Local
from zato.common.rule_engine.sql import InvalidStoreInputError, RuleDefinitionRecord, RuleSQLBackend, VersionConflictError
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
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
    # Keep the stable rule identifier inside one complete document.
    out = {
        'rules': [
            {
                'id': 'excellent-credit',
                'if': {'customer.creditScore': {'at_least': minimum_score}},
                'then': {'loan.approved': True},
            }
        ],
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

def test_create_definition_and_snapshot(backend:'RuleSQLBackend') -> 'None':
    """ A definition and its first snapshot commit together.
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

    # .. and verify the first immutable snapshot is complete.
    version = backend.versions.get(definition.id, 1)
    assert version.document == definition.document
    assert version.comment == _initial_comment

# ################################################################################################################################

def test_definition_identity_and_search(backend:'RuleSQLBackend') -> 'None':
    """ Identity constraints and document search use promoted columns.
    """
    # Create a ruleset ..
    definition = _create_ruleset(backend)

    # .. locate it by content rather than its name ..
    matches = backend.definitions.list(search_text='creditScore')
    assert matches == [definition]

    # .. and reject a duplicate identity of the same type.
    with pytest.raises(InvalidStoreInputError):
        _ = _create_ruleset(backend)

# ################################################################################################################################

def test_optimistic_versions_and_publish(backend:'RuleSQLBackend') -> 'None':
    """ Edits are optimistic and publication moves the one live pointer.
    """
    # Create and publish the first snapshot ..
    definition = _create_ruleset(backend)
    first_live = backend.versions.publish(definition_id=definition.id, version=1)
    assert first_live.version == 1

    # .. verify the one live pointer, the promoted definition column, follows publication ..
    current = backend.definitions.get(definition.id)
    assert current.live_version == 1

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
    current = backend.definitions.get(definition.id)
    assert current.current_version == 2
    assert current.live_version == 1

    # .. reject a stale editor attempting to create the same next version ..
    with pytest.raises(VersionConflictError):
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=second_document,
            author='review.agent',
            comment='Attempt an edit from a stale version',
        )

    # .. and publish the second snapshot, which moves the one pointer.
    second_live = backend.versions.publish(definition_id=definition.id, version=2)
    assert second_live.version == 2

    current = backend.definitions.get(definition.id)
    assert current.live_version == 2

# ################################################################################################################################

def test_mandatory_comment(backend:'RuleSQLBackend') -> 'None':
    """ Every version has a reason for the change.
    """
    definition = _create_ruleset(backend)
    document = _ruleset_document(700)

    with pytest.raises(InvalidStoreInputError):
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=_author,
            comment='',
        )

# ################################################################################################################################
# ################################################################################################################################
