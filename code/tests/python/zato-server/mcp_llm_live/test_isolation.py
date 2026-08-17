# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK

# local
import _agent
import _audit
import _constants
import _enmasse
import _helpers
from _client import MCPClient

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_

    MCPClient = MCPClient

# ################################################################################################################################
# ################################################################################################################################

# How long a re-imported change may take to reach live enforcement, in seconds
_reimport_timeout = 60

# How often to poll for it, in seconds
_reimport_poll_interval = 0.5

# How long to give the asynchronous audit writer before asserting that nothing landed, in seconds
_audit_silence_wait = 2

# Every trace key any option family can write - the pass-through side of each
# isolation pair must carry none of them
_all_trace_keys = (
    'pii_removed',
    'nulls_removed',
    'whitespace_chars_removed',
    'base64_blobs_removed',
    'unicode_chars_removed',
    'markup_items_removed',
    'urls_flagged',
    'was_truncated',
    'tokens_before',
    'tokens_after',
    'reject_kind',
    'agent_filter',
)

# What the stable-replacement PII gateways make of the network field - the numbering
# starts at one inside every response, never carrying over from another one
_network_replaced = 'primary REPLACED_IPV4_1 standby REPLACED_IPV4_1 gateway REPLACED_IPV4_2'

# The stable replacement the one email of the record becomes
_replacement_email_stable = 'REPLACED_EMAIL_1'

# A URL path that shares the isolation pair's prefix but belongs to no gateway
_path_unrouted = '/mcp/llm/crm-nothing'

# How many invoices make a response that goes over the shaping gateways' cap
_oversized_count = '200'

# ################################################################################################################################
# ################################################################################################################################

def _make_client_a(zato_server:'anydict') -> 'MCPClient':
    """ A client for the A side of the isolation pair, on the shared credentials
    both sides accept.
    """

    out = _helpers.make_client(zato_server, _constants.Path_Iso_A, auth=zato_server['basic_auth_shared'])
    return out

# ################################################################################################################################

def _make_client_b(zato_server:'anydict') -> 'MCPClient':
    """ A client for the B side of the isolation pair, on the same shared credentials.
    """

    out = _helpers.make_client(zato_server, _constants.Path_Iso_B, auth=zato_server['basic_auth_shared'])
    return out

# ################################################################################################################################

def _call_customer(zato_server:'anydict', url_path:'str', gateway_name:'str') -> 'tuple':
    """ One customer call through the given gateway on the main credentials,
    returning the record and the audit data document of the call's event.
    """

    audit_db_path = zato_server['audit_db_path']
    min_id = _audit.last_event_id(audit_db_path)

    client = _helpers.make_client(zato_server, url_path)
    session_id = _helpers.open_session(client)

    body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get,
        {'customer_id': _constants.Customer_ID})

    events = _audit.wait_for_events(
        audit_db_path, 1,
        object_name=gateway_name,
        event_type=AuditEvent.MCP_Tools_Call,
        min_id=min_id)

    out = body, events[-1]['data']
    return out

# ################################################################################################################################

def _assert_no_trace_keys(event_data:'anydict') -> 'None':
    """ The audit data document of a pass-through call carries no trace key of any family.
    """

    for key in _all_trace_keys:
        assert key not in event_data, (key, event_data)

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

class TestToolIsolation:
    """ A tool assigned to one gateway does not exist on any other - not in the listing
    and not for calls either, and the failed attempt lands in the right gateway's audit log.
    """

