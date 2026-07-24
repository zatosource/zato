# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Chat_Kinds, Delivery_Status_Delivered, Delivery_Status_Error
from .data import anydict, chat_config_record_list, destination_record_list, RuleChatConfigRecord, \
    RuleNotifyDestinationRecord
from .database import SessionFactory
from .errors import InvalidStoreInputError, RecordNotFoundError
from .records import chat_config_record, destination_record, job_cursor_record
from .schema import rule_chat_config_table, rule_event_table, rule_job_cursor_table, rule_notify_destination_table
from .store_common import get_definition, require_text
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

def _require_kind(kind:'str') -> 'None':
    """ Rejects a chat platform this store does not know.
    """
    if kind not in Chat_Kinds:
        message = f'Unknown chat kind -> {kind}'
        raise InvalidStoreInputError(message)

# ################################################################################################################################
# ################################################################################################################################

class NotificationStore:
    """ Chat credentials, per-ruleset notification destinations and named job cursors.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def set_chat_config(self, *, kind:'str', payload:'str', actor:'str') -> 'None':
        """ Stores or replaces one chat platform's already-encrypted credentials payload.
        """
        # Validate the identity fields before opening a transaction ..
        _require_kind(kind)
        require_text(payload, 'Chat config payload')
        require_text(actor, 'Chat config actor')
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Look for the platform's current row ..
                query = select(rule_chat_config_table.c.id)
                cluster_condition = rule_chat_config_table.c.cluster_id == default_cluster_id
                kind_condition = rule_chat_config_table.c.kind == kind
                query = query.where(cluster_condition)
                query = query.where(kind_condition)
                result = session.execute(query)
                row = result.one_or_none()

                # .. replace the payload in place when it exists ..
                if row:
                    statement = update(rule_chat_config_table)
                    id_condition = rule_chat_config_table.c.id == row.id
                    statement = statement.where(id_condition)
                    statement = statement.values(payload=payload, updated_at=now, updated_by=actor)
                    _ = session.execute(statement)

                # .. or create the platform's first row.
                else:
                    values = {
                        'cluster_id': default_cluster_id,
                        'kind':       kind,
                        'payload':    payload,
                        'updated_at': now,
                        'updated_by': actor,
                    }
                    statement = insert(rule_chat_config_table)
                    _ = session.execute(statement, values)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def get_chat_config(self, kind:'str') -> 'RuleChatConfigRecord | None':
        """ Returns one chat platform's credentials row or None when the platform is not configured.
        """
        # Validate the platform before querying ..
        _require_kind(kind)

        query = select(rule_chat_config_table)
        cluster_condition = rule_chat_config_table.c.cluster_id == default_cluster_id
        kind_condition = rule_chat_config_table.c.kind == kind
        query = query.where(cluster_condition)
        query = query.where(kind_condition)
        session = self._session_factory()

        # .. load the optional row ..
        try:
            result = session.execute(query)
            row = result.one_or_none()

            if row:
                out = chat_config_record(row)
            else:
                out = None

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list_chat_configs(self) -> 'chat_config_record_list':
        """ Returns every configured chat platform's credentials row.
        """
        query = select(rule_chat_config_table)
        cluster_condition = rule_chat_config_table.c.cluster_id == default_cluster_id
        query = query.where(cluster_condition)
        session = self._session_factory()

        # Load every configured platform ..
        try:
            result = session.execute(query)
            out:'chat_config_record_list' = []

            for row in result:
                record = chat_config_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def add_destination(
        self,
        *,
        definition_id:'int',
        kind:'str',
        target:'str',
        actor:'str',
        ) -> 'RuleNotifyDestinationRecord':
        """ Adds one destination to one ruleset, its cursor starting at the current end of the feed.
        """
        # Validate the identity fields before opening a transaction ..
        _require_kind(kind)
        require_text(target, 'Destination target')
        require_text(actor, 'Destination actor')
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the parent exists inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. new destinations only hear about changes made after they were added,
                # .. so the cursor starts at the newest event already in the feed ..
                cursor_id = _newest_event_id(session)

                # .. and insert the destination row.
                values = {
                    'cluster_id':       default_cluster_id,
                    'definition_id':    definition_id,
                    'kind':             kind,
                    'target':           target,
                    'is_active':        True,
                    'cursor_id':        cursor_id,
                    'last_status':      None,
                    'last_error':       None,
                    'last_delivery_at': None,
                    'created_at':       now,
                    'created_by':       actor,
                }
                statement = insert(rule_notify_destination_table)
                result = session.execute(statement, values)
                result = cast_(CursorResult, result)
                primary_key = result.inserted_primary_key
                destination_id = primary_key[0]

                out = RuleNotifyDestinationRecord(
                    id=destination_id,
                    cluster_id=default_cluster_id,
                    definition_id=definition_id,
                    kind=kind,
                    target=target,
                    is_active=True,
                    cursor_id=cursor_id,
                    last_status=None,
                    last_error=None,
                    last_delivery_at=None,
                    created_at=now,
                    created_by=actor,
                )

        # Translate a duplicate destination into a domain error ..
        except IntegrityError as e:
            message = f'Destination `{target}` ({kind}) already exists for rule definition {definition_id}'
            raise InvalidStoreInputError(message) from e

        # .. and release the session in every case.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def list_destinations(
        self,
        *,
        definition_id:'int | None' = None,
        include_inactive:'bool' = False,
        ) -> 'destination_record_list':
        """ Returns destinations, all of them or one ruleset's.
        """
        # Start with the cluster every list uses ..
        query = select(rule_notify_destination_table)
        cluster_condition = rule_notify_destination_table.c.cluster_id == default_cluster_id
        query = query.where(cluster_condition)

        # .. add the optional parent filter ..
        if definition_id is not None:
            parent_condition = rule_notify_destination_table.c.definition_id == definition_id
            query = query.where(parent_condition)

        if not include_inactive:
            active_condition = rule_notify_destination_table.c.is_active.is_(True)
            query = query.where(active_condition)

        # .. apply stable ordering ..
        query = query.order_by(rule_notify_destination_table.c.id)
        session = self._session_factory()

        # .. load every matching destination ..
        try:
            result = session.execute(query)
            out:'destination_record_list' = []

            for row in result:
                record = destination_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def delete_destination(self, destination_id:'int') -> 'None':
        """ Removes one destination together with its cursor and delivery status.
        """
        statement = delete(rule_notify_destination_table)
        cluster_condition = rule_notify_destination_table.c.cluster_id == default_cluster_id
        id_condition = rule_notify_destination_table.c.id == destination_id
        statement = statement.where(cluster_condition)
        statement = statement.where(id_condition)
        session = self._session_factory()

        # Delete the row inside one transaction ..
        try:
            with session.begin():
                result = session.execute(statement)
                result = cast_(CursorResult, result)

                # .. deleting a destination that does not exist is an error worth reporting.
                if result.rowcount != 1:
                    message = f'No such notification destination -> {destination_id}'
                    raise RecordNotFoundError(message)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def mark_delivered(self, destination_id:'int', event_id:'int') -> 'None':
        """ Moves one destination's cursor past a delivered event and records the success.
        """
        now = utc_now()
        values = {
            'cursor_id':        event_id,
            'last_status':      Delivery_Status_Delivered,
            'last_error':       None,
            'last_delivery_at': now,
        }

        self._update_destination(destination_id, values)

# ################################################################################################################################

    def advance_cursor(self, destination_id:'int', event_id:'int') -> 'None':
        """ Moves one destination's cursor past an event that produced no message,
        leaving the delivery status untouched.
        """
        values = {
            'cursor_id': event_id,
        }

        self._update_destination(destination_id, values)

# ################################################################################################################################

    def mark_failed(self, destination_id:'int', error:'str') -> 'None':
        """ Records a delivery failure without moving the cursor, so the next pass retries.
        """
        values = {
            'last_status': Delivery_Status_Error,
            'last_error':  error,
        }

        self._update_destination(destination_id, values)

# ################################################################################################################################

    def _update_destination(self, destination_id:'int', values:'anydict') -> 'None':
        """ Applies one set of delivery-state values to one destination row.
        """
        statement = update(rule_notify_destination_table)
        cluster_condition = rule_notify_destination_table.c.cluster_id == default_cluster_id
        id_condition = rule_notify_destination_table.c.id == destination_id
        statement = statement.where(cluster_condition)
        statement = statement.where(id_condition)
        statement = statement.values(**values)
        session = self._session_factory()

        # Apply the update inside one transaction ..
        try:
            with session.begin():
                _ = session.execute(statement)

        # .. and release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def get_job_cursor(self, name:'str') -> 'int':
        """ Returns a named job's feed position, 0 when the job has never run.
        """
        query = select(rule_job_cursor_table)
        cluster_condition = rule_job_cursor_table.c.cluster_id == default_cluster_id
        name_condition = rule_job_cursor_table.c.name == name
        query = query.where(cluster_condition)
        query = query.where(name_condition)
        session = self._session_factory()

        # Load the optional cursor row ..
        try:
            result = session.execute(query)
            row = result.one_or_none()

            if row:
                record = job_cursor_record(row)
                out = record.last_id
            else:
                out = 0

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def set_job_cursor(self, name:'str', last_id:'int') -> 'None':
        """ Stores a named job's feed position.
        """
        # Validate the cursor name before opening a transaction ..
        require_text(name, 'Job cursor name')
        now = utc_now()
        session = self._session_factory()

        try:
            with session.begin():

                # Look for the job's current position ..
                query = select(rule_job_cursor_table.c.id)
                cluster_condition = rule_job_cursor_table.c.cluster_id == default_cluster_id
                name_condition = rule_job_cursor_table.c.name == name
                query = query.where(cluster_condition)
                query = query.where(name_condition)
                result = session.execute(query)
                row = result.one_or_none()

                # .. move it in place when it exists ..
                if row:
                    statement = update(rule_job_cursor_table)
                    id_condition = rule_job_cursor_table.c.id == row.id
                    statement = statement.where(id_condition)
                    statement = statement.values(last_id=last_id, updated_at=now)
                    _ = session.execute(statement)

                # .. or create the job's first position row.
                else:
                    values = {
                        'cluster_id': default_cluster_id,
                        'name':       name,
                        'last_id':    last_id,
                        'updated_at': now,
                    }
                    statement = insert(rule_job_cursor_table)
                    _ = session.execute(statement, values)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################
# ################################################################################################################################

def _newest_event_id(session:'Session') -> 'int':
    """ Returns the newest event id in the caller's transaction, 0 for an empty feed.
    """
    query = select(func.max(rule_event_table.c.id))
    cluster_condition = rule_event_table.c.cluster_id == default_cluster_id
    query = query.where(cluster_condition)
    result = session.execute(query)
    newest_id = result.scalar()

    # An empty feed has no maximum id.
    if newest_id is None:
        out = 0
    else:
        out = newest_id

    return out

# ################################################################################################################################
# ################################################################################################################################
