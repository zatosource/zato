# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import NOT_FOUND, OK

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
    from zato.common.typing_ import anydict, callable_

# ################################################################################################################################
# ################################################################################################################################

# How long a re-imported change may take to reach live enforcement, in seconds
_reimport_timeout = 60

# How often to poll for it, in seconds
_reimport_poll_interval = 0.5

# A response of this many invoices goes over the lifecycle gateway's cap
_oversized_count = '200'

# How many tool calls run in parallel against one gateway
_parallel_call_count = 8

# ################################################################################################################################
# ################################################################################################################################

def _call_invoices(zato_server:'anydict') -> 'anydict':
    """ One oversized invoice call through the lifecycle gateway, on a fresh session,
    returning the whole response body.
    """

    client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)
    session_id = _helpers.open_session(client)

    out = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, {'count': _oversized_count})
    return out

# ################################################################################################################################

def _wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls until the condition function returns True, which is how the tests wait
    for a re-imported change to reach live enforcement.
    """

    deadline = time.monotonic() + _reimport_timeout

    while time.monotonic() < deadline:

        if condition():
            return

        time.sleep(_reimport_poll_interval)

    raise Exception(f'Condition did not hold within {_reimport_timeout}s: {description}')

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayLifecycle:
    """ Enmasse re-imports change a live gateway's behavior without a restart -
    options flip, activity toggles and the gateway itself can be deleted.
    """

# ################################################################################################################################

    def test_a_reimport_flips_truncate_to_block_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        # In truncate mode, the oversized call comes back cut but not refused ..
        body = _call_invoices(zato_server)
        assert 'isError' not in body['result'], body

        try:
            # .. one re-import flips the mode to block ..
            overrides = {_constants.Gateway_Lifecycle: {'size_cap_mode': 'block'}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. and the very same call is refused now.
            def call_is_blocked() -> 'bool':
                body = _call_invoices(zato_server)
                out = 'isError' in body['result']
                return out

            _wait_until(call_is_blocked, 'block mode reached enforcement')

        finally:
            # The gateway always goes back to truncate mode for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def call_is_truncated() -> 'bool':
                body = _call_invoices(zato_server)
                out = 'isError' not in body['result']
                return out

            _wait_until(call_is_truncated, 'truncate mode came back')

# ################################################################################################################################

    def test_is_active_toggles_the_gateway_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)

        # The gateway serves while it is active ..
        response = _helpers.initialize_response(client)
        assert response.status_code == OK, response.text

        try:
            # .. a re-import turns it off and requests are refused ..
            overrides = {_constants.Gateway_Lifecycle: {'is_active': False}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def gateway_refuses() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code != OK
                return out

            _wait_until(gateway_refuses, 'the inactive gateway refuses requests')

        finally:
            # .. and turning it back on restores service.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def gateway_serves() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code == OK
                return out

            _wait_until(gateway_serves, 'the reactivated gateway serves again')

# ################################################################################################################################

    def test_parallel_tool_calls_all_succeed_and_are_all_audited(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        def one_call(call_index:'int') -> 'anydict':
            arguments = {'order_id': f'{_constants.Order_ID}-{call_index}'}

            out = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments)
            return out

        with ThreadPoolExecutor(max_workers=_parallel_call_count) as executor:
            futures = []

            for call_index in range(_parallel_call_count):
                futures.append(executor.submit(one_call, call_index))

            bodies = []

            for future in futures:
                bodies.append(future.result())

        # Every parallel call succeeded ..
        for body in bodies:
            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        # .. and every one of them is audited.
        events = _audit.wait_for_events(
            audit_db_path, _parallel_call_count,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        for event in events:
            assert event['outcome'] == AuditOutcome.OK, event
            assert event['endpoint'] == _constants.Service_Order_Status, event

# ################################################################################################################################

    def test_deleting_a_gateway_removes_its_routing(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)

        # The gateway serves before the deletion ..
        response = _helpers.initialize_response(client)
        assert response.status_code == OK, response.text

        try:
            # .. one re-import deletes it and its url_path stops existing ..
            overrides = {_constants.Gateway_Lifecycle: {'should_delete': True}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def path_is_gone() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code == NOT_FOUND
                return out

            _wait_until(path_is_gone, 'the deleted gateway answers 404')

        finally:
            # .. and the standard configuration recreates it for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def gateway_is_back() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code == OK
                return out

            _wait_until(gateway_is_back, 'the recreated gateway serves again')

# ################################################################################################################################
# ################################################################################################################################
