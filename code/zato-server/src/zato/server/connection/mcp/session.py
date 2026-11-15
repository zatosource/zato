# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic
from uuid import uuid4

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import delete, func, or_, select, text, update

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import mcp_session_table
from zato.common.util.logging_ import count_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, strlist, strnone, strtuple

    any_ = any_
    Engine = Engine
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# Default session TTL in seconds (30 minutes)
_default_session_ttl = 1800

# Default absolute max session lifetime in seconds (24 hours)
_default_max_lifetime = 86400

# Default maximum sessions per sec_def per gateway
_default_max_sessions = 100

# Validation result constants
Session_Valid             = 'session_valid'
Session_Not_Found        = 'session_not_found'
Session_Expired          = 'session_expired'
Session_Invalid_Identity = 'session_invalid_identity'

# Error message when session cap is reached (logged server-side, not sent to client)
_message_session_limit_reached = 'Session limit reached for client'

# Prefix for all MCP session IDs
_session_id_prefix = 'mcp'

# On PostgreSQL, the sessions of one identity in one gateway are created one at a time under this advisory lock,
# so that the workers of the server never exceed the cap together.
_create_lock_statement = text('SELECT pg_advisory_xact_lock(hashtext(:lock_key))')

# ################################################################################################################################
# ################################################################################################################################

def remove_all_sessions(engine:'Engine') -> 'None':
    """ Removes the sessions of every gateway, which a server calls once at startup, before it forks its workers,
    because the times of a session are readings of the monotonic clock of the host that created it.
    """
    with engine.begin() as connection:
        _ = connection.execute(delete(mcp_session_table))

# ################################################################################################################################
# ################################################################################################################################

class MCPSessionManager:
    """ Manages the MCP sessions of one gateway in the session table of the pub/sub database,
    which every worker process of the server shares.
    Sessions are created on initialize, validated on every subsequent request,
    and cleaned up when deleted or after TTL expiry.
    """

    def __init__(
        self,
        gateway_name:'str',
        ttl:'int' = _default_session_ttl,
        max_lifetime:'int' = _default_max_lifetime,
        max_sessions:'int' = _default_max_sessions,
        ) -> 'None':
        self.gateway_name = gateway_name
        self.ttl          = ttl
        self.max_lifetime = max_lifetime
        self.max_sessions = max_sessions

# ################################################################################################################################

    def _is_live(self, now:'float') -> 'any_':
        """ Returns the condition that a session is neither idle beyond the TTL nor past the absolute max lifetime.
        """
        idle_since = now - self.ttl
        created_since = now - self.max_lifetime

        out = (mcp_session_table.c.last_seen_at >= idle_since) & (mcp_session_table.c.created_at >= created_since)
        return out

# ################################################################################################################################

    def _insert_session(self, engine:'Engine', session_id:'str', protocol_version:'str', identity:'str') -> 'bool':
        """ Inserts a session unless the identity has reached its cap, counting and inserting in one transaction,
        and returns whether it inserted it.
        """
        with engine.begin() as connection:

            # Concurrent creations for the same identity wait for one another on PostgreSQL,
            # while on SQLite each worker writes the file in its turn ..
            if connection.dialect.name == Type_PostgreSQL:
                lock_key = f'{self.gateway_name}:{identity}'
                _ = connection.execute(_create_lock_statement, {'lock_key': lock_key})

            # .. count how many live sessions this identity already owns, an expired session awaiting the reaper
            # taking no place ..
            now = monotonic()

            count_query = select(func.count()).select_from(mcp_session_table)
            count_query = count_query.where(mcp_session_table.c.gateway_name == self.gateway_name)
            count_query = count_query.where(mcp_session_table.c.identity == identity)
            count_query = count_query.where(self._is_live(now))

            identity_count = connection.execute(count_query).scalar_one()

            # .. reject if the cap is reached ..
            if identity_count >= self.max_sessions:
                return False

            # .. and register the session.
            insert_statement = mcp_session_table.insert().values(
                session_id=session_id,
                gateway_name=self.gateway_name,
                identity=identity,
                protocol_version=protocol_version,
                created_at=now,
                last_seen_at=now,
            )
            _ = connection.execute(insert_statement)

        return True

