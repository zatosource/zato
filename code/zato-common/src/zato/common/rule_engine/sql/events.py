# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.defaults import default_cluster_id

# Local
from .data import anydict, event_record_list, RuleEventRecord, strlist
from .database import SessionFactory
from .errors import InvalidStoreInputError
from .records import event_record
from .schema import rule_event_table
from .store_common import add_event, get_definition, require_text

# ################################################################################################################################
# ################################################################################################################################

class EventStore:
    """ Append-only review, state, publication, follow, test and activity events.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def append(
        self,
        *,
        definition_id:'int',
        version:'int | None',
        event_type:'str',
        actor:'str',
        payload:'anydict | None',
        ) -> 'RuleEventRecord':
        """ Appends one event after confirming that its parent definition exists.
        """
        # Validate the feed fields before opening a transaction ..
        require_text(event_type, 'Event type')
        require_text(actor, 'Event actor')
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the parent inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. and append the event as the transaction's only write.
                out = add_event(
                    session,
                    definition_id=definition_id,
                    version=version,
                    event_type=event_type,
                    actor=actor,
                    payload=payload,
                )

        # Release the transactional session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list(
        self,
        *,
        definition_id:'int | None' = None,
        before_id:'int | None' = None,
        limit:'int' = 100,
        ) -> 'event_record_list':
        """ Returns the newest feed events using keyset pagination.
        """
        # Validate pagination before constructing the query ..
        if limit < 1:
            raise InvalidStoreInputError('Event list limit must be at least 1')

        # .. start with the cluster shared by all feed views ..
        query = select(rule_event_table)
        cluster_condition = rule_event_table.c.cluster_id == default_cluster_id
        query = query.where(cluster_condition)

        # .. add the optional parent and keyset boundaries ..
        if definition_id is not None:
            definition_condition = rule_event_table.c.definition_id == definition_id
            query = query.where(definition_condition)

        if before_id is not None:
            id_condition = rule_event_table.c.id < before_id
            query = query.where(id_condition)

        # .. request one stable page from newest to oldest ..
        event_id_descending = rule_event_table.c.id.desc()
        query = query.order_by(event_id_descending)
        query = query.limit(limit)
        session = self._session_factory()

        # .. load the page ..
        try:
            result = session.execute(query)
            out:'event_record_list' = []

            for row in result:
                record = event_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list_since(
        self,
        *,
        since_id:'int',
        definition_id:'int | None' = None,
        event_types:'strlist | None' = None,
        limit:'int' = 100,
        ) -> 'event_record_list':
        """ Returns events newer than a cursor, oldest first, for forward-reading consumers.
        """
        # Validate pagination before constructing the query ..
        if limit < 1:
            raise InvalidStoreInputError('Event list limit must be at least 1')

        # .. start with the cluster shared by all feed views ..
        query = select(rule_event_table)
        cluster_condition = rule_event_table.c.cluster_id == default_cluster_id
        query = query.where(cluster_condition)

        # .. everything a consumer reads lies strictly past its cursor ..
        cursor_condition = rule_event_table.c.id > since_id
        query = query.where(cursor_condition)

        # .. add the optional parent and event-type filters ..
        if definition_id is not None:
            definition_condition = rule_event_table.c.definition_id == definition_id
            query = query.where(definition_condition)

        if event_types is not None:
            type_condition = rule_event_table.c.event_type.in_(event_types)
            query = query.where(type_condition)

        # .. request one stable page from oldest to newest ..
        event_id_ascending = rule_event_table.c.id.asc()
        query = query.order_by(event_id_ascending)
        query = query.limit(limit)
        session = self._session_factory()

        # .. load the page ..
        try:
            result = session.execute(query)
            out:'event_record_list' = []

            for row in result:
                record = event_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################
