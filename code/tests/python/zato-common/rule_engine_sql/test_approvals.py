# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import update

# Local
from zato.common.rule_engine.sql import ApprovalContentMismatchError, ApprovalRequiredError, InvalidStoreInputError, \
    RuleDefinitionRecord, RuleSQLBackend, SelfApprovalNotAllowedError
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Event_Type_Approval_Gate_Off, \
    Event_Type_Approval_Gate_On, Event_Type_Approval_Requested, Event_Type_Self_Approval, Event_Type_Version_Approved
from zato.common.rule_engine.sql.data import anydict, strset
from zato.common.rule_engine.sql.document import content_hash
from zato.common.rule_engine.sql.schema import rule_version_table

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'
_approver = 'risk.reviewer'
_ruleset_name = 'Loan approval'
_initial_comment = 'Create the first complete ruleset'

# ################################################################################################################################
# ################################################################################################################################

def _ruleset_document(minimum_score:'int') -> 'anydict':
    """ Returns one realistic complete ruleset document.
    """
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

def _create_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ Creates the common ruleset used by approval tests.
    """
    document = _ruleset_document(740)
    out = backend.definitions.create(
        name=_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment=_initial_comment,
    )
    return out

# ################################################################################################################################

def _event_types(backend:'RuleSQLBackend', definition_id:'int') -> 'strset':
    """ Returns every event type in one definition's feed.
    """
    events = backend.events.list(definition_id=definition_id)
    out:'strset' = set()

    for event in events:
        out.add(event.event_type)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_gate_off_by_default_and_status_is_readable(backend:'RuleSQLBackend') -> 'None':
    """ An unconfigured definition publishes exactly as before and its approval state is readable.
    """
    # Create one definition with no approval configuration at all ..
    definition = _create_ruleset(backend)

    # .. verify the effective defaults are visible through the status API ..
    status = backend.approvals.get_status(definition.id, 1)
    assert status.gate_enabled is False
    assert status.allow_self_approval is False
    assert status.is_approved is False
    assert status.content_matches is False
    assert status.approval is None

    # .. and verify an unapproved version publishes while the gate is off.
    published = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)
    assert published.version == 1

# ################################################################################################################################

def test_gate_on_blocks_publish_until_approved(backend:'RuleSQLBackend') -> 'None':
    """ While the gate is on, publish requires an approval bound to the exact version and content hash.
    """
    # Create one definition and turn its gate on ..
    definition = _create_ruleset(backend)
    config = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    assert config.gate_enabled is True

    # .. verify the unapproved version cannot be published ..
    with pytest.raises(ApprovalRequiredError):
        _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    # .. approve the version through a different named approver ..
    approval = backend.approvals.approve(
        definition_id=definition.id,
        version=1,
        approver=_approver,
        comment='Reviewed against the Q3 lending policy',
    )
    assert approval.approver == _approver

    # .. verify the approval is bound to the exact bytes of the approved snapshot ..
    version = backend.versions.get(definition.id, 1)
    expected_hash = content_hash(version.document)
    assert approval.content_hash == expected_hash

    # .. verify the approved version now publishes ..
    published = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)
    assert published.version == 1

    # .. verify one-hop traceability from the live version to its approval with the matching hash ..
    live = backend.versions.get_live(definition.id)
    status = backend.approvals.get_status(definition.id, live.version)
    assert status.is_approved is True
    assert status.content_matches is True
    assert status.approval == approval

    # .. and verify both the gate change and the approval left their audit events.
    event_types = _event_types(backend, definition.id)
    assert Event_Type_Approval_Gate_On in event_types
    assert Event_Type_Version_Approved in event_types

# ################################################################################################################################

def test_self_approval_is_blocked_by_default_and_configurable(backend:'RuleSQLBackend') -> 'None':
    """ The author cannot approve their own version unless self-approval was explicitly allowed.
    """
    # Create one definition with the gate on ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')

    # .. verify the author is rejected as their own approver ..
    with pytest.raises(SelfApprovalNotAllowedError):
        _ = backend.approvals.approve(definition_id=definition.id, version=1, approver=_author)

    # .. allow self-approval through the logged configuration change ..
    config = backend.approvals.set_self_approval(definition_id=definition.id, allowed=True, actor='compliance.admin')
    assert config.allow_self_approval is True

    # .. verify the author can now approve their own version ..
    approval = backend.approvals.approve(definition_id=definition.id, version=1, approver=_author)
    assert approval.approver == _author

    # .. and verify the toggle left its own audit event.
    event_types = _event_types(backend, definition.id)
    assert Event_Type_Self_Approval in event_types

# ################################################################################################################################

def test_approval_is_immutable_and_singular(backend:'RuleSQLBackend') -> 'None':
    """ A version has exactly one immutable approval.
    """
    # Create one definition and approve its first version ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.approve(definition_id=definition.id, version=1, approver=_approver)

    # .. and verify a second approval of the same version is rejected.
    with pytest.raises(InvalidStoreInputError):
        _ = backend.approvals.approve(definition_id=definition.id, version=1, approver='another.reviewer')

# ################################################################################################################################

def test_approval_does_not_carry_over_to_new_versions(backend:'RuleSQLBackend') -> 'None':
    """ An approval binds to one exact version, a newer version starts unapproved.
    """
    # Create one definition with the gate on and approve version 1 ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    _ = backend.approvals.approve(definition_id=definition.id, version=1, approver=_approver)

    # .. create a second version with different content ..
    second_document = _ruleset_document(720)
    second = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=second_document,
        author=_author,
        comment='Lower the minimum score after portfolio review',
    )
    assert second.version == 2

    # .. verify the new version cannot ride on the old approval ..
    with pytest.raises(ApprovalRequiredError):
        _ = backend.versions.publish(definition_id=definition.id, version=2, actor=_author)

    # .. while the approved first version still publishes.
    published = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)
    assert published.version == 1

# ################################################################################################################################

def test_tampered_content_is_rejected_at_publish_time(backend:'RuleSQLBackend') -> 'None':
    """ Publish verifies that the approved bytes equal the bytes about to go live.
    """
    # Create one definition with the gate on and approve version 1 ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    _ = backend.approvals.approve(definition_id=definition.id, version=1, approver=_approver)

    # .. simulate tampering by rewriting the stored snapshot behind the store's back ..
    tampered_document = '{"rules":[]}'
    session = backend.session_factory()

    try:
        with session.begin():
            statement = update(rule_version_table)
            definition_condition = rule_version_table.c.definition_id == definition.id
            version_condition = rule_version_table.c.version == 1
            statement = statement.where(definition_condition)
            statement = statement.where(version_condition)
            statement = statement.values(document=tampered_document)
            _ = session.execute(statement)
    finally:
        session.close()

    # .. verify the status API reports the mismatch ..
    status = backend.approvals.get_status(definition.id, 1)
    assert status.is_approved is True
    assert status.content_matches is False

    # .. and verify publication of the tampered snapshot is rejected.
    with pytest.raises(ApprovalContentMismatchError):
        _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

# ################################################################################################################################

def test_gate_toggles_are_logged_and_turning_it_off_reopens_publish(backend:'RuleSQLBackend') -> 'None':
    """ Turning the gate on or off is itself a logged event and the off state restores plain publishing.
    """
    # Create one definition, turn the gate on, then off again ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    config = backend.approvals.set_gate(definition_id=definition.id, enabled=False, actor='compliance.admin')
    assert config.gate_enabled is False

    # .. verify both directions left their own audit events ..
    event_types = _event_types(backend, definition.id)
    assert Event_Type_Approval_Gate_On in event_types
    assert Event_Type_Approval_Gate_Off in event_types

    # .. and verify the unapproved version publishes again with the gate off.
    published = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)
    assert published.version == 1

# ################################################################################################################################

def test_config_change_that_changes_nothing_logs_nothing(backend:'RuleSQLBackend') -> 'None':
    """ Re-applying the current configuration writes no misleading audit event.
    """
    # Create one definition and disable the gate that is already off by default ..
    definition = _create_ruleset(backend)
    config = backend.approvals.set_gate(definition_id=definition.id, enabled=False, actor='compliance.admin')
    assert config.gate_enabled is False

    # .. and verify no gate event was appended.
    event_types = _event_types(backend, definition.id)
    assert Event_Type_Approval_Gate_On not in event_types
    assert Event_Type_Approval_Gate_Off not in event_types

# ################################################################################################################################

def test_new_version_announces_awaiting_approval_only_while_the_gate_is_on(backend:'RuleSQLBackend') -> 'None':
    """ A version created while the gate is on leaves an awaiting-approval event, a gate-off version does not.
    """
    # Create one definition and a second version while the gate is still off ..
    definition = _create_ruleset(backend)
    second_document = _ruleset_document(720)
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=second_document,
        author=_author,
        comment='Lower the minimum score after portfolio review',
    )

    # .. verify no awaiting-approval event was appended ..
    event_types = _event_types(backend, definition.id)
    assert Event_Type_Approval_Requested not in event_types

    # .. turn the gate on and create a third version ..
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    third_document = _ruleset_document(700)
    third = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=2,
        document=third_document,
        author=_author,
        comment='Lower the minimum score again for the pilot region',
    )

    # .. and verify the feed now announces the version awaiting its approval.
    events = backend.events.list(definition_id=definition.id)

    for event in events:
        if event.event_type == Event_Type_Approval_Requested:
            awaiting = event
            break
    else:
        raise Exception('No awaiting-approval event was appended')

    assert awaiting.version == third.version
    assert awaiting.actor == _author

# ################################################################################################################################

def test_restore_bypasses_the_gate(backend:'RuleSQLBackend') -> 'None':
    """ A rollback is the emergency path back to a previously live document and never waits for an approval.
    """
    # Create one definition, approve and publish version 1 while the gate is on ..
    definition = _create_ruleset(backend)
    _ = backend.approvals.set_gate(definition_id=definition.id, enabled=True, actor='compliance.admin')
    _ = backend.approvals.approve(definition_id=definition.id, version=1, approver=_approver)
    _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    # .. create and approve a second version, then publish it ..
    second_document = _ruleset_document(720)
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=second_document,
        author=_author,
        comment='Lower the minimum score after portfolio review',
    )
    _ = backend.approvals.approve(definition_id=definition.id, version=2, approver=_approver)
    _ = backend.versions.publish(definition_id=definition.id, version=2, actor=_author)

    # .. and verify rolling back to version 1 succeeds with no approval of the new version 3.
    restored = backend.versions.restore(
        definition_id=definition.id,
        source_version=1,
        expected_current_version=2,
        actor=_author,
        comment='Emergency rollback after the score change misfired',
    )
    assert restored.version == 3
    live = backend.versions.get_live(definition.id)
    assert live.version == 3

# ################################################################################################################################
# ################################################################################################################################