# ################################################################################################################################

    def create(self, protocol_version:'str', identity:'str', remote_address:'str' = '') -> 'str':
        """ Creates a new session and returns its ID.
        Raises ValueError if the per-identity session cap has been reached -
        only live sessions count against it, never expired ones the reaper
        has not swept yet.
        """

        # Build a unique prefixed ID ..
        session_uuid = uuid4()
        unique_id = session_uuid.hex
        session_id = f'{_session_id_prefix}{unique_id}'

        # .. register the session in the table ..
        engine = get_pubsub_engine()
        is_created = call_database(engine, self._insert_session, engine, session_id, protocol_version, identity)

        # .. unless the cap is reached ..
        if not is_created:
            raise ValueError(_message_session_limit_reached)

        logger.info('MCP: Created session `%s` (remote_addr: %s)', session_id, remote_address)

        # .. and return the session ID to the caller.
        return session_id

# ################################################################################################################################

    def _validate(self, engine:'Engine', session_id:'str', identity:'str') -> 'strtuple':
        """ Returns a validation result constant with the identity that owns the session, and touches a live session.
        """
        with engine.begin() as connection:

            query = select(mcp_session_table.c.identity, mcp_session_table.c.created_at, mcp_session_table.c.last_seen_at)
            query = query.where(mcp_session_table.c.session_id == session_id)
            query = query.where(mcp_session_table.c.gateway_name == self.gateway_name)

            # If the session does not exist, it is unknown ..
            if not (row := connection.execute(query).first()):
                return Session_Not_Found, ''

            # .. reject if the session belongs to a different identity ..
            if row.identity != identity:
                return Session_Invalid_Identity, row.identity

            now = monotonic()

            # .. reject if the session has exceeded the absolute max lifetime ..
            lifetime = now - row.created_at

            if lifetime > self.max_lifetime:
                return Session_Expired, row.identity

            # .. reject if the session has been idle longer than the TTL ..
            idle_time = now - row.last_seen_at

            if idle_time > self.ttl:
                return Session_Expired, row.identity

            # .. the session is alive, refresh its last-seen timestamp.
            touch_statement = update(mcp_session_table)
            touch_statement = touch_statement.where(mcp_session_table.c.session_id == session_id)
            touch_statement = touch_statement.values(last_seen_at=now)

            _ = connection.execute(touch_statement)

        return Session_Valid, row.identity

# ################################################################################################################################

    def validate(self, session_id:'str', identity:'str') -> 'str':
        """ Returns a validation result constant indicating the session state.
        Touching a live session updates its last_seen_at timestamp.
        Ownership is always enforced - a session is only valid for the identity that created it.
        """
        engine = get_pubsub_engine()
        out, owner = call_database(engine, self._validate, engine, session_id, identity)

        if out == Session_Invalid_Identity:
            logger.info('MCP: Session `%s` owned by `%s`, caller is `%s`', session_id, owner, identity)

        return out

# ################################################################################################################################

    def _get_protocol_version(self, engine:'Engine', session_id:'str') -> 'strnone':
        query = select(mcp_session_table.c.protocol_version)
        query = query.where(mcp_session_table.c.session_id == session_id)
        query = query.where(mcp_session_table.c.gateway_name == self.gateway_name)

        with engine.connect() as connection:
            out = connection.execute(query).scalar()

        return out

# ################################################################################################################################

    def get_protocol_version(self, session_id:'str') -> 'strnone':
        """ Returns the protocol version negotiated for a session, or None if unknown.
        """
        engine = get_pubsub_engine()
        out = call_database(engine, self._get_protocol_version, engine, session_id)

        return out

# ################################################################################################################################

    def _delete(self, engine:'Engine', session_id:'str') -> 'int':
        statement = delete(mcp_session_table)
        statement = statement.where(mcp_session_table.c.session_id == session_id)
        statement = statement.where(mcp_session_table.c.gateway_name == self.gateway_name)

        with engine.begin() as connection:
            result = connection.execute(statement)

        out = result.rowcount
        return out

