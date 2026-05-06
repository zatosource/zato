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

# Zato
from zato.common.typing_ import strlist

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
    session_id:     'str'
    created_at:     'float'
    last_seen_at:   'float'
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
    def __init__(self, ttl:'int'=_default_session_ttl) -> 'None':
        self.ttl = ttl
        self._sessions:'session_dict' = {}

# ################################################################################################################################

    def create(self, protocol_version:'str', remote_address:'str'='') -> 'str':
        """ Creates a new session and returns its ID.
        """

        session = MCPSession()
        session.session_id = f'{_session_id_prefix}{uuid4().hex}'
        session.protocol_version = protocol_version

        now = monotonic()
        session.created_at   = now
        session.last_seen_at = now

        self._sessions[session.session_id] = session

        logger.info('MCP: Created session `%s` (remote_addr: %s)', session.session_id, remote_address)

        out = session.session_id
        return out

# ################################################################################################################################

    def validate(self, session_id:'str') -> 'bool':
        """ Returns True if the session exists, False otherwise.
        Touching the session updates its last_seen_at timestamp.
        """

        if session := self._sessions.get(session_id):
            session.last_seen_at = monotonic()
            return True

        return False

# ################################################################################################################################

    def delete(self, session_id:'str') -> 'bool':
        """ Deletes a session. Returns True if it existed, False otherwise.
        """

        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info('MCP: Deleted session `%s`', session_id)
            return True

        return False

# ################################################################################################################################

    def cleanup_expired(self) -> 'int':
        """ Removes sessions that have not been seen within the TTL.
        Returns the number of sessions removed.
        """

        now = monotonic()
        expired:'strlist' = []

        for session_id, session in self._sessions.items():
            age = now - session.last_seen_at

            if age > self.ttl:
                expired.append(session_id)

        for session_id in expired:
            del self._sessions[session_id]
            logger.info('MCP: Expired session `%s`', session_id)

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
