# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import func, insert, or_, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.rule_engine.changes import Change_Definition_Created
from zato.common.typing_ import anytuple, cast_

# Local
from .constants import Definition_Type_Ruleset, Definition_Types
from .data import anydict, definition_record_list, RuleDefinitionRecord
from .database import SessionFactory
from .document import deserialize_document, serialize_document
from .errors import InvalidStoreInputError
from .records import definition_record
from .schema import rule_definition_table, rule_version_table
from .store_common import get_definition, parent_key, require_text
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

class DefinitionStore:
    """ Current rule-engine objects and their complete JSON documents.
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
        name:'str',
        object_type:'str',
        document:'anydict',
        author:'str',
        comment:'str',
        parent_id:'int | None' = None,
        ) -> 'RuleDefinitionRecord':
        """ Creates a definition and its first snapshot in one transaction.
        """
        # Validate all user-facing identity and history fields ..
        require_text(name, 'Definition name')
        require_text(author, 'Version author')
        require_text(comment, 'Version comment')

        if object_type not in Definition_Types:
            message = f'Unknown rule definition type -> {object_type}'
            raise InvalidStoreInputError(message)

        # .. serialize the complete document before opening a transaction ..
        document_text = serialize_document(document)
        now = utc_now()

        try:
            definition = self._session_factory.write(self._create_rows, name, object_type, parent_id, document_text, now,
                author, comment)

        # Translate a duplicate portable identity into a domain error ..
        except IntegrityError as e:
            message = f'A rule definition named "{name}" already exists under the same parent and type'
            raise InvalidStoreInputError(message) from e

        # Announce the committed creation - a name that servers cached as unknown may exist now.
        self._announce_change(Change_Definition_Created, definition.id, name, object_type)

        return definition

# ################################################################################################################################

    def _create_rows(
        self,
        session:'Session',
        name:'str',
        object_type:'str',
        parent_id:'int | None',
        document_text:'str',
        now:'datetime',
        author:'str',
        comment:'str',
        ) -> 'RuleDefinitionRecord':
        """ Writes a definition and its first snapshot and returns the definition.
        """
        # Resolve the optional parent ..
        if parent_id is not None:
            _ = get_definition(session, parent_id)

        # .. insert the current definition ..
        definition_parent_key = parent_key(parent_id)
        definition_values = {
            'parent_id':       parent_id,
            'parent_key':      definition_parent_key,
            'name':            name,
            'object_type':     object_type,
            'current_version': 1,
            'live_version':    None,
            'is_active':       True,
            'created_at':      now,
            'updated_at':      now,
            'document':        document_text,
        }
        statement = insert(rule_definition_table)
        result = session.execute(statement, definition_values)
        result = cast_(CursorResult, result)
        primary_key = cast_(anytuple, result.inserted_primary_key)
        definition_id = primary_key[0]

        # .. preserve the first immutable full snapshot in the same commit ..
        version_values = {
            'definition_id': definition_id,
            'version':       1,
            'author':        author,
            'comment':       comment,
            'created_at':    now,
            'document':      document_text,
        }
        statement = insert(rule_version_table)
        _ = session.execute(statement, version_values)

        # .. and build the detached definition from the values just written, avoiding a redundant re-read.
        definition = RuleDefinitionRecord(
            id=definition_id,
            parent_id=parent_id,
            parent_key=definition_parent_key,
            name=name,
            object_type=object_type,
            current_version=1,
            live_version=None,
            is_active=True,
            created_at=now,
            updated_at=now,
            document=document_text,
        )

        return definition

# ################################################################################################################################

    def get(self, definition_id:'int') -> 'RuleDefinitionRecord':
        """ Returns one definition by id.
        """
        # Load the definition through the shared query ..
        session = self._session_factory()

        try:
            out = get_definition(session, definition_id)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get_document(self, definition_id:'int') -> 'anydict':
        """ Returns the current complete document of one definition.
        """
        # Read the promoted definition row ..
        definition = self.get(definition_id)

        # .. and decode its opaque TEXT document in application code.
        out = deserialize_document(definition.document)
        return out

# ################################################################################################################################

    def find_by_name(self, *, name:'str', object_type:'str') -> 'definition_record_list':
        """ Returns every active definition of one type with the given name, across all parents.

        Names are unique only within one parent, so a bare name can match more than one
        definition - the caller decides what an ambiguous match means at its boundary.
        """
        # Match the exact name of one type anywhere in the tree ..
        query = select(rule_definition_table)
        type_condition = rule_definition_table.c.object_type == object_type
        name_condition = rule_definition_table.c.name == name
        active_condition = rule_definition_table.c.is_active.is_(True)
        query = query.where(type_condition)
        query = query.where(name_condition)
        query = query.where(active_condition)
        query = query.order_by(rule_definition_table.c.id)
        session = self._session_factory()

        # .. load every match ..
        try:
            result = session.execute(query)
            out:'definition_record_list' = []

            for row in result:
                record = definition_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list_published_rulesets(self) -> 'definition_record_list':
        """ Returns every active ruleset with a live version, across all parents.

        This is the complete REST-invokable catalog - what the generated API documentation
        enumerates before grants narrow it down per API object.
        """
        # Match active rulesets whose live pointer is set, anywhere in the tree ..
        query = select(rule_definition_table)
        type_condition = rule_definition_table.c.object_type == Definition_Type_Ruleset
        active_condition = rule_definition_table.c.is_active.is_(True)
        live_condition = rule_definition_table.c.live_version.isnot(None)
        query = query.where(type_condition)
        query = query.where(active_condition)
        query = query.where(live_condition)
        query = query.order_by(rule_definition_table.c.name, rule_definition_table.c.id)
        session = self._session_factory()

        # .. load every match ..
        try:
            result = session.execute(query)
            out:'definition_record_list' = []

            for row in result:
                record = definition_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list(
        self,
        *,
        parent_id:'int | None' = None,
        object_type:'str | None' = None,
        search_text:'str | None' = None,
        include_inactive:'bool' = False,
        limit:'int' = 100,
        offset:'int' = 0,
        ) -> 'definition_record_list':
        """ Lists definitions by promoted paths with portable content search over the document TEXT.
        """
        # Validate pagination before constructing the query ..
        if limit < 1:
            raise InvalidStoreInputError('Definition list limit must be at least 1')

        if offset < 0:
            raise InvalidStoreInputError('Definition list offset cannot be negative')

        # .. start with the parent path every list uses ..
        query = select(rule_definition_table)
        definition_parent_key = parent_key(parent_id)
        parent_condition = rule_definition_table.c.parent_key == definition_parent_key
        query = query.where(parent_condition)

        # .. add optional promoted filters ..
        if object_type is not None:
            type_condition = rule_definition_table.c.object_type == object_type
            query = query.where(type_condition)

        if not include_inactive:
            active_condition = rule_definition_table.c.is_active.is_(True)
            query = query.where(active_condition)

        # .. escape content-search metacharacters before using portable LIKE ..
        if search_text is not None:
            search_text = search_text.lower()
            search_text = search_text.replace('\\', '\\\\')
            search_text = search_text.replace('%', '\\%')
            search_text = search_text.replace('_', '\\_')
            pattern = f'%{search_text}%'

            lower_name = func.lower(rule_definition_table.c.name)
            lower_document = func.lower(rule_definition_table.c.document)
            name_condition = lower_name.like(pattern, escape='\\')
            document_condition = lower_document.like(pattern, escape='\\')
            search_condition = or_(name_condition, document_condition)
            query = query.where(search_condition)

        # .. apply stable ordering and pagination ..
        query = query.order_by(rule_definition_table.c.name, rule_definition_table.c.id)
        query = query.limit(limit)
        query = query.offset(offset)
        session = self._session_factory()

        # .. load the page ..
        try:
            result = session.execute(query)
            out:'definition_record_list' = []

            for row in result:
                record = definition_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################
