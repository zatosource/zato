# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import func, insert, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Definition_Types, Event_Type_Definition_Archived, Event_Type_Definition_Created, \
    Event_Type_Version_Created
from .data import anydict, definition_record_list, RuleDefinitionRecord
from .database import SessionFactory
from .document import deserialize_document, serialize_document
from .errors import InvalidStoreInputError
from .records import definition_record
from .schema import rule_definition_table, rule_version_table
from .store_common import add_event, get_definition, parent_key, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

class DefinitionStore:
    """ Current rule-engine objects and their complete JSON documents.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

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
        """ Creates a definition, its first snapshot and its creation events in one transaction.
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
        session = self._session_factory()

        try:
            with session.begin():

                # Resolve the optional parent in the same cluster ..
                if parent_id is not None:
                    _ = get_definition(session, parent_id)

                # .. insert the current definition ..
                definition_parent_key = parent_key(parent_id)
                definition_values = {
                    'cluster_id':      default_cluster_id,
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
                primary_key = result.inserted_primary_key
                definition_id = primary_key[0]

                # .. preserve the first immutable full snapshot ..
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

                # .. append the definition creation event ..
                created_payload = {'name': name, 'object_type': object_type}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=1,
                    event_type=Event_Type_Definition_Created,
                    actor=author,
                    payload=created_payload,
                )

                # .. append the first version event in the same commit ..
                version_payload = {'comment': comment}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=1,
                    event_type=Event_Type_Version_Created,
                    actor=author,
                    payload=version_payload,
                )

                # .. and build the detached definition from the values just written, avoiding a redundant re-read.
                definition = RuleDefinitionRecord(
                    id=definition_id,
                    cluster_id=default_cluster_id,
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

        # Translate a duplicate portable identity into a domain error ..
        except IntegrityError as e:
            message = f'A rule definition named "{name}" already exists under the same parent and type'
            raise InvalidStoreInputError(message) from e

        # .. and release the session in every case.
        finally:
            session.close()

        return definition

# ################################################################################################################################

    def get(self, definition_id:'int') -> 'RuleDefinitionRecord':
        """ Returns one definition by id.
        """
        # Load the definition through the shared cluster-aware query ..
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

        # .. start with the cluster and parent path every list uses ..
        query = select(rule_definition_table)
        cluster_condition = rule_definition_table.c.cluster_id == default_cluster_id
        query = query.where(cluster_condition)
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

    def archive(self, *, definition_id:'int', actor:'str') -> 'None':
        """ Makes a definition unavailable for new versions without deleting its history.
        """
        # Validate the actor before changing state ..
        require_text(actor, 'Archive actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Mark the current object inactive ..
                definition = get_definition(session, definition_id)
                now = utc_now()
                statement = update(rule_definition_table)
                id_condition = rule_definition_table.c.id == definition_id
                statement = statement.where(id_condition)
                statement = statement.values(is_active=False, updated_at=now)
                _ = session.execute(statement)

                # .. and preserve the state transition in the same commit.
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=definition.current_version,
                    event_type=Event_Type_Definition_Archived,
                    actor=actor,
                    payload=None,
                )

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################
# ################################################################################################################################