# ################################################################################################################################

    def delete(self, session_id:'str') -> 'bool':
        """ Deletes a session. Returns True if it existed, False otherwise.
        """
        engine = get_pubsub_engine()
        deleted_count = call_database(engine, self._delete, engine, session_id)

        # If the session existed, it is now removed from the table ..
        if deleted_count:
            logger.info('MCP: Deleted session `%s`', session_id)
            return True

        # .. otherwise there was nothing to delete.
        return False

# ################################################################################################################################

    def _delete_expired(self, engine:'Engine') -> 'strlist':
        """ Deletes the sessions that are idle beyond the TTL or past the absolute max lifetime and returns their IDs.
        """
        now = monotonic()
        idle_since = now - self.ttl
        created_since = now - self.max_lifetime

        is_expired = or_(mcp_session_table.c.last_seen_at < idle_since, mcp_session_table.c.created_at < created_since)

        query = select(mcp_session_table.c.session_id)
        query = query.where(mcp_session_table.c.gateway_name == self.gateway_name)
        query = query.where(is_expired)

        with engine.begin() as connection:
            out = list(connection.execute(query).scalars())

            if out:
                statement = delete(mcp_session_table)
                statement = statement.where(mcp_session_table.c.session_id.in_(out))
                _ = connection.execute(statement)

        return out

# ################################################################################################################################

    def cleanup_expired(self) -> 'int':
        """ Removes sessions that are idle beyond the TTL or past the absolute max lifetime.
        Returns the number of sessions removed.
        """
        engine = get_pubsub_engine()
        expired:'strlist' = call_database(engine, self._delete_expired, engine)

        for session_id in expired:
            logger.info('MCP: Expired session `%s`', session_id)

        out = len(expired)
        return out

# ################################################################################################################################

    def _count_sessions(self, engine:'Engine') -> 'int':
        query = select(func.count()).select_from(mcp_session_table)
        query = query.where(mcp_session_table.c.gateway_name == self.gateway_name)

        with engine.connect() as connection:
            out = connection.execute(query).scalar_one()

        return out

# ################################################################################################################################

    @property
    def session_count(self) -> 'int':
        """ Returns the number of sessions of the gateway in every worker process.
        """
        engine = get_pubsub_engine()
        out = call_database(engine, self._count_sessions, engine)

        return out
# ################################################################################################################################
# ################################################################################################################################

# Default interval between reaper sweeps in seconds (60 seconds)
_default_reaper_interval = 60

# ################################################################################################################################
# ################################################################################################################################

class MCPSessionReaper:
    """ Periodically sweeps all MCP gateway session managers to remove expired sessions.
    One instance per server process, spawned as a gevent greenlet after MCP gateways are built.
    """

    def __init__(self, gateway_mcp_dict:'anydict', interval:'int' = _default_reaper_interval) -> 'None':
        self.gateway_mcp_dict = gateway_mcp_dict
        self.interval = interval
        self.keep_running = True

# ################################################################################################################################

    def run(self) -> 'None':
        """ Main loop - sleeps between sweeps and calls cleanup_expired on every session manager.
        """

        # Sleep for the configured interval between sweeps ..
        while self.keep_running:
            sleep(self.interval)

            # .. check again after waking up in case stop() was called during sleep ..
            if not self.keep_running:
                break

            # .. and run the sweep.
            self._sweep()

# ################################################################################################################################

    def _sweep(self) -> 'None':
        """ Iterates over all MCP gateway wrappers and cleans up expired sessions.
        """

        # Walk each gateway config, reaching the wrapper through its .conn attribute ..
        for gateway_config in self.gateway_mcp_dict.values():

            wrapper = gateway_config.conn

            # .. skip gateways that were deleted mid-sweep and have no handler anymore ..
            handler = wrapper.handler

            if handler is None:
                continue

            # .. run cleanup on the gateway's session manager ..
            session_manager = handler.session_manager
            removed = session_manager.cleanup_expired()

            # .. log how many were removed, if any.
            if removed:
                gateway_name = wrapper.config.name
                removed_count_text = count_text(removed, 'expired session', 'expired sessions')
                logger.info('MCP: Reaper removed %s from gateway `%s`', removed_count_text, gateway_name)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Signals the reaper loop to exit.
        """

        self.keep_running = False

# ################################################################################################################################
# ################################################################################################################################
