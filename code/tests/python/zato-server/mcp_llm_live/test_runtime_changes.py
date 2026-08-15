# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import OK

# local
import _agent
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

# How many milliseconds one second has
_ms_per_second = 1000

# The order the two-attempt confirmation test confirms
_confirm_order_id = 'ORD-4501'

# How long a hot-deployed change may take to serve, in seconds
_hot_deploy_timeout = 60

# How often to poll for it, in seconds
_hot_deploy_poll_interval = 0.5

# The fingerprint the mid-conversation redeploy serves and the optional field it adds
_redeployed_fingerprint = 'fp-replica'
_redeployed_field       = 'verbose'

# ################################################################################################################################
# ################################################################################################################################

class TestRuntimeChanges:
    """ Conversations continue while the environment changes around them -
    slow services, re-imports, restarts, hot deploys and retried confirmations.
    """

# ################################################################################################################################

    def test_a_slow_service_is_measured_not_lost(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Runtime)
        session_id = _helpers.open_session(client)

        # The slow echo completes within the client's own timeout ..
        message = 'Replica catch-up check'
        body = _helpers.call_tool(client, session_id, _constants.Service_Echo_Slow, {'message': message})

        data = _helpers.get_result_data(body)
        assert data['echo'] == message, body

        # .. and the audit event's duration reflects the sleep.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Runtime,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']
        expected_minimum_ms = _constants.Slow_Echo_Seconds * _ms_per_second

        assert event_data['duration_ms'] >= expected_minimum_ms, event_data

# ################################################################################################################################

    def test_a_reimport_under_traffic_changes_nothing_it_should_not(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The same configuration is imported again while the conversation keeps calling ..
        config = _enmasse.build_suite_config()

        with ThreadPoolExecutor(max_workers=1) as executor:

            import_future = executor.submit(_enmasse.run_import, server_directory, config)

            bodies = []
            call_index = 0

            while not import_future.done():

                arguments = {'order_id': f'{_constants.Order_ID}-{call_index}'}
                bodies.append(_helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments))

                call_index += 1

            import_future.result()

        # .. no request of the conversation failed ..
        assert bodies, 'No calls ran during the import'

        for body in bodies:
            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        # .. and the session is as valid after the import as it was before.
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status,
            {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

# ################################################################################################################################

    def test_a_restart_starts_clean(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        old_session_id = _helpers.open_session(client)

        max_id_before = _audit.last_event_id(audit_db_path)

        # The server restarts ..
        zato_server['restart']()

        # .. the session from before the restart is refused ..
        response = client.jsonrpc('tools/list', session_id=old_session_id)
        assert response.status_code != OK, response.text

        # .. a fresh agent re-initializes and completes its task ..
        task = f'What city does customer {_constants.Customer_ID} live in?'
        result = _agent.run_agent(client, task)

        assert _helpers.text_contains(result.final_text, _constants.Customer_City), result.final_text

        # .. and the audit event ids continue past the pre-restart ones without duplicates.
        events = _audit.read_events(audit_db_path, min_id=max_id_before)
        assert events, 'No audit events after the restart'

        event_ids = []

        for event in events:
            assert event['id'] > max_id_before, event
            event_ids.append(event['id'])

        assert len(event_ids) == len(set(event_ids)), event_ids

# ################################################################################################################################

    def test_hot_deploy_lands_between_two_calls_of_one_conversation(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Docstring)
        session_id = _helpers.open_session(client)

        # The conversation's first call serves whatever build is live now ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Docstring_Probe, {'revision': 'r1'})

        data = _helpers.get_result_data(body)
        assert data['fingerprint'] != _redeployed_fingerprint, data

        # .. a new build with a new fingerprint and one more optional field
        # goes out through the pickup directory ..
        fixtures_directory = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
        probe_path = os.path.join(fixtures_directory, 'crm_docstring.py')

        with open(probe_path) as probe_file:
            probe_source = probe_file.read()

        # The leading dash is what declares the new field optional in Zato input syntax
        new_declaration = "input = 'revision', '-{}'".format(_redeployed_field)
        probe_source = probe_source.replace("input = 'revision'", new_declaration, 1)
        probe_source = probe_source.replace("'fp-first'", f"'{_redeployed_fingerprint}'")

        pickup_path = os.path.join(zato_server['pickup_directory'], 'crm_docstring.py')

        with open(pickup_path, 'w') as pickup_file:
            _ = pickup_file.write(probe_source)

        # .. the conversation's next call serves the new behavior once hot deploy lands ..
        deadline = time.monotonic() + _hot_deploy_timeout

        while time.monotonic() < deadline:

            body = _helpers.call_tool(client, session_id, _constants.Service_Docstring_Probe, {'revision': 'r2'})
            data = _helpers.get_result_data(body)

            if data['fingerprint'] == _redeployed_fingerprint:
                break

            time.sleep(_hot_deploy_poll_interval)

        else:
            raise Exception(f'The redeployed service did not serve within {_hot_deploy_timeout}s: {data}')

        # .. and the same session's next tools/list advertises the new schema.
        tools = _helpers.list_tools(client, session_id)

        schemas = {}

        for tool in tools:
            schemas[tool['name']] = tool['inputSchema']

        schema = schemas[_constants.Service_Docstring_Probe]
        assert _redeployed_field in schema['properties'], schema
        assert schema['required'] == ['revision'], schema

# ################################################################################################################################

    def test_a_retried_confirmation_leaves_an_exact_trail(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Runtime)

        task = f'Confirm order {_confirm_order_id} in the fulfilment system.'
        system_text = 'A confirmation may fail on its first attempt - when it does, call the tool once more.'

        result = _agent.run_agent(client, task, system_text=system_text)

        # The first attempt failed and a later one succeeded ..
        call_count = len(result.tool_calls)
        assert call_count >= 2, result.tool_calls

        first_call = result.tool_calls[0]
        last_call = result.tool_calls[-1]

        assert first_call.is_error, result.tool_calls
        assert not last_call.is_error, result.tool_calls

        # .. the final answer reports the confirmation ..
        assert _helpers.text_contains(result.final_text, 'confirm'), result.final_text

        # .. and the audit shows the error event before the success event, same conversation.
        events = _audit.wait_for_events(
            audit_db_path, call_count,
            object_name=_constants.Gateway_Runtime,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        outcomes = []

        for event in events:
            if event['sub_key'] == result.session_id:
                outcomes.append(event['outcome'])

        assert outcomes[0] == AuditOutcome.Error, outcomes
        assert outcomes[-1] == AuditOutcome.OK, outcomes

# ################################################################################################################################
# ################################################################################################################################
