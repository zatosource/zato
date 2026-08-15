# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# local
import _audit
import _constants
import _enmasse
import _helpers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# What the client is told when a service failed - and nothing more
_generic_error_text = 'Bad request'

# How many milliseconds one second has
_ms_per_second = 1000

# How long the archive build would run if nothing cut it off, in seconds
_archive_build_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

class TestServiceConduct:
    """ The gateway contains whatever a service does - hangs, exceptions,
    unserializable output, empty responses and tools that vanish mid-conversation.
    """

# ################################################################################################################################

    def test_a_hanging_tool_is_cut_off_at_the_bound(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Ops)
        session_id = _helpers.open_session(client)

        # The archive build sleeps past the gateway's invoke timeout -
        # the answer arrives when the bound expires, not when the sleep ends ..
        start_time = time.monotonic()
        body = _helpers.call_tool(client, session_id, _constants.Service_Archive_Build,
            {'customer_id': _constants.Customer_ID})
        elapsed = time.monotonic() - start_time

        assert elapsed < _archive_build_seconds, elapsed

        # .. the response is the generic error - the bound is never named to the client ..
        result = body['result']
        assert result['isError'], body

        text = result['content'][0]['text']
        assert text == _generic_error_text, body

        # .. and the audit records the error with the duration column filled
        # and the bound named in the trace's error message.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Ops,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event

        expected_minimum_ms = _constants.Invoke_Timeout_Seconds * _ms_per_second
        assert event['data']['duration_ms'] >= expected_minimum_ms, event

        error_message = event['data']['error_message']
        assert 'timed out' in error_message, event
        assert str(_constants.Invoke_Timeout_Seconds) in error_message, event

# ################################################################################################################################

    def test_an_exception_maps_to_one_error_shape(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The uncancellable order makes the service raise ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Cancel,
            {'order_id': _constants.Order_ID_Not_Cancellable})

        # .. the client sees the one defined error shape and nothing of the traceback ..
        result = body['result']
        assert result['isError'], body

        text = result['content'][0]['text']
        assert text == _generic_error_text, body
        assert 'Traceback' not in text, body

        # .. while the audit data records the service's own error message.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert 'cannot be cancelled' in event['data']['error_message'], event

# ################################################################################################################################

    def test_unserializable_output_is_refused_cleanly(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Ops)
        session_id = _helpers.open_session(client)

        # Binary image bytes and a JSON-unrepresentable set each map to the same
        # defined error - never an HTTP-level failure.
        tool_names = [_constants.Service_Badge_Render, _constants.Service_Tag_Collect]

        for tool_name in tool_names:

            response = client.jsonrpc('tools/call',
                params={'name': tool_name, 'arguments': {'customer_id': _constants.Customer_ID}},
                session_id=session_id)

            assert response.status_code == OK, response.text

            result = response.json()['result']
            assert result['isError'], response.text
            assert result['content'][0]['text'] == _generic_error_text, response.text

# ################################################################################################################################

    def test_an_empty_response_is_a_defined_shape(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Ops)
        session_id = _helpers.open_session(client)

        # A service that says nothing back still answers with the defined empty content ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Ack_Silent,
            {'customer_id': _constants.Customer_ID})

        result = body['result']
        assert 'isError' not in result, body
        assert result['content'][0]['text'] == '', body

        # .. the outcome is OK and the shaping pipeline left it alone - the audit data
        # carries the request's own facts and not one shaping key.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Ops,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.OK, event

        data_keys = set(event['data'])
        assert data_keys == {'remote_address', 'method', 'duration_ms', 'request_size'}, event

# ################################################################################################################################

    def test_a_tool_that_vanishes_between_list_and_call(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Ops)
        session_id = _helpers.open_session(client)

        # tools/list advertises the order status tool ..
        tools = _helpers.list_tools(client, session_id)
        tool_names = _helpers.get_tool_names(tools)
        assert _constants.Service_Order_Status in tool_names, tool_names

        # A changed gateway rebuilds its wrapper, which drops its sessions, so every
        # probe below runs on a session of its own and cleans it up right away.
        def _probe_call() -> 'anydict':
            probe_session = _helpers.open_session(client)
            out = _helpers.call_tool(client, probe_session, _constants.Service_Order_Status,
                {'order_id': _constants.Order_ID})
            _ = client.delete_session(probe_session)
            return out

        def _probe_tool_names() -> 'list':
            probe_session = _helpers.open_session(client)
            tools = _helpers.list_tools(client, probe_session)
            _ = client.delete_session(probe_session)
            out = _helpers.get_tool_names(tools)
            return out

        try:
            # .. the tool is taken off the gateway while the conversation is underway ..
            remaining_services = [
                _constants.Service_Archive_Build,
                _constants.Service_Badge_Render,
                _constants.Service_Tag_Collect,
                _constants.Service_Ack_Silent,
            ]
            overrides = {_constants.Gateway_Ops: {'services': remaining_services}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. the call refuses as an unknown tool once the change is live ..
            def call_is_refused() -> 'bool':
                body = _probe_call()

                if error := body.get('error'):
                    out = error['code'] == _constants.Error_Method_Not_Found
                else:
                    out = False

                return out

            _helpers.wait_until(call_is_refused, 'the removed tool refuses as unknown')

            # .. and the next tools/list no longer names it.
            tool_names = _probe_tool_names()
            assert _constants.Service_Order_Status not in tool_names, tool_names

        finally:
            # The gateway always goes back to its full tool set for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def tool_is_back() -> 'bool':
                out = _constants.Service_Order_Status in _probe_tool_names()
                return out

            _helpers.wait_until(tool_is_back, 'the restored tool is advertised again')

# ################################################################################################################################
# ################################################################################################################################
