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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# Default session TTL in seconds (30 minutes)
_default_session_ttl = 1800

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

    def __init__(self, ttl:'int' = _default_session_ttl) -> 'None':
        self.ttl = ttl
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
        """ Returns True if the session exists, False otherwise.
        Touching the session updates its last_seen_at timestamp.
        """

        # If the session exists, touch its timestamp and confirm ..
        if session := self._sessions.get(session_id):
            session.last_seen_at = monotonic()
            return True

        # .. otherwise the session is unknown.
        return False

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
        """ Removes sessions that have not been seen within the TTL.
        Returns the number of sessions removed.
        """

        # Collect session IDs that have exceeded the TTL ..
        now = monotonic()
        expired:'strlist' = []

        for session_id, session in self._sessions.items():
            age = now - session.last_seen_at

            if age > self.ttl:
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
