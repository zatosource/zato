# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from logging import getLogger
from time import monotonic
from uuid import uuid4

# gevent
from gevent import sleep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# Default session TTL in seconds (30 minutes)
_default_session_ttl = 1800

# Default absolute max session lifetime in seconds (24 hours)
_default_max_lifetime = 86400

# Prefix for all MCP session IDs
_session_id_prefix = 'mcp'

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass(init=False)
class MCPSession:
    """ Holds state for a single MCP session.
    """
    session_id:       'str'
    created_at:       'float'
    last_seen_at:     'float'
    protocol_version: 'str'

# ################################################################################################################################
# ################################################################################################################################

# Type alias for the session store
session_dict = dict[str, MCPSession]

# ################################################################################################################################
# ################################################################################################################################

class MCPSessionManager:
    """ Manages MCP sessions in memory.
    Sessions are created on initialize, validated on every subsequent request,
    and cleaned up when deleted or after TTL expiry.
    """

    def __init__(self, ttl:'int' = _default_session_ttl, max_lifetime:'int' = _default_max_lifetime) -> 'None':
        self.ttl = ttl
        self.max_lifetime = max_lifetime
        self._sessions:'session_dict' = {}

# ################################################################################################################################

    def create(self, protocol_version:'str', remote_address:'str' = '') -> 'str':
        """ Creates a new session and returns its ID.
        """

        # Build a new session object with a unique prefixed ID ..
        session = MCPSession()

        unique_id = uuid4().hex
        session.session_id = f'{_session_id_prefix}{unique_id}'
        session.protocol_version = protocol_version

        # .. record the creation time ..
        now = monotonic()
        session.created_at   = now
        session.last_seen_at = now

        # .. register it in the session store ..
        self._sessions[session.session_id] = session

        logger.info('MCP: Created session `%s` (remote_addr: %s)', session.session_id, remote_address)

        # .. and return the session ID to the caller.
        out = session.session_id
        return out

# ################################################################################################################################

    def validate(self, session_id:'str') -> 'bool':
        """ Returns True if the session is alive, False otherwise.
        A session is dead if it does not exist, has been idle longer than the TTL,
        or has exceeded the absolute max lifetime since creation.
        Touching a live session updates its last_seen_at timestamp.
        """

        # If the session does not exist, it is unknown ..
        if not (session := self._sessions.get(session_id)):
            return False

        now = monotonic()

        # .. reject if the session has exceeded the absolute max lifetime ..
        lifetime = now - session.created_at

        if lifetime > self.max_lifetime:
            return False

        # .. reject if the session has been idle longer than the TTL ..
        idle_time = now - session.last_seen_at

        if idle_time > self.ttl:
            return False

        # .. the session is alive, refresh its last-seen timestamp.
        session.last_seen_at = now
        return True

# ################################################################################################################################

    def get_protocol_version(self, session_id:'str') -> 'strnone':
        """ Returns the protocol version negotiated for a session, or None if unknown.
        """

        # Look up the session, returning its negotiated version when present ..
        if session := self._sessions.get(session_id):
            return session.protocol_version

        # .. otherwise the session is unknown.
        return None

# ################################################################################################################################

    def delete(self, session_id:'str') -> 'bool':
        """ Deletes a session. Returns True if it existed, False otherwise.
        """

        # If the session exists, remove it from the store ..
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info('MCP: Deleted session `%s`', session_id)
            return True

        # .. otherwise there is nothing to delete.
        return False

# ################################################################################################################################

    def cleanup_expired(self) -> 'int':
        """ Removes sessions that are idle beyond the TTL or past the absolute max lifetime.
        Returns the number of sessions removed.
        """

        # Collect session IDs that have exceeded the idle TTL or the max lifetime ..
        now = monotonic()
        expired:'strlist' = []

        for session_id, session in self._sessions.items():

            idle_time = now - session.last_seen_at
            lifetime = now - session.created_at

            if idle_time > self.ttl or lifetime > self.max_lifetime:
                expired.append(session_id)

        # .. remove each expired session from the store ..
        for session_id in expired:
            del self._sessions[session_id]
            logger.info('MCP: Expired session `%s`', session_id)

        # .. and return how many were cleaned up.
        out = len(expired)
        return out

# ################################################################################################################################

    @property
    def session_count(self) -> 'int':
        """ Returns the number of active sessions.
        """

        out = len(self._sessions)
        return out

# ################################################################################################################################
# ################################################################################################################################

# Default interval between reaper sweeps in seconds (60 seconds)
_default_reaper_interval = 60

# ################################################################################################################################
# ################################################################################################################################

class MCPSessionReaper:
    """ Periodically sweeps all MCP channel session managers to remove expired sessions.
    One instance per server process, spawned as a gevent greenlet after MCP channels are built.
    """

    def __init__(self, channel_mcp_dict:'anydict', interval:'int' = _default_reaper_interval) -> 'None':
        self.channel_mcp_dict = channel_mcp_dict
        self.interval = interval
        self.keep_running = True

# ################################################################################################################################

    def run(self) -> 'None':
        """ Main loop - sleeps between sweeps and calls cleanup_expired on every session manager.
        """

        while self.keep_running:
            sleep(self.interval)

            if not self.keep_running:
                break

            self._sweep()

# ################################################################################################################################

    def _sweep(self) -> 'None':
        """ Iterates over all MCP channel wrappers and cleans up expired sessions.
        """

        for wrapper in self.channel_mcp_dict.values():
            session_manager = wrapper.handler.session_manager
            removed = session_manager.cleanup_expired()

            if removed:
                logger.info('MCP: Reaper removed %d expired session(s) from channel `%s`', removed, wrapper.config.name)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Signals the reaper loop to exit.
        """

        self.keep_running = False

# ################################################################################################################################
# ################################################################################################################################
