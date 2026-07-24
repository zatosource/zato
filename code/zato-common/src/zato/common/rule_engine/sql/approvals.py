# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import insert, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Default_Allow_Self_Approval, Default_Approval_Gate_Enabled, Event_Type_Approval_Gate_Off, \
    Event_Type_Approval_Gate_On, Event_Type_Self_Approval, Event_Type_Version_Approved
from .data import ApprovalStatus, RuleApprovalConfigRecord, RuleApprovalRecord
from .database import SessionFactory
from .document import content_hash
from .errors import ApprovalContentMismatchError, ApprovalRequiredError, InvalidStoreInputError, \
    SelfApprovalNotAllowedError
from .records import approval_config_record, approval_record
from .schema import rule_approval_config_table, rule_approval_table
from .store_common import add_event, get_definition, get_version, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

def get_config_row(session:'Session', definition_id:'int') -> 'RuleApprovalConfigRecord | None':
    """ Returns one definition's stored gate configuration in the caller's transaction, or None when never configured.
    """
    # Query the one promoted configuration identity ..
    query = select(rule_approval_config_table)
    cluster_condition = rule_approval_config_table.c.cluster_id == default_cluster_id
    definition_condition = rule_approval_config_table.c.definition_id == definition_id
    query = query.where(cluster_condition)
    query = query.where(definition_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. and convert the row when the definition was ever configured.
    if row:
        out = approval_config_record(row)
    else:
        out = None

    return out

# ################################################################################################################################

def get_version_approval(session:'Session', definition_id:'int', version:'int') -> 'RuleApprovalRecord | None':
    """ Returns one version's approval in the caller's transaction, or None when the version was never approved.
    """
    # Query the one promoted approval identity ..
    query = select(rule_approval_table)
    cluster_condition = rule_approval_table.c.cluster_id == default_cluster_id
    definition_condition = rule_approval_table.c.definition_id == definition_id
    version_condition = rule_approval_table.c.version == version
    query = query.where(cluster_condition)
    query = query.where(definition_condition)
    query = query.where(version_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. and convert the row when the version has its approval.
    if row:
        out = approval_record(row)
    else:
        out = None

    return out

# ################################################################################################################################

def is_gate_enabled(session:'Session', definition_id:'int') -> 'bool':
    """ Returns one definition's effective gate state in the caller's transaction,
    an unconfigured definition uses the module-level default.
    """
    config = get_config_row(session, definition_id)

    if config is None:
        out = Default_Approval_Gate_Enabled
    else:
        out = config.gate_enabled

    return out

# ################################################################################################################################

def assert_version_publishable(session:'Session', definition_id:'int', version:'int', document_text:'str') -> 'None':
    """ Blocks publication in the caller's transaction while the gate is on and the version has no matching approval.
    """
    # Read the effective gate state ..
    gate_enabled = is_gate_enabled(session, definition_id)

    # .. a definition with the gate off publishes exactly as before ..
    if not gate_enabled:
        return

    # .. the gate is on, so the version must have its one approval ..
    approval = get_version_approval(session, definition_id, version)

    if approval is None:
        message = f'Version {version} of rule definition {definition_id} requires an approval before it can be published'
        raise ApprovalRequiredError(message)

    # .. and the approved bytes must equal the bytes about to go live, the tamper-evidence half of the gate.
    expected_hash = content_hash(document_text)

    if approval.content_hash != expected_hash:
        message = f'Approval for version {version} of rule definition {definition_id} was made against different content ' + \
            f'-> approved {approval.content_hash}, current {expected_hash}'
        raise ApprovalContentMismatchError(message)

# ################################################################################################################################
# ################################################################################################################################

class ApprovalStore:
    """ The thin publish approval gate - immutable approvals bound to one exact version and content hash,
    with a per-definition on/off gate whose every change is itself a logged event.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def approve(
        self,
        *,
        definition_id:'int',
        version:'int',
        approver:'str',
        comment:'str | None' = None,
        ) -> 'RuleApprovalRecord':
        """ Binds a named approver to one exact version and the content hash of its serialized document,
        recorded as an immutable approval row plus its history event in one transaction.
        """
        # Validate the approver before opening a transaction ..
        require_text(approver, 'Approval approver')
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm that the definition exists and still accepts changes ..
                definition = get_definition(session, definition_id)
                if not definition.is_active:
                    message = f'Rule definition {definition_id} is archived'
                    raise InvalidStoreInputError(message)

                # .. resolve the exact immutable snapshot being approved ..
                target = get_version(session, definition_id, version)

                # .. enforce author and approver separation unless self-approval was explicitly allowed ..
                config = get_config_row(session, definition_id)

                if config is None:
                    allow_self_approval = Default_Allow_Self_Approval
                else:
                    allow_self_approval = config.allow_self_approval

                if target.author == approver:
                    if not allow_self_approval:
                        message = f'Author {approver} cannot approve their own version {version} ' + \
                            f'of rule definition {definition_id}'
                        raise SelfApprovalNotAllowedError(message)

                # .. bind the approval to the exact bytes of the approved snapshot ..
                approved_hash = content_hash(target.document)

                # .. stage the immutable approval row ..
                values = {
                    'cluster_id':    default_cluster_id,
                    'definition_id': definition_id,
                    'version':       version,
                    'content_hash':  approved_hash,
                    'approver':      approver,
                    'comment':       comment,
                    'created_at':    now,
                }
                statement = insert(rule_approval_table)
                result = session.execute(statement, values)
                result = cast_(CursorResult, result)
                primary_key = result.inserted_primary_key
                approval_id = primary_key[0]

                # .. append its history event in the same commit ..
                payload = {'content_hash': approved_hash, 'comment': comment}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=version,
                    event_type=Event_Type_Version_Approved,
                    actor=approver,
                    payload=payload,
                )

                # .. and build the detached record from the values just written, avoiding a redundant re-read.
                out = RuleApprovalRecord(
                    id=approval_id,
                    cluster_id=default_cluster_id,
                    definition_id=definition_id,
                    version=version,
                    content_hash=approved_hash,
                    approver=approver,
                    comment=comment,
                    created_at=now,
                )

        # A uniqueness failure means the version already has its one immutable approval ..
        except IntegrityError as e:
            message = f'Version {version} of rule definition {definition_id} is already approved'
            raise InvalidStoreInputError(message) from e

        # .. and every path releases the session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get_approval(self, definition_id:'int', version:'int') -> 'RuleApprovalRecord | None':
        """ Returns one version's approval, or None when the version was never approved.
        """
        # Load the optional approval through the shared session-level query ..
        session = self._session_factory()

        try:
            out = get_version_approval(session, definition_id, version)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get_config(self, definition_id:'int') -> 'RuleApprovalConfigRecord | None':
        """ Returns one definition's stored gate configuration, or None when the definition was never configured.
        """
        # Load the optional configuration through the shared session-level query ..
        session = self._session_factory()

        try:
            out = get_config_row(session, definition_id)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get_status(self, definition_id:'int', version:'int') -> 'ApprovalStatus':
        """ Returns the complete readable approval state of one version - the effective gate settings,
        whether the version is approved and whether the approved content still matches the stored snapshot.
        """
        session = self._session_factory()

        try:
            # Confirm the definition and resolve the exact snapshot being asked about ..
            _ = get_definition(session, definition_id)
            target = get_version(session, definition_id, version)

            # .. read the effective gate state, an unconfigured definition uses the module-level defaults ..
            config = get_config_row(session, definition_id)

            if config is None:
                gate_enabled = Default_Approval_Gate_Enabled
                allow_self_approval = Default_Allow_Self_Approval
            else:
                gate_enabled = config.gate_enabled
                allow_self_approval = config.allow_self_approval

            # .. and read the version's optional approval with its hash verified against the stored snapshot.
            approval = get_version_approval(session, definition_id, version)

            if approval is None:
                is_approved = False
                content_matches = False
            else:
                is_approved = True
                current_hash = content_hash(target.document)
                content_matches = approval.content_hash == current_hash

        # Release the read-only session in every case.
        finally:
            session.close()

        out = ApprovalStatus(
            definition_id=definition_id,
            version=version,
            gate_enabled=gate_enabled,
            allow_self_approval=allow_self_approval,
            is_approved=is_approved,
            content_matches=content_matches,
            approval=approval,
        )
        return out

# ################################################################################################################################

    def set_gate(self, *, definition_id:'int', enabled:'bool', actor:'str') -> 'RuleApprovalConfigRecord':
        """ Turns the publish approval gate on or off, the change itself recorded as a logged event.
        """
        out = self._set_config_field(
            definition_id=definition_id,
            field_name='gate_enabled',
            field_value=enabled,
            actor=actor,
        )
        return out

# ################################################################################################################################

    def set_self_approval(self, *, definition_id:'int', allowed:'bool', actor:'str') -> 'RuleApprovalConfigRecord':
        """ Allows or forbids authors approving their own versions, the change itself recorded as a logged event.
        """
        out = self._set_config_field(
            definition_id=definition_id,
            field_name='allow_self_approval',
            field_value=allowed,
            actor=actor,
        )
        return out

# ################################################################################################################################

    def _set_config_field(
        self,
        *,
        definition_id:'int',
        field_name:'str',
        field_value:'bool',
        actor:'str',
        ) -> 'RuleApprovalConfigRecord':
        """ Applies one gate configuration change and appends its audit event in the same transaction.
        """
        # Validate the actor before opening a transaction ..
        require_text(actor, 'Approval config actor')
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the definition exists inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. read the current configuration, an unconfigured definition starts from the module-level defaults ..
                existing = get_config_row(session, definition_id)

                if existing is None:
                    current_values = {
                        'gate_enabled':        Default_Approval_Gate_Enabled,
                        'allow_self_approval': Default_Allow_Self_Approval,
                    }
                else:
                    current_values = {
                        'gate_enabled':        existing.gate_enabled,
                        'allow_self_approval': existing.allow_self_approval,
                    }

                # .. a change that changes nothing writes nothing and logs nothing ..
                has_changed = current_values[field_name] != field_value

                # .. apply the one changed field over the current state ..
                current_values[field_name] = field_value

                # .. store the configuration in place or create its first row ..
                if existing is None:
                    insert_values = {
                        'cluster_id':          default_cluster_id,
                        'definition_id':       definition_id,
                        'gate_enabled':        current_values['gate_enabled'],
                        'allow_self_approval': current_values['allow_self_approval'],
                        'updated_at':          now,
                        'updated_by':          actor,
                    }
                    statement = insert(rule_approval_config_table)
                    result = session.execute(statement, insert_values)
                    result = cast_(CursorResult, result)
                    primary_key = result.inserted_primary_key
                    config_id = primary_key[0]

                else:
                    update_values = {
                        'gate_enabled':        current_values['gate_enabled'],
                        'allow_self_approval': current_values['allow_self_approval'],
                        'updated_at':          now,
                        'updated_by':          actor,
                    }
                    statement = update(rule_approval_config_table)
                    id_condition = rule_approval_config_table.c.id == existing.id
                    statement = statement.where(id_condition)
                    statement = statement.values(**update_values)
                    _ = session.execute(statement)
                    config_id = existing.id

                # .. an actual change appends its audit event in the same commit,
                # .. so the gate can never be reconfigured without a trace ..
                if has_changed:
                    event_type = _config_event_type(field_name, field_value)
                    payload = {field_name: field_value}
                    _ = add_event(
                        session,
                        definition_id=definition_id,
                        version=None,
                        event_type=event_type,
                        actor=actor,
                        payload=payload,
                    )

                # .. and build the detached record from the values just written.
                out = RuleApprovalConfigRecord(
                    id=config_id,
                    cluster_id=default_cluster_id,
                    definition_id=definition_id,
                    gate_enabled=current_values['gate_enabled'],
                    allow_self_approval=current_values['allow_self_approval'],
                    updated_at=now,
                    updated_by=actor,
                )

        # Release the transactional session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################

def _config_event_type(field_name:'str', field_value:'bool') -> 'str':
    """ Returns the audit event type matching one gate configuration change.
    """
    # The gate itself has one distinct event per direction ..
    if field_name == 'gate_enabled':
        if field_value:
            out = Event_Type_Approval_Gate_On
        else:
            out = Event_Type_Approval_Gate_Off

    # .. while the self-approval toggle uses one event with the direction in its payload.
    else:
        out = Event_Type_Self_Approval

    return out

# ################################################################################################################################
# ################################################################################################################################
