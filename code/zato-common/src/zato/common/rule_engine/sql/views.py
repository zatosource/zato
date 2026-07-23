# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import CursorResult

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Default_Recent_Limit
from .data import anydict, recent_record_list, RuleViewRecord, view_record_list
from .database import SessionFactory
from .document import serialize_document
from .errors import InvalidStoreInputError, RecordNotFoundError
from .records import recent_record, view_record
from .schema import rule_recent_table, rule_view_table
from .store_common import get_definition, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

def _get_view(session:'Session', actor:'str', name:'str') -> 'RuleViewRecord | None':
    """ Returns one saved view in the caller's transaction, or None when the actor has no such view.
    """
    # Query the one promoted view identity ..
    query = select(rule_view_table)
    cluster_condition = rule_view_table.c.cluster_id == default_cluster_id
    actor_condition = rule_view_table.c.actor == actor
    name_condition = rule_view_table.c.name == name
    query = query.where(cluster_condition)
    query = query.where(actor_condition)
    query = query.where(name_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. and convert the row when the view exists.
    if row:
        out = view_record(row)
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

class ViewStore:
    """ Saved views and recently visited definitions, per actor.

    A saved view is a named filter payload the rulesets home screen can re-apply,
    and recents remember which definitions an actor visited, newest first.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def save(self, *, actor:'str', name:'str', payload:'anydict') -> 'RuleViewRecord':
        """ Creates one saved view or replaces the payload of an existing one.
        """
        # Validate identity fields and serialize the payload before any database work ..
        require_text(actor, 'View actor')
        require_text(name, 'View name')
        payload_text = serialize_document(payload)
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Saving over an existing name replaces its payload ..
                existing = _get_view(session, actor, name)

                if existing:
                    statement = update(rule_view_table)
                    id_condition = rule_view_table.c.id == existing.id
                    statement = statement.where(id_condition)
                    statement = statement.values(payload=payload_text, updated_at=now)
                    _ = session.execute(statement)

                    # .. and the record keeps its original creation time.
                    out = RuleViewRecord(
                        id=existing.id,
                        cluster_id=default_cluster_id,
                        actor=actor,
                        name=name,
                        payload=payload_text,
                        created_at=existing.created_at,
                        updated_at=now,
                    )

                # .. while a new name stores a whole new view.
                else:
                    values = {
                        'cluster_id': default_cluster_id,
                        'actor':      actor,
                        'name':       name,
                        'payload':    payload_text,
                        'created_at': now,
                        'updated_at': now,
                    }
                    statement = insert(rule_view_table)
                    result = session.execute(statement, values)
                    result = cast_(CursorResult, result)
                    primary_key = result.inserted_primary_key
                    view_id = primary_key[0]

                    out = RuleViewRecord(
                        id=view_id,
                        cluster_id=default_cluster_id,
                        actor=actor,
                        name=name,
                        payload=payload_text,
                        created_at=now,
                        updated_at=now,
                    )

        # Release the transactional session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def get(self, *, actor:'str', name:'str') -> 'RuleViewRecord':
        """ Returns one saved view by its owner and name.
        """
        session = self._session_factory()

        try:
            existing = _get_view(session, actor, name)
        finally:
            session.close()

        # A view that does not exist is named directly, never returned as None.
        if existing is None:
            message = f'Actor {actor} has no saved view named `{name}`'
            raise RecordNotFoundError(message)

        out = existing
        return out

# ################################################################################################################################

    def list(self, actor:'str') -> 'view_record_list':
        """ Returns one actor's saved views, by name.
        """
        # Validate the actor before constructing the query ..
        require_text(actor, 'View actor')

        # .. ask for the actor's complete view list ..
        query = select(rule_view_table)
        cluster_condition = rule_view_table.c.cluster_id == default_cluster_id
        actor_condition = rule_view_table.c.actor == actor
        query = query.where(cluster_condition)
        query = query.where(actor_condition)
        query = query.order_by(rule_view_table.c.name)
        session = self._session_factory()

        # .. load every view ..
        try:
            result = session.execute(query)
            out:'view_record_list' = []

            for row in result:
                record = view_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def delete(self, *, actor:'str', name:'str') -> 'None':
        """ Deletes one saved view.
        """
        session = self._session_factory()

        try:
            with session.begin():

                # Remove the one promoted view identity ..
                statement = delete(rule_view_table)
                cluster_condition = rule_view_table.c.cluster_id == default_cluster_id
                actor_condition = rule_view_table.c.actor == actor
                name_condition = rule_view_table.c.name == name
                statement = statement.where(cluster_condition)
                statement = statement.where(actor_condition)
                statement = statement.where(name_condition)
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                # .. a view that does not exist cannot be deleted - name it directly.
                if result.rowcount != 1:
                    message = f'Actor {actor} has no saved view named `{name}`'
                    raise RecordNotFoundError(message)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def touch_recent(self, *, actor:'str', definition_id:'int') -> 'None':
        """ Records one actor's visit to one definition, moving it to the top of their recents.
        """
        # Validate the actor before any database work ..
        require_text(actor, 'Recent actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the definition exists inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. a repeat visit only moves its timestamp forward ..
                now = utc_now()
                statement = update(rule_recent_table)
                cluster_condition = rule_recent_table.c.cluster_id == default_cluster_id
                actor_condition = rule_recent_table.c.actor == actor
                definition_condition = rule_recent_table.c.definition_id == definition_id
                statement = statement.where(cluster_condition)
                statement = statement.where(actor_condition)
                statement = statement.where(definition_condition)
                statement = statement.values(visited_at=now)
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                # .. while a first visit stores the one row this pair will ever have.
                if result.rowcount == 0:
                    values = {
                        'cluster_id':    default_cluster_id,
                        'definition_id': definition_id,
                        'actor':         actor,
                        'visited_at':    now,
                    }
                    statement = insert(rule_recent_table)
                    _ = session.execute(statement, values)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def list_recents(self, actor:'str', limit:'int' = Default_Recent_Limit) -> 'recent_record_list':
        """ Returns one actor's recently visited definitions, newest first.
        """
        # Validate the actor and pagination before constructing the query ..
        require_text(actor, 'Recent actor')

        if limit < 1:
            raise InvalidStoreInputError('Recents limit must be at least 1')

        # .. ask for the newest visits first ..
        query = select(rule_recent_table)
        cluster_condition = rule_recent_table.c.cluster_id == default_cluster_id
        actor_condition = rule_recent_table.c.actor == actor
        query = query.where(cluster_condition)
        query = query.where(actor_condition)
        visited_descending = rule_recent_table.c.visited_at.desc()
        id_descending = rule_recent_table.c.id.desc()
        query = query.order_by(visited_descending, id_descending)
        query = query.limit(limit)
        session = self._session_factory()

        # .. load the page ..
        try:
            result = session.execute(query)
            out:'recent_record_list' = []

            for row in result:
                record = recent_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################
