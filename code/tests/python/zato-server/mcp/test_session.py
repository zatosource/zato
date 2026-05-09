# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, NOT_FOUND, OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.mcp.handler import MCPHandler, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry for session tests.
    """
    def get_tools(self): # type: ignore
        return []

    def get_tools_page(self, cursor=None): # type: ignore
        return [], None

    def is_tool_allowed(self, service_name): # type: ignore
        return False

    def rebuild(self): # type: ignore
        pass

# ################################################################################################################################
# ################################################################################################################################

def _invoke_noop(service_name, payload): # type: ignore
    return {}

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(session_manager=None): # type: ignore
    """ Creates an MCPHandler with a session manager for tests.
    """
    registry = _MockToolRegistry()

    if session_manager is None:
        session_manager = MCPSessionManager()

    out = MCPHandler(registry, _invoke_noop, session_manager)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerCreate(TestCase):

    def test_create_returns_session_id(self): # type: ignore

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version)

        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)

    def test_create_increments_count(self): # type: ignore

        manager = MCPSessionManager()

        self.assertEqual(manager.session_count, 0)

        manager.create(_mcp_protocol_version)
        self.assertEqual(manager.session_count, 1)

        manager.create(_mcp_protocol_version)
        self.assertEqual(manager.session_count, 2)

    def test_each_session_has_unique_id(self): # type: ignore

        manager = MCPSessionManager()

        session_id_1 = manager.create(_mcp_protocol_version)
        session_id_2 = manager.create(_mcp_protocol_version)

        self.assertNotEqual(session_id_1, session_id_2)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerValidate(TestCase):

    def test_validate_existing_session(self): # type: ignore

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version)

        result = manager.validate(session_id)

        self.assertTrue(result)

    def test_validate_unknown_session(self): # type: ignore

        manager = MCPSessionManager()

        result = manager.validate('nonexistent-session-id')

        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerDelete(TestCase):

    def test_delete_existing_session(self): # type: ignore

        manager = MCPSessionManager()
        session_id = manager.create(_mcp_protocol_version)

        result = manager.delete(session_id)

        self.assertTrue(result)
        self.assertEqual(manager.session_count, 0)
        self.assertFalse(manager.validate(session_id))

    def test_delete_unknown_session(self): # type: ignore

        manager = MCPSessionManager()

        result = manager.delete('nonexistent-session-id')

        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerCleanup(TestCase):

    def test_cleanup_removes_expired(self): # type: ignore

        manager = MCPSessionManager(ttl=0)
        manager.create(_mcp_protocol_version)
        manager.create(_mcp_protocol_version)

        removed = manager.cleanup_expired()

        self.assertEqual(removed, 2)
        self.assertEqual(manager.session_count, 0)

    def test_cleanup_keeps_fresh_sessions(self): # type: ignore

        manager = MCPSessionManager(ttl=9999)
        manager.create(_mcp_protocol_version)

        removed = manager.cleanup_expired()

        self.assertEqual(removed, 0)
        self.assertEqual(manager.session_count, 1)

# ################################################################################################################################
# ################################################################################################################################

class HandlerInitializeCreatesSession(TestCase):

    def test_initialize_returns_session_id(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        request = {
            'jsonrpc': '2.0',
            'method': 'initialize',
            'id': 1,
            'params': {},
        }
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsNotNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 1)

        # The session ID must not leak into the JSON-RPC result
        result = mcp_response.body['result']
        self.assertNotIn('_mcp_session_id', result)

    def test_initialize_in_batch_returns_session_id(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        batch = [
            {'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': {}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsNotNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 1)

# ################################################################################################################################
# ################################################################################################################################

class HandlerSessionValidation(TestCase):

    def test_valid_session_id_accepted(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # First, initialize to get a session ..
        init_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': {}})
        init_response = handler.handle_raw_request(init_request)
        session_id = init_response.session_id

        # .. then use the session ID for a subsequent request.
        ping_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 2})
        ping_response = handler.handle_raw_request(ping_request, session_id=session_id)

        self.assertEqual(ping_response.status_code, OK)
        self.assertEqual(ping_response.body['result'], {})

    def test_invalid_session_id_rejected(self): # type: ignore

        handler = _make_handler()

        request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        mcp_response = handler.handle_raw_request(request, session_id='bogus-session-id')

        self.assertEqual(mcp_response.status_code, NOT_FOUND)

    def test_no_session_id_accepted(self): # type: ignore

        handler = _make_handler()

        request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        mcp_response = handler.handle_raw_request(request)

        self.assertEqual(mcp_response.status_code, OK)

# ################################################################################################################################
# ################################################################################################################################

class HandlerDeleteSession(TestCase):

    def test_delete_existing_session(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create a session ..
        init_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': {}})
        init_response = handler.handle_raw_request(init_request)
        session_id = init_response.session_id

        # .. delete it.
        delete_response = handler.handle_delete_session(session_id)

        self.assertEqual(delete_response.status_code, OK)
        self.assertEqual(session_manager.session_count, 0)

    def test_delete_unknown_session(self): # type: ignore

        handler = _make_handler()

        delete_response = handler.handle_delete_session('nonexistent-session-id')

        self.assertEqual(delete_response.status_code, NOT_FOUND)

    def test_delete_without_session_id(self): # type: ignore

        handler = _make_handler()

        delete_response = handler.handle_delete_session(None)

        self.assertEqual(delete_response.status_code, NOT_FOUND)

    def test_deleted_session_is_rejected(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create and delete a session ..
        init_request = dumps({'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': {}})
        init_response = handler.handle_raw_request(init_request)
        session_id = init_response.session_id

        handler.handle_delete_session(session_id)

        # .. using the deleted session ID must fail.
        ping_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 2})
        ping_response = handler.handle_raw_request(ping_request, session_id=session_id)

        self.assertEqual(ping_response.status_code, NOT_FOUND)

# ################################################################################################################################
# ################################################################################################################################

class SessionManagerNotifications(TestCase):

    def test_queue_notification_for_all(self): # type: ignore

        manager = MCPSessionManager()
        sid_1 = manager.create(_mcp_protocol_version)
        sid_2 = manager.create(_mcp_protocol_version)

        notification = {'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}
        count = manager.queue_notification_for_all(notification)

        self.assertEqual(count, 2)

        # Both sessions should have the notification pending
        n1 = manager.drain_notifications(sid_1)
        n2 = manager.drain_notifications(sid_2)

        self.assertEqual(len(n1), 1)
        self.assertEqual(n1[0]['method'], 'notifications/tools/list_changed')
        self.assertEqual(len(n2), 1)

    def test_queue_notification_no_sessions(self): # type: ignore

        manager = MCPSessionManager()

        notification = {'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}
        count = manager.queue_notification_for_all(notification)

        self.assertEqual(count, 0)

    def test_drain_clears_queue(self): # type: ignore

        manager = MCPSessionManager()
        sid = manager.create(_mcp_protocol_version)

        notification = {'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}
        manager.queue_notification_for_all(notification)

        # First drain returns the notification
        n1 = manager.drain_notifications(sid)
        self.assertEqual(len(n1), 1)

        # Second drain returns empty
        n2 = manager.drain_notifications(sid)
        self.assertEqual(len(n2), 0)

    def test_drain_unknown_session_returns_empty(self): # type: ignore

        manager = MCPSessionManager()

        result = manager.drain_notifications('nonexistent')

        self.assertEqual(result, [])

    def test_multiple_notifications_queued(self): # type: ignore

        manager = MCPSessionManager()
        sid = manager.create(_mcp_protocol_version)

        n1 = {'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}
        n2 = {'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}

        manager.queue_notification_for_all(n1)
        manager.queue_notification_for_all(n2)

        result = manager.drain_notifications(sid)

        self.assertEqual(len(result), 2)

# ################################################################################################################################
# ################################################################################################################################

class HandlerNotifyToolsChanged(TestCase):

    def test_notify_tools_changed_queues_for_all_sessions(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        # Create two sessions
        sid_1 = session_manager.create(_mcp_protocol_version)
        sid_2 = session_manager.create(_mcp_protocol_version)

        count = handler.notify_tools_changed()

        self.assertEqual(count, 2)

        n1 = session_manager.drain_notifications(sid_1)
        n2 = session_manager.drain_notifications(sid_2)

        self.assertEqual(len(n1), 1)
        self.assertEqual(n1[0]['method'], 'notifications/tools/list_changed')
        self.assertEqual(len(n2), 1)

    def test_notify_tools_changed_no_sessions(self): # type: ignore

        handler = _make_handler()

        count = handler.notify_tools_changed()

        self.assertEqual(count, 0)

# ################################################################################################################################
# ################################################################################################################################

class HandlerGetPendingNotifications(TestCase):

    def test_get_notifications_returns_pending(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        sid = session_manager.create(_mcp_protocol_version)
        handler.notify_tools_changed()

        response = handler.get_pending_notifications(sid)

        self.assertEqual(response.status_code, OK)
        self.assertIsInstance(response.body, list)
        self.assertEqual(len(response.body), 1)
        self.assertEqual(response.body[0]['method'], 'notifications/tools/list_changed')

    def test_get_notifications_empty_returns_no_content(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        sid = session_manager.create(_mcp_protocol_version)

        response = handler.get_pending_notifications(sid)

        self.assertEqual(response.status_code, NO_CONTENT)
        self.assertIsNone(response.body)

    def test_get_notifications_unknown_session_returns_not_found(self): # type: ignore

        handler = _make_handler()

        response = handler.get_pending_notifications('nonexistent')

        self.assertEqual(response.status_code, NOT_FOUND)

    def test_get_notifications_no_session_id_returns_not_found(self): # type: ignore

        handler = _make_handler()

        response = handler.get_pending_notifications(None)

        self.assertEqual(response.status_code, NOT_FOUND)

    def test_get_notifications_drains_queue(self): # type: ignore

        session_manager = MCPSessionManager()
        handler = _make_handler(session_manager=session_manager)

        sid = session_manager.create(_mcp_protocol_version)
        handler.notify_tools_changed()

        # First GET drains
        response1 = handler.get_pending_notifications(sid)
        self.assertEqual(response1.status_code, OK)
        self.assertEqual(len(response1.body), 1)

        # Second GET is empty
        response2 = handler.get_pending_notifications(sid)
        self.assertEqual(response2.status_code, NO_CONTENT)

# ################################################################################################################################
# ################################################################################################################################
