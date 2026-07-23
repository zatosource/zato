# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import insert, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.typing_ import cast_

# Local
from .constants import Event_Type_Version_Created, Event_Type_Version_Published, Event_Type_Version_Restored
from .data import anydict, RuleVersionRecord
from .database import SessionFactory
from .document import serialize_document
from .errors import InvalidStoreInputError, RecordNotFoundError, VersionConflictError
from .schema import rule_definition_table, rule_version_table
from .store_common import add_event, get_definition, get_version, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

class VersionStore:
    """ Immutable full snapshots, optimistic edits, atomic publishing and linear restores.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def create(
        self,
        *,
        definition_id:'int',
        expected_current_version:'int',
        document:'anydict',
        author:'str',
        comment:'str',
        ) -> 'RuleVersionRecord':
        """ Adds a full snapshot using an optimistic check, so concurrent edits cannot overwrite each other.
        """
        # Validate history metadata and serialize the whole document before opening a transaction ..
        require_text(author, 'Version author')
        require_text(comment, 'Version comment')
        document_text = serialize_document(document)
        new_version = expected_current_version + 1
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm that the definition exists and still accepts edits ..
                definition = get_definition(session, definition_id)
                if not definition.is_active:
                    message = f'Rule definition {definition_id} is archived'
                    raise InvalidStoreInputError(message)

                # .. claim the next version with one optimistic update ..
                statement = update(rule_definition_table)
                id_condition = rule_definition_table.c.id == definition_id
                version_condition = rule_definition_table.c.current_version == expected_current_version
                statement = statement.where(id_condition)
                statement = statement.where(version_condition)
                statement = statement.values(current_version=new_version, document=document_text, updated_at=now)
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                if result.rowcount != 1:
                    message = f'Rule definition {definition_id} is no longer at version {expected_current_version}'
                    raise VersionConflictError(message)

                # .. stage the immutable full snapshot ..
                version_values = {
                    'definition_id': definition_id,
                    'version':       new_version,
                    'author':        author,
                    'comment':       comment,
                    'created_at':    now,
                    'document':      document_text,
                }
                statement = insert(rule_version_table)
                insert_result = session.execute(statement, version_values)
                insert_result = cast_(CursorResult, insert_result)
                primary_key = insert_result.inserted_primary_key
                version_id = primary_key[0]

                # .. append its history event in the same commit ..
                payload = {'comment': comment}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=new_version,
                    event_type=Event_Type_Version_Created,
                    actor=author,
                    payload=payload,
                )

                # .. and build the detached snapshot from the values just written, avoiding a redundant re-read.
                version = RuleVersionRecord(
                    id=version_id,
                    definition_id=definition_id,
                    version=new_version,
                    author=author,
                    comment=comment,
                    created_at=now,
                    document=document_text,
                )

        # A uniqueness failure means another transaction claimed the same version ..
        except IntegrityError as e:
            message = f'Rule definition {definition_id} was changed while version {new_version} was being created'
            raise VersionConflictError(message) from e

        # .. and every path releases the session.
        finally:
            session.close()

        return version

# ################################################################################################################################

    def publish(self, *, definition_id:'int', version:'int', actor:'str') -> 'RuleVersionRecord':
        """ Makes exactly one existing snapshot live in an atomic transaction.
        """
        # Validate the actor before changing publication state ..
        require_text(actor, 'Publish actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Resolve the active definition and target snapshot ..
                definition = get_definition(session, definition_id)
                if not definition.is_active:
                    message = f'Rule definition {definition_id} is archived'
                    raise InvalidStoreInputError(message)

                target = get_version(session, definition_id, version)

                # .. move the one live pointer, the promoted definition column, to the requested snapshot ..
                statement = update(rule_definition_table)
                id_condition = rule_definition_table.c.id == definition_id
                statement = statement.where(id_condition)
                now = utc_now()
                statement = statement.values(live_version=version, updated_at=now)
                _ = session.execute(statement)

                # .. and append the publication event in the same commit.
                payload = {'published_version': version}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=version,
                    event_type=Event_Type_Version_Published,
                    actor=actor,
                    payload=payload,
                )

        # Release the transactional session in every case.
        finally:
            session.close()

        return target

# ################################################################################################################################

    def restore(
        self,
        *,
        definition_id:'int',
        source_version:'int',
        expected_current_version:'int',
        actor:'str',
        comment:'str',
        ) -> 'RuleVersionRecord':
        """ Copies a past snapshot into a new linear version and publishes the copy atomically.
        """
        # Validate history metadata and reserve the next linear number ..
        require_text(actor, 'Restore actor')
        require_text(comment, 'Restore comment')
        new_version = expected_current_version + 1
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Resolve both the current definition and the source snapshot ..
                definition = get_definition(session, definition_id)
                source = get_version(session, definition_id, source_version)

                if not definition.is_active:
                    message = f'Rule definition {definition_id} is archived'
                    raise InvalidStoreInputError(message)

                # .. claim a new current and live version with the source document ..
                statement = update(rule_definition_table)
                id_condition = rule_definition_table.c.id == definition_id
                version_condition = rule_definition_table.c.current_version == expected_current_version
                statement = statement.where(id_condition)
                statement = statement.where(version_condition)
                statement = statement.values(
                    current_version=new_version,
                    live_version=new_version,
                    document=source.document,
                    updated_at=now,
                )
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                if result.rowcount != 1:
                    message = f'Rule definition {definition_id} is no longer at version {expected_current_version}'
                    raise VersionConflictError(message)

                # .. preserve the restored document as a new immutable snapshot ..
                restored_values = {
                    'definition_id': definition_id,
                    'version':       new_version,
                    'author':        actor,
                    'comment':       comment,
                    'created_at':    now,
                    'document':      source.document,
                }
                statement = insert(rule_version_table)
                insert_result = session.execute(statement, restored_values)
                insert_result = cast_(CursorResult, insert_result)
                primary_key = insert_result.inserted_primary_key
                restored_id = primary_key[0]

                # .. record where the restored document came from ..
                restored_payload = {'source_version': source_version, 'comment': comment}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=new_version,
                    event_type=Event_Type_Version_Restored,
                    actor=actor,
                    payload=restored_payload,
                )

                # .. record publication in the same commit ..
                published_payload = {'published_version': new_version}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=new_version,
                    event_type=Event_Type_Version_Published,
                    actor=actor,
                    payload=published_payload,
                )

                # .. and build the detached restored snapshot from the values just written.
                restored = RuleVersionRecord(
                    id=restored_id,
                    definition_id=definition_id,
                    version=new_version,
                    author=actor,
                    comment=comment,
                    created_at=now,
                    document=source.document,
                )

        # A uniqueness failure means another transaction claimed the same version ..
        except IntegrityError as e:
            message = f'Rule definition {definition_id} was changed while version {new_version} was being restored'
            raise VersionConflictError(message) from e

        # .. and every path releases the session.
        finally:
            session.close()

        return restored

# ################################################################################################################################

    def get(self, definition_id:'int', version:'int') -> 'RuleVersionRecord':
        """ Returns one immutable version.
        """
        # Load the snapshot through the shared composite-key query ..
        session = self._session_factory()

        try:
            out = get_version(session, definition_id, version)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get_live(self, definition_id:'int') -> 'RuleVersionRecord':
        """ Returns the one live version of a definition.
        """
        # Read the promoted live version without opening any snapshot document ..
        session = self._session_factory()

        try:
            definition = get_definition(session, definition_id)
            if definition.live_version is None:
                message = f'Rule definition {definition_id} has no live version'
                raise RecordNotFoundError(message)

            # .. then resolve that immutable snapshot inside the same read transaction.
            out = get_version(session, definition_id, definition.live_version)

        # Release the read-only session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################
