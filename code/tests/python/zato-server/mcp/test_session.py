# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, NOT_FOUND, OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps
from zato.common.test import _test_sec_def_id
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_request, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager, MCPSessionReaper, \
    Session_Expired, Session_Invalid_Identity, Session_Not_Found, Session_Valid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strnone

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry for session tests.
    """
    def get_tools(self) -> 'anylist':
        return []

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return False

    def rebuild(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class _MockReaperConfig:
    """ Mock config object for reaper tests, carrying a channel name.
    """
    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class _MockReaperHandler:
    """ Mock handler for reaper tests, carrying a session manager.
    """
    def __init__(self, session_manager:'any_') -> 'None':
        self.session_manager = session_manager

# ################################################################################################################################
# ################################################################################################################################

class _MockReaperWrapper:
    """ Mock channel wrapper for reaper tests.
    """
    def __init__(self, session_manager:'any_', name:'str') -> 'None':
        self.handler = _MockReaperHandler(session_manager)
        self.config = _MockReaperConfig(name)

# ################################################################################################################################
# ################################################################################################################################

class _MockReaperChannelConfig:
    """ Mock channel config for reaper tests, exposing the wrapper via .conn.
    """
    def __init__(self, conn:'any_') -> 'None':
        self.conn = conn

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

def _invoke_noop(service_name:'str', payload:'anydict') -> 'anydict':
    return {}

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(session_manager:'any_'=None) -> 'MCPHandler':
    """ Creates an MCPHandler with a session manager for tests.
    """

    registry = _MockToolRegistry()

    if session_manager is None:
        session_manager = MCPSessionManager()

    out = MCPHandler(registry, _invoke_noop, session_manager) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################

# Standard params for initialize requests in tests
_initialize_params = {'protocolVersion': '2025-11-05', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1.0'}}

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerCreate(TestCase):

    def test_create_returns_session_id(self) -> 'None':

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)

    def test_create_increments_count(self) -> 'None':

        manager = MCPSessionManager()

        self.assertEqual(manager.session_count, 0)

        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)
        self.assertEqual(manager.session_count, 1)

        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)
        self.assertEqual(manager.session_count, 2)

    def test_each_session_has_unique_id(self) -> 'None':

        manager = MCPSessionManager()

        session_id_1 = manager.create(_mcp_protocol_version, _test_sec_def_id)
        session_id_2 = manager.create(_mcp_protocol_version, _test_sec_def_id)

        self.assertNotEqual(session_id_1, session_id_2)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerValidate(TestCase):

    def test_validate_existing_session(self) -> 'None':

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        result = manager.validate(session_id, _test_sec_def_id)

        self.assertEqual(result, Session_Valid)

    def test_validate_unknown_session(self) -> 'None':

        manager = MCPSessionManager()

        result = manager.validate('nonexistent-session-id', _test_sec_def_id)

        self.assertEqual(result, Session_Not_Found)

    def test_validate_session_of_another_identity(self) -> 'None':
        """ A session is only valid for the identity that created it.
        """

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        other_sec_def_id = _test_sec_def_id + 1
        result = manager.validate(session_id, other_sec_def_id)

        self.assertEqual(result, Session_Invalid_Identity)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerDelete(TestCase):

    def test_delete_existing_session(self) -> 'None':

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        result = manager.delete(session_id)

        self.assertTrue(result)
        self.assertEqual(manager.session_count, 0)
        self.assertEqual(manager.validate(session_id, _test_sec_def_id), Session_Not_Found)

    def test_delete_unknown_session(self) -> 'None':

        manager = MCPSessionManager()

        result = manager.delete('nonexistent-session-id')

        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerCleanup(TestCase):

    def test_cleanup_removes_expired(self) -> 'None':

        manager = MCPSessionManager(ttl=0)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)

        removed = manager.cleanup_expired()

        self.assertEqual(removed, 2)
        self.assertEqual(manager.session_count, 0)

    def test_cleanup_keeps_fresh_sessions(self) -> 'None':

        manager = MCPSessionManager(ttl=9999)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)

        removed = manager.cleanup_expired()

        self.assertEqual(removed, 0)
        self.assertEqual(manager.session_count, 1)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerReaping(TestCase):

    def test_idle_session_rejected_by_validate_after_ttl(self) -> 'None':
        """ With a 0-second TTL, validate rejects an existing session without waiting for the sweep.
        """

        manager = MCPSessionManager(ttl=0, max_lifetime=9999)
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        # The session was just created but the TTL is 0, so any elapsed time makes it idle-expired ..
        is_valid = manager.validate(session_id, _test_sec_def_id)

        self.assertEqual(is_valid, Session_Expired)

# ################################################################################################################################

    def test_cleanup_expired_removes_idle_sessions(self) -> 'None':
        """ Sessions older than the idle TTL are removed by cleanup_expired.
        """

        manager = MCPSessionManager(ttl=0, max_lifetime=9999)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)

        self.assertEqual(manager.session_count, 2)

        # With ttl=0 both sessions are idle-expired immediately ..
        removed = manager.cleanup_expired()

        self.assertEqual(removed, 2)
        self.assertEqual(manager.session_count, 0)

# ################################################################################################################################

    def test_session_dropped_past_absolute_max_lifetime(self) -> 'None':
        """ A session past max lifetime is rejected by validate even when last_seen_at is fresh.
        """

        # Use a generous idle TTL but a 0-second max lifetime ..
        manager = MCPSessionManager(ttl=9999, max_lifetime=0)
        session_id = manager.create(_mcp_protocol_version, _test_sec_def_id)

        # The session was just created but max_lifetime=0 means any elapsed time exceeds it ..
        is_valid = manager.validate(session_id, _test_sec_def_id)

        self.assertEqual(is_valid, Session_Expired)

# ################################################################################################################################

    def test_scheduled_cleanup_runs_across_managers(self) -> 'None':
        """ The MCPSessionReaper sweeps all managers it is given.
        """

        # Build two managers, each with one expired session ..
        orders_manager = MCPSessionManager(ttl=0, max_lifetime=9999)
        _ = orders_manager.create(_mcp_protocol_version, _test_sec_def_id)

        notifications_manager = MCPSessionManager(ttl=0, max_lifetime=9999)
        _ = notifications_manager.create(_mcp_protocol_version, _test_sec_def_id)

        # .. mock the channel_mcp_dict structure that the reaper expects ..
        channel_dict:'anydict' = {
            'test.mcp.orders': _MockReaperChannelConfig(_MockReaperWrapper(orders_manager, 'test.mcp.orders')),
            'test.mcp.notifications': _MockReaperChannelConfig(_MockReaperWrapper(notifications_manager, 'test.mcp.notifications')),
        }

        reaper = MCPSessionReaper(channel_dict)

        # .. run a single sweep directly (not the loop) ..
        reaper._sweep()

        # .. both managers must now be empty.
        self.assertEqual(orders_manager.session_count, 0)
        self.assertEqual(notifications_manager.session_count, 0)

# ################################################################################################################################

    def test_cleanup_expired_removes_max_lifetime_sessions(self) -> 'None':
        """ cleanup_expired removes sessions past max lifetime even when they are not idle.
        """

        # Use a generous idle TTL but a 0-second max lifetime ..
        manager = MCPSessionManager(ttl=9999, max_lifetime=0)
        _ = manager.create(_mcp_protocol_version, _test_sec_def_id)

        self.assertEqual(manager.session_count, 1)

        # The session is not idle (ttl=9999) but is past max lifetime (max_lifetime=0) ..
        removed = manager.cleanup_expired()

        self.assertEqual(removed, 1)
        self.assertEqual(manager.session_count, 0)

# ################################################################################################################################
# ################################################################################################################################

class HandlerInitializeCreatesSession(TestCase):

    def test_initialize_returns_session_id(self) -> 'None':

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        request = {
            'jsonrpc': '2.0',
            'method': 'initialize',
            'id': 1,
            'params': _initialize_params,
        }
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsNotNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 1)

        # The session ID must not leak into the JSON-RPC result
        result = mcp_response.body['result']
        self.assertNotIn('_mcp_session_id', result)

    def test_initialize_without_protocol_version_rejected(self) -> 'None':
        """ Initialize with no protocolVersion in params is rejected.
        """

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Send an initialize with empty params (no protocolVersion) ..
        request = {
            'jsonrpc': '2.0',
            'method': 'initialize',
            'id': 1,
            'params': {},
        }
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        # .. must return an error ..
        self.assertEqual(mcp_response.status_code, OK)
        self.assertIn('error', mcp_response.body)

        error = mcp_response.body['error']
        self.assertEqual(error['code'], _error_invalid_request)

        # .. and no session must have been created.
        self.assertEqual(session_manager.session_count, 0)
        self.assertIsNone(mcp_response.session_id)

    def test_initialize_in_batch_rejected(self) -> 'None':
        """ The MCP spec forbids initialize inside a batch.
        """

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        batch = [
            {'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': {}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_request)
        self.assertIsNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 0)

# ################################################################################################################################
# ################################################################################################################################

class HandlerSessionValidation(TestCase):

    def test_valid_session_id_accepted(self) -> 'None':

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # First, initialize to get a session ..
        initialize_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': _initialize_params})
        initialize_response = handler.handle_raw_request(initialize_request, _test_sec_def_id)
        session_id = initialize_response.session_id

        # .. then use the session ID for a subsequent request.
        ping_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 2})
        ping_response = handler.handle_raw_request(ping_request, _test_sec_def_id, session_id=session_id)

        self.assertEqual(ping_response.status_code, OK)

        body = ping_response.body
        result = body['result']
        self.assertEqual(result, {})

    def test_invalid_session_id_rejected(self) -> 'None':

        handler = _make_handler()

        request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        mcp_response = handler.handle_raw_request(request, _test_sec_def_id, session_id='bogus-session-id')

        self.assertEqual(mcp_response.status_code, BAD_REQUEST)

    def test_no_session_id_rejected(self) -> 'None':

        handler = _make_handler()

        request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        mcp_response = handler.handle_raw_request(request, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, BAD_REQUEST)

    def test_session_of_another_identity_rejected(self) -> 'None':
        """ A request presenting a session created by a different identity is rejected.
        """

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create a session for one identity ..
        initialize_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': _initialize_params})
        initialize_response = handler.handle_raw_request(initialize_request, _test_sec_def_id)
        session_id = initialize_response.session_id

        # .. then present it as a different identity.
        other_sec_def_id = _test_sec_def_id + 1
        ping_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 2})
        ping_response = handler.handle_raw_request(ping_request, other_sec_def_id, session_id=session_id)

        self.assertEqual(ping_response.status_code, BAD_REQUEST)

# ################################################################################################################################
# ################################################################################################################################

class HandlerDeleteSession(TestCase):

    def test_delete_existing_session(self) -> 'None':

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create a session ..
        initialize_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': _initialize_params})
        initialize_response = handler.handle_raw_request(initialize_request, _test_sec_def_id)
        session_id = initialize_response.session_id

        # .. delete it.
        delete_response = handler.handle_delete_session(session_id, _test_sec_def_id)

        self.assertEqual(delete_response.status_code, OK)
        self.assertEqual(session_manager.session_count, 0)

    def test_delete_unknown_session(self) -> 'None':

        handler = _make_handler()

        delete_response = handler.handle_delete_session('nonexistent-session-id', _test_sec_def_id)

        self.assertEqual(delete_response.status_code, NOT_FOUND)

    def test_delete_without_session_id(self) -> 'None':

        handler = _make_handler()

        delete_response = handler.handle_delete_session(None, _test_sec_def_id)

        self.assertEqual(delete_response.status_code, NOT_FOUND)

    def test_delete_session_of_another_identity(self) -> 'None':
        """ Deleting a session created by a different identity is rejected with 400.
        """

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create a session for one identity ..
        initialize_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': _initialize_params})
        initialize_response = handler.handle_raw_request(initialize_request, _test_sec_def_id)
        session_id = initialize_response.session_id

        # .. attempt deletion as a different identity.
        other_sec_def_id = _test_sec_def_id + 1
        delete_response = handler.handle_delete_session(session_id, other_sec_def_id)

        self.assertEqual(delete_response.status_code, BAD_REQUEST)

        # .. the session must remain intact.
        self.assertEqual(session_manager.session_count, 1)

    def test_deleted_session_is_rejected(self) -> 'None':

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create and delete a session ..
        initialize_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': _initialize_params})
        initialize_response = handler.handle_raw_request(initialize_request, _test_sec_def_id)
        session_id = initialize_response.session_id

        _ = handler.handle_delete_session(session_id, _test_sec_def_id)

        # .. using the deleted session ID must fail.
        ping_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 2})
        ping_response = handler.handle_raw_request(ping_request, _test_sec_def_id, session_id=session_id)

        self.assertEqual(ping_response.status_code, BAD_REQUEST)

# ################################################################################################################################
# ################################################################################################################################
