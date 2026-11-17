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
from zato.common.rule_engine.changes import Change_Version_Created, Change_Version_Published
from zato.common.typing_ import anytuple, cast_

# Local
from .data import anydict, RuleVersionRecord
from .database import SessionFactory
from .document import serialize_document
from .errors import InvalidStoreInputError, VersionConflictError
from .schema import rule_definition_table, rule_version_table
from .store_common import get_definition, get_version, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.orm import Session
    from zato.common.rule_engine.changes import ChangePublisher

    # Dummy assignments to satisfy type checkers
    ChangePublisher = ChangePublisher
    datetime = datetime
    Session = Session

# ################################################################################################################################
# ################################################################################################################################

class VersionStore:
    """ Immutable full snapshots, optimistic edits and atomic publishing.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

        # When set, every committed write is announced on the change stream,
        # which is what lets server processes evict the RAM entries the write invalidates.
        self.change_publisher:'ChangePublisher | None' = None

# ################################################################################################################################

    def _announce_change(self, kind:'str', definition_id:'int', name:'str', object_type:'str') -> 'None':
        """ Announces one committed change, when a publisher is configured.
        """
        if self.change_publisher:
            self.change_publisher.publish(kind, definition_id, name, object_type)

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

        try:
            definition, version = self._session_factory.write(self._create_rows, definition_id, expected_current_version,
                new_version, document_text, now, author, comment)

        # A uniqueness failure means another transaction claimed the same version ..
        except IntegrityError as e:
            message = f'Rule definition {definition_id} was changed while version {new_version} was being created'
            raise VersionConflictError(message) from e

        # Announce the committed snapshot - for a vocabulary this is also an edit of its current document.
        self._announce_change(Change_Version_Created, definition_id, definition.name, definition.object_type)

        return version

# ################################################################################################################################

    def _create_rows(
        self,
        session:'Session',
        definition_id:'int',
        expected_current_version:'int',
        new_version:'int',
        document_text:'str',
        now:'datetime',
        author:'str',
        comment:'str',
        ) -> 'anytuple':
        """ Writes the next version of a definition and returns the definition and the version.
        """
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

        # .. stage the immutable full snapshot in the same commit ..
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
        primary_key = cast_(anytuple, insert_result.inserted_primary_key)
        version_id = primary_key[0]

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

        return definition, version

# ################################################################################################################################

    def publish(self, *, definition_id:'int', version:'int') -> 'RuleVersionRecord':
        """ Makes exactly one existing snapshot live in an atomic transaction.
        """
        definition, target = self._session_factory.write(self._publish_rows, definition_id, version)

        # Announce the committed publication - servers re-read the live pointer on their next request.
        self._announce_change(Change_Version_Published, definition_id, definition.name, definition.object_type)

        return target

# ################################################################################################################################

    def _publish_rows(self, session:'Session', definition_id:'int', version:'int') -> 'anytuple':
        """ Moves the live pointer of a definition to one snapshot and returns the definition and the snapshot.
        """
        # Resolve the active definition and target snapshot ..
        definition = get_definition(session, definition_id)
        if not definition.is_active:
            message = f'Rule definition {definition_id} is archived'
            raise InvalidStoreInputError(message)

        target = get_version(session, definition_id, version)

        # .. and move the one live pointer, the promoted definition column, to the requested snapshot.
        statement = update(rule_definition_table)
        id_condition = rule_definition_table.c.id == definition_id
        statement = statement.where(id_condition)
        now = utc_now()
        statement = statement.values(live_version=version, updated_at=now)
        _ = session.execute(statement)

        return definition, target

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
# ################################################################################################################################