# ################################################################################################################################

    def test_a_tool_of_one_gateway_does_not_exist_on_the_others(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        # The probe service is assigned to A but neither to B nor to C ..
        client_a = _make_client_a(zato_server)
        session_a = _helpers.open_session(client_a)

        tools = _helpers.list_tools(client_a, session_a)
        tools_a = _helpers.get_tool_names(tools)
        assert _constants.Service_Deploy_Probe in tools_a, tools_a

        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)

        tools = _helpers.list_tools(client_b, session_b)
        tools_b = _helpers.get_tool_names(tools)
        assert _constants.Service_Deploy_Probe not in tools_b, tools_b

        bearer = _helpers.bearer_headers(zato_server['bearer_static_token'])
        client_c = _helpers.make_client(zato_server, _constants.Path_Iso_C, auth=None)
        session_c = _helpers.open_session(client_c, extra_headers=bearer)

        tools = _helpers.list_tools(client_c, session_c, extra_headers=bearer)
        tools_c = _helpers.get_tool_names(tools)
        assert tools_c == [_constants.Service_Order_Status], tools_c

        # .. calling it on B is the unknown-tool error, audited against B ..
        min_id = _audit.last_event_id(audit_db_path)

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Deploy_Probe, {'revision': 'one'})
        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Iso_B,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['endpoint'] == _constants.Service_Deploy_Probe, event

        # .. and calling a CRM tool on C fails the same way, audited against C.
        min_id = _audit.last_event_id(audit_db_path)

        body = _helpers.call_tool(client_c, session_c, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID}, extra_headers=bearer)
        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Iso_C,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['endpoint'] == _constants.Service_Customer_Get, event

# ################################################################################################################################
# ################################################################################################################################

class TestProcessingIsolation:
    """ The same service behaves per each gateway's own options - one side transforms
    and traces, the other passes content through untouched with no trace keys.
    """

# ################################################################################################################################

    def test_the_same_service_processes_differently_per_gateway(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        arguments = {'customer_id': _constants.Customer_ID}

        # Through A, whose PII removal is on, the email is a token ..
        min_id = _audit.last_event_id(audit_db_path)

        client_a = _make_client_a(zato_server)
        session_a = _helpers.open_session(client_a)

        body = _helpers.call_tool(client_a, session_a, _constants.Service_Customer_Get, arguments)
        data = _helpers.get_result_data(body)

        assert data['email'] == _replacement_email_stable, data['email']
        assert _constants.Customer_Email not in str(data), data

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Iso_A,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data_a = events[-1]['data']
        assert event_data_a['pii_removed']['email'] == 1, event_data_a

        # .. A's row carries only its own family's trace keys ..
        assert 'nulls_removed' not in event_data_a, event_data_a
        assert 'was_truncated' not in event_data_a, event_data_a
        assert 'markup_items_removed' not in event_data_a, event_data_a

        # .. and through B, whose PII removal is off, the same input comes back raw
        # with no trace key at all.
        min_id = _audit.last_event_id(audit_db_path)

        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Customer_Get, arguments)
        data = _helpers.get_result_data(body)

        assert data['email'] == _constants.Customer_Email, data['email']

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Iso_B,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        _assert_no_trace_keys(events[-1]['data'])

