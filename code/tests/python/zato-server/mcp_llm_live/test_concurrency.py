# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor
from http.client import INTERNAL_SERVER_ERROR, OK

# local
import _audit
import _constants
import _enmasse
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How many calls the one-session parallel test fires at once
_parallel_session_calls = 12

# How many conversations run at once and how many calls each makes
_concurrent_conversations = 24
_calls_per_conversation = 3

# How many threads write per gateway in the parallel-writers test and how many calls each makes
_writer_threads = 8
_writes_per_thread = 5

# A response of this many invoices goes over the lifecycle gateway's cap
_oversized_count = '200'

# How many creations past the cap the contention test attempts
_past_cap_count = 20

# How many sessions the contention test frees and refills
_refill_count = 10

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrency:
    """ Real parallelism through direct clients in thread pools - one session under
    parallel calls, many conversations at once, a re-import racing in-flight traffic,
    the audit log under parallel writers and the session cap under contention.
    """

# ################################################################################################################################

    def test_parallel_calls_on_one_session_match_their_requests(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # Simultaneous calls with distinct ids and distinct arguments through one session ..
        def one_call(call_index:'int') -> 'anydict':
            arguments = {'order_id': f'{_constants.Order_ID}-{call_index}'}
            params = {'name': _constants.Service_Order_Status, 'arguments': arguments}

            response = client.jsonrpc('tools/call', params=params, request_id=call_index, session_id=session_id)
            out = response.json()
            return out

        with ThreadPoolExecutor(max_workers=_parallel_session_calls) as executor:
            futures = []

            for call_index in range(_parallel_session_calls):
                futures.append(executor.submit(one_call, call_index))

            bodies = []

            for future in futures:
                bodies.append(future.result())

        # .. every response carries its own request's id and its own request's arguments ..
        for call_index, body in enumerate(bodies):
            assert body['id'] == call_index, body

            data = _helpers.get_result_data(body)
            assert data['order_id'] == f'{_constants.Order_ID}-{call_index}', body

        # .. and the audit holds exactly one row per call, each with a CID of its own.
        _ = _audit.wait_for_events(
            audit_db_path, _parallel_session_calls,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        events = _audit.read_events(
            audit_db_path, object_name=_constants.Gateway_Main, event_type=AuditEvent.MCP_Tools_Call, min_id=min_id)

        session_events = []

        for event in events:
            if event['sub_key'] == session_id:
                session_events.append(event)

        assert len(session_events) == _parallel_session_calls, session_events

        cids = set()

        for event in session_events:
            cids.add(event['cid'])

        assert len(cids) == _parallel_session_calls, cids

# ################################################################################################################################

    def test_many_conversations_at_once_stay_apart(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        # Dozens of conversations, each on its own session, each asking about
        # order ids of its own ..
        def one_conversation(conversation_index:'int') -> 'str':

            session_id = _helpers.open_session(client)

            for call_index in range(_calls_per_conversation):

                order_id = f'{_constants.Order_ID}-c{conversation_index}-n{call_index}'
                body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': order_id})

                # No response ever carries another conversation's data
                data = _helpers.get_result_data(body)
                assert data['order_id'] == order_id, body

            return session_id

        with ThreadPoolExecutor(max_workers=_concurrent_conversations) as executor:
            futures = []

            for conversation_index in range(_concurrent_conversations):
                futures.append(executor.submit(one_conversation, conversation_index))

            session_ids = []

            for future in futures:
                session_ids.append(future.result())

        # Every conversation ran on a session of its own ..
        assert len(set(session_ids)) == _concurrent_conversations, session_ids

        # .. and filtering the audit by session returns exactly that conversation's events,
        # with no CID ever shared between two conversations.
        total_calls = _concurrent_conversations * _calls_per_conversation

        _ = _audit.wait_for_events(
            audit_db_path, total_calls,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        events = _audit.read_events(
            audit_db_path, object_name=_constants.Gateway_Main, event_type=AuditEvent.MCP_Tools_Call, min_id=min_id)

        events_by_session = {}

        for event in events:
            events_by_session.setdefault(event['sub_key'], []).append(event)

        all_cids = set()

        for session_id in session_ids:

            session_events = events_by_session[session_id]
            assert len(session_events) == _calls_per_conversation, session_events

            for event in session_events:
                all_cids.add(event['cid'])

        assert len(all_cids) == total_calls, all_cids

        # The sessions are cleaned up for the other tests.
        for session_id in session_ids:
            _ = client.delete_session(session_id)

# ################################################################################################################################

    def test_a_changing_reimport_races_in_flight_calls(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)

        def one_oversized_call() -> 'anydict':
            """ One oversized invoice call on a session of its own, returning the status
            code and the body together, so the caller can classify what happened.
            """
            initialize = _helpers.initialize_response(client)

            # The rebuild can refuse the initialize itself - that refusal is this call's outcome
            if 'Mcp-Session-Id' not in initialize.headers:
                out = {'status_code': initialize.status_code, 'body': initialize.json()}
                return out

            session_id = initialize.headers['Mcp-Session-Id']

            params = {'name': _constants.Service_Invoice_List, 'arguments': {'count': _oversized_count}}
            response = client.jsonrpc('tools/call', params=params, session_id=session_id)

            # Each call cleans up its own session
            _ = client.delete_session(session_id)

            out = {'status_code': response.status_code, 'body': response.json()}
            return out

        try:
            # The re-import flips the gateway's cap from truncate to block while calls fly ..
            overrides = {_constants.Gateway_Lifecycle: {'size_cap_mode': 'block'}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)

            with ThreadPoolExecutor(max_workers=1) as executor:

                import_future = executor.submit(_enmasse.run_import, server_directory, config)

                results = []

                while not import_future.done():
                    results.append(one_oversized_call())

                import_future.result()

            # .. every in-flight call completed under one config or the other -
            # truncated, blocked, or refused because the rebuild dropped its session -
            # and none of them ever failed with a server fault.
            assert results, 'No calls ran during the import'

            for result in results:

                assert result['status_code'] < INTERNAL_SERVER_ERROR, result

                body = result['body']

                if 'result' in body:
                    continue

                assert body['error']['code'] == _constants.Error_Invalid_Request, result

            # .. and the first call after the import sees the new config - the cap blocks now.
            def call_is_blocked() -> 'bool':
                body = one_oversized_call()['body']

                if result := body.get('result'):
                    out = 'isError' in result
                else:
                    out = False

                return out

            _helpers.wait_until(call_is_blocked, 'block mode reached enforcement')

        finally:
            # The gateway always goes back to truncate mode for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def call_is_truncated() -> 'bool':
                body = one_oversized_call()['body']

                if result := body.get('result'):
                    out = 'isError' not in result
                else:
                    out = False

                return out

            _helpers.wait_until(call_is_truncated, 'truncate mode came back')

# ################################################################################################################################

    def test_the_audit_log_under_parallel_writers(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # Sustained parallel traffic on two gateways at once ..
        gateways = [
            (_constants.Gateway_Main, _constants.Path_Main),
            (_constants.Gateway_Ops, _constants.Path_Ops),
        ]

        def one_writer(url_path:'str', writer_index:'int') -> 'None':

            client = _helpers.make_client(zato_server, url_path)
            session_id = _helpers.open_session(client)

            for call_index in range(_writes_per_thread):

                order_id = f'{_constants.Order_ID}-w{writer_index}-n{call_index}'
                body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': order_id})

                data = _helpers.get_result_data(body)
                assert data['order_id'] == order_id, body

            _ = client.delete_session(session_id)

        worker_count = _writer_threads * len(gateways)

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = []

            for _, url_path in gateways:
                for writer_index in range(_writer_threads):
                    futures.append(executor.submit(one_writer, url_path, writer_index))

            for future in futures:
                future.result()

        # .. and each gateway's audit holds exactly one row per call - no insert
        # was ever lost or duplicated, each with a CID of its own.
        expected_per_gateway = _writer_threads * _writes_per_thread

        for gateway_name, _ in gateways:

            _ = _audit.wait_for_events(
                audit_db_path, expected_per_gateway,
                object_name=gateway_name,
                event_type=AuditEvent.MCP_Tools_Call,
                min_id=min_id)

            events = _audit.read_events(
                audit_db_path, object_name=gateway_name, event_type=AuditEvent.MCP_Tools_Call, min_id=min_id)

            assert len(events) == expected_per_gateway, (gateway_name, len(events))

            cids = set()

            for event in events:
                assert event['outcome'] == AuditOutcome.OK, event
                cids.add(event['cid'])

            assert len(cids) == expected_per_gateway, cids

# ################################################################################################################################

    def test_the_session_cap_under_contention(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Sessions)

        attempt_count = _constants.Session_Cap + _past_cap_count

        def one_initialize(_:'int') -> 'anydict':

            response = _helpers.initialize_response(client)

            out = {'body': response.json(), 'session_id': response.headers.get('Mcp-Session-Id')}
            return out

        session_ids = []

        try:
            # Parallel session creation against the capped gateway ..
            with ThreadPoolExecutor(max_workers=attempt_count) as executor:
                results = list(executor.map(one_initialize, range(attempt_count)))

            refusals = []

            for result in results:

                if result['session_id']:
                    session_ids.append(result['session_id'])
                else:
                    refusals.append(result['body'])

            # .. exactly the cap was admitted and every rejection carries the defined error ..
            assert len(session_ids) == _constants.Session_Cap, len(session_ids)
            assert len(refusals) == _past_cap_count, len(refusals)

            for body in refusals:
                assert body['error']['code'] == _constants.Error_Invalid_Request, body

            # .. deletions under the same contention free slots that new creations then take.
            to_delete = session_ids[:_refill_count]
            session_ids = session_ids[_refill_count:]

            def one_delete(session_id:'str') -> 'int':
                response = client.delete_session(session_id)
                out = response.status_code
                return out

            with ThreadPoolExecutor(max_workers=_refill_count) as executor:
                delete_statuses = list(executor.map(one_delete, to_delete))

            for status_code in delete_statuses:
                assert status_code == OK, delete_statuses

            with ThreadPoolExecutor(max_workers=_refill_count) as executor:
                refill_results = list(executor.map(one_initialize, range(_refill_count)))

            for result in refill_results:
                assert result['session_id'], result
                session_ids.append(result['session_id'])

            assert len(session_ids) == _constants.Session_Cap, len(session_ids)

        finally:
            # The gateway goes back to its idle state for the other tests.
            for session_id in session_ids:
                _ = client.delete_session(session_id)

# ################################################################################################################################
# ################################################################################################################################
