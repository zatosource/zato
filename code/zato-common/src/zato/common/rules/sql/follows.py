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
from .constants import Default_Feed_Limit, Event_Type_Follow_Changed
from .data import event_record_list, follow_record_list, RuleEventRecord, RuleFollowRecord
from .database import SessionFactory
from .errors import InvalidStoreInputError, RecordNotFoundError
from .records import event_record, follow_record
from .schema import rule_event_table, rule_follow_table
from .store_common import add_event, get_definition, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

def _get_follow(session:'Session', actor:'str', definition_id:'int') -> 'RuleFollowRecord | None':
    """ Returns one follow row in the caller's transaction, or None when the actor does not follow.
    """
    # Query the one promoted follow identity ..
    query = select(rule_follow_table)
    cluster_condition = rule_follow_table.c.cluster_id == default_cluster_id
    actor_condition = rule_follow_table.c.actor == actor
    definition_condition = rule_follow_table.c.definition_id == definition_id
    query = query.where(cluster_condition)
    query = query.where(actor_condition)
    query = query.where(definition_condition)
    result = session.execute(query)
    row = result.one_or_none()

    # .. and convert the row when the actor follows the definition.
    if row:
        out = follow_record(row)
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

class FollowStore:
    """ Which actors follow which definitions and what changed since they last looked.

    Following starts the clock - the feed returns only events newer than the follow's
    last-seen timestamp, and marking a definition seen moves that clock forward.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def follow(self, *, actor:'str', definition_id:'int') -> 'RuleFollowRecord':
        """ Starts following one definition, appending the change to its activity feed.
        """
        # Validate the actor before any database work ..
        require_text(actor, 'Follow actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the definition exists inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. following twice is the same follow, with its original clock ..
                existing = _get_follow(session, actor, definition_id)

                if existing:
                    out = existing

                else:
                    # .. store the follow with its clock starting now ..
                    now = utc_now()
                    values = {
                        'cluster_id':    default_cluster_id,
                        'definition_id': definition_id,
                        'actor':         actor,
                        'created_at':    now,
                        'last_seen_at':  now,
                    }
                    statement = insert(rule_follow_table)
                    result = session.execute(statement, values)
                    result = cast_(CursorResult, result)
                    primary_key = result.inserted_primary_key
                    follow_id = primary_key[0]

                    # .. record the change in the activity feed in the same commit ..
                    payload = {'following': True}
                    _ = add_event(
                        session,
                        definition_id=definition_id,
                        version=None,
                        event_type=Event_Type_Follow_Changed,
                        actor=actor,
                        payload=payload,
                    )

                    # .. and build the detached record from the values just written.
                    out = RuleFollowRecord(
                        id=follow_id,
                        cluster_id=default_cluster_id,
                        definition_id=definition_id,
                        actor=actor,
                        created_at=now,
                        last_seen_at=now,
                    )

        # Release the transactional session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def unfollow(self, *, actor:'str', definition_id:'int') -> 'None':
        """ Stops following one definition, appending the change to its activity feed.
        """
        # Validate the actor before any database work ..
        require_text(actor, 'Follow actor')
        session = self._session_factory()

        try:
            with session.begin():

                # A follow that does not exist cannot be removed - name it directly ..
                existing = _get_follow(session, actor, definition_id)

                if existing is None:
                    message = f'Actor {actor} does not follow definition {definition_id}'
                    raise RecordNotFoundError(message)

                # .. remove the one follow row ..
                statement = delete(rule_follow_table)
                id_condition = rule_follow_table.c.id == existing.id
                statement = statement.where(id_condition)
                _ = session.execute(statement)

                # .. and record the change in the activity feed in the same commit.
                payload = {'following': False}
                _ = add_event(
                    session,
                    definition_id=definition_id,
                    version=None,
                    event_type=Event_Type_Follow_Changed,
                    actor=actor,
                    payload=payload,
                )

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def is_following(self, *, actor:'str', definition_id:'int') -> 'bool':
        """ Returns whether one actor follows one definition.
        """
        session = self._session_factory()

        try:
            existing = _get_follow(session, actor, definition_id)
        finally:
            session.close()

        out = existing is not None
        return out

# ################################################################################################################################

    def list_followed(self, actor:'str') -> 'follow_record_list':
        """ Returns everything one actor follows.
        """
        # Validate the actor before constructing the query ..
        require_text(actor, 'Follow actor')

        # .. ask for the actor's complete follow list ..
        query = select(rule_follow_table)
        cluster_condition = rule_follow_table.c.cluster_id == default_cluster_id
        actor_condition = rule_follow_table.c.actor == actor
        query = query.where(cluster_condition)
        query = query.where(actor_condition)
        query = query.order_by(rule_follow_table.c.definition_id)
        session = self._session_factory()

        # .. load every follow ..
        try:
            result = session.execute(query)
            out:'follow_record_list' = []

            for row in result:
                record = follow_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def mark_seen(self, *, actor:'str', definition_id:'int') -> 'None':
        """ Moves one follow's clock forward to now, emptying its feed of past events.
        """
        # Validate the actor before any database work ..
        require_text(actor, 'Follow actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Move the clock on the one promoted follow identity ..
                now = utc_now()
                statement = update(rule_follow_table)
                cluster_condition = rule_follow_table.c.cluster_id == default_cluster_id
                actor_condition = rule_follow_table.c.actor == actor
                definition_condition = rule_follow_table.c.definition_id == definition_id
                statement = statement.where(cluster_condition)
                statement = statement.where(actor_condition)
                statement = statement.where(definition_condition)
                statement = statement.values(last_seen_at=now)
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                # .. a follow that does not exist has no clock to move - name it directly.
                if result.rowcount != 1:
                    message = f'Actor {actor} does not follow definition {definition_id}'
                    raise RecordNotFoundError(message)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def feed(self, actor:'str', limit:'int' = Default_Feed_Limit) -> 'event_record_list':
        """ Returns the newest events on followed definitions since each follow was last seen.
        """
        # Validate pagination before any database work ..
        if limit < 1:
            raise InvalidStoreInputError('Feed limit must be at least 1')

        # .. resolve what the actor follows and each follow's clock ..
        follows = self.list_followed(actor)
        collected:'event_record_list' = []
        session = self._session_factory()

        try:
            for follow in follows:

                # .. each followed definition contributes only events newer than its clock ..
                query = select(rule_event_table)
                cluster_condition = rule_event_table.c.cluster_id == default_cluster_id
                definition_condition = rule_event_table.c.definition_id == follow.definition_id
                seen_condition = rule_event_table.c.created_at > follow.last_seen_at
                query = query.where(cluster_condition)
                query = query.where(definition_condition)
                query = query.where(seen_condition)
                event_id_descending = rule_event_table.c.id.desc()
                query = query.order_by(event_id_descending)
                query = query.limit(limit)
                result = session.execute(query)

                for row in result:
                    record = event_record(row)
                    collected.append(record)

        # Release the read-only session in every case.
        finally:
            session.close()

        # Merge every definition's events into one page, newest first.
        def _event_id(record:'RuleEventRecord') -> 'int':
            return record.id

        collected.sort(key=_event_id, reverse=True)

        out = collected[:limit]
        return out

# ################################################################################################################################
# ################################################################################################################################