# ################################################################################################################################

    def test_each_option_family_stays_within_its_gateway(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        # For every family, the same call runs through the gateway that has the family on
        # and through the B side that has everything off - only the former transforms and traces.

        # Shaping - the oversized listing truncates on the shaping gateway ..
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Shaping_Truncate)
        session_id = _helpers.open_session(client)

        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, {'count': _oversized_count})
        data = _helpers.get_result_data(body)
        assert len(data['invoices']) < int(_oversized_count), len(data['invoices'])

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Shaping_Truncate,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        assert events[-1]['data']['was_truncated'] is True, events[-1]['data']

        # .. while B returns the whole listing with no trace keys ..
        min_id = _audit.last_event_id(audit_db_path)

        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Invoice_List, {'count': _oversized_count})
        data = _helpers.get_result_data(body)
        assert len(data['invoices']) == int(_oversized_count), len(data['invoices'])

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Iso_B,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        _assert_no_trace_keys(events[-1]['data'])

        # .. compaction strips the nulls only on the compaction gateway ..
        body, event_data = _call_customer(zato_server, _constants.Path_Compaction, _constants.Gateway_Compaction)
        data = _helpers.get_result_data(body)

        assert 'fax' not in data, data
        assert event_data['nulls_removed'] > 0, event_data

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID})
        data = _helpers.get_result_data(body)
        assert data['fax'] is None, data

        # .. content safety cleans the notes only on the safety gateway ..
        body, event_data = _call_customer(zato_server, _constants.Path_Safety, _constants.Gateway_Safety)
        data = _helpers.get_result_data(body)

        assert '<script>' not in data['notes'], data['notes']
        assert event_data['markup_items_removed'] >= 1, event_data

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID})
        data = _helpers.get_result_data(body)
        assert '<script>' in data['notes'], data['notes']

        # .. validation refuses bad arguments only on the validating gateway ..
        validate_client = _helpers.make_client(zato_server, _constants.Path_Validate)
        validate_session = _helpers.open_session(validate_client)

        body = _helpers.call_tool(validate_client, validate_session, _constants.Service_Customer_Get, {})
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        body = _helpers.call_tool(client_b, session_b, _constants.Service_Customer_Get, {})
        assert 'error' not in body, body

        # .. and agent filters are advertised only on the filters gateway.
        filters_client = _helpers.make_client(zato_server, _constants.Path_Filters)
        filters_session = _helpers.open_session(filters_client)

        tools = _helpers.list_tools(filters_client, filters_session)
        first_tool = tools[0]
        properties = first_tool['inputSchema']['properties']
        assert 'response_filter' in properties, first_tool

        tools = _helpers.list_tools(client_b, session_b)
        first_tool = tools[0]
        properties = first_tool['inputSchema']['properties']
        assert 'response_filter' not in properties, first_tool

# ################################################################################################################################

    def test_stable_replacements_do_not_leak_across_gateways_or_responses(self, zato_server:'anydict') -> 'None':

        arguments = {'customer_id': _constants.Customer_ID}

        # Two responses in a row through A - the numbering starts at one inside each,
        # never carrying over from the response before ..
        client_a = _make_client_a(zato_server)
        session_a = _helpers.open_session(client_a)

        body = _helpers.call_tool(client_a, session_a, _constants.Service_Customer_Get, arguments)
        first = _helpers.get_result_data(body)

        body = _helpers.call_tool(client_a, session_a, _constants.Service_Customer_Get, arguments)
        second = _helpers.get_result_data(body)

        assert first['network'] == _network_replaced, first['network']
        assert second['network'] == _network_replaced, second['network']

        # .. and the same input through the PII gateway, another stable-replacement gateway,
        # gets the same fresh numbering - no mapping travels between gateways.
        pii_client = _helpers.make_client(zato_server, _constants.Path_PII)
        pii_session = _helpers.open_session(pii_client)

        body = _helpers.call_tool(pii_client, pii_session, _constants.Service_Customer_Get, arguments)
        third = _helpers.get_result_data(body)

        assert third['network'] == _network_replaced, third['network']
        assert third['email'] == _replacement_email_stable, third['email']

# ################################################################################################################################
# ################################################################################################################################

class TestSecurityIsolation:
    """ Credentials belong to groups and groups to gateways - what opens one door
    does not open another, and group changes cut off only their own gateway.
    """

# ################################################################################################################################

    def test_credentials_of_one_group_do_not_open_another_gateway(self, zato_server:'anydict') -> 'None':

        # The main basic auth definition sits in A's group but not in B's or C's ..
        client = _helpers.make_client(zato_server, _constants.Path_Iso_A)
        response = _helpers.initialize_response(client)
        assert response.status_code == OK, response.text

        client = _helpers.make_client(zato_server, _constants.Path_Iso_B)
        response = _helpers.initialize_response(client)
        assert response.status_code == FORBIDDEN, response.text

        client = _helpers.make_client(zato_server, _constants.Path_Iso_C)
        response = _helpers.initialize_response(client)
        assert response.status_code == FORBIDDEN, response.text

        # .. and C's own bearer token opens neither A nor B.
        bearer = _helpers.bearer_headers(zato_server['bearer_static_token'])

        client = _helpers.make_client(zato_server, _constants.Path_Iso_A, auth=None)
        response = _helpers.initialize_response(client, extra_headers=bearer)
        assert response.status_code == FORBIDDEN, response.text

        client = _helpers.make_client(zato_server, _constants.Path_Iso_B, auth=None)
        response = _helpers.initialize_response(client, extra_headers=bearer)
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################

    def test_removing_a_shared_definition_from_one_group_cuts_off_only_that_gateway(
        self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        # The shared definition opens both A and B ..
        client_a = _make_client_a(zato_server)
        client_b = _make_client_b(zato_server)

        response = _helpers.initialize_response(client_a)
        assert response.status_code == OK, response.text

        response = _helpers.initialize_response(client_b)
        assert response.status_code == OK, response.text

        try:
            # .. one re-import removes it from A's group only ..
            config = _enmasse.build_suite_config(shared_a_members=[_constants.Sec_Basic])
            _enmasse.run_import(server_directory, config)

            def a_refuses() -> 'bool':
                response = _helpers.initialize_response(client_a)
                out = response.status_code == FORBIDDEN
                return out

            _wait_until(a_refuses, 'the removal reached enforcement on A')

            # .. B keeps accepting the very same credentials ..
            response = _helpers.initialize_response(client_b)
            assert response.status_code == OK, response.text

            # .. and A's other definition keeps working, so A itself is alive.
            main_client = _helpers.make_client(zato_server, _constants.Path_Iso_A)
            response = _helpers.initialize_response(main_client)
            assert response.status_code == OK, response.text

        finally:
            # The standard groups always come back for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def a_accepts() -> 'bool':
                response = _helpers.initialize_response(client_a)
                out = response.status_code == OK
                return out

            _wait_until(a_accepts, 'the restored group reached enforcement on A')

# ################################################################################################################################
# ################################################################################################################################

class TestSessionIsolation:
    """ A session lives inside one gateway and belongs to one caller -
    it opens no other gateway and serves no other caller.
    """

# ################################################################################################################################

    def test_a_session_of_one_gateway_is_refused_by_another(self, zato_server:'anydict') -> 'None':

        client_a = _make_client_a(zato_server)
        client_b = _make_client_b(zato_server)

        session_a = _helpers.open_session(client_a)
        session_b = _helpers.open_session(client_b)

        # A's session opens nothing on B ..
        response = client_b.jsonrpc('tools/list', session_id=session_a)
        assert response.status_code == BAD_REQUEST, response.text

        # .. deleting A's session leaves B's sessions untouched ..
        response = client_a.delete_session(session_a)
        assert response.status_code == OK, response.text

        tools = _helpers.list_tools(client_b, session_b)
        assert tools, tools

        # .. and the deleted session is unknown to B just the same.
        response = client_b.delete_session(session_a)
        assert response.status_code == NOT_FOUND, response.text

# ################################################################################################################################

    def test_a_session_of_one_caller_is_refused_for_another(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # Two callers with different credentials, both accepted on A ..
        client_shared = _make_client_a(zato_server)
        client_main = _helpers.make_client(zato_server, _constants.Path_Iso_A)

        session_shared = _helpers.open_session(client_shared)
        session_main = _helpers.open_session(client_main)

        assert session_shared != session_main, (session_shared, session_main)

        # .. neither caller can use the other's session ..
        response = client_main.jsonrpc('tools/list', session_id=session_shared)
        assert response.status_code == BAD_REQUEST, response.text

        response = client_shared.jsonrpc('tools/list', session_id=session_main)
        assert response.status_code == BAD_REQUEST, response.text

        # .. each caller keeps working within its own session ..
        tools = _helpers.list_tools(client_shared, session_shared)
        assert tools, tools

        tools = _helpers.list_tools(client_main, session_main)
        assert tools, tools

        # .. and every audit row attributes the session to the right caller.
        events = _audit.wait_for_events(
            audit_db_path, 2,
            object_name=_constants.Gateway_Iso_A,
            event_type=AuditEvent.MCP_Tools_List,
            min_id=min_id)

        for event in events:

            if event['sub_key'] == session_shared:
                if event['outcome'] == AuditOutcome.OK:
                    assert event['ext_client_id'] == _constants.Sec_Basic_Shared, event

            if event['sub_key'] == session_main:
                if event['outcome'] == AuditOutcome.OK:
                    assert event['ext_client_id'] == _constants.Sec_Basic, event

# ################################################################################################################################
# ################################################################################################################################

class TestSkillIsolation:
    """ Each gateway serves only its own skills - the neighbor's skills are neither
    listed nor readable, while its own stay unaffected.
    """

# ################################################################################################################################

    def test_skills_do_not_leak_between_gateways(self, zato_server:'anydict') -> 'None':

        client_a = _make_client_a(zato_server)
        client_b = _make_client_b(zato_server)

        session_a = _helpers.open_session(client_a)
        session_b = _helpers.open_session(client_b)

        # A lists only its own skill ..
        response = client_a.jsonrpc('prompts/list', session_id=session_a)
        prompts_a = response.json()['result']['prompts']

        names_a = []
        for prompt in prompts_a:
            names_a.append(prompt['name'])

        assert names_a == [_constants.Skill_House_Style], names_a

        # .. B lists only its own ..
        response = client_b.jsonrpc('prompts/list', session_id=session_b)
        prompts_b = response.json()['result']['prompts']

        names_b = []
        for prompt in prompts_b:
            names_b.append(prompt['name'])

        assert names_b == [_constants.Skill_Iso_B], names_b

        # .. reading A's skill on B fails ..
        params = {'name': _constants.Skill_House_Style}
        response = client_b.jsonrpc('prompts/get', params=params, session_id=session_b)

        body = response.json()
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        # .. and B's own skill stays readable.
        params = {'name': _constants.Skill_Iso_B}
        response = client_b.jsonrpc('prompts/get', params=params, session_id=session_b)

        body = response.json()
        messages = body['result']['messages']
        assert messages, body

# ################################################################################################################################
# ################################################################################################################################

class TestRoutingIsolation:
    """ URL paths with a shared prefix route to their own gateways only,
    and a path that matches neither is a 404 with no audit trace anywhere.
    """

# ################################################################################################################################

    def test_a_shared_path_prefix_routes_to_the_right_gateway(self, zato_server:'anydict') -> 'None':

        # The pair's paths differ only past the shared /mcp/llm/crm prefix -
        # each answers with its own tool set, so each request reached its own gateway.
        client_a = _make_client_a(zato_server)
        session_a = _helpers.open_session(client_a)

        tools = _helpers.list_tools(client_a, session_a)
        tools_a = _helpers.get_tool_names(tools)
        assert _constants.Service_Deploy_Probe in tools_a, tools_a

        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)

        tools = _helpers.list_tools(client_b, session_b)
        tools_b = _helpers.get_tool_names(tools)
        assert _constants.Service_Deploy_Probe not in tools_b, tools_b

# ################################################################################################################################

    def test_an_unrouted_path_is_a_404_with_no_audit_event(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # The path continues the pair's shared prefix but belongs to no gateway ..
        client = _helpers.make_client(zato_server, _path_unrouted, auth=zato_server['basic_auth_shared'])

        response = _helpers.initialize_response(client)
        assert response.status_code == NOT_FOUND, response.text

        # .. and after giving the audit writer time to run, neither neighbor has a new event.
        time.sleep(_audit_silence_wait)

        events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Iso_A, min_id=min_id)
        assert not events, events

        events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Iso_B, min_id=min_id)
        assert not events, events

# ################################################################################################################################
# ################################################################################################################################

class TestLifecycleIsolation:
    """ Reconfiguring, deactivating or deleting one gateway leaves its neighbor's
    sessions, tools and audit trail untouched.
    """

# ################################################################################################################################

    def test_changes_to_one_gateway_leave_the_neighbor_alone(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']
        audit_db_path = zato_server['audit_db_path']

        # B's session opens before anything happens to A ..
        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)

        client_a = _make_client_a(zato_server)

        try:
            # .. A goes inactive - B's live session keeps serving ..
            overrides = {_constants.Gateway_Iso_A: {'is_active': False}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def a_refuses() -> 'bool':
                response = _helpers.initialize_response(client_a)
                out = response.status_code != OK
                return out

            _wait_until(a_refuses, 'the inactive A refuses requests')

            tools = _helpers.list_tools(client_b, session_b)
            tools_b = _helpers.get_tool_names(tools)
            assert sorted(tools_b) == sorted(_constants.Service_List_CRM), tools_b

            # .. A is deleted outright - B's session, tools and audit trail are still intact ..
            min_id = _audit.last_event_id(audit_db_path)

            overrides = {_constants.Gateway_Iso_A: {'should_delete': True}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def a_is_gone() -> 'bool':
                response = _helpers.initialize_response(client_a)
                out = response.status_code == NOT_FOUND
                return out

            _wait_until(a_is_gone, 'the deleted A answers 404')

            body = _helpers.call_tool(client_b, session_b, _constants.Service_Order_Status,
                {'order_id': _constants.Order_ID})

            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

            events = _audit.wait_for_events(
                audit_db_path, 1,
                object_name=_constants.Gateway_Iso_B,
                event_type=AuditEvent.MCP_Tools_Call,
                min_id=min_id)

            assert events[-1]['outcome'] == AuditOutcome.OK, events

        finally:
            # The standard configuration recreates A for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def a_serves() -> 'bool':
                response = _helpers.initialize_response(client_a)
                out = response.status_code == OK
                return out

            _wait_until(a_serves, 'the recreated A serves again')

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentIsolation:
    """ Two agents on gateways with contradictory options at the same time - each
    transcript shows only its own gateway's behavior and each audit trail stays home.
    """

# ################################################################################################################################

    def test_concurrent_agents_on_contradictory_gateways(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # One agent runs against the truncating gateway, the other against the blocking one,
        # both asking for the same oversized listing at the same time.
        client_truncate = _helpers.make_client(zato_server, _constants.Path_Shaping_Truncate)
        client_block = _helpers.make_client(zato_server, _constants.Path_Shaping_Block)

        # The invoice tool takes only a count, so the task names no customer.
        task = (
            f'Use the invoice tool to list the last {_oversized_count} invoices '
            'and report their invoice numbers. If the tools cannot give you the data, say so plainly.')

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_truncate = executor.submit(_agent.run_agent, client_truncate, task)
            future_block = executor.submit(_agent.run_agent, client_block, task)

            result_truncate = future_truncate.result()
            result_block = future_block.result()

        # Each conversation ran in its own session ..
        assert result_truncate.session_id != result_block.session_id, \
            (result_truncate.session_id, result_block.session_id)

        # .. the truncating side saw cut but successful listings ..
        truncate_calls = []

        for call in result_truncate.tool_calls:
            if call.tool_name == _constants.Service_Invoice_List:
                truncate_calls.append(call)

        assert truncate_calls, result_truncate.messages

        for call in truncate_calls:
            assert not call.is_error, call.result_text

        # .. the blocking side saw at least one refusal ..
        blocked_calls = []

        for call in result_block.tool_calls:
            if call.tool_name == _constants.Service_Invoice_List:
                if call.is_error:
                    blocked_calls.append(call)

        assert blocked_calls, result_block.messages

        # .. and in the audit trail, each gateway holds only its own agent's events,
        # with no CID appearing under both.
        events_truncate = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Shaping_Truncate, min_id=min_id)

        events_block = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Shaping_Block, min_id=min_id)

        cids_truncate = set()

        for event in events_truncate:
            assert event['sub_key'] == result_truncate.session_id, event
            cids_truncate.add(event['cid'])

        cids_block = set()

        for event in events_block:
            assert event['sub_key'] == result_block.session_id, event
            cids_block.add(event['cid'])

        assert not (cids_truncate & cids_block), (cids_truncate, cids_block)

        # .. with the truncation and the refusal each traced on its own side only.
        was_truncated_seen = False

        for event in events_truncate:
            if event['data'].get('was_truncated'):
                was_truncated_seen = True
            assert 'reject_kind' not in event['data'], event['data']

        assert was_truncated_seen, events_truncate

        reject_seen = False

        for event in events_block:
            if event['data'].get('reject_kind') == 'size':
                reject_seen = True
            assert 'was_truncated' not in event['data'], event['data']

        assert reject_seen, events_block

# ################################################################################################################################
# ################################################################################################################################

class TestAuditIsolation:
    """ Per-gateway audit queries return only that gateway's events, the counts add up
    exactly and no event ever carries another gateway's name or another caller's identity.
    """

# ################################################################################################################################

    def test_audit_events_never_cross_gateways_or_callers(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        # The counts below are exact, so any in-flight audit write of earlier traffic
        # must land before the snapshot is taken.
        time.sleep(_audit_silence_wait)
        min_id = _audit.last_event_id(audit_db_path)

        # One identical conversation per gateway, each on its own credentials ..
        client_a = _make_client_a(zato_server)
        session_a = _helpers.open_session(client_a)
        _ = _helpers.list_tools(client_a, session_a)

        client_b = _make_client_b(zato_server)
        session_b = _helpers.open_session(client_b)
        _ = _helpers.list_tools(client_b, session_b)

        bearer = _helpers.bearer_headers(zato_server['bearer_static_token'])
        client_c = _helpers.make_client(zato_server, _constants.Path_Iso_C, auth=None)
        session_c = _helpers.open_session(client_c, extra_headers=bearer)
        _ = _helpers.list_tools(client_c, session_c, extra_headers=bearer)

        # .. each gateway's query returns exactly its own two events ..
        events_a = _audit.wait_for_events(audit_db_path, 2, object_name=_constants.Gateway_Iso_A, min_id=min_id)
        events_b = _audit.wait_for_events(audit_db_path, 2, object_name=_constants.Gateway_Iso_B, min_id=min_id)
        events_c = _audit.wait_for_events(audit_db_path, 2, object_name=_constants.Gateway_Iso_C, min_id=min_id)

        assert len(events_a) == 2, events_a
        assert len(events_b) == 2, events_b
        assert len(events_c) == 2, events_c

        # .. every event carries its own gateway's name, its own session and its own caller ..
        for event in events_a:
            assert event['object_name'] == _constants.Gateway_Iso_A, event
            assert event['sub_key'] == session_a, event
            assert event['ext_client_id'] == _constants.Sec_Basic_Shared, event

        for event in events_b:
            assert event['object_name'] == _constants.Gateway_Iso_B, event
            assert event['sub_key'] == session_b, event
            assert event['ext_client_id'] == _constants.Sec_Basic_Shared, event

        for event in events_c:
            assert event['object_name'] == _constants.Gateway_Iso_C, event
            assert event['sub_key'] == session_c, event
            assert event['ext_client_id'] == _constants.Sec_Bearer_Static, event

        # .. the counts add up exactly - the three queries cover everything the trio wrote ..
        all_events = _audit.read_events(audit_db_path, min_id=min_id)

        trio_events = []

        for event in all_events:
            if event['object_name'] in (_constants.Gateway_Iso_A, _constants.Gateway_Iso_B, _constants.Gateway_Iso_C):
                trio_events.append(event)

        total = len(events_a) + len(events_b) + len(events_c)
        assert len(trio_events) == total, (len(trio_events), total)

        # .. and no CID ever appears under more than one gateway.
        cids = set()

        for event in trio_events:
            assert event['cid'] not in cids, event
            cids.add(event['cid'])

# ################################################################################################################################
# ################################################################################################################################
